# === chatbot/utils/session_manager.py ===
import streamlit as st
from enum import Enum

class PlannerStage(str, Enum):
    GATHERING = "gathering_requirements"
    CONFIRMING = "final_confirmation"
    GENERATING = "generating_solution"
    SHOWING_WIDGETS = "showing_widgets"

class SessionManager:
    @staticmethod
    def get_conversation_id() -> str:
        if "conversation_id" not in st.session_state:
            st.session_state.conversation_id = "conv-" + str(hash(st.session_state.get("user_email", "anon")))
        return st.session_state.conversation_id

    @staticmethod
    def get_stage() -> PlannerStage:
        return PlannerStage(st.session_state.get("planner_stage", PlannerStage.GATHERING))

    @staticmethod
    def set_stage(stage: PlannerStage) -> None:
        st.session_state.planner_stage = stage

    @staticmethod
    def get_messages() -> list:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        return st.session_state.messages

    @staticmethod
    def add_message(role: str, content: str):
        SessionManager.get_messages().append({"role": role, "content": content})
