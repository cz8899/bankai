# test/test_agent.py

import pytest
from chatbot.agent import call_claude, get_ranked_chunks


def test_call_claude_minimal():
    response = call_claude("Say hello")
    assert isinstance(response, str)
    assert "hello" in response.lower()


def test_get_ranked_chunks_returns_subset():
    dummy_chunks = [{"content": f"Chunk {i}", "metadata": {}} for i in range(10)]
    top_chunks = get_ranked_chunks("test query", dummy_chunks)
    assert len(top_chunks) <= 10
    assert all("content" in c for c in top_chunks)

def test_call_claude_mock(monkeypatch):
    def mock_invoke(messages): return "Mocked Claude Response"
    monkeypatch.setattr(agent, "call_claude", mock_invoke)
    assert agent.call_claude([{"role": "user", "content": "Hi"}]) == "Mocked Claude Response"

def test_chunk_ranking():
    chunks = ["chunk1", "chunk2", "chunk3"]
    ranked = agent.get_ranked_chunks("query", chunks)
    assert len(ranked) <= 5
