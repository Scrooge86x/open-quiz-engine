import random
from datetime import datetime

from src.clients.trivia_client import TriviaQuestion
from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.errors.base import QuizError
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
            category="Science &amp; Nature",
            text="What is the &quot;Powerhouse&quot; of the cell?",
            correct_answer="Mitochondria",
            incorrect_answers=["Nucleus", "Ribosome", "Chloroplast"],
        ),
        TriviaQuestion(
            question_type="boolean",
            difficulty="easy",
            category="General Knowledge",
            text="The sky is &quot;blue&quot;.",
            correct_answer="True",
            incorrect_answers=["False"],
        ),
    ]

    with session_factory() as session:
        fake_client = FakeTriviaClient(fake_questions)
        service = QuizService(
            session=session,
            trivia_client=fake_client,
            rng=random.Random(1),
            clock=fixed_clock,
        )

        quiz = service.create_quiz(question_count=2, difficulty="medium")
        print(f"Created Quiz ID: {quiz.id}")
        print(f"Question count: {quiz.question_count}")

        for question in quiz.questions:
            print(
                f"Question {question.position}: text='{question.text}', "
                f"category='{question.category}', options={question.options}, "
                f"correct_index={question.correct_index}"
            )

        loaded_quiz = service.get_quiz(quiz.id)
        print(f"get_quiz returned same quiz: {loaded_quiz.id == quiz.id}")

        try:
            service.get_quiz("non-existent-id")
        except QuizError as exc:
            print(f"Unknown ID raised: {type(exc).__name__} (error_code='{exc.error_code}')")

        empty_service = QuizService(
            session=session,
            trivia_client=FakeTriviaClient([]),
            rng=random.Random(1),
            clock=fixed_clock,
        )
        try:
            empty_service.create_quiz(question_count=2, difficulty="medium")
        except QuizError as exc:
            print(f"Empty client list raised: {type(exc).__name__} (error_code='{exc.error_code}')")


if __name__ == "__main__":
    main()
