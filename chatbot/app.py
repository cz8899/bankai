# chatbot/app.py

import streamlit as st
import uuid
from chatbot.styles import inject_custom_css
from chatbot.planner import planner
from chatbot.utils.constants import (
    TRUIST_PURPLE, LOGO_PATH, SYSTEM_MESSAGE
)
from chatbot.utils.context_manager import init_session
from chatbot.utils.cost_utils import track_usage, get_cost_estimate
from chatbot.utils.streamlit_widgets import (
    generate_arch,
    generate_cdk,
    generate_cfn,
    generate_cost_estimate,
    generate_doc,
    generate_drawio
)

# --- Setup ---
st.set_page_config(page_title="DevGenius AI", layout="wide")
inject_custom_css()
init_session()

# --- Session Metadata ---
if 'conversation_id' not in st.session_state:
    st.session_state['conversation_id'] = str(uuid.uuid4())

if not st.session_state.get("messages"):
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": SYSTEM_MESSAGE})

# --- Header ---
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(LOGO_PATH, width=90)
with col2:
    st.markdown(
        f"<h1 style='color:{TRUIST_PURPLE}; margin-top: 0.3em;'>DevGenius AI Co-Pilot</h1>",
        unsafe_allow_html=True
    )

# --- Mode Toggle ---
mode = st.radio(
    "Select Assistant Mode:",
    ["Claude", "Agent", "RAG+Chunks"],
    horizontal=True,
    key="chat_mode"
)

# --- Chat Input ---
if prompt := st.chat_input("What do you want to build today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        with track_usage(model=mode, user_input=prompt) as usage:
            response = planner(st.session_state.messages, mode=mode)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(
            f"💰 Estimated cost: <span style='color:green;'>**${get_cost_estimate(usage)}**</span>",
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error("❗ An error occurred. Falling back to Claude.")
        fallback_mode = "Claude" if mode != "Claude" else "Agent"
        with track_usage(model=fallback_mode, user_input=prompt) as usage:
            response = planner(st.session_state.messages, mode=fallback_mode)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- Message Loop ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Planner Stage Gate ---
if st.session_state.planner_stage == "final_confirmation":
    st.warning("🧠 Just one more confirmation before I generate your solution…")

if st.session_state.planner_stage == "generating_solution":
    st.info("⚙️ Generating architecture and initial proposal…")

# --- Widget Panel ---
if st.session_state.planner_stage == "showing_widgets":
    st.divider()
    st.subheader("📦 Deliverable Generators")
    generate_arch(st.session_state.messages)
    generate_cdk(st.session_state.messages)
    generate_cfn(st.session_state.messages)
    generate_cost_estimate(st.session_state.messages)
    generate_doc(st.session_state.messages)
    generate_drawio(st.session_state.messages)

# --- Footer ---
st.markdown(
    f"<footer style='margin-top:3em; text-align:center; font-size:0.8rem; color:gray;'>"
    f"Built by Truist Engineering & AI Lab | Powered by AWS Bedrock + OpenSearch"
    f"</footer>",
    unsafe_allow_html=True
)
