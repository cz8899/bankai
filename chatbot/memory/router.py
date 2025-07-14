# memory/router.py — Routes interaction history into long-term memory (e.g., Chroma)

from datetime import datetime
from chatbot.memory.summarizer import summarize_messages
from chatbot.vector_store.chroma import store_summary_if_relevant
from chatbot.logger import logger


def summarize_and_store(messages: list[dict]) -> None:
    """
    If messages exceed threshold, summarize and store in ChromaDB.
    """
    if not messages or len(messages) < 4:
        return

    try:
        summary = summarize_messages(messages)
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "tags": list(set(msg.get("type", "qa") for msg in messages)),
            "user": "session_user"  # Customize per auth context
        }
        store_summary_if_relevant(summary, metadata)
        logger.info("[Memory] Summary stored to Chroma vector memory.")

    except Exception as e:
        logger.warning("[Memory] Summarization failed: %s", str(e))
