import pytest
from unittest.mock import patch, MagicMock
from chatbot.agent import call_claude, call_bedrock_agent, get_ranked_chunks

# === Test Claude ===
@patch("chatbot.agent.bedrock.invoke_model")
def test_call_claude_success(mock_invoke):
    mock_response = MagicMock()
    mock_response["body"].read.return_value = b'{"content": "Hello from Claude"}'
    mock_invoke.return_value = mock_response

    output = call_claude("What is a VPC?")
    assert isinstance(output, str)
    assert "Hello from Claude" in output


@patch("chatbot.agent.bedrock.invoke_model", side_effect=Exception("Mock Claude error"))
def test_call_claude_failure(mock_invoke):
    output = call_claude("Trigger failure")
    assert output.startswith("⚠️ Claude error:")


# === Test Bedrock Agent ===
@patch("chatbot.agent.agent_runtime.invoke_agent")
def test_call_bedrock_agent_success(mock_invoke):
    mock_invoke.return_value = {
        "completion": {
            "content": '{"message": "Response from Agent"}'
        }
    }
    response = call_bedrock_agent("Summarize compliance")
    assert isinstance(response, str)
    assert "Response from Agent" in response


@patch("chatbot.agent.agent_runtime.invoke_agent", side_effect=Exception("Agent down"))
def test_call_bedrock_agent_failure(mock_invoke):
    response = call_bedrock_agent("Trigger failure")
    assert response.startswith("⚠️ Agent error:")


@patch("chatbot.agent.agent_runtime.invoke_agent")
def test_call_bedrock_agent_empty(mock_invoke):
    mock_invoke.return_value = {
        "completion": {
            "content": ""
        }
    }
    response = call_bedrock_agent("No message")
    assert response == "[Agent returned no message]"


# === Chunk Ranking ===
def test_get_ranked_chunks_valid():
    chunks = [
        {"content": "This is chunk 1"},
        {"content": "This is chunk 2"},
        {"content": "This is chunk 3"},
    ]
    output = get_ranked_chunks("chunk", chunks)
    assert isinstance(output, list)
    assert len(output) <= 10


def test_get_ranked_chunks_empty():
    output = get_ranked_chunks("test", [])
    assert output == []
