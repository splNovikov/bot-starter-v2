# Decorators - the main interface for defining sequences
from .decorators import (
    generates_summary,
    get_behavior_type,
    get_sequence_metadata,
    get_sequence_name,
    is_anonymous_sequence,
    is_scored_sequence,
    is_sequence_handler,
    sequence_handler,
)

# Factories
from .factories import (
    create_translator,
    set_translator_factory,
)

# Protocol interfaces
from .protocols import (
    SequenceManagerProtocol,
    SequenceProviderProtocol,
    SequenceQuestionRendererProtocol,
    SequenceResultHandlerProtocol,
    SequenceServiceProtocol,
)

# FSM states
from .states import SequenceStateManager, SequenceStates, get_sequence_states
from .types import (
    HandlerCategory,
    QuestionType,
    SequenceAnswer,
    SequenceDefinition,
    SequenceOption,
    SequenceQuestion,
    SequenceSession,
    SequenceStatus,
)

# Services module is deprecated - use dependency injection instead


__version__ = "1.0.0"

# Main exports organized by category
__all__ = [
    # Core types and enums
    "SequenceStatus",
    "QuestionType",
    "SequenceOption",
    "SequenceQuestion",
    "SequenceAnswer",
    "SequenceSession",
    "SequenceDefinition",
    "HandlerCategory",
    # Protocol interfaces
    "SequenceManagerProtocol",
    "SequenceProviderProtocol",
    "SequenceServiceProtocol",
    "SequenceResultHandlerProtocol",
    "SequenceQuestionRendererProtocol",
    # FSM states
    "SequenceStates",
    "SequenceStateManager",
    "get_sequence_states",
    # Factories
    "create_translator",
    "set_translator_factory",
    # Decorators - primary interface
    "sequence_handler",
    "is_sequence_handler",
    "get_sequence_metadata",
    "get_behavior_type",
    "get_sequence_name",
    "is_scored_sequence",
    "is_anonymous_sequence",
    "generates_summary",
]


# Convenience functions for common use cases


def create_simple_sequence_definition(
    name: str,
    question_keys: list,
    title: str = None,
    description: str = None,
    **behavior_config,
) -> SequenceDefinition:
    questions = []
    for key in question_keys:
        question = SequenceQuestion(
            key=key,
            question_text=f"Please provide your {key.replace('_', ' ')}:",
            question_type=QuestionType.TEXT,
            is_required=True,
        )
        questions.append(question)

    return SequenceDefinition(
        name=name,
        questions=questions,
        title=title,
        description=description,
        **behavior_config,
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
__all__.extend(
    ["create_simple_sequence_definition", "create_sequence_handler_with_config"]
)
