# 3. generate_cost_estimate_widget.py
import streamlit as st
import uuid
from chatbot.utils import (
    BEDROCK_MODEL_ID, store_in_s3, save_conversation, collect_feedback, invoke_bedrock_model_streaming
)
from chatbot.utils.prompt_templates import COST_ESTIMATE_PROMPT

@st.fragment
def generate_cost_estimate(cost_messages):
    cost_messages = cost_messages[-10:]
    st.session_state.setdefault("cost_messages", [])
    st.session_state.setdefault("cost_user_select", False)

    st.markdown("<h5>💰 Estimate AWS Cost</h5>", unsafe_allow_html=True)
    select_cost = st.checkbox("Generate AWS Cost Estimate", key="cost")

    if select_cost:
        st.session_state.cost_user_select = True

    if st.session_state.cost_user_select:
        st.session_state.cost_messages.append({"role": "user", "content": COST_ESTIMATE_PROMPT})
        cost_messages.append({"role": "user", "content": COST_ESTIMATE_PROMPT})

        with st.spinner("Estimating AWS cost using Claude 3 Sonnet..."):
            try:
                response, _ = invoke_bedrock_model_streaming(cost_messages)
                st.markdown(response)
                store_in_s3(response, "cost_estimate")
                save_conversation(st.session_state["conversation_id"], COST_ESTIMATE_PROMPT, response)
                collect_feedback(str(uuid.uuid4()), response, "generate_cost", BEDROCK_MODEL_ID)
                st.download_button("⬇️ Download Cost Estimate", data=response, file_name="aws_cost.md", mime="text/markdown")
            except Exception as e:
                st.error(f"Error estimating cost: {str(e)}")
