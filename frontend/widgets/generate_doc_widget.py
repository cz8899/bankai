# 2. generate_doc_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming
)
from chatbot.utils.prompt_templates import DOCUMENTATION_PROMPT

@st.fragment
def generate_doc(doc_messages):
    doc_messages = doc_messages[-10:]
    st.session_state.setdefault("doc_messages", [])
    st.session_state.setdefault("doc_user_select", False)

    st.markdown("<h5>📄 Generate Documentation</h5>", unsafe_allow_html=True)
    select_doc = st.checkbox("Generate technical documentation", key="doc")

    if select_doc:
        st.session_state.doc_user_select = True

    if st.session_state.doc_user_select:
        st.session_state.doc_messages.append({"role": "user", "content": DOCUMENTATION_PROMPT})
        doc_messages.append({"role": "user", "content": DOCUMENTATION_PROMPT})

        with st.spinner("Generating docs via Claude 3 Sonnet..."):
            try:
                response, _ = invoke_bedrock_model_streaming(doc_messages)
                st.markdown(response)
                store_in_s3(response, "documentation")
                save_conversation(st.session_state["conversation_id"], DOCUMENTATION_PROMPT, response)
                collect_feedback(str(uuid.uuid4()), response, "generate_doc", BEDROCK_MODEL_ID)
                st.download_button("⬇️ Download Markdown", data=response, file_name="documentation.md", mime="text/markdown")
            except Exception as e:
                st.error(f"Claude generation failed: {str(e)}")
