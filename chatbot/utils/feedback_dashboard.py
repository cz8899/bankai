# === chatbot/pages/feedback_dashboard.py ===
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from chatbot.utils.auth_utils import is_admin_user

FEEDBACK_LOG_PATH = Path("logs/feedback.jsonl")

st.set_page_config(page_title="Feedback Dashboard", layout="wide")
st.title("📋 Feedback Dashboard")

if not is_admin_user():
    st.warning("You are not authorized to view this page.")
    st.stop()

if not FEEDBACK_LOG_PATH.exists():
    st.info("No feedback data yet.")
    st.stop()

records = []
with FEEDBACK_LOG_PATH.open() as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

df = pd.DataFrame(records)
if df.empty:
    st.info("No valid feedback entries to show.")
else:
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False), file_name="feedback_log.csv")
