from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import LEADERBOARD_SIZE
from src.db.models.attempt import Attempt
from src.db.models.quiz import Quiz
from src.errors.not_found import QuizNotFoundError
from src.logic.leaderboard_order import LeaderboardRow, sort_leaderboard_rows


@dataclass(frozen=True)
class LeaderboardEntry:
    rank: int
    nick: str
    score: int
    duration_seconds: float


class LeaderboardService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_leaderboard(
        self,
        quiz_id: str,
        limit: int = LEADERBOARD_SIZE,
    ) -> list[LeaderboardEntry]:
        quiz = self._session.get(Quiz, quiz_id)
        if quiz is None:
            raise QuizNotFoundError()

        statement = select(Attempt).where(
            Attempt.quiz_id == quiz_id,
            Attempt.finished_at.is_not(None),
        )
        attempts = list(self._session.scalars(statement).all())

        rows: list[LeaderboardRow] = []
        for attempt in attempts:
            if attempt.finished_at is not None:
                duration = (attempt.finished_at - attempt.started_at).total_seconds()
                rows.append(
                    LeaderboardRow(
                        nick=attempt.nick,
                        score=attempt.score,
                        duration_seconds=round(duration, 1),
                        finished_at=attempt.finished_at,
                    )
                )

        sorted_rows = sort_leaderboard_rows(rows)
        limited_rows = sorted_rows[:limit]

        return [
            LeaderboardEntry(
                rank=rank,
                nick=row.nick,
                score=row.score,
                duration_seconds=round(row.duration_seconds, 1),
            )
            for rank, row in enumerate(limited_rows, start=1)
        ]
