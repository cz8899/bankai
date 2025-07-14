# Summarizes conversation history using Claude (or fallback)
from chatbot.agent import call_claude
from chatbot.logger import logger


def summarize_messages(messages: list[dict]) -> str:
    """
    Summarizes a list of conversation messages into a compact narrative.
    Args:
        messages: A list of {"role": ..., "content": ...} dicts.
    Returns:
        A single summary string.
    """
    if not messages:
        return "No conversation to summarize."

    try:
        transcript = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in messages)
        prompt = f"""
        Please summarize the following conversation into a short, fact-preserving narrative
        for long-term memory storage. Focus on intent, decisions, and knowledge shared.

        Conversation:
        {transcript}

        Summary:
        """
        return call_claude(prompt)

    except Exception as e:
        logger.exception("[Summarizer] Failed to summarize: %s", e)
        return "⚠️ Summarization failed."

