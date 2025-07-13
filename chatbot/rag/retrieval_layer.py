# chatbot/rag/retrieval_layer.py

import os
from typing import List, Dict, Literal, Optional
from chatbot.utils.constants import (
    RETRIEVAL_BACKEND,
    BEDROCK_KB_ID,
    BEDROCK_REGION,
    MAX_CHUNKS,
)
from chatbot.logger import logger
from chatbot.ranking import rank_chunks_by_similarity
from chatbot.utils.text_utils import clean_text

# Optional: boto3 Bedrock client for KB
import boto3

if RETRIEVAL_BACKEND == "bedrock":
    bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

# Optional: OpenSearch connector
try:
    from chatbot.rag.opensearch_client import search_opensearch
except ImportError:
    search_opensearch = None


def get_relevant_chunks(query: str, top_k: int = MAX_CHUNKS) -> List[Dict]:
    """
    Unified interface to retrieve relevant context chunks.
    Supports Bedrock KB or OpenSearch, based on config.
    """
    logger.info(f"[Retrieval] Backend: {RETRIEVAL_BACKEND} | Query: {query}")

    if RETRIEVAL_BACKEND == "bedrock":
        return query_bedrock_knowledge_base(query, top_k)

    elif RETRIEVAL_BACKEND == "opensearch" and search_opensearch:
        return query_opensearch(query, top_k)

    else:
        logger.warning(f"Unknown retrieval backend or OpenSearch client missing.")
        return []


def query_bedrock_knowledge_base(query: str, top_k: int) -> List[Dict]:
    """
    Query Amazon Bedrock Knowledge Base and extract normalized chunks.
    """
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=BEDROCK_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": top_k}},
        )

        results = response.get("retrievalResults", [])
        chunks = []
        for item in results:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            chunks.append({
                "content": clean_text(content),
                "metadata": metadata,
                "source": "bedrock_kb"
            })

        return chunks

    except Exception as e:
        logger.exception(f"[Bedrock KB] Retrieval failed: {e}")
        return []


def query_opensearch(query: str, top_k: int) -> List[Dict]:
    """
    Query OpenSearch index for relevant chunks using similarity search.
    """
    try:
        raw_hits = search_opensearch(query, k=top_k)
        chunks = []
        for hit in raw_hits:
            chunks.append({
                "content": clean_text(hit["_source"].get("content", "")),
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit["_score"],
                "source": "opensearch"
            })

        return chunks

    except Exception as e:
        logger.exception(f"[OpenSearch] Retrieval failed: {e}")
        return []


def get_ranked_relevant_chunks(query: str, all_chunks: List[Dict], top_k: int = MAX_CHUNKS) -> List[Dict]:
    """
    Rerank chunks using local embedding similarity (fallback or hybrid mode).
    """
    if not all_chunks:
        return []

    ranked = rank_chunks_by_similarity(query, all_chunks)
    return ranked[:top_k]
