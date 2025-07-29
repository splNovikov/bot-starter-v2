"""
Core sequence framework package.

Provides unified sequence infrastructure components for all interactive flows:
questionnaires, quizzes, surveys, and single question+summary interactions.

- Type definitions and protocols for sequences
- Abstract base services for session management and sequence provision  
- Core orchestration services
- Unified decorator for sequence handler registration
- FSM states for sequence interactions

Usage Example:
    ```python
    from core.sequence import (
        sequence_handler,
        SequenceService
    )
    
    @sequence_handler(
        "bio",
        questions=["name", "age", "location", "interests"],
        description="Collect user biography information",
        show_progress=True
    )
    async def cmd_bio(message: Message, state: FSMContext):
        # Handler implementation using sequence framework
        pass
    ```
"""

# Core types and enums
from .types import (
    SequenceStatus,
    QuestionType,
    SequenceOption,
    SequenceQuestion,
    SequenceAnswer,
    SequenceSession,
    SequenceDefinition,
    HandlerCategory  # Re-exported for convenience
)

# Protocol interfaces
from .protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceServiceProtocol,
    SequenceResultHandlerProtocol,
    SequenceQuestionRendererProtocol
)

# FSM states
from .states import (
    SequenceStates,
    SequenceStateManager,
    get_sequence_states
)

# Services
from .services import (
    BaseSequenceManager,
    SequenceService,
    get_sequence_service,
    set_sequence_service
)

# Adapters removed - unified sequence system only

# Decorators - the main interface for defining sequences
from .decorators import (
    sequence_handler,
    is_sequence_handler,
    get_sequence_metadata,
    get_behavior_type,
    get_sequence_name,
    is_scored_sequence,
    is_anonymous_sequence,
    generates_summary
)

__version__ = "1.0.0"

# Main exports organized by category
__all__ = [
    # Core types and enums
    'SequenceStatus',
    'QuestionType', 
    'SequenceOption',
    'SequenceQuestion',
    'SequenceAnswer',
    'SequenceSession',
    'SequenceDefinition',
    'HandlerCategory',
    
    # Protocol interfaces
    'SequenceManagerProtocol',
    'SequenceProviderProtocol',
    'SequenceServiceProtocol', 
    'SequenceResultHandlerProtocol',
    'SequenceQuestionRendererProtocol',
    
    # FSM states
    'SequenceStates',
    'SequenceStateManager',
    'get_sequence_states',
    
    # Services
    'BaseSequenceManager',
    'SequenceService',
    'get_sequence_service',
    'set_sequence_service',
    
    # Decorators - primary interface
    'sequence_handler',
    'is_sequence_handler',
    'get_sequence_metadata',
    'get_behavior_type',
    'get_sequence_name',
    'is_scored_sequence',
    'is_anonymous_sequence',
    'generates_summary'
]


# Convenience functions for common use cases

def create_simple_sequence_definition(
    name: str,
    question_keys: list,
    title: str = None,
    description: str = None,
    **behavior_config
) -> SequenceDefinition:
    """
    Create a simple sequence definition with text questions.
    
    Args:
        name: Sequence name
        question_keys: List of question identifiers
        title: Optional title
        description: Optional description
        **behavior_config: Behavior configuration flags (scored, anonymous, etc.)
        
    Returns:
        SequenceDefinition object
        
    Example:
        ```python
        # Simple questionnaire
        seq_def = create_simple_sequence_definition(
            "user_bio",
            ["name", "age", "location"],
            title="User Biography",
            description="Collect basic user information"
        )
        
        # Quiz with scoring
        quiz_def = create_simple_sequence_definition(
            "trivia",
            ["q1", "q2", "q3"],
            title="Trivia Quiz",
            scored=True,
            show_correct_answers=True
        )
        ```
    """
    questions = []
    for key in question_keys:
        question = SequenceQuestion(
            key=key,
            question_text=f"Please provide your {key.replace('_', ' ')}:",
            question_type=QuestionType.TEXT,
            is_required=True
        )
        questions.append(question)
    
    return SequenceDefinition(
        name=name,
        questions=questions,
        title=title,
        description=description,
        **behavior_config
    )


def create_sequence_handler_with_config(**config_kwargs):
    """
    Create a sequence handler with specific configuration.
    
    This is a helper function that returns the sequence_handler decorator
    with pre-configured behavior flags.
    
    Args:
        **config_kwargs: Configuration arguments for sequence behavior
        
    Returns:
        Configured sequence_handler decorator function
        
    Example:
        ```python
        # Create a quiz-like sequence handler
        quiz_sequence = create_sequence_handler_with_config(
            scored=True, 
            show_correct_answers=True,
            allow_restart=False
        )
        
        @quiz_sequence("trivia", description="Trivia quiz")
        async def cmd_trivia(message, state):
            pass
        ```
    """
    def configured_decorator(command_name: str, **kwargs):
        # Merge provided config with additional kwargs
        merged_kwargs = {**config_kwargs, **kwargs}
        return sequence_handler(command_name, **merged_kwargs)
    
    return configured_decorator


# Add convenience functions to exports
__all__.extend([
    'create_simple_sequence_definition',
    'create_sequence_handler_with_config'
]) 