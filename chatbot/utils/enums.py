# chatbot/utils/enums.py

from enum import Enum


class PlannerStage(Enum):
    GATHERING = "gathering_requirements"
    FINAL_CONFIRMATION = "final_confirmation"
    GENERATING_SOLUTION = "generating_solution"
    SHOWING_WIDGETS = "showing_widgets"
