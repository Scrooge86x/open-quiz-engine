from src.errors.base import QuizError


class QuizNotFoundError(QuizError):
    error_code: str = "quiz_not_found"
    default_message: str = "Quiz not found."
