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

# === Streamlit Config ===
st.set_page_config(page_title="DevGenius Monitor", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=30_000, key="refresh_dashboard")

# === Branding Header ===
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image(LOGO_PATH, width=90)
with col2:
    st.markdown(f"<h1 style='color:{TRUIST_PURPLE}; margin-top:0.4em;'>DevGenius Usage Monitor</h1>", unsafe_allow_html=True)

# === Load Logs ===
logs = load_logs()
if logs.empty:
    st.warning("No logs found.")
    st.stop()

# === Load Usage Records ===
usage_records = load_usage_data()
if usage_records.empty:
    st.warning("No usage data found.")
    st.stop()

# === Optional Mode Filter ===
with st.sidebar:
    st.subheader("🔍 Filter Logs")
    all_modes = sorted(logs["mode"].dropna().unique().tolist())
    selected_mode = st.selectbox("Assistant Mode", ["All"] + all_modes)

    if selected_mode != "All":
        logs = logs[logs["mode"] == selected_mode]
        usage_records = usage_records[usage_records["mode"] == selected_mode]

# === KPI Summary ===
df_cost = summarize_costs(logs)
if df_cost.empty:
    st.warning("No cost data available.")
    st.stop()

total_cost = df_cost["cost"].sum()
total_tokens = df_cost["tokens"].sum()
unique_users = df_cost["user"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Cost", f"${total_cost:,.2f}")
col2.metric("🔢 Total Tokens", f"{total_tokens:,}")
col3.metric("👥 Unique Users", unique_users)

# === Usage Summary by Mode ===
st.subheader("📊 Usage Summary by Mode")
df_usage = summarize_usage_by_mode(usage_records)
st.dataframe(df_usage, use_container_width=True)

st.download_button(
    label="⬇️ Download Usage Summary CSV",
    data=df_usage.to_csv(index=False),
    file_name="usage_summary.csv",
    mime="text/csv"
)

# === Daily Trend Chart ===
st.subheader("📈 Daily Cost Trend")
daily_df = summarize_usage_aggregated(df_cost, by="date")
if not daily_df.empty:
    st.line_chart(daily_df.set_index("date")["cost"])
else:
    st.info("No daily cost trend data available.")

# === Anomaly Detection ===
st.subheader("⚠️ Cost Anomaly Alerts")
spikes = detect_cost_spikes(df_cost, threshold=5.0)

if not spikes.empty:
    st.error("⚠️ High-cost spikes detected!")
    st.dataframe(spikes)

    alert_body = f"DevGenius Cost Spike Alert:\n\n{spikes.to_string(index=False)}"
    if send_cost_alert("⚠️ DevGenius Cost Spike Detected", alert_body):
        st.success("📧 Alert email sent to monitoring team.")
    else:
        st.warning("⚠️ Failed to send alert email.")
else:
    st.success("✅ No major cost anomalies detected.")

# === Cost Table ===
st.subheader("💰 Cost Breakdown")
st.dataframe(df_cost, use_container_width=True)

# === Retrieval Source Breakdown ===
st.subheader("🔎 Retrieval Context Sources")
retrieval_df = get_retrieval_insights(logs)
st.dataframe(retrieval_df, use_container_width=True)

# === Raw Logs ===
with st.expander("🧾 View Raw Logs (Last 200 Entries)"):
    st.dataframe(logs.tail(200), use_container_width=True)

st.download_button(
    label="⬇️ Download Full Logs",
    data=logs.to_csv(index=False),
    file_name="devgenius_logs.csv",
    mime="text/csv"
)
