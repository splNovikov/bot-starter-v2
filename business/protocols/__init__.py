"""
Business layer protocol interfaces.

Contains business domain-specific protocol definitions that define
contracts for business services and use cases.
"""

from .questionnaire import (
    QuestionOption,
    QuestionData,
    SessionManagerProtocol, 
    QuestionProviderProtocol
)

__all__ = [
    'QuestionOption',
    'QuestionData', 
    'SessionManagerProtocol',
    'QuestionProviderProtocol'
] 