import streamlit as st
import uuid
from chatbot.styles import inject_custom_css
from chatbot.planner import planner
from chatbot.utils.constants import TRUIST_PURPLE, LOGO_PATH, SYSTEM_MESSAGE
from chatbot.utils.context_manager import init_session
from chatbot.utils.cost_utils import track_usage, get_cost_estimate
from chatbot.utils.auth_utils import is_admin_user
from chatbot.utils.streamlit_widgets import (
    generate_arch, generate_cdk, generate_cfn,
    generate_cost_estimate, generate_doc, generate_drawio
)
from chatbot.memory.router import recall_similar_memories
from chatbot.utils.conversation_manager import ConversationManager
from chatbot.utils.fallback_router import fallback_router
from chatbot.utils.prompt_cleaner import sanitize_prompt
from chatbot.utils.enums import PlannerStage

# --- Setup ---
st.set_page_config(page_title="DevGenius AI", layout="wide")
inject_custom_css()
init_session()

# --- Session Metadata ---
if 'conversation_id' not in st.session_state:
    st.session_state['conversation_id'] = str(uuid.uuid4())

conversation = ConversationManager()

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
mode = st.radio("Select Assistant Mode:", ["Claude", "Agent", "RAG+Chunks"], horizontal=True, key="chat_mode")

# --- Chat Input ---
if prompt := st.chat_input("What do you want to build today?"):
    clean_prompt = sanitize_prompt(prompt)
    conversation.append_user(clean_prompt)

    similar_memories = recall_similar_memories(clean_prompt)
    if similar_memories:
        st.info("🧠 Related Past Conversations:")
        for mem in similar_memories:
            st.markdown(f"- {mem}")

    try:
        with track_usage(model=mode, user_input=clean_prompt) as usage:
            response = planner(conversation.messages, mode=mode)
        conversation.append_assistant(response)
        st.markdown(f"💰 Estimated cost: <span style='color:green;'>**${get_cost_estimate(usage)}**</span>", unsafe_allow_html=True)
    except Exception:
        st.error("❗ Error occurred. Trying fallback strategy.")
        fallback = fallback_router(mode)
        with track_usage(model=fallback, user_input=clean_prompt) as usage:
            response = planner(conversation.messages, mode=fallback)
        conversation.append_assistant(response)

# --- Optional: Memory & Sources ---
if mode == "RAG+Chunks":
    sources = st.session_state.get("rag_sources_used", [])
    if sources:
        st.markdown(f"🔍 Context used from: **{', '.join(sources)}**")

if st.session_state.get("memory_summary_used"):
    st.markdown("🧠 Summary memory was used to shape this response.")

# --- Chat UI Loop ---
for msg in conversation.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Planner Stage Gate ---
stage = st.session_state.get("planner_stage", PlannerStage.GATHERING.value)

if stage == PlannerStage.FINAL_CONFIRMATION.value:
    st.warning("🧠 Just one more confirmation before I generate your solution…")

if stage == PlannerStage.GENERATING_SOLUTION.value:
    st.info("⚙️ Generating architecture and initial proposal…")

# --- Widget Panel (Admin-Only) ---
if stage == PlannerStage.SHOWING_WIDGETS.value:
    if is_admin_user():
        st.divider()
        st.subheader("📦 Deliverable Generators")
        generate_arch(conversation.messages)
        generate_cdk(conversation.messages)
        generate_cfn(conversation.messages)
        generate_cost_estimate(conversation.messages)
        generate_doc(conversation.messages)
        generate_drawio(conversation.messages)
    else:
        st.warning("🔒 This stage is restricted to authorized users.")

# --- Footer ---
st.markdown(
    "<footer style='margin-top:3em; text-align:center; font-size:0.8rem; color:gray;'>"
    "Built by Truist Engineering & AI Lab | Powered by AWS Bedrock + OpenSearch"
    "</footer>",
    unsafe_allow_html=True
)
