from datetime import datetime

from src.logic.leaderboard_order import LeaderboardRow, sort_leaderboard_rows


def main() -> None:
    input_rows = [
        LeaderboardRow(
            nick="Alice (Lower score)",
            score=5,
            duration_seconds=15.0,
            finished_at=datetime(2026, 11, 21, 10, 0),
        ),
        LeaderboardRow(
            nick="Bob (High score, slower)",
            score=10,
            duration_seconds=30.0,
            finished_at=datetime(2026, 11, 21, 10, 0),
        ),
        LeaderboardRow(
            nick="Charlie (High score, faster, later finish)",
            score=10,
            duration_seconds=20.0,
            finished_at=datetime(2026, 11, 21, 11, 0),
        ),
        LeaderboardRow(
            nick="David (High score, faster, earlier finish)",
            score=10,
            duration_seconds=20.0,
            finished_at=datetime(2026, 11, 21, 10, 0),
        ),
    ]

    print("--- Input Order ---")
    for row in input_rows:
        print(
            f"Nick: {row.nick}, Score: {row.score}, "
            f"Duration: {row.duration_seconds}s, Finished: {row.finished_at}"
        )

    sorted_rows = sort_leaderboard_rows(input_rows)

    print("\n--- Sorted Order ---")
    for rank, row in enumerate(sorted_rows, start=1):
        print(
            f"Rank {rank}: {row.nick} -> Score: {row.score}, "
            f"Duration: {row.duration_seconds}s, Finished: {row.finished_at}"
        )


if __name__ == "__main__":
    main()
