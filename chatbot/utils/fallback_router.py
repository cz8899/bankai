# chatbot/utils/fallback_router.py

def fallback_router(current_mode: str) -> str:
    """
    Determines fallback mode based on current setting.
    """
    if current_mode == "Claude":
        return "Agent"
    elif current_mode == "Agent":
        return "Claude"
    else:
        return "Claude"  # Default fallback for unknown modes
