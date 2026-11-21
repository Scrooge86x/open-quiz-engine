import random
from collections.abc import Callable, Generator
from datetime import datetime, timezone

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from src.clients.trivia_client import HttpTriviaClient, TriviaClient
from src.services.attempt_service import AttemptService
from src.services.leaderboard_service import LeaderboardService
from src.services.quiz_service import QuizService


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_session(request: Request) -> Generator[Session, None, None]:
    session_factory: sessionmaker[Session] = request.app.state.session_factory
    with session_factory() as session:
        yield session


def get_trivia_client() -> TriviaClient:
    return HttpTriviaClient()


def get_rng() -> random.Random:
    return random.Random()


def get_clock() -> Callable[[], datetime]:
    return utc_now


def get_quiz_service(
    session: Session = Depends(get_session),
    trivia_client: TriviaClient = Depends(get_trivia_client),
    rng: random.Random = Depends(get_rng),
    clock: Callable[[], datetime] = Depends(get_clock),
) -> QuizService:
    return QuizService(
        session=session,
        trivia_client=trivia_client,
        rng=rng,
        clock=clock,
    )


def get_attempt_service(
    session: Session = Depends(get_session),
    clock: Callable[[], datetime] = Depends(get_clock),
) -> AttemptService:
    return AttemptService(
        session=session,
        clock=clock,
    )


def get_leaderboard_service(
    session: Session = Depends(get_session),
) -> LeaderboardService:
    return LeaderboardService(session=session)
