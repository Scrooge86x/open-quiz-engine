from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.config import RATE_LIMIT_RETRY_SECONDS
from src.errors.base import QuizError

STATUS_BY_ERROR_CODE: dict[str, int] = {
    "quiz_not_found": status.HTTP_404_NOT_FOUND,
    "attempt_not_found": status.HTTP_404_NOT_FOUND,
    "invalid_nick": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "invalid_option": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "not_enough_questions": status.HTTP_422_UNPROCESSABLE_CONTENT,
    "attempt_finished": status.HTTP_409_CONFLICT,
    "wrong_question": status.HTTP_409_CONFLICT,
    "upstream_rate_limited": status.HTTP_503_SERVICE_UNAVAILABLE,
    "upstream_unavailable": status.HTTP_502_BAD_GATEWAY,
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(QuizError)
    def quiz_error_handler(request: Request, exc: QuizError) -> JSONResponse:
        status_code = STATUS_BY_ERROR_CODE.get(
            exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        headers: dict[str, str] = {}
        if exc.error_code == "upstream_rate_limited":
            headers["Retry-After"] = str(RATE_LIMIT_RETRY_SECONDS)

        return JSONResponse(
            status_code=status_code,
            content={"error": exc.error_code, "message": exc.message},
            headers=headers if headers else None,
        )
