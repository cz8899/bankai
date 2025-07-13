# chatbot/utils/cost_utils.py

import time
from contextlib import contextmanager
from chatbot.utils.constants import (
    COST_PER_1K_CLAUDE_INPUT,
    COST_PER_1K_CLAUDE_OUTPUT,
    COST_PER_RETRIEVAL,
    COST_TRACKING_ENABLED,
)

def count_tokens(text: str) -> int:
    """Rudimentary token estimate: 1 token ≈ 4 characters"""
    return max(1, len(text) // 4)

def get_cost_estimate(usage: dict) -> float:
    """Calculate estimated cost in USD from usage stats"""
    cost = 0.0
    cost += usage.get("input_tokens", 0) / 1000 * COST_PER_1K_CLAUDE_INPUT
    cost += usage.get("output_tokens", 0) / 1000 * COST_PER_1K_CLAUDE_OUTPUT
    if usage.get("retrieval_count"):
        cost += usage["retrieval_count"] * COST_PER_RETRIEVAL
    return round(cost, 4)

@contextmanager
def track_usage(model="Claude", user_input=""):
    """Context manager to simulate usage tracking."""
    usage = {"input_tokens": 0, "output_tokens": 0, "retrieval_count": 0}
    start = time.time()
    usage["input_tokens"] = count_tokens(user_input)

    yield usage

    # Simulated output size and retrievals
    usage["output_tokens"] = usage["input_tokens"] * 1.5
    usage["retrieval_count"] = 1 if model in ["RAG+Chunks", "Hybrid"] else 0
    usage["duration"] = round(time.time() - start, 2)
