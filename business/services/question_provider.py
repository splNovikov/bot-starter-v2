"""
Question provider service for questionnaire logic.

Concrete implementation extending the core base question provider
with business-specific question definitions and logic.
"""

from typing import List, Optional, Dict

from aiogram.types import User

from core.questionnaire.services import BaseQuestionProvider
from core.questionnaire.types import QuestionData, QuestionOption, QuestionType
from core.services.localization import t
from core.utils.logger import get_logger

logger = get_logger()


class QuestionProvider(BaseQuestionProvider):
    """Provides questions and manages question flow logic."""
    
    def __init__(self):
        """Initialize question provider."""
        super().__init__()
    
    def get_question_sequence(self, user: User) -> List[str]:
        """
        Get the sequence of question keys for a user.
        
        Args:
            user: Telegram user object
            
        Returns:
            List of question keys in order
        """
        return [
            'question_1',
            'question_2', 
            'gender'
        ]
    
    def _load_question_data(self, question_key: str, user: User) -> QuestionData:
        """
        Load question data from localization source.
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            QuestionData object with question details
        """
        question_data_raw = t(f"questionnaire.questions.{question_key}", user=user, raw=True)
        
        if isinstance(question_data_raw, dict):
            options = []
            if question_data_raw.get('options'):
                options = [
                    QuestionOption(text=opt['text'], value=opt['value'])
                    for opt in question_data_raw['options']
                ]
            
            return QuestionData(
                text=question_data_raw.get('text', ''),
                image=question_data_raw.get('image'),
                question_type=QuestionType(question_data_raw.get('type', 'text')),
                options=options if options else None
            )
        else:
            return QuestionData(
                text=str(question_data_raw),
                question_type=QuestionType.TEXT
            )

    
    def should_ask_additional_question(self, answers: Dict[str, str]) -> bool:
        """
        Determine if additional questions should be asked based on answers.
        
        Args:
            answers: Dictionary of current answers
            
        Returns:
            True if additional question should be asked
        """
        gender_answer = answers.get('gender', '').lower()
        # Check for female values in button format and legacy text format
        female_values = ['female', 'woman', 'f', 'женщина', 'ж', 'mujer', 'm', 'femenino']
        return gender_answer in female_values
    
    def _get_additional_questions(self, current_answers: Dict[str, str], user: User) -> List[str]:
        """
        Get additional questions based on current answers.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            List of additional question keys
        """
        return ['question_4']


# Global question provider instance
_question_provider: Optional[QuestionProvider] = None


def get_question_provider() -> QuestionProvider:
    """Get the global question provider instance."""
    global _question_provider
    if _question_provider is None:
        _question_provider = QuestionProvider()
    return _question_provider 