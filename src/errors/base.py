class QuizError(Exception):
    error_code: str = "quiz_error"
    default_message: str = "An unexpected quiz error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message if message is not None else self.default_message
        super().__init__(self.message)
