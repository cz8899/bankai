# Lightweight wrapper around ChromaDB for memory storage

from chromadb import PersistentClient
from chromadb.config import Settings
from uuid import uuid4
from typing import Dict

# Configure ChromaDB location (mounted volume or embedded)
chroma_client = PersistentClient(path="chroma_data", settings=Settings(anonymized_telemetry=False))
memory_collection = chroma_client.get_or_create_collection("devgenius_memory")


def store_summary_if_relevant(summary: str, metadata: Dict) -> None:
    """
    Stores a summary into ChromaDB with associated metadata.
    Args:
        summary: The distilled memory to store.
        metadata: Dict including timestamp, user, tags, etc.
    """
    if not summary or len(summary.split()) < 10:
        return  # Too short to store

    memory_collection.add(
        documents=[summary],
        ids=[str(uuid4())],
        metadatas=[metadata]
    )
