# chatbot/utils/streamlit_widgets/generate_doc_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID,
    store_in_s3,
    save_conversation,
    collect_feedback,
    invoke_bedrock_model_streaming,
)
from chatbot.utils.prompt_templates import DOCUMENTATION_PROMPT


@st.fragment
def generate_doc(doc_messages):
    doc_messages = doc_messages[-10:]
    st.session_state.setdefault("doc_messages", [])
    st.session_state.setdefault("doc_user_select", False)

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown("<div style='font-size: 18px'><b>Generate Technical Documentation</b></div>", unsafe_allow_html=True)
        st.divider()
        if st.checkbox("Check to generate docs", key="doc"):
            st.session_state.doc_user_select = True

    with right:
        if st.session_state.doc_user_select and st.button("\u27F3 Retry", key="retry-doc", type="secondary"):
            st.session_state.doc_user_select = True

    if st.session_state.doc_user_select:
        st.session_state.doc_messages.append({"role": "user", "content": DOCUMENTATION_PROMPT})
        doc_messages.append({"role": "user", "content": DOCUMENTATION_PROMPT})

        try:
            response, stop_reason = invoke_bedrock_model_streaming(doc_messages)
            st.session_state.doc_messages.append({"role": "assistant", "content": response})
            st.markdown(response)

            st.session_state.interaction.append({"type": "Documentation", "details": response})
            store_in_s3(content=response, content_type="documentation")
            save_conversation(st.session_state["conversation_id"], DOCUMENTATION_PROMPT, response)
            collect_feedback(str(uuid.uuid4()), response, "generate_doc", BEDROCK_MODEL_ID)

            st.download_button("📄 Download Documentation", data=response, file_name="documentation.md", mime="text/markdown")

        except Exception as e:
            st.error("Failed to generate documentation.")
