def bootstrap_user_session():
    import streamlit as st

    # Assume you decode from Cognito JWT or session
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = os.getenv("USER_EMAIL", "guest@example.com")
