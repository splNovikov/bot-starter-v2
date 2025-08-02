"""
FSM states for sequence framework.

Defines state machines for sequence interactions with support for
dynamic state generation based on sequence definitions.
"""

from typing import Dict, Type

from aiogram.fsm.state import State, StatesGroup


class SequenceStates(StatesGroup):
    """FSM states for all sequence interactions."""

    # Initial state
    sequence_started = State()

    # Generic waiting states
    waiting_for_answer = State()
    waiting_for_confirmation = State()
    waiting_for_restart_decision = State()

    # Completion states
    sequence_completed = State()
    sequence_abandoned = State()


class SequenceStateManager:
    """
    Manager for dynamic sequence state generation and mapping.

    Provides utilities to generate FSM states dynamically based on
    sequence definitions and manage state transitions.
    """

    @classmethod
    def get_initial_state(cls) -> State:
        """
        Get the initial state for any sequence.

        Returns:
            Initial State object
        """
        return SequenceStates.sequence_started

    @classmethod
    def get_waiting_state(cls) -> State:
        """
        Get the waiting state for any sequence.

        Returns:
            Waiting State object
        """
        return SequenceStates.waiting_for_answer

    @classmethod
    def get_completion_state(cls) -> State:
        """
        Get the completion state for any sequence.

        Returns:
            Completion State object
        """
        return SequenceStates.sequence_completed

    @classmethod
    def generate_dynamic_states(
        cls, sequence_name: str, question_keys: list
    ) -> Dict[str, State]:
        """
        Generate dynamic states for a sequence with specific question keys.

        Args:
            sequence_name: Name of the sequence
            question_keys: List of question identifiers

        Returns:
            Dictionary mapping question keys to State objects
        """
        # Create a dynamic StatesGroup
        class_name = f"{sequence_name.title().replace('_', '')}States"
        attrs = {}

        # Add standard states
        attrs["sequence_started"] = State()
        attrs["sequence_completed"] = State()

        # Add states for each question
        for question_key in question_keys:
            state_name = f"waiting_for_{question_key}"
            attrs[state_name] = State()

        # Create the dynamic class
        dynamic_state_group = type(class_name, (StatesGroup,), attrs)

        # Return mapping of question keys to states
        return {
            key: getattr(dynamic_state_group, f"waiting_for_{key}")
            for key in question_keys
        }


def get_sequence_states() -> Type[StatesGroup]:
    """
    Get state group for sequences.

    Returns:
        StatesGroup class
    """
    return SequenceStates


__all__ = ["SequenceStates", "SequenceStateManager", "get_sequence_states"]
