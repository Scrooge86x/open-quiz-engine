import random
from datetime import datetime

from src.clients.trivia_client import TriviaQuestion
from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.errors.base import QuizError
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
    engine = create_db_engine("sqlite://")
    create_tables(engine)
    session_factory = create_session_factory(engine)

    fake_questions = [
        TriviaQuestion(
            question_type="boolean",
            difficulty="easy",
            category="General",
            text="The Earth is round.",
            correct_answer="True",
            incorrect_answers=["False"],
        ),
        TriviaQuestion(
            question_type="multiple",
            difficulty="easy",
            category="General",
            text="What is 1 + 1?",
            correct_answer="2",
            incorrect_answers=["1", "3", "4"],
        ),
    ]

    with session_factory() as session:
        quiz_service = QuizService(
            session=session,
            trivia_client=FakeTriviaClient(fake_questions),
            rng=random.Random(1),
            clock=fixed_clock,
        )
        quiz = quiz_service.create_quiz(question_count=2)

        attempt_service = AttemptService(
            session=session,
            clock=fixed_clock,
        )
        attempt = attempt_service.start_attempt(quiz_id=quiz.id, nick="Alice")

        # Question 1: Boolean (2 options)
        q1 = attempt_service.get_current_question(attempt.id)
        print(f"--- Question 1 (options count: {len(q1.options)}) ---")

        # Test index -1
        try:
            attempt_service.submit_answer(attempt.id, q1.id, -1)
        except QuizError as exc:
            print(f"Index -1 raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        # Test index 2
        try:
            attempt_service.submit_answer(attempt.id, q1.id, 2)
        except QuizError as exc:
            print(f"Index 2 raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        print(
            f"State after invalid attempts -> current_position: {attempt.current_position}, "
            f"score: {attempt.score}"
        )

        # Valid index 1 on boolean question
        outcome1 = attempt_service.submit_answer(attempt.id, q1.id, 1)
        print(f"Index 1 accepted -> outcome: {outcome1}")

        # Question 2: Multiple (4 options)
        q2 = attempt_service.get_current_question(attempt.id)
        print(f"\n--- Question 2 (options count: {len(q2.options)}) ---")

        # Test index 4
        try:
            attempt_service.submit_answer(attempt.id, q2.id, 4)
        except QuizError as exc:
            print(f"Index 4 raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        print(
            f"State after invalid attempt -> current_position: {attempt.current_position}, "
            f"score: {attempt.score}"
        )

        # Valid index 3 on multiple question
        outcome2 = attempt_service.submit_answer(attempt.id, q2.id, 3)
        print(f"Index 3 accepted -> outcome: {outcome2}")


if __name__ == "__main__":
    main()
