# chatbot/utils/auth_utils.py

import streamlit as st
import os
import logging

logger = logging.getLogger(__name__)

# Default admin list (can be extended via env or config)
STATIC_ADMINS = {
    "admin@yourcompany.com",
    "ops@yourcompany.com"
}

def get_user_email() -> str:
    """
    Return current user's email from session or fallback.
    """
    return st.session_state.get("user_email", "")


def is_admin_user() -> bool:
    """
    Return True if the current user is an authorized admin.
    Supports both static list and comma-separated ADMIN_EMAILS env variable.
    """
    user_email = get_user_email()
    dynamic_admins = os.getenv("ADMIN_EMAILS", "")
    allowed = STATIC_ADMINS.union({email.strip() for email in dynamic_admins.split(",") if email.strip()})

    if user_email in allowed:
        logger.info(f"[Auth] Admin access granted: {user_email}")
        return True
    else:
        logger.warning(f"[Auth] Unauthorized admin attempt: {user_email}")
        return False
