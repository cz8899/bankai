# chatbot/utils/monitor_utils.py

import pandas as pd
import os
import json
from typing import Literal, Optional, List, Union
from datetime import datetime

from chatbot.utils.config_loader import get_config_value
from chatbot.logger import logger

# === Paths ===
INTERACTIONS_LOG = os.getenv("INTERACTIONS_LOG_PATH", "logs/interactions.jsonl")


# === Log Loaders ===
def load_logs() -> pd.DataFrame:
    if not os.path.exists(INTERACTIONS_LOG):
        logger.warning("[Monitor] Log file not found.")
        return pd.DataFrame()

    records = []
    with open(INTERACTIONS_LOG, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                logger.warning("[Monitor] Skipping malformed log line.")
                continue

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df


def load_interaction_log() -> List[dict]:
    if not os.path.exists(INTERACTIONS_LOG):
        return []

    records = []
    with open(INTERACTIONS_LOG, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return records


# === Cost Summary ===
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


# === Usage Aggregations ===
def summarize_usage_by_mode(logs: pd.DataFrame) -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame(columns=["Mode", "Total Cost ($)", "Total Tokens"])

    df = summarize_costs(logs)
    return df.groupby("mode")[["cost", "tokens"]].sum().reset_index().rename(columns={
        "mode": "Mode",
        "cost": "Total Cost ($)",
        "tokens": "Total Tokens"
    })


def summarize_usage_aggregated(logs: pd.DataFrame, by: Literal["date", "user"] = "date") -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame()

    df = summarize_costs(logs)
    if by == "date":
        df["date"] = df["timestamp"].dt.date
        return df.groupby("date")[["cost", "tokens"]].sum().reset_index()
    elif by == "user":
        return df.groupby("user")[["cost", "tokens"]].sum().reset_index()
    return pd.DataFrame()


# === RAG Insights ===
def safe_parse_sources(val: Union[str, list]) -> List[str]:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except Exception:
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


# === Anomaly Detection ===
def detect_cost_spikes(logs: pd.DataFrame, threshold: Optional[float] = None) -> pd.DataFrame:
    if logs.empty:
        return pd.DataFrame(columns=["date", "Total Cost"])

    if threshold is None:
        threshold = get_config_value("COST_SPIKE_THRESHOLD", 5.0)

    df = summarize_costs(logs)
    df["date"] = df["timestamp"].dt.date
    daily_totals = df.groupby("date")["cost"].sum()
    spikes = daily_totals[daily_totals > threshold]
    return spikes.reset_index(name="Total Cost")


# === Recent Questions ===
def extract_recent_questions(logs: pd.DataFrame, limit: int = 10) -> List[dict]:
    if logs.empty:
        return []

    qa_logs = logs[logs["type"] == "qa"].copy()
    qa_logs = qa_logs.sort_values("timestamp", ascending=False).head(limit)
    return qa_logs[["timestamp", "prompt", "response", "mode", "source"]].to_dict(orient="records")


# === UTC Timestamp Helper ===
def get_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
