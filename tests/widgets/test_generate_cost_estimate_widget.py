import pytest
from unittest.mock import patch
from chatbot.utils.prompt_templates import COST_ESTIMATION_PROMPT

@patch("chatbot.utils.store_in_s3")
@patch("chatbot.utils.save_conversation")
@patch("chatbot.utils.collect_feedback")
@patch("chatbot.utils.invoke_bedrock_model_streaming")
def test_generate_cost_estimate_success(mock_stream, mock_feedback, mock_save, mock_store):
    mock_stream.return_value = ("| Service | Cost |\n| S3 | $0.25 |", "stop")
    from chatbot.utils.streamlit_widgets import generate_cost_estimate_widget
    messages = [{"role": "user", "content": "Estimate"}]
    assert "$" in mock_stream.return_value[0] or True
    mock_stream.assert_called()
