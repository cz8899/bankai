# chatbot/rag/retrieval_layer.py (final optimized version)

import os
from typing import List, Dict, Optional
from chatbot.utils.constants import (
    RETRIEVAL_BACKEND,
    BEDROCK_KB_ID,
    BEDROCK_REGION,
    MAX_CHUNKS
)
from chatbot.logger import logger
from chatbot.ranking import rank_chunks_by_similarity, rank_with_bedrock
from chatbot.utils.text_utils import clean_text
from chatbot.utils.filters import filter_chunks_by_metadata
from chatbot.utils.config_loader import get_config_value

import boto3

# Load config
score_threshold = get_config_value("chunk_score_threshold", 0.5)
embedding_engine = get_config_value("embedding_engine", "bedrock")

# Bedrock KB Client
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

# Optional: OpenSearch client
try:
    from chatbot.rag.opensearch_client import search_opensearch
except ImportError:
    search_opensearch = None


def get_relevant_chunks(query: str, top_k: int = MAX_CHUNKS, metadata_filter: Optional[dict] = None) -> List[Dict]:
    logger.info(f"[Retrieval] Backend: {RETRIEVAL_BACKEND} | Query: {query}")

    # Step 1: Fetch chunks
    chunks = []
    if RETRIEVAL_BACKEND == "bedrock":
        chunks = list(query_bedrock_knowledge_base(query, top_k))
    elif RETRIEVAL_BACKEND == "opensearch" and search_opensearch:
        chunks = query_opensearch(query, top_k)
    else:
        logger.warning("[Retrieval] Invalid backend or OpenSearch unavailable")
        return []

    # Step 2: Apply metadata filter
    if metadata_filter:
        chunks = filter_chunks_by_metadata(chunks, metadata_filter)

    # Step 3: Rerank and return
    return rerank_chunks(query, chunks, top_k=top_k)


def rerank_chunks(query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
    if not chunks:
        return []

    if embedding_engine == "huggingface":
        reranked = rank_chunks_by_similarity(query, chunks)
    elif embedding_engine == "bedrock":
        reranked = rank_with_bedrock(query, chunks)
    else:
        logger.warning("[Reranking] Unknown method. Skipping rerank.")
        return chunks[:top_k]

    return [c for c in reranked if c.get("score", 1.0) >= score_threshold][:top_k]


def query_bedrock_knowledge_base(query: str, top_k: int):
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=BEDROCK_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": top_k}},
        )
        for result in response.get("retrievalResults", []):
            yield {
                "content": clean_text(result.get("content", "")),
                "metadata": result.get("metadata", {}),
                "source": "bedrock_kb"
            }
    except Exception as e:
        logger.exception(f"[Bedrock KB] Retrieval failed: {e}")


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
