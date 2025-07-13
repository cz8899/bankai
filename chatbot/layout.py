# chatbot/layout.py

import streamlit as st
from chatbot.utils.constants import TRUIST_PURPLE, LOGO_PATH


def render_header():
    """Displays Truist-branded header with logo and title."""
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(LOGO_PATH, width=90)
    with col2:
        st.markdown(
            f"<h1 style='color:{TRUIST_PURPLE}; margin-top: 0.3em;'>DevGenius AI Co-Pilot</h1>",
            unsafe_allow_html=True
        )


def render_footer():
    """Displays footer branding."""
    st.markdown(
        f"<footer style='margin-top:3em; text-align:center; font-size:0.8rem; color:gray;'>"
        f"Built by Truist Engineering & AI Lab | Powered by AWS Bedrock"
        f"</footer>",
        unsafe_allow_html=True
    )
