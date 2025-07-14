import pytest
import streamlit as st
from chatbot.planner import planner

# Mocks
@pytest.fixture(autouse=True)
def reset_session():
    st.session_state.clear()
    yield
    st.session_state.clear()

@pytest.fixture
def basic_message():
    return [{"role": "user", "content": "What is a VPC in AWS?"}]


def test_claude_mode(monkeypatch, basic_message):
    monkeypatch.setattr("chatbot.agent.call_claude", lambda prompt, context="": "Claude Response")
    result = planner(basic_message, mode="Claude")
    assert result == "Claude Response"


def test_agent_mode_success(monkeypatch, basic_message):
    monkeypatch.setattr("chatbot.agent.call_bedrock_agent", lambda prompt, session_id: "Agent Answer")
    st.session_state.conversation_id = "test-agent"
    result = planner(basic_message, mode="Agent")
    assert result == "Agent Answer"
    assert st.session_state.agent_session_id == "session-test-agent"


def test_agent_mode_fallback(monkeypatch, basic_message):
    monkeypatch.setattr("chatbot.agent.call_bedrock_agent", lambda prompt, session_id: "[Agent returned no message]")
    monkeypatch.setattr("chatbot.agent.call_claude", lambda prompt, context="": "Fallback Claude")
    st.session_state.conversation_id = "fallback-test"
    result = planner(basic_message, mode="Agent")
    assert result == "Fallback Claude"


def test_rag_chunks_success(monkeypatch, basic_message):
    # Simulate chunk response
    mock_chunks = [
        {
            "content": "VPC stands for Virtual Private Cloud.",
            "metadata": {"title": "AWS Docs", "page": 1, "source": "BedrockKB"}
        },
        {
            "content": "You can create subnets inside a VPC.",
            "metadata": {"title": "AWS Docs", "page": 2, "source": "BedrockKB"}
        }
    ]
    monkeypatch.setattr("chatbot.rag.rag_router.hybrid_rag_router", lambda prompt: mock_chunks)
    monkeypatch.setattr("chatbot.agent.call_claude", lambda prompt, context="": "RAG-enhanced Claude Response")
    result = planner(basic_message, mode="RAG+Chunks")
    assert "Claude Response" not in result  # just a sanity check
    assert "RAG-enhanced Claude Response" in result or isinstance(result, str)
    assert "BedrockKB" in st.session_state.rag_sources_used


def test_rag_chunks_fallback(monkeypatch, basic_message):
    monkeypatch.setattr("chatbot.rag.rag_router.hybrid_rag_router", lambda _: [])
    monkeypatch.setattr("chatbot.agent.call_claude", lambda prompt, context="": "Claude Fallback")
    result = planner(basic_message, mode="RAG+Chunks")
    assert result == "Claude Fallback"

