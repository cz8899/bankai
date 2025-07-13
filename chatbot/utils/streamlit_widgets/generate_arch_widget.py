# chatbot/utils/streamlit_widgets/generate_arch_widget.py
import uuid
import re
import streamlit as st
from chatbot.utils import (
    BEDROCK_MODEL_ID,
    store_in_s3,
    save_conversation,
    collect_feedback,
    continuation_prompt,
    convert_xml_to_html,
    invoke_bedrock_model_streaming,
)
from chatbot.logger import logger
from chatbot.utils.prompt_templates import ARCHITECTURE_PROMPT


def extract_xml_from_markdown(markdown_response):
    matches = re.findall(r"```xml(.*?)```", markdown_response, re.DOTALL)
    return matches[0].strip() if matches else ""


@st.fragment
def generate_arch(arch_messages):
    arch_messages = arch_messages[-10:]
    st.session_state.setdefault("arch_messages", [])
    st.session_state.setdefault("arch_user_select", False)

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown("<div style='font-size: 18px'><b>Generate Architecture Diagram</b></div>", unsafe_allow_html=True)
        st.divider()
        if st.checkbox("Check to generate AWS architecture diagram", key="arch"):
            st.session_state.arch_user_select = True

    with right:
        if st.session_state.arch_user_select:
            if st.button(label="\u27F3 Retry", key="retry-arch", type="secondary"):
                st.session_state.arch_user_select = True

    if st.session_state.arch_user_select:
        st.session_state.arch_messages.append({"role": "user", "content": ARCHITECTURE_PROMPT})
        arch_messages.append({"role": "user", "content": ARCHITECTURE_PROMPT})

        full_response_array = []
        for _ in range(4):
            try:
                arch_gen_response, stop_reason = invoke_bedrock_model_streaming(arch_messages, enable_reasoning=True)
                full_response_array.append(arch_gen_response)
                if stop_reason != "max_tokens":
                    break
                full_response = ''.join(full_response_array)
                arch_messages = continuation_prompt(ARCHITECTURE_PROMPT, full_response)
            except Exception as e:
                logger.exception("Claude streaming failed for arch generation: %s", str(e))
                break

        try:
            full_response = ''.join(full_response_array)
            arch_content_xml = extract_xml_from_markdown(full_response)
            arch_content_html = convert_xml_to_html(arch_content_xml)

            with st.container():
                st.components.v1.html(arch_content_html, scrolling=True, height=400)

            st.session_state.interaction.append({"type": "Architecture", "details": full_response})
            store_in_s3(content=full_response, content_type='architecture')
            save_conversation(st.session_state['conversation_id'], ARCHITECTURE_PROMPT, full_response)
            collect_feedback(str(uuid.uuid4()), arch_content_xml, "generate_architecture", BEDROCK_MODEL_ID)

            st.download_button("📥 Download draw.io File", arch_content_xml, file_name="aws_architecture.xml", mime="text/xml")

        except Exception as e:
            st.error("Could not render architecture. Try again.")
            logger.exception("Error rendering architecture HTML: %s", str(e))
