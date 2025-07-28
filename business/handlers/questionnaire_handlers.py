"""
Questionnaire command handlers for the Telegram bot.

Implements /questionnaire and /gender commands with FSM-based conversation flow,
conditional question logic, and API integration for data persistence.
"""

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger
from business.services.localization import t
from business.services.questionnaire_service import get_questionnaire_service
from business.states.questionnaire_states import QuestionnaireStates, GenderStates

# Create router for questionnaire handlers
questionnaire_router = Router(name="questionnaire_handlers")

logger = get_logger()

# Get service instances
questionnaire_service = get_questionnaire_service()


@questionnaire_router.message(Command("questionnaire"))
@questionnaire_router.message(Command("quiz"))
@questionnaire_router.message(Command("survey"))
@command(
    "questionnaire",
    description="Start an interactive questionnaire with multiple questions",
    category=HandlerCategory.USER,
    usage="/questionnaire",
    examples=["/questionnaire"],
    aliases=["quiz", "survey"]
)
async def cmd_questionnaire(message: Message, state: FSMContext) -> None:
    """Handle /questionnaire command to start questionnaire flow."""
    try:
        user_id = message.from_user.id
        
        # Check if user already has an active session
        existing_session = questionnaire_service.get_session(user_id)
        if existing_session:
            # Ask if they want to restart
            restart_msg = t("questionnaire.restart_prompt", user=message.from_user)
            await message.answer(restart_msg)
            return
        
        # Start new questionnaire session
        session_id = questionnaire_service.start_questionnaire(user_id)
        
        # Get first question
        first_question_key = questionnaire_service.get_current_question_key(user_id, message.from_user)
        if not first_question_key:
            error_msg = t("questionnaire.errors.no_questions", user=message.from_user)
            await message.answer(error_msg)
            return
        
        # Send welcome message and first question
        welcome_msg = t("questionnaire.welcome", user=message.from_user)
        progress_msg = questionnaire_service.get_progress_text(user_id, message.from_user)
        question_text = questionnaire_service.get_question_text(first_question_key, message.from_user)
        
        full_message = f"{welcome_msg}\n\n{progress_msg}\n\n{question_text}"
        await message.answer(full_message)
        
        # Set FSM state
        await state.set_state(QuestionnaireStates.waiting_for_question_1)
        
        logger.info(f"Started questionnaire for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error starting questionnaire for user {message.from_user.id}: {e}")
        error_msg = t("questionnaire.errors.start_failed", user=message.from_user)
        await message.answer(error_msg)


@questionnaire_router.message(Command("gender"))
@command(
    "gender",
    description="Provide your gender information",
    category=HandlerCategory.USER,
    usage="/gender",
    examples=["/gender"]
)
async def cmd_gender(message: Message, state: FSMContext) -> None:
    """Handle /gender command for standalone gender question."""
    try:
        # Send gender question
        question_text = t("questionnaire.questions.gender", user=message.from_user)
        instruction_text = t("questionnaire.gender_instruction", user=message.from_user)
        
        full_message = f"{question_text}\n\n{instruction_text}"
        await message.answer(full_message)
        
        # Set FSM state for gender input
        await state.set_state(GenderStates.waiting_for_gender)
        
        logger.info(f"Started gender question for user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error starting gender question for user {message.from_user.id}: {e}")
        error_msg = t("questionnaire.errors.start_failed", user=message.from_user)
        await message.answer(error_msg)


# FSM State Handlers

@questionnaire_router.message(QuestionnaireStates.waiting_for_question_1)
async def handle_question_1_answer(message: Message, state: FSMContext) -> None:
    """Handle answer to question 1."""
    await _handle_questionnaire_answer(message, state, QuestionnaireStates.waiting_for_question_2)


@questionnaire_router.message(QuestionnaireStates.waiting_for_question_2)
async def handle_question_2_answer(message: Message, state: FSMContext) -> None:
    """Handle answer to question 2."""
    await _handle_questionnaire_answer(message, state, QuestionnaireStates.waiting_for_gender)


@questionnaire_router.message(QuestionnaireStates.waiting_for_gender)
async def handle_gender_answer(message: Message, state: FSMContext) -> None:
    """Handle gender answer in questionnaire flow."""
    await _handle_questionnaire_answer(message, state, QuestionnaireStates.waiting_for_question_4)


@questionnaire_router.message(QuestionnaireStates.waiting_for_question_4)
async def handle_question_4_answer(message: Message, state: FSMContext) -> None:
    """Handle answer to additional question 4 (for female users)."""
    await _handle_questionnaire_answer(message, state, QuestionnaireStates.completing)


