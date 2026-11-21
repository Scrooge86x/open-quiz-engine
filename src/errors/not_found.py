from src.errors.base import QuizError


class QuizNotFoundError(QuizError):
    error_code: str = "quiz_not_found"
    default_message: str = "Quiz not found."


class AttemptNotFoundError(QuizError):
    error_code: str = "attempt_not_found"
    default_message: str = "Attempt not found."
