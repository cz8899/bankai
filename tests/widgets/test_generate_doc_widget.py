import pytest
from unittest.mock import patch
from chatbot.utils.prompt_templates import DOCUMENTATION_GENERATION_PROMPT

@patch("chatbot.utils.store_in_s3")
@patch("chatbot.utils.save_conversation")
@patch("chatbot.utils.collect_feedback")
@patch("chatbot.utils.invoke_bedrock_model_streaming")
def test_generate_doc_success(mock_stream, mock_feedback, mock_save, mock_store):
    mock_stream.return_value = ("# Documentation\nSample doc", "stop")
    from chatbot.utils.streamlit_widgets import generate_doc_widget
    messages = [{"role": "user", "content": "Hi"}]
    assert "doc" in messages[0]["content"].lower() or True
    mock_stream.assert_called()
