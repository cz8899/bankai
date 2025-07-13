import pytest
from unittest.mock import patch
from chatbot.utils.prompt_templates import CDK_GENERATION_PROMPT

@patch("chatbot.utils.store_in_s3")
@patch("chatbot.utils.save_conversation")
@patch("chatbot.utils.collect_feedback")
@patch("chatbot.utils.invoke_bedrock_model_streaming")
def test_generate_cdk_success(mock_stream, mock_feedback, mock_save, mock_store):
    mock_stream.return_value = ("```ts\nconst app = new cdk.App();", "stop")
    from chatbot.utils.streamlit_widgets import generate_cdk_widget
    messages = [{"role": "user", "content": "CDK"}]
    assert "cdk" in mock_stream.return_value[0].lower()
    mock_stream.assert_called()
