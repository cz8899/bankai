# chatbot/rag/retrieval_layer.py (enhanced)

import os
from typing import List, Dict, Literal, Optional
from chatbot.utils.constants import (
    RETRIEVAL_BACKEND,
    BEDROCK_KB_ID,
    BEDROCK_REGION,
    MAX_CHUNKS,
    EMBEDDING_ENGINE  # "bedrock" | "huggingface"
)
from chatbot.logger import logger
from chatbot.ranking import rank_chunks_by_similarity, rank_with_bedrock
from chatbot.utils.text_utils import clean_text
from chatbot.utils.filters import filter_chunks_by_metadata
import boto3

# Bedrock clients
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

# Optional: OpenSearch connector
try:
    from chatbot.rag.opensearch_client import search_opensearch
except ImportError:
    search_opensearch = None


def get_relevant_chunks(query: str, top_k: int = MAX_CHUNKS, metadata_filter: Optional[dict] = None) -> List[Dict]:
    logger.info(f"[Retrieval] Backend: {RETRIEVAL_BACKEND} | Query: {query}")

    chunks = []
    if RETRIEVAL_BACKEND == "bedrock":
        chunks = query_bedrock_knowledge_base(query, top_k)
    elif RETRIEVAL_BACKEND == "opensearch" and search_opensearch:
        chunks = query_opensearch(query, top_k)
    else:
        logger.warning("[Retrieval] Invalid backend or OpenSearch unavailable")
        return []

    if metadata_filter:
        chunks = filter_chunks_by_metadata(chunks, metadata_filter)

    return rerank_chunks(query, chunks, top_k=top_k)


def rerank_chunks(query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
    if not chunks:
        return []

    if EMBEDDING_ENGINE == "huggingface":
        return rank_chunks_by_similarity(query, chunks)[:top_k]
    elif EMBEDDING_ENGINE == "bedrock":
        return rank_with_bedrock(query, chunks)[:top_k]
    else:
        logger.warning("Unknown reranking method. Falling back to default.")
        return chunks[:top_k]


def query_bedrock_knowledge_base(query: str, top_k: int) -> List[Dict]:
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=BEDROCK_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": top_k}},
        )

        results = response.get("retrievalResults", [])
        for r in results:
            yield {
                "content": clean_text(r.get("content", "")),
                "metadata": r.get("metadata", {}),
                "source": "bedrock_kb"
            }

    except Exception as e:
        logger.exception(f"[Bedrock KB] Retrieval failed: {e}")
        return []


def query_opensearch(query: str, top_k: int) -> List[Dict]:
    try:
        raw_hits = search_opensearch(query, k=top_k)
        return [
            {
                "content": clean_text(hit["_source"].get("content", "")),
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit["_score"],
                "source": "opensearch"
            }
            for hit in raw_hits
        ]

    except Exception as e:
        logger.exception(f"[OpenSearch] Retrieval failed: {e}")
        return []
