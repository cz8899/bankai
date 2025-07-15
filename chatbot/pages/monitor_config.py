# chatbot/pages/monitor_config.py

import streamlit as st
import json
from chatbot.utils.config_loader import get_config, save_config
from chatbot.utils.constants import TRUIST_PURPLE
from chatbot.utils.auth_utils import is_admin_user

if not is_admin_user():
    st.warning("⚠️ You are not authorized to edit configurations.")
    st.stop()
    
st.set_page_config(page_title="DevGenius Config Editor", layout="wide")
st.title("🔧 DevGenius AI Tuning Config")

# Load current config
config = get_config()
st.markdown(f"""
<style>
h1 {{ color: {TRUIST_PURPLE}; }}
input {{ font-size: 16px; }}
</style>
""", unsafe_allow_html=True)

st.info("Adjust thresholds without redeploying. Changes apply immediately.")

with st.form("config_editor"):
    rerank_threshold = st.slider("Rerank Score Threshold", 0.0, 1.0, float(config.get("RERANK_THRESHOLD", 0.6)), step=0.01)
    chunk_score_min = st.slider("Minimum Chunk Score (RAG)", 0.0, 1.0, float(config.get("CHUNK_SCORE_MIN", 0.4)), step=0.01)
    summary_length = st.number_input("Summarization Target Length (tokens)", min_value=50, max_value=4096,
                                     value=int(config.get("SUMMARY_LENGTH", 512)))
    embedding_engine = st.selectbox("Embedding Engine", ["bedrock", "huggingface"],
                                     index=0 if config.get("EMBEDDING_ENGINE") == "bedrock" else 1)

    submitted = st.form_submit_button("💾 Save Config")
    if submitted:
        new_config = {
            "RERANK_THRESHOLD": rerank_threshold,
            "CHUNK_SCORE_MIN": chunk_score_min,
            "SUMMARY_LENGTH": summary_length,
            "EMBEDDING_ENGINE": embedding_engine
        }
        success = save_config(new_config)
        if success:
            st.success("✅ Config saved!")
        else:
            st.error("❌ Failed to save config.")

# Show current config
st.subheader("📄 Current Config")
st.json(config)
