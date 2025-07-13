# tests/test_retrieval_layer.py

import pytest
from chatbot.rag import retrieval_layer, rag_router


def test_bedrock_retrieval():
    chunks = retrieval_layer.query_bedrock_knowledge_base("What is S3?")
    assert isinstance(chunks, list)
    if chunks:
        assert "content" in chunks[0]
        assert "metadata" in chunks[0]


def test_opensearch_retrieval():
    chunks = retrieval_layer.query_opensearch("Explain IAM roles")
    assert isinstance(chunks, list)
    if chunks:
        assert "content" in chunks[0]
        assert "metadata" in chunks[0]


def test_hybrid_rag_router():
    results = rag_router.hybrid_rag_router("How does VPC peering work?", top_k=4)
    assert isinstance(results, list)
    if results:
        assert "content" in results[0]
        assert results[0]["source"] in ["bedrock_kb", "opensearch"]
