# chatbot/utils/streamlit_widgets/generate_cfn_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID,
    store_in_s3,
    save_conversation,
    collect_feedback,
    invoke_bedrock_model_streaming,
)
from chatbot.utils.prompt_templates import CLOUDFORMATION_PROMPT


@st.fragment
def generate_cfn(cfn_messages):
    cfn_messages = cfn_messages[-10:]
    st.session_state.setdefault('cfn_messages', [])
    st.session_state.setdefault('cfn_user_select', False)

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown("<div style='font-size: 18px'><b>Generate CloudFormation YAML</b></div>", unsafe_allow_html=True)
        st.divider()
        if st.checkbox("Check to generate CloudFormation", key="cfn"):
            st.session_state.cfn_user_select = True

    with right:
        if st.session_state.cfn_user_select and st.button("\u27F3 Retry", key="retry-cfn", type="secondary"):
            st.session_state.cfn_user_select = True

    if st.session_state.cfn_user_select:
        st.session_state.cfn_messages.append({"role": "user", "content": CLOUDFORMATION_PROMPT})
        cfn_messages.append({"role": "user", "content": CLOUDFORMATION_PROMPT})

        try:
            response, stop_reason = invoke_bedrock_model_streaming(cfn_messages)
            st.session_state.cfn_messages.append({"role": "assistant", "content": response})
            st.markdown(response)
            st.session_state.interaction.append({"type": "CloudFormation", "details": response})
            store_in_s3(content=response, content_type='cloudformation')
            save_conversation(st.session_state['conversation_id'], CLOUDFORMATION_PROMPT, response)
            collect_feedback(str(uuid.uuid4()), response, "generate_cfn", BEDROCK_MODEL_ID)

            st.download_button("📄 Download CFN Template", data=response, file_name="template.yaml", mime="text/yaml")

        except Exception as e:
            st.error("Failed to generate CloudFormation template.")
