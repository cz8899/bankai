# chatbot/rag/retrieval_layer.py

import os
import boto3
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

# === Configurable Thresholds and Engine Selection ===
def _env_float(key: str, fallback: float) -> float:
    try:
        return float(os.getenv(key, fallback))
    except (TypeError, ValueError):
        return fallback

score_threshold: float = _env_float("CHUNK_SCORE_THRESHOLD", get_config_value("chunk_score_threshold", 0.5))
embedding_engine: str = os.getenv("EMBEDDING_ENGINE", get_config_value("embedding_engine", "bedrock"))

# === Bedrock Knowledge Base Client ===
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

# === Optional OpenSearch Client ===
try:
    from chatbot.rag.opensearch_client import search_opensearch
except ImportError:
    search_opensearch = None


# === Unified Chunk Retrieval Flow ===
def get_relevant_chunks(query: str, top_k: int = MAX_CHUNKS, metadata_filter: Optional[dict] = None) -> List[Dict]:
    logger.info(f"[Retrieval] Backend={RETRIEVAL_BACKEND} | Query={query}")

    chunks: List[Dict] = []

    if RETRIEVAL_BACKEND == "bedrock":
        chunks = list(query_bedrock_knowledge_base(query, top_k))

    elif RETRIEVAL_BACKEND == "opensearch" and search_opensearch:
        chunks = query_opensearch(query, top_k)

    else:
        logger.warning("[Retrieval] Invalid backend or OpenSearch not configured.")
        return []

    if metadata_filter:
        chunks = filter_chunks_by_metadata(chunks, metadata_filter)

    return rerank_chunks(query, chunks, top_k=top_k)


# === Reranking ===
def rerank_chunks(query: str, chunks: List[Dict], top_k: int) -> List[Dict]:
    if not chunks:
        return []

    try:
        if embedding_engine == "huggingface":
            reranked = rank_chunks_by_similarity(query, chunks)
        elif embedding_engine == "bedrock":
            reranked = rank_with_bedrock(query, chunks)
        else:
            logger.warning("[Reranking] Unknown embedding engine. Using raw order.")
            return chunks[:top_k]

        filtered = [c for c in reranked if c.get("score", 1.0) >= score_threshold]
        return filtered[:top_k]

    except Exception as e:
        logger.exception(f"[Reranking] Failed during reranking: {e}")
        return chunks[:top_k]


# === Bedrock KB Retrieval ===
def query_bedrock_knowledge_base(query: str, top_k: int):
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=BEDROCK_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": top_k}},
        )
        results = response.get("retrievalResults", [])
        for result in results:
            yield {
                "content": clean_text(result.get("content", "")),
                "metadata": result.get("metadata", {}),
                "source": "bedrock_kb"
            }

    except Exception as e:
        logger.exception(f"[Bedrock KB] Retrieval failed: {e}")
        return []


# === OpenSearch Retrieval ===
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
