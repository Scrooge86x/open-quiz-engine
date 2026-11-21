from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_attempt_service
from src.api.schemas.attempt import (
    AnswerRequest,
    AnswerResponse,
    QuestionResponse,
    ResultResponse,
)
from src.api.schemas.error import ErrorResponse
from src.services.attempt_service import AttemptService

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


@router.get(
    "/{attempt_id}/question",
    response_model=QuestionResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    },
)
def get_current_question(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> QuestionResponse:
    question = attempt_service.get_current_question(attempt_id=attempt_id)
    return QuestionResponse(
        question_id=question.id,
        position=question.position,
        question_count=question.quiz.question_count,
        text=question.text,
        category=question.category,
        difficulty=question.difficulty,
        options=question.options,
    )


@router.post(
    "/{attempt_id}/answer",
    response_model=AnswerResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
def submit_answer(
    attempt_id: str,
    request: AnswerRequest,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> AnswerResponse:
    outcome = attempt_service.submit_answer(
        attempt_id=attempt_id,
        question_id=request.question_id,
        selected_index=request.selected_index,
    )
    return AnswerResponse.model_validate(outcome)


@router.get(
    "/{attempt_id}/result",
    response_model=ResultResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
def get_result(
    attempt_id: str,
    attempt_service: AttemptService = Depends(get_attempt_service),
) -> ResultResponse:
    result = attempt_service.get_result(attempt_id=attempt_id)
    return ResultResponse.model_validate(result)
