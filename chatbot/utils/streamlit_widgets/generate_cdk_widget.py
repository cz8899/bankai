# chatbot/utils/streamlit_widgets/generate_cdk_widget.py
import uuid
import streamlit as st
from chatbot.utils import (
    BEDROCK_MODEL_ID,
    store_in_s3,
    save_conversation,
    collect_feedback,
    invoke_bedrock_model_streaming
)
from chatbot.utils.prompt_templates import CDK_TEMPLATE_PROMPT


@st.fragment
def generate_cdk(cdk_messages):
    cdk_messages = cdk_messages[-10:]
    st.session_state.setdefault('cdk_messages', [])
    st.session_state.setdefault('cdk_user_select', False)

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown("<div style='font-size: 18px'><b>Generate AWS CDK</b></div>", unsafe_allow_html=True)
        st.divider()
        if st.checkbox("Check to generate AWS CDK code", key="cdk"):
            st.session_state.cdk_user_select = True

    with right:
        if st.session_state.cdk_user_select and st.button("\u27F3 Retry", key="retry-cdk", type="secondary"):
            st.session_state.cdk_user_select = True

    if st.session_state.cdk_user_select:
        st.session_state.cdk_messages.append({"role": "user", "content": CDK_TEMPLATE_PROMPT})
        cdk_messages.append({"role": "user", "content": CDK_TEMPLATE_PROMPT})

        try:
            response, stop_reason = invoke_bedrock_model_streaming(cdk_messages)
            st.session_state.cdk_messages.append({"role": "assistant", "content": response})

            st.markdown(response)
            st.session_state.interaction.append({"type": "CDK", "details": response})
            store_in_s3(content=response, content_type='cdk')
            save_conversation(st.session_state['conversation_id'], CDK_TEMPLATE_PROMPT, response)
            collect_feedback(str(uuid.uuid4()), response, "generate_cdk", BEDROCK_MODEL_ID)

            st.download_button("📦 Download CDK Stack", data=response, file_name="cdk_stack.ts", mime="text/plain")

        except Exception as e:
            st.error("Claude failed to generate CDK output.")
