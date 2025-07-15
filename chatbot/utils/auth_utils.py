# chatbot/utils/auth_utils.py

import streamlit as st

ADMIN_EMAILS = {
    "admin@yourcompany.com",
    "ops@yourcompany.com",
    # Add more admins here
}


def is_admin_user() -> bool:
    user_email = st.session_state.get("user_email")
    return user_email in ADMIN_EMAILS
