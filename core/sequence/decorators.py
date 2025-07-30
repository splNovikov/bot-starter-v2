"""
Sequence decorator for the core framework.

Provides a unified decorator for registering sequence-related handlers
with behavior configuration instead of separate handler types.
"""

from typing import Callable, List, Optional, Any
from functools import wraps

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory, HandlerMetadata
from core.utils.logger import get_logger

logger = get_logger()


def sequence_handler(
    command_name: str,
    *,
    sequence_name: Optional[str] = None,
    questions: Optional[List[str]] = None,
    description: str,
    category: HandlerCategory = HandlerCategory.USER,
    usage: Optional[str] = None,
    examples: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    enabled: bool = True,
    
    # Behavior configuration flags (instead of separate types)
    scored: bool = False,  # Enable scoring (makes it "quiz-like")
    anonymous: bool = False,  # Anonymous responses (makes it "survey-like")
    show_progress: bool = True,  # Show progress indicator
    allow_restart: bool = True,  # Allow restarting the sequence
    allow_skip: bool = False,  # Allow skipping questions
    randomize_questions: bool = False,  # Randomize question order
    generate_summary: bool = False,  # Generate AI summary (for single Q+summary)
    
    # Scoring configuration (when scored=True)
    time_limit: Optional[int] = None,  # minutes
    passing_score: Optional[int] = None,
    show_correct_answers: bool = True,
    immediate_feedback: bool = False,  # Show feedback after each question
    
    **kwargs
) -> Callable:
    """
    Universal decorator for registering sequence command handlers.
    
    This decorator handles all sequence types through configuration flags
    rather than separate decorator types, following the principle that
    "everything is a sequence except standalone messages".
    
    Args:
        command_name: Command name (without /)
        sequence_name: Internal sequence identifier (defaults to command_name)
        questions: List of question identifiers this handler manages
        description: Human-readable description
        category: Handler category
        usage: Usage example
        examples: List of usage examples
        aliases: Alternative command names
        enabled: Whether handler is enabled
        
        # Behavior flags:
        scored: Enable scoring and correct answers (quiz-like behavior)
        anonymous: Anonymous responses (survey-like behavior)
        show_progress: Show progress indicators
        allow_restart: Allow restarting sequences
        allow_skip: Allow skipping questions
        randomize_questions: Randomize question order
        generate_summary: Generate AI summary (for single question sequences)
        
        # Scoring configuration (when scored=True):
        time_limit: Time limit in minutes
        passing_score: Minimum score to pass
        show_correct_answers: Show correct answers after completion
        immediate_feedback: Show feedback after each question
        
        **kwargs: Additional metadata
        
    Returns:
        Decorated handler function
        
    Examples:
        # User questionnaire (bio collection, onboarding)
        @sequence_handler(
            "bio",
            questions=["name", "age", "location", "interests"],
            description="Collect user biography information",
            show_progress=True,
            allow_restart=True
        )
        
        # Scored quiz
        @sequence_handler(
            "trivia", 
            questions=["q1", "q2", "q3"],
            description="General knowledge quiz",
            scored=True,
            show_correct_answers=True,
            time_limit=10
        )
        
        # Anonymous survey
        @sequence_handler(
            "feedback",
            questions=["satisfaction", "improvement", "recommendation"],
            description="Customer feedback survey",
            anonymous=True,
            show_progress=True
        )
        
        # Single question with AI summary
        @sequence_handler(
            "example",
            questions=["example_question"],
            description="Example question with AI summary",
            generate_summary=True,
            show_progress=False
        )
    """
    def decorator(func: Callable) -> Callable:
        # Prepare sequence-specific metadata
        sequence_metadata = {
            'sequence_name': sequence_name or command_name,
            'questions': questions or [],
            'scored': scored,
            'anonymous': anonymous,
            'show_progress': show_progress,
            'allow_restart': allow_restart,
            'allow_skip': allow_skip,
            'randomize_questions': randomize_questions,
            'generate_summary': generate_summary,
            'time_limit': time_limit,
            'passing_score': passing_score,
            'show_correct_answers': show_correct_answers,
            'immediate_feedback': immediate_feedback,
            **kwargs
        }
        
        # Determine behavior type for logging/introspection
        behavior_type = "sequence"
        if scored:
            behavior_type = "quiz"
        elif anonymous:
            behavior_type = "survey"  
        elif generate_summary and len(questions or []) == 1:
            behavior_type = "single_question_summary"
        elif questions and len(questions) > 1:
            behavior_type = "questionnaire"
        
        # Filter out sequence-specific fields for base command decorator
        base_command_kwargs = {}
        for key, value in kwargs.items():
            # Only pass through standard command decorator arguments
            if key not in ['scored', 'anonymous', 'show_progress', 'allow_restart', 
                          'allow_skip', 'randomize_questions', 'generate_summary',
                          'time_limit', 'passing_score', 'show_correct_answers', 
                          'immediate_feedback']:
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
            tags=['sequence', behavior_type],
            **base_command_kwargs
        )(func)
        
        # Add sequence-specific wrapper functionality
        @wraps(enhanced_func)
        async def wrapper(*args, **wrapper_kwargs):
            # Log sequence command execution
            logger.debug(f"Executing {behavior_type} sequence command: {command_name}")
            
            # Call the original function
            result = await enhanced_func(*args, **wrapper_kwargs)
            
            # Post-execution logging
            logger.debug(f"Completed {behavior_type} sequence command: {command_name}")
            
            return result
        
        # Preserve metadata for introspection
        wrapper._sequence_metadata = sequence_metadata
        wrapper._is_sequence_handler = True
        wrapper._behavior_type = behavior_type
        
        return wrapper
    
    return decorator


