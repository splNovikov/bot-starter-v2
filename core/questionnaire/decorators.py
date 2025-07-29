"""
Questionnaire-specific decorators for the core framework.

Provides specialized decorators for registering questionnaire-related handlers
with enhanced metadata and integration with the questionnaire framework.
"""

from typing import Callable, List, Optional, Any
from functools import wraps

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory, HandlerMetadata
from core.utils.logger import get_logger

logger = get_logger()


def questionnaire_handler(
    command_name: str,
    *,
    description: str,
    question_keys: Optional[List[str]] = None,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    show_progress: bool = True,
    allow_restart: bool = True,
    **kwargs
) -> Callable:
    """
    Decorator for registering questionnaire command handlers.
    
    This decorator extends the base command decorator with questionnaire-specific
    metadata and functionality.
    
    Args:
        command_name: Command name (without /)
        description: Human-readable description
        question_keys: List of question identifiers this handler manages
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        show_progress: Whether to show progress indicators
        allow_restart: Whether to allow restarting questionnaires
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Example:
        @questionnaire_handler(
            "survey",
            description="Start customer satisfaction survey",
            question_keys=["satisfaction", "recommendation", "feedback"],
            aliases=["feedback", "rate"],
            examples=["/survey", "/feedback", "/rate"]
        )
        async def cmd_survey(message: Message, state: FSMContext):
            # Handler implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Prepare questionnaire-specific metadata
        questionnaire_metadata = {
            'question_keys': question_keys or [],
            'show_progress': show_progress,
            'allow_restart': allow_restart,
            'questionnaire_type': 'multi_step' if question_keys and len(question_keys) > 1 else 'single',
            **kwargs
        }
        
        # Filter out questionnaire-specific fields for base command decorator
        base_command_kwargs = {}
        for key, value in kwargs.items():
            # Only pass through standard command decorator arguments
            if key not in ['question_keys', 'show_progress', 'allow_restart', 'questionnaire_type', 
                          'survey_name', 'anonymous', 'quiz_name', 'scored', 'time_limit']:
                base_command_kwargs[key] = value
        
        # Use the base command decorator with filtered metadata
        enhanced_func = command(
            command_name,
            description=description,
            category=category,
            usage=usage or f"/{command_name}",
            examples=examples or [f"/{command_name}"],
            aliases=aliases or [],
            enabled=enabled,
            tags=['questionnaire'],
            **base_command_kwargs
        )(func)
        
        # Add questionnaire-specific wrapper functionality
        @wraps(enhanced_func)
        async def wrapper(*args, **wrapper_kwargs):
            # Log questionnaire command execution
            logger.debug(f"Executing questionnaire command: {command_name}")
            
            # Call the original function
            result = await enhanced_func(*args, **wrapper_kwargs)
            
            # Post-execution logging
            logger.debug(f"Completed questionnaire command: {command_name}")
            
            return result
        
        # Preserve metadata for introspection
        wrapper._questionnaire_metadata = questionnaire_metadata
        wrapper._is_questionnaire_handler = True
        
        return wrapper
    
    return decorator


def single_question_handler(
    command_name: str,
    question_key: str,
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    **kwargs
) -> Callable:
    """
    Decorator for single question handlers (e.g., /gender, /age).
    
    Args:
        command_name: Command name (without /)
        question_key: Single question identifier
        description: Human-readable description
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Example:
        @single_question_handler(
            "gender",
            "gender",
            description="Submit your gender information",
            aliases=["sex"],
            examples=["/gender"]
        )
        async def cmd_gender(message: Message, state: FSMContext):
            # Handler implementation
            pass
    """
    return questionnaire_handler(
        command_name,
        description=description,
        question_keys=[question_key],
        category=category,
        usage=usage,
        examples=examples,
        aliases=aliases,
        enabled=enabled,
        show_progress=False,
        allow_restart=False,
        questionnaire_type='single',
        **kwargs
    )


def multi_step_questionnaire_handler(
    command_name: str,
    question_keys: List[str],
    *,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    show_progress: bool = True,
    allow_restart: bool = True,
    **kwargs
) -> Callable:
    """
    Decorator for multi-step questionnaire handlers.
    
    Args:
        command_name: Command name (without /)
        question_keys: List of question identifiers in order
        description: Human-readable description
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        show_progress: Whether to show progress indicators
        allow_restart: Whether to allow restarting questionnaires
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Example:
        @multi_step_questionnaire_handler(
            "onboarding",
            ["name", "age", "interests", "experience"],
            description="Complete user onboarding questionnaire",
            aliases=["setup", "register"],
            examples=["/onboarding", "/setup"]
        )
        async def cmd_onboarding(message: Message, state: FSMContext):
            # Handler implementation
            pass
    """
    return questionnaire_handler(
        command_name,
        description=description,
        question_keys=question_keys,
        category=category,
        usage=usage,
        examples=examples,
        aliases=aliases,
        enabled=enabled,
        show_progress=show_progress,
        allow_restart=allow_restart,
        questionnaire_type='multi_step',
        **kwargs
    )


def survey_handler(
    command_name: str,
    *,
    description: str,
    survey_name: str,
    question_keys: Optional[List[str]] = None,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    anonymous: bool = False,
    **kwargs
) -> Callable:
    """
    Decorator for survey handlers with survey-specific metadata.
    
    Args:
        command_name: Command name (without /)
        description: Human-readable description
        survey_name: Internal survey identifier
        question_keys: List of question identifiers
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        anonymous: Whether survey responses are anonymous
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Example:
        @survey_handler(
            "satisfaction",
            description="Customer satisfaction survey",
            survey_name="customer_satisfaction_2024",
            aliases=["feedback", "rate"],
            anonymous=True
        )
        async def cmd_satisfaction(message: Message, state: FSMContext):
            # Handler implementation
            pass
    """
    return questionnaire_handler(
        command_name,
        description=description,
        question_keys=question_keys,
        category=category,
        usage=usage,
        examples=examples,
        aliases=aliases,
        enabled=enabled,
        show_progress=True,
        allow_restart=True,
        questionnaire_type='survey',
        survey_name=survey_name,
        anonymous=anonymous,
        **kwargs
    )


def quiz_handler(
    command_name: str,
    *,
    description: str,
    quiz_name: str,
    question_keys: Optional[List[str]] = None,
    category: HandlerCategory = HandlerCategory.FUN,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    scored: bool = True,
    time_limit: Optional[int] = None,
    **kwargs
) -> Callable:
    """
    Decorator for quiz handlers with quiz-specific metadata.
    
    Args:
        command_name: Command name (without /)
        description: Human-readable description
        quiz_name: Internal quiz identifier
        question_keys: List of question identifiers
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        scored: Whether quiz has scoring
        time_limit: Time limit in minutes (None for no limit)
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Example:
        @quiz_handler(
            "trivia",
            description="General knowledge trivia quiz",
            quiz_name="general_trivia",
            aliases=["knowledge", "test"],
            scored=True,
            time_limit=10
        )
        async def cmd_trivia(message: Message, state: FSMContext):
            # Handler implementation
            pass
    """
    return questionnaire_handler(
        command_name,
        description=description,
        question_keys=question_keys,
        category=category,
        usage=usage,
        examples=examples,
        aliases=aliases,
        enabled=enabled,
        show_progress=True,
        allow_restart=False,  # Quizzes typically don't allow restart
        questionnaire_type='quiz',
        quiz_name=quiz_name,
        scored=scored,
        time_limit=time_limit,
        **kwargs
    )


# Utility functions for metadata inspection

def is_questionnaire_handler(func: Callable) -> bool:
    """
    Check if a function is a questionnaire handler.
    
    Args:
        func: Function to check
        
    Returns:
        True if function is a questionnaire handler
    """
    return hasattr(func, '_is_questionnaire_handler') and func._is_questionnaire_handler


def get_questionnaire_metadata(func: Callable) -> Optional[dict]:
    """
    Get questionnaire metadata from a handler function.
    
    Args:
        func: Handler function
        
    Returns:
        Questionnaire metadata dictionary or None
    """
    if is_questionnaire_handler(func):
        return getattr(func, '_questionnaire_metadata', None)
    return None


def get_questionnaire_type(func: Callable) -> Optional[str]:
    """
    Get questionnaire type from a handler function.
    
    Args:
        func: Handler function
        
    Returns:
        Questionnaire type string or None
    """
    metadata = get_questionnaire_metadata(func)
    return metadata.get('questionnaire_type') if metadata else None 