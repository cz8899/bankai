import pandas as pd
import os
import json
from typing import Literal, Optional, List
from datetime import datetime

# === Paths ===
INTERACTIONS_LOG = os.getenv("INTERACTIONS_LOG_PATH", "logs/interactions.jsonl")

# === Log Loader ===
def load_logs() -> pd.DataFrame:
    if not os.path.exists(INTERACTIONS_LOG):
        return pd.DataFrame()

    records = []
    with open(INTERACTIONS_LOG, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue  # skip malformed rows

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def load_interaction_log() -> List[dict]:
    if not os.path.exists(INTERACTIONS_LOG):
        return []
    with open(INTERACTIONS_LOG, "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


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


# === Aggregated Usage Summary (by date or user) ===
def summarize_usage_aggregated(logs: pd.DataFrame, by: Literal["date", "user"] = "date") -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame()

    df = summarize_costs(logs)
    if by == "date":
        df["date"] = df["timestamp"].dt.date
        return df.groupby("date")[["cost", "tokens"]].sum().reset_index()
    elif by == "user":
        return df.groupby("user")[["cost", "tokens"]].sum().reset_index()
    else:
        return pd.DataFrame()


# === Retrieval Source Analysis ===
def safe_parse_sources(val) -> List[str]:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            return [s.strip() for s in val.split(",")]
    return []

def get_retrieval_insights(logs: pd.DataFrame) -> pd.DataFrame:
    if logs.empty or "retrieval_sources" not in logs.columns:
        return pd.DataFrame(columns=["source", "count"])

    parsed = logs["retrieval_sources"].dropna().map(safe_parse_sources)
    exploded = parsed.explode().dropna()
    return exploded.value_counts().reset_index().rename(columns={
        "index": "source",
        "retrieval_sources": "count"
    })


# === Anomaly Detection (per day) ===
def detect_cost_spikes(logs: pd.DataFrame, threshold: float = 10.0) -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame(columns=["date", "Total Cost"])

    df = summarize_costs(logs)
    df["date"] = df["timestamp"].dt.date
    daily_totals = df.groupby("date")["cost"].sum()
    spikes = daily_totals[daily_totals > threshold]
    return spikes.reset_index(name="Total Cost")


# === Recent Q&A for export ===
def extract_recent_questions(logs: pd.DataFrame, limit: int = 10) -> List[dict]:
    if logs.empty:
        return []

    qa_logs = logs[logs["type"] == "qa"]
    qa_logs = qa_logs.sort_values("timestamp", ascending=False).head(limit)
    return qa_logs[["timestamp", "prompt", "response", "mode", "source"]].to_dict(orient="records")


# === Timestamp Helper ===
def get_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
