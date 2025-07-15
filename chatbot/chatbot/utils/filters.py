# === chatbot/utils/filters.py ===
from typing import List, Dict, Optional

def filter_chunks_by_metadata(chunks: List[Dict], metadata_filter: Optional[Dict[str, str]] = None) -> List[Dict]:
    """
    Filters chunks by specified metadata. Example filter:
    metadata_filter = {"source": "SharePoint", "author": "Alice"}
    """
    if not metadata_filter:
        return chunks

    def matches(chunk: Dict) -> bool:
        metadata = chunk.get("metadata", {})
        for k, v in metadata_filter.items():
            if metadata.get(k) != v:
                return False
        return True

    return [chunk for chunk in chunks if matches(chunk)]


# === chatbot/ranking.py ===
from typing import List, Dict
from chatbot.utils.embeddings import embed_text_huggingface, embed_text_bedrock
from chatbot.utils.constants import EMBEDDING_ENGINE
import numpy as np
import logging

logger = logging.getLogger(__name__)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def rank_chunks_by_similarity(query: str, chunks: List[Dict]) -> List[Dict]:
    logger.info(f"[Ranking] Using engine: {EMBEDDING_ENGINE}")
    if EMBEDDING_ENGINE == "bedrock":
        return rank_with_bedrock(query, chunks)
    return rank_with_huggingface(query, chunks)


def rank_with_huggingface(query: str, chunks: List[Dict]) -> List[Dict]:
    query_vec = embed_text_huggingface(query)
    for chunk in chunks:
        chunk_vec = embed_text_huggingface(chunk["content"])
        chunk["score"] = cosine_similarity(query_vec, chunk_vec)
    return sorted(chunks, key=lambda x: x["score"], reverse=True)


def rank_with_bedrock(query: str, chunks: List[Dict]) -> List[Dict]:
    try:
        query_vec = embed_text_bedrock(query)
        for chunk in chunks:
            chunk_vec = embed_text_bedrock(chunk["content"])
            chunk["score"] = cosine_similarity(query_vec, chunk_vec)
        return sorted(chunks, key=lambda x: x["score"], reverse=True)
    except Exception as e:
        logger.warning(f"[Ranking] Bedrock rerank failed: {e}. Falling back to HuggingFace.")
        return rank_with_huggingface(query, chunks)
