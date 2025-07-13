# chatbot/utils/context_manager.py

import streamlit as st
import uuid

def init_session():
    st.session_state.setdefault("planner_stage", "gathering_requirements")
    st.session_state.setdefault("conversation_id", str(uuid.uuid4()))
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("interaction", [])

def advance_stage():
    from chatbot.utils.constants import PLANNER_STAGES
    current = st.session_state.get("planner_stage", "gathering_requirements")
    idx = PLANNER_STAGES.index(current)
    if idx < len(PLANNER_STAGES) - 1:
        st.session_state.planner_stage = PLANNER_STAGES[idx + 1]