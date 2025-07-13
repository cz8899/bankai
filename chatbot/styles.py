# chatbot/styles.py
import streamlit as st
from chatbot.utils.constants import TRUIST_PURPLE

def inject_custom_css():
    st.markdown("""
        <style>
            .main {
                background-color: #ffffff;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }
            .stButton > button {
                background-color: #4B2885 !important;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.5rem 1rem;
                font-weight: bold;
            }
            .stButton > button:hover {
                background-color: #371b61 !important;
            }
            .stChatMessage {
                padding: 0.5rem;
                margin-bottom: 0.5rem;
                border-radius: 10px;
            }
            .stChatMessage.user {
                background-color: #f2f2f2;
            }
            .stChatMessage.assistant {
                background-color: #f0e8fa;
            }
            .stDownloadButton button {
                background-color: #4B2885 !important;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)
