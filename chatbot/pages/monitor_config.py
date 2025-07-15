# chatbot/pages/monitor_config.py

import streamlit as st
from chatbot.utils.config_loader import load_config, save_config
from chatbot.utils.auth_utils import is_admin_user
from chatbot.utils.constants import TRUIST_PURPLE

# === Page Setup ===
st.set_page_config(page_title="DevGenius Config Editor", layout="centered")

# === Auth Check ===
if not is_admin_user():
    st.error("🚫 You are not authorized to edit configurations.")
    st.stop()

# === UI Header ===
st.markdown(f"<h1 style='color:{TRUIST_PURPLE}'>🔧 DevGenius Configuration Dashboard</h1>", unsafe_allow_html=True)
st.info("Edit model and retrieval thresholds without redeploying. Changes apply immediately.")

# === Load Current Config ===
config = load_config()

# === Admin Config Form ===
with st.form("config_form"):
    st.subheader("📊 Thresholds & Parameters")

    config["chunk_score_threshold"] = st.slider(
        "Minimum Chunk Score (RAG)", 0.0, 1.0, float(config.get("chunk_score_threshold", 0.5)), 0.01)

    config["rerank_top_k"] = st.slider(
        "Rerank Top-K Chunks", 1, 20, int(config.get("rerank_top_k", 5)))

    config["summarization_tokens"] = st.slider(
        "Summarization Token Limit", 100, 4096, int(config.get("summarization_tokens", 512)))

    config["embedding_engine"] = st.selectbox(
        "Embedding Engine", ["bedrock", "huggingface"],
        index=["bedrock", "huggingface"].index(config.get("embedding_engine", "bedrock"))
    )

    submitted = st.form_submit_button("💾 Save Changes")

    if submitted:
        success = save_config(config)
        if success:
            st.success("✅ Config saved.")
        else:
            st.error("❌ Failed to save config.")

# === Display Final Config for Review ===
st.subheader("📄 Current Configuration")
st.json(config)
