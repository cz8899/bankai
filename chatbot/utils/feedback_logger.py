# === chatbot/utils/feedback_logger.py ===
import json
from datetime import datetime
from pathlib import Path

FEEDBACK_LOG_PATH = Path("logs/feedback.jsonl")
FEEDBACK_LOG_PATH.parent.mkdir(exist_ok=True)

def log_feedback(prompt: str, response: str, rating: str, notes: str = "", user: str = "anon") -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "prompt": prompt,
        "response": response,
        "rating": rating,
        "notes": notes
    }
    with FEEDBACK_LOG_PATH.open("a") as f:
        f.write(json.dumps(record) + "\n")
