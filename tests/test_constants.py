# test/test_constants.py
from chatbot.utils import constants

def test_model_ids():
    assert "claude" in constants.CLAUDE_MODEL_ID.lower()
    assert constants.BEDROCK_REGION == "us-west-2"

def test_stage_sequence():
    assert constants.PLANNER_STAGES[0] == "gathering_requirements"
    assert "showing_widgets" in constants.PLANNER_STAGES