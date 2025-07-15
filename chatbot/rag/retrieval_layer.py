# chatbot/rag/retrieval_layer.py

import os
from typing import List, Dict
from chatbot.utils.constants import (
    RETRIEVAL_BACKEND,
    BEDROCK_KB_ID,
    BEDROCK_REGION,
    MAX_CHUNKS,
)
from chatbot.logger import logger
from chatbot.ranking import rank_chunks_by_similarity
from chatbot.utils.text_utils import clean_text

import boto3

# === Bedrock KB Client ===
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

# === OpenSearch (optional) ===
try:
    from chatbot.rag.opensearch_client import search_opensearch
except ImportError:
    search_opensearch = None


def get_relevant_chunks(query: str, top_k: int = MAX_CHUNKS) -> List[Dict]:
    """
    Unified RAG interface — returns chunks from backend of choice.
    """
    logger.info(f"[Retrieval] Backend: {RETRIEVAL_BACKEND} | Query: {query}")

    if RETRIEVAL_BACKEND == "bedrock":
        return query_bedrock_knowledge_base(query, top_k)

    elif RETRIEVAL_BACKEND == "opensearch" and search_opensearch:
        return query_opensearch(query, top_k)

    else:
        logger.warning("[Retrieval] Unknown backend or OpenSearch not available")
        return []


def query_bedrock_knowledge_base(query: str, top_k: int) -> List[Dict]:
    """
    Queries Bedrock Knowledge Base and formats chunks with metadata.
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
            content = clean_text(item.get("content", ""))
            metadata = item.get("metadata", {})
            chunks.append({
                "content": content,
                "metadata": metadata,
                "score": 0.8,  # Estimated base score for unranked Bedrock KB results
                "source": "bedrock_kb"
            })

        logger.info(f"[Bedrock KB] Retrieved {len(chunks)} chunks")
        return chunks

    except Exception as e:
        logger.exception(f"[Bedrock KB] Retrieval failed: {e}")
        return []


def query_opensearch(query: str, top_k: int) -> List[Dict]:
    """
    Retrieves top chunks from OpenSearch with similarity scores.
    """
    try:
        raw_hits = search_opensearch(query, k=top_k)
        chunks = []
        for hit in raw_hits:
            chunks.append({
                "content": clean_text(hit["_source"].get("content", "")),
                "metadata": hit["_source"].get("metadata", {}),
                "score": hit.get("_score", 0.0),
                "source": "opensearch"
            })

        logger.info(f"[OpenSearch] Retrieved {len(chunks)} chunks")
        return chunks

    except Exception as e:
        logger.exception(f"[OpenSearch] Retrieval failed: {e}")
        return []


def get_ranked_relevant_chunks(query: str, all_chunks: List[Dict], top_k: int = MAX_CHUNKS) -> List[Dict]:
    """
    Final reranker for relevance based on local embedding similarity.
    """
    if not all_chunks:
        return []

    ranked = rank_chunks_by_similarity(query, all_chunks)
    return ranked[:top_k]
