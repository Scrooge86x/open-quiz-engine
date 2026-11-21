from src.errors.base import QuizError


class AttemptFinishedError(QuizError):
    error_code: str = "attempt_finished"
    default_message: str = "Attempt is already finished."


class WrongQuestionError(QuizError):
    error_code: str = "wrong_question"
    default_message: str = "Submitted answer is for the wrong question."
