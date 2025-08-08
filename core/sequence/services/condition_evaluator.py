"""
Condition evaluator service for sequence framework.

Evaluates conditional logic for showing/hiding questions based on previous answers.
"""

from typing import Any, Dict

from core.utils.logger import get_logger

from ..types import SequenceSession

logger = get_logger()


class ConditionEvaluator:
    """
    Evaluates conditions for sequence questions.

    Supports various condition types and operators for determining
    whether questions should be shown or skipped.
    """

    def __init__(self):
        """Initialize condition evaluator."""

    def evaluate_condition(
        self, condition: Dict[str, Any], session: SequenceSession
    ) -> bool:
        """
        Evaluate a condition against session data.

        Args:
            condition: Condition dictionary with evaluation logic
            session: Current sequence session with answers

        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return True  # No condition means always show

        # Handle complex operators (and, or, not)
        if "operator" in condition:
            return self._evaluate_operator_condition(condition, session)

        # Handle simple conditions
        return self._evaluate_simple_condition(condition, session)

    def _evaluate_operator_condition(
        self, condition: Dict[str, Any], session: SequenceSession
    ) -> bool:
        """Evaluate conditions with operators (and, or, not)."""
        operator = condition.get("operator", "and")
        conditions = condition.get("conditions", [])

        if not conditions:
            return True

        if operator == "and":
            return all(self.evaluate_condition(cond, session) for cond in conditions)
        elif operator == "or":
            return any(self.evaluate_condition(cond, session) for cond in conditions)
        elif operator == "not":
            if len(conditions) != 1:
                logger.warning("NOT operator should have exactly one condition")
                return True
            return not self.evaluate_condition(conditions[0], session)
        else:
            logger.warning(f"Unknown operator: {operator}")
            return True

    def _evaluate_simple_condition(
        self, condition: Dict[str, Any], session: SequenceSession
    ) -> bool:
        """Evaluate a simple condition."""
        condition_type = condition.get("condition", "equals")
        question_key = condition.get("question")
        expected_value = condition.get("value")

        if not question_key:
            logger.warning("Condition missing question key")
            return True

        # Get the answer for the referenced question
        answer = session.get_answer(question_key)
        if not answer:
            logger.debug(f"No answer found for question: {question_key}")
            return False

        actual_value = answer.answer_value

        # Evaluate based on condition type
        if condition_type == "equals":
            return str(actual_value).lower() == str(expected_value).lower()
        elif condition_type == "not_equals":
            return str(actual_value).lower() != str(expected_value).lower()
        elif condition_type == "contains":
            return str(expected_value).lower() in str(actual_value).lower()
        elif condition_type == "not_contains":
            return str(expected_value).lower() not in str(actual_value).lower()
        elif condition_type == "in_list":
            if isinstance(expected_value, list):
                return str(actual_value).lower() in [
                    str(v).lower() for v in expected_value
                ]
            return False
        elif condition_type == "not_in_list":
            if isinstance(expected_value, list):
                return str(actual_value).lower() not in [
                    str(v).lower() for v in expected_value
                ]
            return True
        elif condition_type == "is_empty":
            return not actual_value or str(actual_value).strip() == ""
        elif condition_type == "is_not_empty":
            return actual_value and str(actual_value).strip() != ""
        else:
            logger.warning(f"Unknown condition type: {condition_type}")
            return True

    def should_show_question(self, question: Any, session: SequenceSession) -> bool:
        """
        Determine if a question should be shown based on conditions.

        Args:
            question: SequenceQuestion object
            session: Current sequence session

        Returns:
            True if question should be shown, False if it should be skipped
        """
        # Check show_if condition
        if hasattr(question, "show_if") and question.show_if:
            if not self.evaluate_condition(question.show_if, session):
                logger.debug(f"Question {question.key} hidden by show_if condition")
                return False

        # Check skip_if condition
        if hasattr(question, "skip_if") and question.skip_if:
            if self.evaluate_condition(question.skip_if, session):
                logger.debug(f"Question {question.key} skipped by skip_if condition")
                return False

        return True


# Global instance for easy access
condition_evaluator = ConditionEvaluator()


__all__ = ["ConditionEvaluator", "condition_evaluator"]
