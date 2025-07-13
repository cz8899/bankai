# chatbot/utils/streamlit_widgets/generate_cost_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID,
    store_in_s3,
    save_conversation,
    collect_feedback,
    invoke_bedrock_model_streaming,
)
from chatbot.utils.prompt_templates import COST_ESTIMATE_PROMPT


@st.fragment
def generate_cost(cost_messages):
    cost_messages = cost_messages[-10:]
    st.session_state.setdefault("cost_messages", [])
    st.session_state.setdefault("cost_user_select", False)

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown("<div style='font-size: 18px'><b>Estimate AWS Costs</b></div>", unsafe_allow_html=True)
        st.divider()
        if st.checkbox("Check to generate cost estimate", key="cost"):
            st.session_state.cost_user_select = True

    with right:
        if st.session_state.cost_user_select and st.button("\u27F3 Retry", key="retry-cost", type="secondary"):
            st.session_state.cost_user_select = True

    if st.session_state.cost_user_select:
        st.session_state.cost_messages.append({"role": "user", "content": COST_ESTIMATE_PROMPT})
        cost_messages.append({"role": "user", "content": COST_ESTIMATE_PROMPT})

        try:
            response, stop_reason = invoke_bedrock_model_streaming(cost_messages)
            st.session_state.cost_messages.append({"role": "assistant", "content": response})
            st.markdown(response)

            st.session_state.interaction.append({"type": "Cost Estimate", "details": response})
            store_in_s3(content=response, content_type='cost_estimate')
            save_conversation(st.session_state['conversation_id'], COST_ESTIMATE_PROMPT, response)
            collect_feedback(str(uuid.uuid4()), response, "generate_cost", BEDROCK_MODEL_ID)

            st.download_button("💰 Download Cost Estimate", data=response, file_name="aws_costs.md", mime="text/markdown")

        except Exception as e:
            st.error("Failed to generate cost estimate.")
