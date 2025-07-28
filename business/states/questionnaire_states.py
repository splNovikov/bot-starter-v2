"""
FSM states for questionnaire interactions.

Defines conversation states for /questionnaire and /gender commands,
supporting multi-step question flows with conditional logic.
"""

from aiogram.fsm.state import State, StatesGroup


class QuestionnaireStates(StatesGroup):
    """FSM states for questionnaire flow."""
    
    # Basic questionnaire flow
    waiting_for_question_1 = State()  # First question
    waiting_for_question_2 = State()  # Second question  
    waiting_for_gender = State()      # Gender question (can be standalone or part of questionnaire)
    waiting_for_question_4 = State()  # Additional question for female users
    completing = State()              # Final processing state


class GenderStates(StatesGroup):
    """FSM states for standalone gender command."""
    
    waiting_for_gender = State()      # Gender question for /gender command 