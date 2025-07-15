# chatbot/utils/conversation_manager.py

import streamlit as st
from typing import List


class ConversationManager:
    """
    Manages session-based conversation history.
    """
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @property
    def messages(self) -> List[dict]:
        return st.session_state.messages

    def append_user(self, content: str) -> None:
        st.session_state.messages.append({"role": "user", "content": content})

    def append_assistant(self, content: str) -> None:
        st.session_state.messages.append({"role": "assistant", "content": content})
