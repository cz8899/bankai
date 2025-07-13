# chatbot/rag/rag_router.py

from chatbot.rag.retrieval_layer import (
    query_bedrock_knowledge_base,
    query_opensearch,
    get_ranked_relevant_chunks
)
from chatbot.logger import logger


def hybrid_rag_router(query: str, top_k: int = 5) -> list[dict]:
    """
    Combines Bedrock KB + OpenSearch results for broader context.
    You can adjust ratios below as needed.
    """
    logger.info(f"[RAG Router] Hybrid retrieval triggered | Query: {query}")

    try:
        bedrock_chunks = query_bedrock_knowledge_base(query, top_k=3)
        os_chunks = query_opensearch(query, top_k=3)

        combined = bedrock_chunks + os_chunks
        ranked_chunks = get_ranked_relevant_chunks(query, combined, top_k=top_k)

        for c in ranked_chunks:
            logger.info(f"[RAG Router] Chunk Source: {c.get('source')} | Snippet: {c['content'][:60]}...")

        return ranked_chunks

    except Exception as e:
        logger.exception(f"[RAG Router] Retrieval failed: {e}")
        return []
