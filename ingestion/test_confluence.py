import pytest
import os
from unittest.mock import patch, MagicMock
from chatbot.ingestion import confluence

@patch("chatbot.ingestion.confluence.requests.get")
def test_fetch_page_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"body": {"storage": {"value": "<p>Sample content</p>"}}}
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    os.environ["CONFLUENCE_API_TOKEN"] = "fake-token"
    os.environ["CONFLUENCE_EMAIL"] = "test@example.com"
    result = confluence.fetch_confluence_page_content("12345")
    assert "<p>Sample content</p>" in result

def test_get_confluence_auth_missing_env():
    if "CONFLUENCE_API_TOKEN" in os.environ: del os.environ["CONFLUENCE_API_TOKEN"]
    if "CONFLUENCE_EMAIL" in os.environ: del os.environ["CONFLUENCE_EMAIL"]
    with pytest.raises(EnvironmentError):
        confluence.get_confluence_auth()
