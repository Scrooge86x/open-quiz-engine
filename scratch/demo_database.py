from datetime import datetime, timezone

from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.db.models import Answer, Attempt, Question, Quiz


def main() -> None:
    engine = create_db_engine("sqlite://")
    create_tables(engine)
    session_factory = create_session_factory(engine)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    with session_factory() as session:
        quiz = Quiz(difficulty="medium", created_at=now)
        question_first = Question(
            position=0,
            text="What is the capital of France?",
            category="Geography",
            difficulty="medium",
            options=["Berlin", "Madrid", "Paris", "Rome"],
            correct_index=2,
        )
        question_second = Question(
            position=1,
            text="Is the Earth flat?",
            category="Science",
            difficulty="easy",
            options=["True", "False"],
            correct_index=1,
        )
        quiz.questions.extend([question_first, question_second])
        session.add(quiz)
        session.flush()

        attempt = Attempt(
            quiz_id=quiz.id,
            nick="Alice",
            started_at=now,
        )
        session.add(attempt)
        session.flush()

        answer = Answer(
            attempt_id=attempt.id,
            question_id=question_first.id,
            selected_index=2,
            is_correct=True,
        )
        attempt.answers.append(answer)
        session.commit()

        quiz_id = quiz.id
        attempt_id = attempt.id

    with session_factory() as session:
        loaded_quiz = session.get(Quiz, quiz_id)
        if loaded_quiz is None:
            raise RuntimeError("Quiz was not found in the database.")

        print(f"Quiz ID: {loaded_quiz.id}")
        print(f"Question count: {loaded_quiz.question_count}")

        for question in loaded_quiz.questions:
            print(f"Question {question.position} options: {question.options}")

        loaded_attempt = session.get(Attempt, attempt_id)
        if loaded_attempt is None:
            raise RuntimeError("Attempt was not found in the database.")

        print(f"Attempt is_finished before setting finished_at: {loaded_attempt.is_finished}")

        loaded_attempt.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.commit()

        print(f"Attempt is_finished after setting finished_at: {loaded_attempt.is_finished}")


if __name__ == "__main__":
    main()
