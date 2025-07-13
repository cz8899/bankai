# Batch 1: UI Widgets - Finalized Production-Ready Versions
# Includes:
# - generate_arch_widget.py
# - generate_doc_widget.py
# - generate_cost_estimate_widget.py
# - generate_cfn_widget.py
# - generate_cdk_widget.py

# 1. generate_arch_widget.py
import uuid
import re
import streamlit as st
from chatbot.utils import (
    store_in_s3, save_conversation, collect_feedback, convert_xml_to_html,
    continuation_prompt, invoke_bedrock_model_streaming, BEDROCK_MODEL_ID
)
from chatbot.utils.prompt_templates import ARCHITECTURE_PROMPT

@st.fragment
def generate_arch(arch_messages):
    arch_messages = arch_messages[-10:]
    st.session_state.setdefault("arch_messages", [])
    st.session_state.setdefault("arch_user_select", False)

    st.markdown("<h5>🧱 Solution Architecture Generation</h5>", unsafe_allow_html=True)
    select_arch = st.checkbox("Generate AWS Architecture Diagram", key="arch")

    if select_arch:
        st.session_state.arch_user_select = True

    if st.session_state.arch_user_select:
        st.session_state.arch_messages.append({"role": "user", "content": ARCHITECTURE_PROMPT})
        arch_messages.append({"role": "user", "content": ARCHITECTURE_PROMPT})

        try:
            full_response_array = []
            for attempt in range(3):
                response, stop_reason = invoke_bedrock_model_streaming(arch_messages, enable_reasoning=True)
                full_response_array.append(response)
                if stop_reason != "max_tokens":
                    break
                arch_messages = continuation_prompt(ARCHITECTURE_PROMPT, ''.join(full_response_array))

            full_response = ''.join(full_response_array)
            xml_content = re.findall(r"```xml(.*?)```", full_response, re.DOTALL)
            xml_data = xml_content[0].strip() if xml_content else ""
            html_data = convert_xml_to_html(xml_data)

            st.components.v1.html(html_data, scrolling=True, height=400)
            st.download_button("⬇️ Download as .drawio", xml_data, file_name="architecture.drawio", mime="application/xml")

            store_in_s3(full_response, "architecture")
            save_conversation(st.session_state["conversation_id"], ARCHITECTURE_PROMPT, full_response)
            collect_feedback(str(uuid.uuid4()), xml_data, "generate_architecture", BEDROCK_MODEL_ID)
        except Exception as e:
            st.error(f"Failed to generate architecture: {str(e)}")
