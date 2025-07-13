# 4. generate_cfn_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming
)
from chatbot.utils.prompt_templates import CLOUDFORMATION_PROMPT

@st.fragment
def generate_cfn(cfn_messages):
    cfn_messages = cfn_messages[-10:]
    st.session_state.setdefault("cfn_messages", [])
    st.session_state.setdefault("cfn_user_select", False)

    st.markdown("<h5>🧾 Generate CloudFormation Template</h5>", unsafe_allow_html=True)
    select_cfn = st.checkbox("Generate CloudFormation Template", key="cfn")

    if select_cfn:
        st.session_state.cfn_user_select = True

    if st.session_state.cfn_user_select:
        st.session_state.cfn_messages.append({"role": "user", "content": CLOUDFORMATION_PROMPT})
        cfn_messages.append({"role": "user", "content": CLOUDFORMATION_PROMPT})

        with st.spinner("Creating CloudFormation template..."):
            try:
                response, _ = invoke_bedrock_model_streaming(cfn_messages)
                st.markdown(response)
                store_in_s3(response, "cloudformation")
                save_conversation(st.session_state["conversation_id"], CLOUDFORMATION_PROMPT, response)
                collect_feedback(str(uuid.uuid4()), response, "generate_cfn", BEDROCK_MODEL_ID)
                st.download_button("⬇️ Download YAML", data=response, file_name="stack.yaml", mime="text/yaml")
            except Exception as e:
                st.error(f"CloudFormation generation failed: {str(e)}")
