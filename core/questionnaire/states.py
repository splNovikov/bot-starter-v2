"""
FSM state definitions for the core questionnaire framework.

Provides base state classes that can be extended by specific implementations
while maintaining clean architecture separation.
"""

from aiogram.fsm.state import State, StatesGroup


class BaseQuestionnaireStates(StatesGroup):
    """Base FSM states for questionnaire flows."""
    
    # Initial states
    starting = State()                # Initializing questionnaire
    welcome = State()                 # Showing welcome message
    
    # Question flow states  
    asking_question = State()         # Asking a question
    waiting_for_answer = State()      # Waiting for user response
    validating_answer = State()       # Validating user input
    processing_answer = State()       # Processing and storing answer
    
    # Progress states
    showing_progress = State()        # Displaying progress information
    transitioning = State()           # Moving between questions
    
    # Completion states
    completing = State()              # Final processing
    completed = State()               # Questionnaire finished
    
    # Error and cancellation states
    error = State()                   # Error occurred
    cancelled = State()               # User cancelled
    timeout = State()                 # Session timed out


class BaseGenderStates(StatesGroup):
    """Base FSM states for gender-related questionnaire flows."""
    
    # Gender question flow
    asking_gender = State()           # Asking gender question
    waiting_for_gender = State()      # Waiting for gender response
    processing_gender = State()       # Processing gender answer
    gender_complete = State()         # Gender question completed


class BaseMultiStepStates(StatesGroup):
    """Base FSM states for multi-step questionnaire processes."""
    
    # Multi-step coordination
    step_starting = State()           # Starting a step
    step_in_progress = State()        # Step in progress
    step_completed = State()          # Step completed
    step_failed = State()             # Step failed
    
    # Branching and conditional logic
    evaluating_condition = State()    # Evaluating conditional logic
    branching = State()               # Choosing next path
    
    # Review and confirmation
    reviewing_answers = State()       # User reviewing their answers
    confirming_submission = State()   # Confirming final submission
    
    # Advanced features
    saving_draft = State()            # Saving partial progress
    loading_draft = State()           # Loading saved progress
    editing_previous = State()        # Editing previous answers


class BaseSessionStates(StatesGroup):
    """Base FSM states for session management."""
    
    # Session lifecycle
    session_created = State()         # New session created
    session_active = State()          # Session is active
    session_paused = State()          # Session paused by user
    session_resuming = State()        # Resuming paused session
    session_ended = State()           # Session ended
    
    # Session validation
    session_validating = State()      # Validating session state
    session_corrupted = State()       # Session data corrupted
    session_recovered = State()       # Session recovered from error


# Factory function for creating custom questionnaire states
def create_questionnaire_states(
    question_keys: list[str], 
    base_class: type = BaseQuestionnaireStates
) -> type:
    """
    Factory function to create custom questionnaire states based on question keys.
    
    Args:
        question_keys: List of question identifiers
        base_class: Base state class to extend
        
    Returns:
        Dynamically created StatesGroup class
    """
    # Create dynamic state attributes
    state_attrs = {}
    
    # Add base states from parent class
    for attr_name in dir(base_class):
        if isinstance(getattr(base_class, attr_name), State):
            state_attrs[attr_name] = State()
    
    # Add question-specific states
    for i, question_key in enumerate(question_keys, 1):
        state_attrs[f'waiting_for_{question_key}'] = State()
        state_attrs[f'processing_{question_key}'] = State()
    
    # Create dynamic class
    return type(
        'DynamicQuestionnaireStates',
        (StatesGroup,),
        state_attrs
    )


__all__ = [
    'BaseQuestionnaireStates',
    'BaseGenderStates', 
    'BaseMultiStepStates',
    'BaseSessionStates',
    'create_questionnaire_states'
] 