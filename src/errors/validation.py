from src.errors.base import QuizError


class NotEnoughQuestionsError(QuizError):
    error_code: str = "not_enough_questions"
    default_message: str = "Not enough questions available for the requested parameters."