@questionnaire_router.message(GenderStates.waiting_for_gender)
async def handle_standalone_gender_answer(message: Message, state: FSMContext) -> None:
    """Handle standalone gender answer from /gender command."""
    try:
        user_id = message.from_user.id
        gender_answer = message.text.strip()
        
        if not gender_answer:
            error_msg = t("questionnaire.errors.empty_answer", user=message.from_user)
            await message.answer(error_msg)
            return
        
        # Submit gender answer
        success, response_msg, summary = await questionnaire_service.submit_standalone_gender(
            user_id, gender_answer, message.from_user
        )
        
        if success:
            # Show summary and success message
            full_response = f"{summary}\n\n{response_msg}"
            await message.answer(full_response)
            await state.clear()
            logger.info(f"Successfully processed standalone gender for user {user_id}")
        else:
            await message.answer(response_msg)
            # Keep user in state to retry
        
    except Exception as e:
        logger.error(f"Error handling standalone gender answer for user {message.from_user.id}: {e}")
        error_msg = t("questionnaire.errors.processing_failed", user=message.from_user)
        await message.answer(error_msg)


async def _handle_questionnaire_answer(message: Message, state: FSMContext, next_state) -> None:
    """
    Generic handler for questionnaire answers.
    
    Args:
        message: User message with answer
        state: FSM context
        next_state: Next FSM state to transition to
    """
    try:
        user_id = message.from_user.id
        answer = message.text.strip()
        
        if not answer:
            error_msg = t("questionnaire.errors.empty_answer", user=message.from_user)
            await message.answer(error_msg)
            return
        
        # Submit answer and get next question
        success, next_question_key, error_msg = await questionnaire_service.submit_answer(
            user_id, answer, message.from_user
        )
        
        if not success:
            await message.answer(error_msg)
            return
        
        # Check if questionnaire is complete
        if next_question_key is None:
            # Questionnaire completed - generate summary
            summary = questionnaire_service.generate_questionnaire_summary(user_id, message.from_user)
            completion_msg = t("questionnaire.completed", user=message.from_user)
            thank_you_msg = t("questionnaire.thank_you", user=message.from_user)
            
            full_message = f"{summary}\n\n{completion_msg}\n\n{thank_you_msg}"
            await message.answer(full_message)
            
            await state.clear()
            logger.info(f"Questionnaire completed for user {user_id}")
            return
        
        # Send next question
        progress_msg = questionnaire_service.get_progress_text(user_id, message.from_user)
        question_text = questionnaire_service.get_question_text(next_question_key, message.from_user)
        
        full_message = f"{progress_msg}\n\n{question_text}"
        await message.answer(full_message)
        
        # Transition to next state
        await state.set_state(next_state)
        
    except Exception as e:
        logger.error(f"Error handling questionnaire answer for user {message.from_user.id}: {e}")
        error_msg = t("questionnaire.errors.processing_failed", user=message.from_user)
        await message.answer(error_msg)


# Cancel command for questionnaire
@questionnaire_router.message(Command("cancel"))
@command(
    "cancel",
    description="Cancel current questionnaire session",
    category=HandlerCategory.USER,
    usage="/cancel",
    examples=["/cancel"],
    hidden=True  # Hidden since it's context-dependent
)
async def cmd_cancel_questionnaire(message: Message, state: FSMContext) -> None:
    """Handle /cancel command to cancel active questionnaire."""
    try:
        current_state = await state.get_state()
        
        if current_state and (
            current_state.startswith("QuestionnaireStates:") or 
            current_state.startswith("GenderStates:")
        ):
            user_id = message.from_user.id
            
            # Cancel questionnaire session
            questionnaire_service.cancel_session(user_id)
            
            # Clear FSM state
            await state.clear()
            
            # Send cancellation message
            cancel_msg = t("questionnaire.cancelled", user=message.from_user)
            await message.answer(cancel_msg)
            
            logger.info(f"Cancelled questionnaire session for user {user_id}")
        else:
            # No active questionnaire
            no_session_msg = t("questionnaire.errors.no_active_session", user=message.from_user)
            await message.answer(no_session_msg)
            
    except Exception as e:
        logger.error(f"Error cancelling questionnaire for user {message.from_user.id}: {e}")
        error_msg = t("questionnaire.errors.cancel_failed", user=message.from_user)
        await message.answer(error_msg) 