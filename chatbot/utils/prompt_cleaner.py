import re


def sanitize_prompt(prompt: str) -> str:
    """
    Preprocess the prompt to remove problematic characters,
    normalize formatting, and ensure consistent syntax.

    - Strips emojis/symbols
    - Removes extra whitespace
    - Cleans assistant-style prefixes
    - Ensures proper sentence punctuation
    """

    if not isinstance(prompt, str) or not prompt.strip():
        return ""

    # Remove LLM-like prompt prefixes
    prompt = re.sub(r"^(user|assistant|system)\s*[:\-]\s*", "", prompt, flags=re.IGNORECASE)

    # Remove emojis or non-standard characters (basic Unicode-safe filtering)
    prompt = re.sub(r"[^\w\s.,!?;:()\-\'\"]+", "", prompt, flags=re.UNICODE)

    # Collapse whitespace
    prompt = re.sub(r"\s+", " ", prompt).strip()

    # Enforce sentence-ending punctuation
    if prompt and prompt[-1] not in ".!?":
        prompt += "."

    return prompt
