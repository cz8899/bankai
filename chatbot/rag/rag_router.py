# chatbot/rag/rag_router.py

from typing import List, Dict
from chatbot.rag.retrieval_layer import (
    query_bedrock_knowledge_base,
    query_opensearch,
    get_ranked_relevant_chunks
)
from chatbot.utils.synthesizer import synthesize_chunks
from chatbot.agent import call_claude
from chatbot.logger import logger

# === Configurable Constants ===
MIN_CONFIDENCE_THRESHOLD = 0.55  # Minimum chunk confidence score
FALLBACK_TO_CLAUDE = True        # Enable Claude fallback if no strong context


def hybrid_rag_router(query: str, top_k: int = 5) -> List[Dict]:
    """
    RAG Router that:
    - Combines Bedrock KB and OpenSearch
    - Reranks using multi-vector strategy
    - Applies score threshold
    - Performs chunk synthesis
    - Falls back to Claude if needed
    """
    logger.info(f"[RAG Router] Hybrid retrieval triggered | Query: {query}")

    try:
        # === Step 1: Retrieve chunks ===
        kb_chunks = query_bedrock_knowledge_base(query, top_k=top_k)
        os_chunks = query_opensearch(query, top_k=top_k)
        combined_chunks = kb_chunks + os_chunks

        if not combined_chunks:
            logger.warning("[RAG Router] No chunks retrieved")
            return _fallback_to_claude(query, reason="empty-retrieval")

        logger.info(f"[RAG Router] Retrieved {len(combined_chunks)} chunks total")

        # === Step 2: Rerank ===
        reranked = get_ranked_relevant_chunks(query, combined_chunks, top_k=top_k)
        if not reranked:
            logger.warning("[RAG Router] Reranking returned empty result")
            return _fallback_to_claude(query, reason="empty-rerank")

        # === Step 3: Score Filtering ===
        filtered = [c for c in reranked if c.get("score", 0.0) >= MIN_CONFIDENCE_THRESHOLD]
        if not filtered:
            logger.warning("[RAG Router] All chunks below threshold — fallback")
            return _fallback_to_claude(query, reason="score-below-threshold")

        logger.info(f"[RAG Router] {len(filtered)} chunks passed score ≥ {MIN_CONFIDENCE_THRESHOLD}")

        # === Step 4: Build Chunk Graph (dedup sources) ===
        graph_nodes = []
        seen_sources = set()
        for chunk in filtered:
            src = chunk["metadata"].get("source", "unknown")
            if src not in seen_sources:
                graph_nodes.append(chunk)
                seen_sources.add(src)

        if not graph_nodes:
            logger.warning("[RAG Router] No distinct sources available")
            return _fallback_to_claude(query, reason="graph-empty")

        # === Step 5: Chunk Synthesis ===
        synthesized_context = synthesize_chunks(graph_nodes)
        logger.info(f"[RAG Router] Synthesized {len(graph_nodes)} chunks into fused context")

        return [{
            "content": synthesized_context,
            "metadata": {
                "source": "+".join([c["metadata"].get("source", "unknown") for c in graph_nodes]),
                "synthesized": True,
                "score": min(c.get("score", 1.0) for c in graph_nodes),
                "chunks_used": len(graph_nodes)
            }
        }]

    except Exception as e:
        logger.exception(f"[RAG Router] Unhandled exception: {e}")
        return _fallback_to_claude(query, reason="exception")


# === Helper for Graceful Claude Fallback ===
def _fallback_to_claude(query: str, reason: str = "unknown") -> List[Dict]:
    if not FALLBACK_TO_CLAUDE:
        return []

    logger.warning(f"[RAG Router] Falling back to Claude due to: {reason}")
    response = call_claude(query)
    return [{
        "content": response,
        "metadata": {
            "source": f"claude-fallback:{reason}",
            "synthesized": False,
            "score": 0.0,
            "chunks_used": 0
        }
    }]
