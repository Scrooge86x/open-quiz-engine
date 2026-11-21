import random
from datetime import datetime

from src.clients.trivia_client import TriviaQuestion
from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.errors.base import QuizError
from src.services.attempt_service import AttemptService
from src.services.quiz_service import QuizService


class FakeTriviaClient:
    def __init__(self, questions: list[TriviaQuestion] | None = None) -> None:
        self.questions = questions if questions is not None else []

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
            question_type="multiple",
            difficulty="medium",
            category="Geography",
            text="What is the capital of Italy?",
            correct_answer="Rome",
            incorrect_answers=["Milan", "Naples", "Turin"],
        ),
        TriviaQuestion(
            question_type="boolean",
            difficulty="easy",
            category="Science",
            text="Water boils at 100 degrees Celsius at sea level.",
            correct_answer="True",
            incorrect_answers=["False"],
        ),
    ]

    with session_factory() as session:
        quiz_service = QuizService(
            session=session,
            trivia_client=FakeTriviaClient(fake_questions),
            rng=random.Random(1),
            clock=fixed_clock,
        )
        quiz = quiz_service.create_quiz(question_count=2, difficulty="medium")

        attempt_service = AttemptService(
            session=session,
            clock=fixed_clock,
        )

        attempt = attempt_service.start_attempt(quiz_id=quiz.id, nick="Alice")
        print(f"Created Attempt ID: {attempt.id}")
        print(f"Current position: {attempt.current_position}")
        print(f"Is finished: {attempt.is_finished}")

        question = attempt_service.get_current_question(attempt.id)
        print(f"First question text: {question.text}")

        # Test unknown quiz ID
        try:
            attempt_service.start_attempt("unknown-quiz-id", "Bob")
        except QuizError as exc:
            print(f"Unknown Quiz ID raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        # Test unknown attempt ID
        try:
            attempt_service.get_attempt("unknown-attempt-id")
        except QuizError as exc:
            print(
                f"Unknown Attempt ID raised: {type(exc).__name__} (error_code='{exc.error_code}')"
            )

        # Manually set finished_at and test get_current_question
        attempt.finished_at = fixed_clock()
        session.commit()

        try:
            attempt_service.get_current_question(attempt.id)
        except QuizError as exc:
            print(
                f"Finished attempt question request raised: {type(exc).__name__} "
                f"(error_code='{exc.error_code}')"
            )


if __name__ == "__main__":
    main()
