# chatbot/utils/monitor_utils.py

import pandas as pd
import os
import json
from typing import Literal, Optional
from datetime import datetime

# === Paths ===
INTERACTIONS_LOG = os.getenv("INTERACTIONS_LOG_PATH", "logs/interactions.jsonl")

# === Log Loader ===
def load_logs() -> pd.DataFrame:
    if not os.path.exists(INTERACTIONS_LOG):
        return pd.DataFrame()
    with open(INTERACTIONS_LOG, "r") as f:
        records = [json.loads(line) for line in f if line.strip()]
    return pd.DataFrame(records)

# === Fallback log parser for legacy support ===
def load_interaction_log() -> list[dict]:
    if not os.path.exists(INTERACTIONS_LOG):
        return []
    with open(INTERACTIONS_LOG, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

# === Cost Summary by Entry ===
def summarize_costs(logs: pd.DataFrame, mode_filter: Optional[Literal["Claude", "Agent", "RAG"]] = None) -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame(columns=["timestamp", "type", "tokens", "cost", "mode", "user"])
    
    df = logs.copy()
    if mode_filter:
        df = df[df["mode"] == mode_filter]

    return df[["timestamp", "type", "tokens", "cost", "mode", "user"]].fillna({
        "tokens": 0,
        "cost": 0.0,
        "mode": "unknown",
        "user": "anon"
    })

# === Usage Summary by Mode ===
def summarize_usage_by_mode(logs: pd.DataFrame) -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame(columns=["Mode", "Total Cost ($)", "Total Tokens"])
    
    df = summarize_costs(logs)
    return df.groupby("mode")[["cost", "tokens"]].sum().reset_index().rename(columns={
        "mode": "Mode",
        "cost": "Total Cost ($)",
        "tokens": "Total Tokens"
    })

# === Usage loader (if needed as alias) ===
def load_usage_data() -> pd.DataFrame:
    return load_logs()

# === Retrieval Source Analysis ===
def get_retrieval_insights(logs: pd.DataFrame) -> pd.DataFrame:
    if logs.empty or "retrieval_sources" not in logs.columns:
        return pd.DataFrame(columns=["source", "count"])

    retrievals = logs["retrieval_sources"].dropna().explode()
    if retrievals.empty:
        return pd.DataFrame(columns=["source", "count"])

    return retrievals.value_counts().reset_index().rename(columns={
        "index": "source",
        "retrieval_sources": "count"
    })

# === Recent Q&A (Optional export) ===
def extract_recent_questions(logs: pd.DataFrame, limit: int = 10) -> list[dict]:
    if logs.empty:
        return []

    qa_logs = logs[logs["type"] == "qa"]
    qa_logs = qa_logs.sort_values("timestamp", ascending=False).head(limit)
    return qa_logs[["timestamp", "prompt", "response", "mode", "source"]].to_dict(orient="records")

# === UTC Timestamp Helper ===
def get_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
