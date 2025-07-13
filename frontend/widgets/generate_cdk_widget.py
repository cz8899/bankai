# 5. generate_cdk_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming
)
from chatbot.utils.prompt_templates import CDK_TEMPLATE_PROMPT

@st.fragment
def generate_cdk(cdk_messages):
    cdk_messages = cdk_messages[-10:]
    st.session_state.setdefault("cdk_messages", [])
    st.session_state.setdefault("cdk_user_select", False)

    st.markdown("<h5>📦 Generate AWS CDK (TypeScript)</h5>", unsafe_allow_html=True)
    select_cdk = st.checkbox("Generate AWS CDK Infrastructure", key="cdk")

    if select_cdk:
        st.session_state.cdk_user_select = True

    if st.session_state.cdk_user_select:
        st.session_state.cdk_messages.append({"role": "user", "content": CDK_TEMPLATE_PROMPT})
        cdk_messages.append({"role": "user", "content": CDK_TEMPLATE_PROMPT})

        with st.spinner("Generating CDK code using Claude 3 Sonnet..."):
            try:
                response, _ = invoke_bedrock_model_streaming(cdk_messages)
                st.markdown(response)
                store_in_s3(response, "cdk")
                save_conversation(st.session_state["conversation_id"], CDK_TEMPLATE_PROMPT, response)
                collect_feedback(str(uuid.uuid4()), response, "generate_cdk", BEDROCK_MODEL_ID)
                st.download_button("⬇️ Download CDK", data=response, file_name="cdk_stack.ts", mime="text/typescript")
            except Exception as e:
                st.error(f"CDK generation failed: {str(e)}")
