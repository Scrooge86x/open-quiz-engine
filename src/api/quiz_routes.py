from fastapi import APIRouter, Depends, status

from src.api.dependencies import (
    get_attempt_service,
    get_leaderboard_service,
    get_quiz_service,
)
from src.api.schemas.attempt import AttemptCreateRequest, AttemptResponse
from src.api.schemas.error import ErrorResponse
from src.api.schemas.leaderboard import LeaderboardEntryResponse
from src.api.schemas.quiz import QuizCreateRequest, QuizResponse
from src.services.attempt_service import AttemptService
from src.services.leaderboard_service import LeaderboardService
from src.services.quiz_service import QuizService

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=QuizResponse,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
        status.HTTP_502_BAD_GATEWAY: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
def create_quiz(
    request: QuizCreateRequest = QuizCreateRequest(),
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizResponse:
    quiz = quiz_service.create_quiz(
        question_count=request.question_count,
        difficulty=request.difficulty,
    )
    return QuizResponse.model_validate(quiz)


@router.get(
    "/{quiz_id}",
    response_model=QuizResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
def get_quiz(
    quiz_id: str,
    quiz_service: QuizService = Depends(get_quiz_service),
) -> QuizResponse:
    quiz = quiz_service.get_quiz(quiz_id=quiz_id)
    return QuizResponse.model_validate(quiz)


@router.post(
    "/{quiz_id}/attempts",
    status_code=status.HTTP_201_CREATED,
    response_model=AttemptResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
def create_attempt(
    quiz_id: str,
    request: AttemptCreateRequest,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> AttemptResponse:
    attempt = attempt_service.start_attempt(quiz_id=quiz_id, nick=request.nick)
    return AttemptResponse.model_validate(attempt)


@router.get(
    "/{quiz_id}/leaderboard",
    response_model=list[LeaderboardEntryResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
def get_leaderboard(
    quiz_id: str,
    leaderboard_service: LeaderboardService = Depends(get_leaderboard_service),
) -> list[LeaderboardEntryResponse]:
    entries = leaderboard_service.get_leaderboard(quiz_id=quiz_id)
    return [LeaderboardEntryResponse.model_validate(entry) for entry in entries]
