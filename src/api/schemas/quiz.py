from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.config import DEFAULT_QUESTIONS, MAX_QUESTIONS, MIN_QUESTIONS


class QuizCreateRequest(BaseModel):
    question_count: int = Field(
        default=DEFAULT_QUESTIONS,
        ge=MIN_QUESTIONS,
        le=MAX_QUESTIONS,
    )
    difficulty: Literal["easy", "medium", "hard"] | None = None


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    difficulty: str | None
    question_count: int
