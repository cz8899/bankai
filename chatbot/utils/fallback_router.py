# === chatbot/utils/fallback_router.py ===
from chatbot.agent import call_claude
from chatbot.logger import logger

def fallback_to_claude(user_input: str) -> str:
    logger.warning("[Fallback] Switching to Claude fallback mode")
    return call_claude(user_input)
