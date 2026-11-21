from collections.abc import Callable

from fastapi.testclient import TestClient

from src.errors.conflict import AttemptFinishedError, WrongQuestionError
from src.errors.not_found import AttemptNotFoundError, QuizNotFoundError
from src.errors.upstream import UpstreamRateLimitedError, UpstreamUnavailableError
from src.errors.validation import (
    InvalidNickError,
    InvalidOptionError,
    NotEnoughQuestionsError,
)
from src.main import create_app


def _make_endpoint(exc_cls: type[Exception]) -> Callable[[], None]:
    def endpoint() -> None:
        raise exc_cls()

    return endpoint


def main() -> None:
    app = create_app("sqlite://")

    errors: list[tuple[str, type[Exception]]] = [
        ("quiz_not_found", QuizNotFoundError),
        ("attempt_not_found", AttemptNotFoundError),
        ("invalid_nick", InvalidNickError),
        ("invalid_option", InvalidOptionError),
        ("not_enough_questions", NotEnoughQuestionsError),
        ("attempt_finished", AttemptFinishedError),
        ("wrong_question", WrongQuestionError),
        ("upstream_rate_limited", UpstreamRateLimitedError),
        ("upstream_unavailable", UpstreamUnavailableError),
    ]

    for path, err_cls in errors:
        app.add_api_route(f"/test/{path}", _make_endpoint(err_cls), methods=["GET"])

    client = TestClient(app)

    print("--- Domain Error Handler Tests ---")
    for path, _ in errors:
        response = client.get(f"/test/{path}")
        retry_after = response.headers.get("retry-after")
        print(
            f"Endpoint: /test/{path:<22} -> Status: {response.status_code} | "
            f"Body: {response.json()} | Retry-After: {retry_after}"
        )


if __name__ == "__main__":
    main()
