# tests/test_generate_arch_widget.py
import streamlit as st
from chatbot.utils.streamlit_widgets import generate_arch

def test_generate_arch(monkeypatch):
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("```xml\n<mxGraphModel>Test</mxGraphModel>\n```", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_arch([])
    assert "arch_messages" in st.session_state

# tests/test_generate_cdk_widget.py
def test_generate_cdk(monkeypatch):
    from chatbot.utils.streamlit_widgets import generate_cdk
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("```ts\nconst bucket = new s3.Bucket()\n```", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_cdk([])

# tests/test_generate_cfn_widget.py
def test_generate_cfn(monkeypatch):
    from chatbot.utils.streamlit_widgets import generate_cfn
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("```yaml\nResources:\n  Bucket:\n    Type: AWS::S3::Bucket\n```", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_cfn([])

# tests/test_generate_doc_widget.py
def test_generate_doc(monkeypatch):
    from chatbot.utils.streamlit_widgets import generate_doc
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("# Documentation\n## Overview\nDetails...", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_doc([])

# tests/test_generate_cost_estimate_widget.py
def test_generate_cost(monkeypatch):
    from chatbot.utils.streamlit_widgets import generate_cost_estimate
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("| Service | Cost |\n|---|---|\n| S3 | $0.10 |", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_cost_estimate([])

# tests/test_generate_drawio_widget.py
def test_generate_drawio(monkeypatch):
    from chatbot.utils.streamlit_widgets import generate_drawio
    st.session_state.clear()
    st.session_state["planner_stage"] = "showing_widgets"
    st.session_state["conversation_id"] = "test-id"
    st.session_state["interaction"] = []

    def mock_invoke(*args, **kwargs):
        return ("```xml\n<mxGraphModel>DrawIO content</mxGraphModel>\n```", "stop")

    monkeypatch.setattr("chatbot.utils.invoke_bedrock_model_streaming", mock_invoke)
    generate_drawio([])

