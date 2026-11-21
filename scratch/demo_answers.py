import random
from datetime import datetime, timedelta

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


class SteppingClock:
    def __init__(self, start_time: datetime, step_seconds: int = 5) -> None:
        self._current_time = start_time
        self._step_seconds = step_seconds

    def __call__(self) -> datetime:
        time_to_return = self._current_time
        self._current_time += timedelta(seconds=self._step_seconds)
        return time_to_return


def main() -> None:
    engine = create_db_engine("sqlite://")
    create_tables(engine)
    session_factory = create_session_factory(engine)

    fake_questions = [
        TriviaQuestion(
            question_type="multiple",
            difficulty="medium",
            category="Geography",
            text="What is the capital of Spain?",
            correct_answer="Madrid",
            incorrect_answers=["Barcelona", "Seville", "Valencia"],
        ),
        TriviaQuestion(
            question_type="boolean",
            difficulty="easy",
            category="Science",
            text="The Earth is the third planet from the Sun.",
            correct_answer="True",
            incorrect_answers=["False"],
        ),
    ]

    clock = SteppingClock(start_time=datetime(2026, 11, 21, 12, 0, 0), step_seconds=5)

    with session_factory() as session:
        quiz_service = QuizService(
            session=session,
            trivia_client=FakeTriviaClient(fake_questions),
            rng=random.Random(1),
            clock=clock,
        )
        quiz = quiz_service.create_quiz(question_count=2, difficulty="medium")

        attempt_service = AttemptService(
            session=session,
            clock=clock,
        )

        attempt = attempt_service.start_attempt(quiz_id=quiz.id, nick="Alice")
        print(f"Started attempt: {attempt.id}")

        # Answer 1: correct answer
        q1 = attempt_service.get_current_question(attempt.id)
        outcome1 = attempt_service.submit_answer(
            attempt_id=attempt.id,
            question_id=q1.id,
            selected_index=q1.correct_index,
        )
        print(f"Answer 1 outcome: {outcome1}")

        # Answer 2: wrong answer
        q2 = attempt_service.get_current_question(attempt.id)
        wrong_index = (q2.correct_index + 1) % len(q2.options)
        outcome2 = attempt_service.submit_answer(
            attempt_id=attempt.id,
            question_id=q2.id,
            selected_index=wrong_index,
        )
        print(f"Answer 2 outcome: {outcome2}")

        # Get final result
        result = attempt_service.get_result(attempt.id)
        print(f"Attempt result: {result}")

        # Test exception: submit after finishing
        try:
            attempt_service.submit_answer(attempt.id, q2.id, 0)
        except QuizError as exc:
            print(
                f"Submit after finish raised: {type(exc).__name__} (error_code='{exc.error_code}')"
            )

        # Start second attempt to test wrong question_id
        second_attempt = attempt_service.start_attempt(quiz.id, "Bob")
        try:
            attempt_service.submit_answer(second_attempt.id, 999999, 0)
        except QuizError as exc:
            print(f"Wrong question_id raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        # Test exception: unknown attempt ID
        try:
            attempt_service.submit_answer("unknown-attempt-id", q1.id, 0)
        except QuizError as exc:
            print(
                f"Unknown attempt ID raised: {type(exc).__name__} (error_code='{exc.error_code}')"
            )


if __name__ == "__main__":
    main()
