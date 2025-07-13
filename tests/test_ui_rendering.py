# tests/test_ui_rendering.py

import streamlit as st
from streamlit.testing.v1 import AppTest
import pytest

# Test that the app launches and renders the logo and title
def test_app_renders_logo_and_title():
    at = AppTest.from_file("chatbot/app.py")
    at.run()

    # Logo image is present
    assert any("tfc_logo.png" in str(img.url) for img in at.images), "Logo image not rendered"

    # Title is present
    title_text = f"DevGenius AI Co-Pilot"
    assert any(title_text in h.body for h in at.markdowns), "App title not found"

# Test that chat input renders
@pytest.mark.skipif("chat_input" not in dir(st), reason="chat_input is Streamlit >=1.30+")
def test_chat_input_visible():
    at = AppTest.from_file("chatbot/app.py")
    at.run()
    assert at.chat_input is not None, "Chat input not rendered"

# Test that widgets are not shown initially
def test_widgets_hidden_initially():
    at = AppTest.from_file("chatbot/app.py")
    at.run()
    widget_labels = ["architecture", "cdk", "cloudformation", "cost estimate", "documentation", "draw.io"]
    widget_found = any(label.lower() in w.label.lower() for label in widget_labels for w in at.checkboxes)
    assert not widget_found, "Widgets should not be visible initially"

# Optional: Test that a planner response can update UI state (mock planner if needed)
def test_message_flow():
    at = AppTest.from_file("chatbot/app.py")
    at.session_state["messages"] = [{"role": "user", "content": "Build me an AWS data lake"}]
    at.session_state["planner_stage"] = "showing_widgets"
    at.run()

    # Confirm widgets now show
    widget_labels = ["architecture", "cdk", "cloudformation", "cost estimate", "documentation", "draw.io"]
    widget_found = any(label.lower() in w.label.lower() for label in widget_labels for w in at.checkboxes)
    assert widget_found, "Widgets should be visible when planner_stage is 'showing_widgets'"