# Utility functions for metadata inspection

def is_sequence_handler(func: Callable) -> bool:
    """
    Check if a function is a sequence handler.
    
    Args:
        func: Function to check
        
    Returns:
        True if function is a sequence handler
    """
    return hasattr(func, '_is_sequence_handler') and func._is_sequence_handler


def get_sequence_metadata(func: Callable) -> Optional[dict]:
    """
    Get sequence metadata from a handler function.
    
    Args:
        func: Handler function
        
    Returns:
        Sequence metadata dictionary or None
    """
    if is_sequence_handler(func):
        return getattr(func, '_sequence_metadata', None)
    return None


def get_behavior_type(func: Callable) -> Optional[str]:
    """
    Get behavior type from a handler function.
    
    Args:
        func: Handler function
        
    Returns:
        Behavior type string ('quiz', 'survey', 'questionnaire', etc.) or None
    """
    if is_sequence_handler(func):
        return getattr(func, '_behavior_type', None)
    return None


def get_sequence_name(func: Callable) -> Optional[str]:
    """
    Get sequence name from a handler function.
    
    Args:
        func: Handler function
        
    Returns:
        Sequence name string or None
    """
    metadata = get_sequence_metadata(func)
    return metadata.get('sequence_name') if metadata else None


def is_scored_sequence(func: Callable) -> bool:
    """
    Check if a sequence handler has scoring enabled.
    
    Args:
        func: Handler function
        
    Returns:
        True if sequence is scored (quiz-like)
    """
    metadata = get_sequence_metadata(func)
    return metadata.get('scored', False) if metadata else False


def is_anonymous_sequence(func: Callable) -> bool:
    """
    Check if a sequence handler is anonymous.
    
    Args:
        func: Handler function
        
    Returns:
        True if sequence is anonymous (survey-like)
    """
    metadata = get_sequence_metadata(func)
    return metadata.get('anonymous', False) if metadata else False


def generates_summary(func: Callable) -> bool:
    """
    Check if a sequence handler generates AI summaries.
    
    Args:
        func: Handler function
        
    Returns:
        True if sequence generates summaries
    """
    metadata = get_sequence_metadata(func)
    return metadata.get('generate_summary', False) if metadata else False


__all__ = [
    'sequence_handler',
    'is_sequence_handler',
    'get_sequence_metadata',
    'get_behavior_type',
    'get_sequence_name',
    'is_scored_sequence',
    'is_anonymous_sequence',
    'generates_summary'
] 