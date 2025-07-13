# test/test_context_manager.py
import streamlit as st
from chatbot.utils.context_manager import init_session, advance_stage
from chatbot.utils.constants import PLANNER_STAGES

def test_init_session_sets_defaults():
    init_session()
    assert st.session_state.planner_stage == "gathering_requirements"
    assert isinstance(st.session_state.messages, list)

def test_advance_stage():
    st.session_state.planner_stage = "gathering_requirements"
    advance_stage()
    assert st.session_state.planner_stage == "refining_scope"
