import uuid
from datetime import datetime, timedelta

from src.db.engine import create_db_engine, create_session_factory, create_tables
from src.db.models import Attempt, Question, Quiz
from src.errors.base import QuizError
from src.services.leaderboard_service import LeaderboardService


def main() -> None:
    engine = create_db_engine("sqlite://")
    create_tables(engine)
    session_factory = create_session_factory(engine)

    base_time = datetime(2026, 11, 21, 10, 0, 0)
    quiz_id = str(uuid.uuid4())

    with session_factory() as session:
        quiz = Quiz(id=quiz_id, difficulty="medium", created_at=base_time)
        q1 = Question(
            quiz_id=quiz_id,
            position=0,
            text="Question 1",
            category="General",
            difficulty="medium",
            options=["A", "B"],
            correct_index=0,
        )
        q2 = Question(
            quiz_id=quiz_id,
            position=1,
            text="Question 2",
            category="General",
            difficulty="medium",
            options=["C", "D"],
            correct_index=1,
        )
        quiz.questions.extend([q1, q2])
        session.add(quiz)

        # Finished Attempt 1: Alice, score 2, duration 10.0s
        attempt1 = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            nick="Alice",
            current_position=2,
            score=2,
            started_at=base_time,
            finished_at=base_time + timedelta(seconds=10),
        )
        # Finished Attempt 2: Bob, score 1, duration 8.0s
        attempt2 = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            nick="Bob",
            current_position=2,
            score=1,
            started_at=base_time,
            finished_at=base_time + timedelta(seconds=8),
        )
        # Finished Attempt 3: Charlie, score 2, duration 12.0s
        attempt3 = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            nick="Charlie",
            current_position=2,
            score=2,
            started_at=base_time,
            finished_at=base_time + timedelta(seconds=12),
        )
        # Unfinished Attempt 4: Dave, score 1, finished_at is None
        attempt4 = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            nick="Dave",
            current_position=1,
            score=1,
            started_at=base_time,
            finished_at=None,
        )
        session.add_all([attempt1, attempt2, attempt3, attempt4])
        session.commit()

    with session_factory() as session:
        service = LeaderboardService(session)

        # 1. Print full leaderboard
        print("--- Full Leaderboard ---")
        leaderboard = service.get_leaderboard(quiz_id)
        for entry in leaderboard:
            print(
                f"Rank {entry.rank}: {entry.nick} | Score: {entry.score} | "
                f"Duration: {entry.duration_seconds}s"
            )

        # 2. Show unfinished attempt is absent
        nicks_in_leaderboard = [entry.nick for entry in leaderboard]
        print(f"\nUnfinished attempt ('Dave') is absent: {'Dave' not in nicks_in_leaderboard}")

        # 3. Show limit works
        print("\n--- Leaderboard with limit=2 ---")
        limited_leaderboard = service.get_leaderboard(quiz_id, limit=2)
        print(f"Number of entries: {len(limited_leaderboard)}")
        for entry in limited_leaderboard:
            print(
                f"Rank {entry.rank}: {entry.nick} | Score: {entry.score} | "
                f"Duration: {entry.duration_seconds}s"
            )

        # 4. Unknown quiz exception
        print("\n--- Unknown Quiz ID Test ---")
        try:
            service.get_leaderboard("non-existent-quiz-id")
        except QuizError as exc:
            print(f"Unknown quiz raised: {type(exc).__name__} (error_code='{exc.error_code}')")


if __name__ == "__main__":
    main()
