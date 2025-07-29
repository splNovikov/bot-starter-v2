"""
Base question provider for questionnaire framework.

Provides abstract base class with common question management functionality
that can be extended by concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
from aiogram.types import User, InlineKeyboardMarkup, InlineKeyboardButton

from core.utils.logger import get_logger
from core.services.localization import t
from ..protocols import QuestionProviderProtocol
from ..types import QuestionData, QuestionOption, QuestionType

logger = get_logger()


class BaseQuestionProvider(QuestionProviderProtocol, ABC):
    """
    Abstract base class for question provider implementations.
    
    Provides common functionality while allowing concrete implementations
    to customize question sources, logic, and localization.
    """
    
    def __init__(self):
        """Initialize base question provider."""
        self._question_cache: Dict[str, QuestionData] = {}
    
    @abstractmethod
    def get_question_sequence(self, user: User) -> List[str]:
        """
        Get the sequence of question keys for a user.
        Must be implemented by subclasses.
        
        Args:
            user: User object for personalization
            
        Returns:
            List of question keys in order
        """
        pass
    
    @abstractmethod
    def _load_question_data(self, question_key: str, user: User) -> QuestionData:
        """
        Load question data from source (implemented by subclasses).
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
        Returns:
            QuestionData object
        """
        pass
    
    def get_question_data(self, question_key: str, user: User) -> QuestionData:
        """
        Get enhanced question data including text, image, and options.
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
        Returns:
            QuestionData object with question details
        """
        try:
            # Check cache first
            cache_key = f"{question_key}_{user.language_code or 'en'}"
            if cache_key in self._question_cache:
                return self._question_cache[cache_key]
            
            # Load from source
            question_data = self._load_question_data(question_key, user)
            
            # Cache the result
            self._question_cache[cache_key] = question_data
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error loading question data for {question_key}: {e}")
            # Return fallback question
            return QuestionData(
                text=f"Question {question_key}",
                question_type=QuestionType.TEXT
            )
    
    def get_question_text(self, question_key: str, user: User) -> str:
        """
        Get localized question text (backward compatibility).
        
        Args:
            question_key: Question identifier
            user: User object for localization
            
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
            user: User object for localization
            
        Returns:
            InlineKeyboardMarkup if question has options, None otherwise
        """
        question_data = self.get_question_data(question_key, user)
        
        if question_data.question_type not in [QuestionType.BUTTONS, QuestionType.MULTIPLE_CHOICE] or not question_data.options:
            return None
        
        # Create keyboard buttons
        keyboard_buttons = []
        
        for option in question_data.options:
            button_text = option.text
            if option.emoji:
                button_text = f"{option.emoji} {button_text}"
                
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=button_text,
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
            user: User object for context
            
        Returns:
            True if answer is valid
        """
        try:
            question_data = self.get_question_data(question_key, user)
            
            # For button/choice questions, validate against options
            if question_data.question_type in [QuestionType.BUTTONS, QuestionType.MULTIPLE_CHOICE, QuestionType.MULTIPLE_SELECT]:
                if question_data.options:
                    valid_values = [option.value for option in question_data.options]
                    return answer in valid_values
                return False
            
            # For scale questions, validate numeric range
            elif question_data.question_type == QuestionType.SCALE:
                try:
                    value = int(answer)
                    validation = question_data.validation or {}
                    min_val = validation.get('min', 1)
                    max_val = validation.get('max', 10)
                    return min_val <= value <= max_val
                except ValueError:
                    return False
            
            # For yes/no questions
            elif question_data.question_type == QuestionType.YES_NO:
                return answer.lower() in ['yes', 'no', 'y', 'n', '1', '0', 'true', 'false']
            
            # For number questions
            elif question_data.question_type == QuestionType.NUMBER:
                try:
                    float(answer)
                    return True
                except ValueError:
                    return False
            
            # For email questions
            elif question_data.question_type == QuestionType.EMAIL:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(email_pattern, answer))
            
            # For text questions, any non-empty answer is valid
            elif question_data.question_type == QuestionType.TEXT:
                return bool(answer.strip())
            
            # Default: accept any non-empty answer
            return bool(answer.strip())
            
        except Exception as e:
            logger.error(f"Error validating answer for {question_key}: {e}")
            return bool(answer.strip())  # Fallback validation
    
    def get_answer_display_text(self, question_key: str, answer: str, user: User) -> str:
        """
        Get display text for an answer value.
        
        Args:
            question_key: Question identifier
            answer: Answer value
            user: User object for localization
            
        Returns:
            Human-readable answer text
        """
        try:
            question_data = self.get_question_data(question_key, user)
            
            if question_data.question_type in [QuestionType.BUTTONS, QuestionType.MULTIPLE_CHOICE] and question_data.options:
                # Find the option with matching value
                for option in question_data.options:
                    if option.value == answer:
                        return option.text
            
            # For yes/no questions, convert to readable format
            elif question_data.question_type == QuestionType.YES_NO:
                if answer.lower() in ['yes', 'y', '1', 'true']:
                    return t("common.yes", user=user)
                elif answer.lower() in ['no', 'n', '0', 'false']:
                    return t("common.no", user=user)
            
            # Return the answer as-is for other question types
            return answer
            
        except Exception as e:
            logger.error(f"Error getting display text for {question_key}: {e}")
            return answer
    
    def should_ask_additional_question(self, answers: Dict[str, str]) -> bool:
        """
        Determine if additional questions should be asked based on answers.
        Base implementation - can be overridden by subclasses.
        
        Args:
            answers: Dictionary of current answers
            
        Returns:
            True if additional question should be asked
        """
        # Base implementation: no additional questions
        return False
    
    def get_next_question(self, current_answers: Dict[str, str], user: User) -> Optional[str]:
        """
        Get the next question key based on current answers.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            Next question key or None if questionnaire is complete
        """
        try:
            # Get base question sequence
            questions = self.get_question_sequence(user)
            
            # Find next unanswered question from base sequence
            for question_key in questions:
                if question_key not in current_answers:
                    return question_key
            
            # Check if we need to ask additional questions
            if self.should_ask_additional_question(current_answers):
                additional_questions = self._get_additional_questions(current_answers, user)
                for question_key in additional_questions:
                    if question_key not in current_answers:
                        return question_key
            
            # No more questions
            return None
            
        except Exception as e:
            logger.error(f"Error getting next question: {e}")
            return None
    
    def get_progress(self, current_answers: Dict[str, str], user: User) -> Tuple[int, int]:
        """
        Get progress information for the current questionnaire.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            Tuple of (current_question_number, total_questions)
        """
        try:
            base_questions = self.get_question_sequence(user)
            total_questions = len(base_questions)
            
            # Add additional questions if applicable
            if self.should_ask_additional_question(current_answers):
                additional_questions = self._get_additional_questions(current_answers, user)
                total_questions += len(additional_questions)
            
            # Count answered questions
            answered_count = sum(1 for q in base_questions if q in current_answers)
            
            # Add answered additional questions
            if self.should_ask_additional_question(current_answers):
                additional_questions = self._get_additional_questions(current_answers, user)
                answered_count += sum(1 for q in additional_questions if q in current_answers)
            
            current = answered_count + 1  # +1 for the question being asked
            
            return min(current, total_questions), total_questions
            
        except Exception as e:
            logger.error(f"Error calculating progress: {e}")
            return 1, 1  # Fallback
    
    # Protected methods for customization
    
    def _get_additional_questions(self, current_answers: Dict[str, str], user: User) -> List[str]:
        """
        Get additional questions based on current answers.
        Can be overridden by subclasses.
        
        Args:
            current_answers: Dictionary of answers so far
            user: User object for personalization
            
        Returns:
            List of additional question keys
        """
        return []
    
    def _clear_cache(self) -> None:
        """Clear the question cache."""
        self._question_cache.clear()
        logger.debug("Question cache cleared")
    
    def _cache_question(self, question_key: str, user: User, question_data: QuestionData) -> None:
        """
        Cache question data.
        
        Args:
            question_key: Question identifier
            user: User object
            question_data: Question data to cache
        """
        cache_key = f"{question_key}_{user.language_code or 'en'}"
        self._question_cache[cache_key] = question_data 