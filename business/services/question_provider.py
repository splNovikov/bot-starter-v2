"""
Question provider service for questionnaire logic.

Handles question sequences, conditional logic, and localization following
the Single Responsibility Principle.
"""

from typing import List, Optional, Dict

from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton

from business.protocols.questionnaire import QuestionProviderProtocol, QuestionData, QuestionOption
from core.services.localization import t
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
    
    def get_question_data(self, question_key: str, user: User) -> QuestionData:
        """
        Get enhanced question data including text, image, and options.
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            QuestionData object with question details
        """
        try:
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
                    question_type=question_data_raw.get('type', 'text'),
                    options=options if options else None
                )
            else:
                return QuestionData(
                    text=str(question_data_raw),
                    question_type='text'
                )
        except Exception as e:
            logger.error(f"Error getting question data for {question_key}: {e}")
            # Fallback to simple text
            return QuestionData(
                text=f"Question {question_key}",
                question_type='text'
            )
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """
        Get localized question text (backward compatibility).
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            Localized question text
        """
        question_data = self.get_question_data(question_key, user)
        return question_data.text
    
    def create_question_keyboard(self, question_key: str, user: User) -> Optional[InlineKeyboardMarkup]:
        """
        Create inline keyboard for question options.
        
        Args:
            question_key: Question identifier
            user: Telegram user object for localization
            
        Returns:
            InlineKeyboardMarkup if question has options, None otherwise
        """
        question_data = self.get_question_data(question_key, user)
        
        if question_data.question_type != 'buttons' or not question_data.options:
            return None
        
        # Create keyboard buttons
        keyboard_buttons = []
        for option in question_data.options:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=option.text,
                    callback_data=f"q_answer:{question_key}:{option.value}"
                )
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    def validate_answer(self, question_key: str, answer: str, user: User) -> bool:
        """
        Validate if the answer is valid for the given question.
        
        Args:
            question_key: Question identifier
            answer: User's answer
            user: Telegram user object for localization
            
        Returns:
            True if answer is valid
        """
        question_data = self.get_question_data(question_key, user)
        
        if question_data.question_type == 'buttons' and question_data.options:
            # Check if answer matches any option value
            valid_values = [option.value for option in question_data.options]
            return answer in valid_values
        
        # For text questions, any non-empty answer is valid
        return bool(answer.strip())
    
    def get_answer_display_text(self, question_key: str, answer: str, user: User) -> str:
        """
        Get display text for an answer value.
        
        Args:
            question_key: Question identifier
            answer: Answer value
            user: Telegram user object for localization
            
        Returns:
            Human-readable answer text
        """
        question_data = self.get_question_data(question_key, user)
        
        if question_data.question_type == 'buttons' and question_data.options:
            # Find the option with matching value
            for option in question_data.options:
                if option.value == answer:
                    return option.text
        
        # Return the answer as-is for text questions or if no match found
        return answer
    
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
    
    def get_next_question(self, current_answers: Dict[str, str], user: User) -> Optional[str]:
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
    
    def get_progress(self, current_answers: Dict[str, str], user: User) -> tuple[int, int]:
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