"""
Question provider service for questionnaire logic.

Handles question sequences, conditional logic, and localization following
the Single Responsibility Principle.
"""

from typing import List, Optional
from aiogram.types import User

from business.services.localization import t
from business.services.interfaces import QuestionProviderProtocol
from core.utils.logger import get_logger

logger = get_logger()


class QuestionProvider(QuestionProviderProtocol):
    """Provides questions and manages question flow logic."""
    
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
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """
        Get localized question text.
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            Localized question text
        """
        return t(f"questionnaire.questions.{question_key}", user=user)
    
    def should_ask_additional_question(self, answers: dict) -> bool:
        """
        Determine if additional questions should be asked based on answers.
        
        Args:
            answers: Dictionary of current answers
            
        Returns:
            True if additional question should be asked
        """
        gender_answer = answers.get('gender', '').lower()
        return gender_answer in ['female', 'woman', 'f', 'женщина', 'ж', 'mujer', 'm']
    
    def get_next_question(self, current_answers: dict, user: User) -> Optional[str]:
        """
        Get the next question key based on current answers and user.
        
        Args:
            current_answers: Dictionary of answers so far
            user: Telegram user object
            
        Returns:
            Next question key or None if questionnaire is complete
        """
        # Get base question sequence
        questions = self.get_question_sequence(user)
        
        # Find next unanswered question from base sequence
        for question_key in questions:
            if question_key not in current_answers:
                return question_key
        
        # Check if we need to ask additional question
        if (self.should_ask_additional_question(current_answers) and 
            'question_4' not in current_answers):
            return 'question_4'
        
        # No more questions
        return None
    
    def get_progress(self, current_answers: dict, user: User) -> tuple[int, int]:
        """
        Get progress information for the current questionnaire.
        
        Args:
            current_answers: Dictionary of answers so far
            user: Telegram user object
            
        Returns:
            Tuple of (current_question_number, total_questions)
        """
        base_questions = self.get_question_sequence(user)
        total_questions = len(base_questions)
        
        # Add 1 if additional question will be asked
        if self.should_ask_additional_question(current_answers):
            total_questions += 1
        
        # Count answered questions
        answered_count = sum(1 for q in base_questions if q in current_answers)
        if 'question_4' in current_answers:
            answered_count += 1
        
        current = answered_count + 1  # +1 for the question being asked
        
        return min(current, total_questions), total_questions


# Global question provider instance
_question_provider: Optional[QuestionProvider] = None


def get_question_provider() -> QuestionProvider:
    """Get the global question provider instance."""
    global _question_provider
    if _question_provider is None:
        _question_provider = QuestionProvider()
    return _question_provider 