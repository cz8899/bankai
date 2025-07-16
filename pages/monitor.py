# chatbot/monitor.py

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from chatbot.utils.constants import TRUIST_PURPLE, LOGO_PATH
from chatbot.utils.monitor_utils import (
    load_logs,
    load_usage_data,
    summarize_costs,
    summarize_usage_by_mode,
    summarize_usage_aggregated,
    get_retrieval_insights,
    detect_cost_spikes
)
from chatbot.utils.email_alert import send_cost_alert
from chatbot.utils.config_loader import get_config_value
from chatbot.utils.auth_utils import is_admin_user

# === Access Control ===
if not is_admin_user():
    st.error("🚫 You are not authorized to view this dashboard.")
    st.stop()

# === Config Settings ===
cost_threshold = get_config_value("COST_SPIKE_THRESHOLD", 5.0)

# === Page Setup ===
st.set_page_config(page_title="DevGenius Monitor", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30_000, key="refresh_dashboard")

# === Header ===
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image(LOGO_PATH, width=90)
with col2:
    st.markdown(f"<h1 style='color:{TRUIST_PURPLE}; margin-top:0.4em;'>DevGenius Usage Monitor</h1>", unsafe_allow_html=True)

# === Load Data ===
logs = load_logs()
usage_records = load_usage_data()

if logs.empty or usage_records.empty:
    st.warning("⚠️ No logs or usage data available.")
    st.stop()

# === Sidebar Filters ===
with st.sidebar:
    st.markdown("🛠️ [Admin Config Dashboard](./monitor_config)")
    st.subheader("🔍 Filter Logs")
    all_modes = sorted(logs["mode"].dropna().unique().tolist())
    selected_mode = st.selectbox("Assistant Mode", ["All"] + all_modes)

    if selected_mode != "All":
        logs = logs[logs["mode"] == selected_mode]
        usage_records = usage_records[usage_records["mode"] == selected_mode]

# === KPI Metrics ===
df_cost = summarize_costs(logs)
if df_cost.empty:
    st.warning("No cost data found.")
    st.stop()

total_cost = df_cost["cost"].sum()
total_tokens = df_cost["tokens"].sum()
unique_users = df_cost["user"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost", f"${total_cost:,.2f}")
col2.metric("🔢 Total Tokens", f"{total_tokens:,}")
col3.metric("👥 Unique Users", unique_users)

# === Usage Summary Table ===
st.subheader("📊 Usage Summary by Mode")
df_usage = summarize_usage_by_mode(usage_records)
st.dataframe(df_usage, use_container_width=True)
st.download_button("⬇️ Download Usage Summary CSV", data=df_usage.to_csv(index=False), file_name="usage_summary.csv", mime="text/csv")

# === Trend Chart ===
st.subheader("📈 Daily Cost Trend")
daily_df = summarize_usage_aggregated(df_cost, by="date")
if not daily_df.empty:
    st.line_chart(daily_df.set_index("date")["cost"])
else:
    st.info("No daily trend data.")

# === Anomaly Detection ===
st.subheader("⚠️ Cost Anomaly Alerts")
spikes = detect_cost_spikes(df_cost, threshold=cost_threshold)
if not spikes.empty:
    st.error("⚠️ High-cost spikes detected!")
    st.dataframe(spikes)

    alert_body = f"DevGenius Cost Spike Alert:\n\n{spikes.to_string(index=False)}"
    if send_cost_alert("⚠️ DevGenius Cost Spike Detected", alert_body):
        st.success("📧 Alert email sent.")
    else:
        st.warning("⚠️ Failed to send email.")
else:
    st.success("✅ No anomalies detected.")

# === Detailed Cost Table ===
st.subheader("💰 Cost Breakdown")
st.dataframe(df_cost, use_container_width=True)

# === RAG Source Analysis ===
st.subheader("🔎 Retrieval Context Sources")
retrieval_df = get_retrieval_insights(logs)
if not retrieval_df.empty:
    st.dataframe(retrieval_df, use_container_width=True)
else:
    st.info("No RAG source logs available.")

# === Raw Logs ===
with st.expander("🧾 View Raw Logs (Last 200 Entries)"):
    st.dataframe(logs.tail(200), use_container_width=True)

st.download_button("⬇️ Download Full Logs", data=logs.to_csv(index=False), file_name="devgenius_logs.csv", mime="text/csv")
