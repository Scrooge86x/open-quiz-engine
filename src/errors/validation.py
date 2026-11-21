from src.errors.base import QuizError


class NotEnoughQuestionsError(QuizError):
    error_code: str = "not_enough_questions"
    default_message: str = "Not enough questions available for the requested parameters."


class InvalidNickError(QuizError):
    error_code: str = "invalid_nick"
    default_message: str = "Nick must be between 1 and 30 printable characters."
