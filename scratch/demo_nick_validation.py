import random
from datetime import datetime

from src.clients.trivia_client import TriviaQuestion
from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.errors.base import QuizError
from src.logic.nick_validator import validate_nick
from src.services.attempt_service import AttemptService
from src.services.quiz_service import QuizService


class FakeTriviaClient:
    def __init__(self, questions: list[TriviaQuestion]) -> None:
        self.questions = questions

    def fetch_questions(
        self,
        question_count: int,
        difficulty: str | None = None,
    ) -> list[TriviaQuestion]:
        return self.questions


def fixed_clock() -> datetime:
    return datetime(2026, 11, 21, 12, 0, 0)


def main() -> None:
    cases = [
        "  Ala ",
        "",
        "   ",
        "a" * 31,
        "a" * 30,
        "a\x07b",
    ]

    print("--- 1. validate_nick results ---")
    for raw_nick in cases:
        try:
            result = validate_nick(raw_nick)
            print(f"{repr(raw_nick)} -> Valid: {repr(result)}")
        except QuizError as exc:
            print(
                f"{repr(raw_nick)} -> Raised: {type(exc).__name__} (error_code='{exc.error_code}')"
            )

    print("\n--- 2. AttemptService.start_attempt with nick validation ---")
    engine = create_db_engine("sqlite://")
    create_tables(engine)
    session_factory = create_session_factory(engine)

    fake_questions = [
        TriviaQuestion(
            question_type="boolean",
            difficulty="easy",
            category="General",
            text="The sky is blue.",
            correct_answer="True",
            incorrect_answers=["False"],
        )
    ]

    with session_factory() as session:
        quiz_service = QuizService(
            session=session,
            trivia_client=FakeTriviaClient(fake_questions),
            rng=random.Random(1),
            clock=fixed_clock,
        )
        quiz = quiz_service.create_quiz(question_count=1)

        attempt_service = AttemptService(
            session=session,
            clock=fixed_clock,
        )

        # Valid nick: "  Ala "
        attempt = attempt_service.start_attempt(quiz_id=quiz.id, nick="  Ala ")
        print(f"Stored nick for '  Ala ': {repr(attempt.nick)}")

        # Invalid nick: ""
        try:
            attempt_service.start_attempt(quiz_id=quiz.id, nick="")
        except QuizError as exc:
            print(f"Empty nick raised: {type(exc).__name__} (error_code='{exc.error_code}')")


if __name__ == "__main__":
    main()
