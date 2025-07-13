# chatbot/monitor.py

import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

from chatbot.utils.monitor_utils import (
    load_logs,
    summarize_costs,
    get_retrieval_insights,
    summarize_usage_by_mode,
    load_usage_data
)
from chatbot.utils.constants import TRUIST_PURPLE, LOGO_PATH

# Page setup
st.set_page_config(page_title="DevGenius Monitor", layout="wide", initial_sidebar_state="expanded")

# Branding
st.image(LOGO_PATH, width=120)
st.markdown(f"<h1 style='color:{TRUIST_PURPLE}'>DevGenius Usage Monitor</h1>", unsafe_allow_html=True)

# === Auto Refresh (30 sec) ===
st_autorefresh(interval=30_000, limit=100, key="auto_refresh")

# === Load logs ===
logs = load_logs()
if logs is None or logs.empty:
    st.warning("No logs found.")
    st.stop()

# === Load usage metrics ===
usage_records = load_usage_data()
if not usage_records:
    st.warning("No usage data found.")
    st.stop()

# === Usage Summary by Mode ===
st.subheader("📊 Usage Summary by Mode")
summary_df = summarize_usage_by_mode(usage_records)
st.dataframe(summary_df, use_container_width=True)

st.download_button(
    label="📄 Download Usage Summary as CSV",
    data=summary_df.to_csv(index=False),
    file_name="usage_summary.csv",
    mime="text/csv"
)

# === Cost Summary ===
st.subheader("💰 Cost Breakdown")
cost_df = summarize_costs(logs)
st.dataframe(cost_df, use_container_width=True)

# === Retrieval Insights ===
st.subheader("🔎 Retrieval Context Sources")
retrieval_df = get_retrieval_insights(logs)
st.dataframe(retrieval_df, use_container_width=True)

# === Raw Log Viewer ===
with st.expander("🧾 View Raw Logs (Last 200 Entries)"):
    st.dataframe(logs.tail(200), use_container_width=True)
