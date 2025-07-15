# chatbot/utils/prompt_cleaner.py

import re


def sanitize_prompt(prompt: str) -> str:
    """
    Preprocess the prompt to remove problematic characters,
    excessive whitespace, or unsupported input formats.
    """
    if not isinstance(prompt, str):
        return ""

    # Remove emojis (basic fallback)
    prompt = re.sub(r"[^\w\s,.!?;:()\-\'\"]+", "", prompt)

    # Normalize whitespace
    prompt = re.sub(r"\s+", " ", prompt)

    # Trim and ensure sentence end punctuation
    prompt = prompt.strip()
    if prompt and prompt[-1] not in ".!?":
        prompt += "."

    return prompt
