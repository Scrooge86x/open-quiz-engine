from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LeaderboardRow:
    nick: str
    score: int
    duration_seconds: float
    finished_at: datetime


def sort_leaderboard_rows(rows: list[LeaderboardRow]) -> list[LeaderboardRow]:
    return sorted(
        rows,
        key=lambda row: (-row.score, row.duration_seconds, row.finished_at),
    )
