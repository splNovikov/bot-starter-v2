from core.sequence.types import (
    SequenceDefinition, 
    SequenceQuestion, 
    SequenceOption,
    QuestionType
)

def create_user_info_sequence() -> SequenceDefinition:
    questions = [
        SequenceQuestion(
            key="eyes_color",
            question_text_key="sequence.user_info.eyes_color.question",
            question_type=QuestionType.SINGLE_CHOICE,
            options=[
                SequenceOption(value="brown", label_key="sequence.user_info.eyes_color.brown", emoji="👁️"),
                SequenceOption(value="blue", label_key="sequence.user_info.eyes_color.blue", emoji="👁️"),
                SequenceOption(value="green", label_key="sequence.user_info.eyes_color.green", emoji="👁️"),
                SequenceOption(value="hazel", label_key="sequence.user_info.eyes_color.hazel", emoji="👁️"),
                SequenceOption(value="gray", label_key="sequence.user_info.eyes_color.gray", emoji="👁️"),
                SequenceOption(value="other", label_key="sequence.user_info.eyes_color.other", emoji="👁️")
            ],
            is_required=True
        ),
        SequenceQuestion(
            key="marital_status",
            question_text_key="sequence.user_info.marital_status.question",
            question_type=QuestionType.SINGLE_CHOICE,
            options=[
                SequenceOption(value="single", label_key="sequence.user_info.marital_status.single", emoji="💚"),
                SequenceOption(value="married", label_key="sequence.user_info.marital_status.married", emoji="💍"),
                SequenceOption(value="divorced", label_key="sequence.user_info.marital_status.divorced", emoji="💔"),
                SequenceOption(value="widowed", label_key="sequence.user_info.marital_status.widowed", emoji="🕊️"),
                SequenceOption(value="prefer_not_to_say", label_key="sequence.user_info.marital_status.prefer_not_to_say", emoji="🤐")
            ],
            is_required=True
        )
    ]
    
    return SequenceDefinition(
        name="user_info",
        questions=questions,
        title_key="sequence.user_info.title",
        description_key="sequence.user_info.description",
        welcome_message_key="sequence.user_info.welcome",
        completion_message_key="sequence.user_info.completion",
        show_progress=True,
        allow_restart=True,
        generate_summary=True
    )

user_info_sequence = create_user_info_sequence()
