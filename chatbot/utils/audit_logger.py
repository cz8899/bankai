# === chatbot/utils/audit_logger.py ===
def log_audit_event(action: str, user: str = "anon", details: dict = {}):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "action": action,
        "details": details
    }
    with open("logs/audit_log.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")
