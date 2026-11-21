from typing import Callable

import httpx

from src.clients.trivia_client import HttpTriviaClient
from src.errors.base import QuizError


def _run_real_api_demo() -> None:
    print("--- (a) Real API Demo: Fetching 3 easy questions ---")
    client = HttpTriviaClient()
    questions = client.fetch_questions(question_count=3, difficulty="easy")
    for index, question in enumerate(questions, start=1):
        print(f"Question {index}: {question}")


def _run_simulated_error_demo() -> None:
    print("\n--- (b) Simulated Errors with MockTransport ---")

    cases: list[tuple[str, Callable[[httpx.Request], httpx.Response]]] = [
        (
            "response_code 1",
            lambda _: httpx.Response(200, json={"response_code": 1, "results": []}),
        ),
        (
            "response_code 5",
            lambda _: httpx.Response(200, json={"response_code": 5, "results": []}),
        ),
        (
            "response_code 2",
            lambda _: httpx.Response(200, json={"response_code": 2, "results": []}),
        ),
        (
            "500 status",
            lambda _: httpx.Response(500, text="Internal Server Error"),
        ),
        (
            "invalid JSON",
            lambda _: httpx.Response(200, content=b"invalid json"),
        ),
        (
            "network error",
            _raise_network_error,
        ),
    ]

    for label, handler in cases:
        mock_transport = httpx.MockTransport(handler)
        mock_client = httpx.Client(transport=mock_transport)
        trivia_client = HttpTriviaClient(client=mock_client)
        try:
            trivia_client.fetch_questions(question_count=3, difficulty="easy")
            print(f"{label}: No exception raised (unexpected)")
        except QuizError as exc:
            print(f"{label} -> Raised: {type(exc).__name__} (error_code='{exc.error_code}')")


def _raise_network_error(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError(f"Connection failed for {request.url}")


def main() -> None:
    _run_real_api_demo()
    _run_simulated_error_demo()


if __name__ == "__main__":
    main()
