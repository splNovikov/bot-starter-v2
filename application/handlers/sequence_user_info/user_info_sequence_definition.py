from core.sequence.types import (
    QuestionType,
    SequenceDefinition,
    SequenceOption,
    SequenceQuestion,
)


def create_user_info_sequence() -> SequenceDefinition:
    questions = [
        SequenceQuestion(
            key="eyes_color",
            question_text_key="handlers.user_info.questions.eyes_color.question",
            question_type=QuestionType.SINGLE_CHOICE,
            options=[
                SequenceOption(
                    value="brown",
                    label_key="handlers.user_info.questions.eyes_color.options.brown",
                    emoji="👁️",
                ),
                SequenceOption(
                    value="blue",
                    label_key="handlers.user_info.questions.eyes_color.options.blue",
                    emoji="👁️",
                ),
                SequenceOption(
                    value="green",
                    label_key="handlers.user_info.questions.eyes_color.options.green",
                    emoji="👁️",
                ),
                SequenceOption(
                    value="hazel",
                    label_key="handlers.user_info.questions.eyes_color.options.hazel",
                    emoji="👁️",
                ),
                SequenceOption(
                    value="gray",
                    label_key="handlers.user_info.questions.eyes_color.options.gray",
                    emoji="👁️",
                ),
                SequenceOption(
                    value="other",
                    label_key="handlers.user_info.questions.eyes_color.options.other",
                    emoji="👁️",
                ),
            ],
            is_required=True,
        ),
        SequenceQuestion(
            key="marital_status",
            question_text_key="handlers.user_info.questions.marital_status.question",
            question_type=QuestionType.SINGLE_CHOICE,
            options=[
                SequenceOption(
                    value="single",
                    label_key="handlers.user_info.questions.marital_status.options.single",
                    emoji="💚",
                ),
                SequenceOption(
                    value="married",
                    label_key="handlers.user_info.questions.marital_status.options.married",
                    emoji="💍",
                ),
                SequenceOption(
                    value="divorced",
                    label_key="handlers.user_info.questions.marital_status.options.divorced",
                    emoji="💔",
                ),
                SequenceOption(
                    value="widowed",
                    label_key="handlers.user_info.questions.marital_status.options.widowed",
                    emoji="🕊️",
                ),
                SequenceOption(
                    value="prefer_not_to_say",
                    label_key="handlers.user_info.questions.marital_status.options.prefer_not_to_say",
                    emoji="🤐",
                ),
            ],
            is_required=True,
        ),
    ]

    return SequenceDefinition(
        name="user_info",
        questions=questions,
        title_key="handlers.user_info.title",
        description_key="handlers.user_info.description",
        welcome_message_key="handlers.user_info.welcome",
        completion_message_key="handlers.user_info.completion",
        show_progress=True,
        allow_restart=True,
        generate_summary=True,
    )


user_info_sequence = create_user_info_sequence()
