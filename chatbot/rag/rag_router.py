# chatbot/rag/rag_router.py

from chatbot.rag.retrieval_layer import (
    query_bedrock_knowledge_base,
    query_opensearch,
    get_ranked_relevant_chunks
)
from chatbot.utils.synthesizer import synthesize_chunks
from chatbot.agent import call_claude
from chatbot.logger import logger

MIN_CONFIDENCE_THRESHOLD = 0.55  # Confidence reranking cutoff
FALLBACK_TO_CLAUDE = True        # Allow graceful Claude fallback


def hybrid_rag_router(query: str, top_k: int = 5) -> list[dict]:
    """
    RAG Router that combines:
    - Retrieval from Bedrock KB and OpenSearch
    - Multi-vector reranking
    - Score filtering
    - Chunk fusion
    - Fallback to Claude if context is weak
    """
    logger.info(f"[RAG Router] Hybrid query: {query}")

    try:
        # Step 1: Retrieve from multiple vector stores
        kb_chunks = query_bedrock_knowledge_base(query, top_k=5)
        oss_chunks = query_opensearch(query, top_k=5)

        all_chunks = kb_chunks + oss_chunks
        logger.info(f"[RAG Router] Retrieved {len(all_chunks)} chunks")

        # Step 2: Multi-vector rerank
        ranked = get_ranked_relevant_chunks(query, all_chunks, top_k=top_k)

        # Step 3: Score filtering
        filtered = [c for c in ranked if c.get("score", 0) >= MIN_CONFIDENCE_THRESHOLD]
        logger.info(f"[RAG Router] {len(filtered)} chunks passed threshold of {MIN_CONFIDENCE_THRESHOLD}")

        # Step 4: Chunk graph trail (experimental)
        graph_nodes = []
        seen_sources = set()
        for chunk in filtered:
            source = chunk["metadata"].get("source", "")
            if source not in seen_sources:
                graph_nodes.append(chunk)
                seen_sources.add(source)

        # Step 5: Synthesize final context
        if not graph_nodes:
            if FALLBACK_TO_CLAUDE:
                logger.warning("[RAG Router] No strong context — fallback to Claude")
                fallback_answer = call_claude(query)
                return [{
                    "content": fallback_answer,
                    "metadata": {"source": "claude-fallback", "score": 0}
                }]
            return []

        fused = synthesize_chunks(graph_nodes)
        return [{
            "content": fused,
            "metadata": {
                "source": "+".join([c["metadata"].get("source", "Unknown") for c in graph_nodes]),
                "synthesized": True,
                "score": min(c.get("score", 1.0) for c in graph_nodes),
                "chunks_used": len(graph_nodes)
            }
        }]

    except Exception as e:
        logger.exception(f"[RAG Router] Critical failure: {e}")
        if FALLBACK_TO_CLAUDE:
            return [{
                "content": call_claude(query),
                "metadata": {"source": "claude-exception-fallback", "score": 0}
            }]
        return []
