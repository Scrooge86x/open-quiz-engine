from src.errors.base import QuizError


class AttemptFinishedError(QuizError):
    error_code: str = "attempt_finished"
    default_message: str = "Attempt is already finished."
