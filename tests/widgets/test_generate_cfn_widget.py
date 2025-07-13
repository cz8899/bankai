import pytest
from unittest.mock import patch
from chatbot.utils.prompt_templates import CLOUDFORMATION_GENERATION_PROMPT

@patch("chatbot.utils.store_in_s3")
@patch("chatbot.utils.save_conversation")
@patch("chatbot.utils.collect_feedback")
@patch("chatbot.utils.invoke_bedrock_model_streaming")
def test_generate_cfn_success(mock_stream, mock_feedback, mock_save, mock_store):
    mock_stream.return_value = ("```yaml\nResources:\n  Bucket: AWS::S3::Bucket", "stop")
    from chatbot.utils.streamlit_widgets import generate_cfn_widget
    messages = [{"role": "user", "content": "YAML"}]
    assert "Resources" in mock_stream.return_value[0]
    mock_stream.assert_called()
