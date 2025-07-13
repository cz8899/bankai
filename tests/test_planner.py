# tests/test_planner.py

import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from chatbot.planner import planner
import pytest

@pytest.fixture
def sample_messages():
    return [{"role": "user", "content": "Please generate an architecture diagram for a secure banking app."}]


def test_claude_mode_response(sample_messages):
    with patch("chatbot.agent.call_claude", return_value="Claude response"):
        response = planner(sample_messages, mode="Claude")
        assert "Claude response" in response


def test_agent_mode_success(sample_messages):
    with patch("chatbot.agent.call_bedrock_agent", return_value="Agent reply"):
        response = planner(sample_messages, mode="Agent")
        assert "Agent reply" in response

def test_claude_mode():
    st.session_state.clear()
    st.session_state.messages = [{"role": "user", "content": "What's a VPC?"}]
    response = planner(st.session_state.messages, mode="Claude")
    assert isinstance(response, str)
    assert len(response) > 0


def test_rag_fallback_on_empty_chunks(monkeypatch):
    st.session_state.clear()
    st.session_state.messages = [{"role": "user", "content": "Zebra banking compliance"}]

    monkeypatch.setattr("chatbot.rag.rag_router.hybrid_rag_router", lambda _: [])
    response = planner(st.session_state.messages, mode="RAG+Chunks")

    assert isinstance(response, str)
    assert "context" not in response.lower() or "couldn't find" not in response.lower()


def test_agent_mode_with_session(monkeypatch):
    st.session_state.clear()
    st.session_state.messages = [{"role": "user", "content": "Tell me about risk scoring"}]
    st.session_state.conversation_id = "test-123"

    monkeypatch.setattr("chatbot.agent.call_bedrock_agent", lambda prompt, session_id: "[Agent returned no message]")

    response = planner(st.session_state.messages, mode="Agent")
    assert isinstance(response, str)

def test_agent_mode_fallback(sample_messages):
    with patch("chatbot.agent.call_bedrock_agent", return_value="[Agent returned no message]"), \
         patch("chatbot.agent.call_claude", return_value="Fallback Claude response"):
        response = planner(sample_messages, mode="Agent")
        assert "Fallback Claude response" in response


def test_rag_mode_with_chunks(sample_messages):
    with patch("chatbot.rag.rag_router.hybrid_rag_router", return_value=[
        {"content": "Chunk 1", "metadata": {"title": "Doc1", "page": 2, "source": "Bedrock KB"}},
        {"content": "Chunk 2", "metadata": {"title": "Doc2", "page": 4, "source": "OpenSearch"}}
    ]), patch("chatbot.agent.call_claude", return_value="Claude with RAG"):
        response = planner(sample_messages, mode="RAG+Chunks")
        assert "Claude with RAG" in response


def test_rag_mode_fallback(sample_messages):
    with patch("chatbot.rag.rag_router.hybrid_rag_router", side_effect=Exception("RAG error")), \
         patch("chatbot.agent.call_claude", return_value="Fallback Claude"):
        response = planner(sample_messages, mode="RAG+Chunks")
        assert "Fallback Claude" in response


class TestPlanner(unittest.TestCase):

    def setUp(self):
        st.session_state.clear()
        st.session_state["conversation_id"] = "test-convo-123"
        st.session_state["planner_stage"] = "gathering_requirements"

    @patch("chatbot.planner.call_claude", return_value="Claude says hello.")
    def test_claude_mode(self, mock_claude):
        messages = [{"role": "user", "content": "How to build a chatbot?"}]
        response = planner(messages, mode="Claude")
        self.assertIn("Claude says hello", response)
        self.assertIn(st.session_state.planner_stage, ["refining_scope", "generating_solution", "final_confirmation", "showing_widgets"])

    @patch("chatbot.planner.call_bedrock_agent", return_value="Agent response here.")
    def test_agent_mode_success(self, mock_agent):
        messages = [{"role": "user", "content": "What’s a good AWS architecture?"}]
        response = planner(messages, mode="Agent")
        self.assertEqual(response, "Agent response here.")
        self.assertTrue(st.session_state.get("agent_session_id"))

    @patch("chatbot.planner.call_bedrock_agent", return_value="[Agent returned no message]")
    @patch("chatbot.planner.call_claude", return_value="Fallback Claude response.")
    def test_agent_mode_fallback(self, mock_claude, mock_agent):
        messages = [{"role": "user", "content": "Generate CDK code."}]
        response = planner(messages, mode="Agent")
        self.assertIn("Fallback Claude response", response)

    @patch("chatbot.planner.get_relevant_chunks")
    @patch("chatbot.planner.call_claude")
    def test_rag_mode_with_context(self, mock_claude, mock_get_chunks):
        mock_get_chunks.return_value = [
            {"content": "S3 bucket with encryption", "metadata": {"title": "Infra Doc", "page": 2}},
            {"content": "Lambda for ETL", "metadata": {"title": "ETL Notes", "page": 1}},
        ]
        mock_claude.return_value = "Contextual answer here."
        messages = [{"role": "user", "content": "How does S3 integrate with Lambda?"}]
        response = planner(messages, mode="RAG+Chunks")
        self.assertIn("Contextual answer here", response)

    @patch("chatbot.planner.get_relevant_chunks", return_value=[])
    def test_rag_mode_no_chunks(self, _):
        messages = [{"role": "user", "content": "Unknown tech XYZ?"}]
        response = planner(messages, mode="RAG+Chunks")
        self.assertIn("couldn’t find relevant context", response)

    def test_unknown_mode(self):
        messages = [{"role": "user", "content": "What now?"}]
        response = planner(messages, mode="Mystery")
        self.assertIn("Unknown mode", response)

if __name__ == "__main__":
    unittest.main()
