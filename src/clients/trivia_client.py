from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from src.config import (
    TRIVIA_API_URL,
    TRIVIA_CODE_NOT_ENOUGH_QUESTIONS,
    TRIVIA_CODE_RATE_LIMITED,
    TRIVIA_CODE_SUCCESS,
    TRIVIA_TIMEOUT_SECONDS,
)
from src.errors.upstream import UpstreamRateLimitedError, UpstreamUnavailableError
from src.errors.validation import NotEnoughQuestionsError


@dataclass(frozen=True)
class TriviaQuestion:
    question_type: str
    difficulty: str
    category: str
    text: str
    correct_answer: str
    incorrect_answers: list[str]


class TriviaClient(Protocol):
    def fetch_questions(
        self,
        question_count: int,
        difficulty: str | None = None,
    ) -> list[TriviaQuestion]: ...


def _parse_trivia_questions(payload: dict[str, Any]) -> list[TriviaQuestion]:
    results = payload.get("results")
    if not isinstance(results, list):
        raise UpstreamUnavailableError("Trivia API response missing results list.")

    questions: list[TriviaQuestion] = []
    for item in results:
        if not isinstance(item, dict):
            raise UpstreamUnavailableError("Invalid question format in Trivia API response.")
        try:
            questions.append(
                TriviaQuestion(
                    question_type=item["type"],
                    difficulty=item["difficulty"],
                    category=item["category"],
                    text=item["question"],
                    correct_answer=item["correct_answer"],
                    incorrect_answers=list(item["incorrect_answers"]),
                )
            )
        except (KeyError, TypeError) as exc:
            raise UpstreamUnavailableError(
                "Trivia API response question missing required keys."
            ) from exc
    return questions


class HttpTriviaClient:
    def __init__(
        self,
        client: httpx.Client | None = None,
        base_url: str = TRIVIA_API_URL,
    ) -> None:
        self._client = client or httpx.Client(timeout=TRIVIA_TIMEOUT_SECONDS)
        self._base_url = base_url

    def fetch_questions(
        self,
        question_count: int,
        difficulty: str | None = None,
    ) -> list[TriviaQuestion]:
        params: dict[str, str | int] = {"amount": question_count}
        if difficulty is not None:
            params["difficulty"] = difficulty

        try:
            response = self._client.get(self._base_url, params=params)
        except httpx.HTTPError as exc:
            raise UpstreamUnavailableError("Trivia API request failed.") from exc

        if response.status_code != 200:
            raise UpstreamUnavailableError(
                f"Trivia API returned unexpected status {response.status_code}."
            )

        try:
            payload = response.json()
        except Exception as exc:
            raise UpstreamUnavailableError("Failed to parse Trivia API JSON response.") from exc

        if not isinstance(payload, dict) or "response_code" not in payload:
            raise UpstreamUnavailableError("Trivia API response missing response_code.")

        response_code = payload["response_code"]
        if response_code == TRIVIA_CODE_SUCCESS:
            return _parse_trivia_questions(payload)
        if response_code == TRIVIA_CODE_NOT_ENOUGH_QUESTIONS:
            raise NotEnoughQuestionsError()
        if response_code == TRIVIA_CODE_RATE_LIMITED:
            raise UpstreamRateLimitedError()
        raise UpstreamUnavailableError(f"Trivia API returned error code {response_code}.")
