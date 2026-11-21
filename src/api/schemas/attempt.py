from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class AttemptCreateRequest(BaseModel):
    nick: str


class AttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attempt_id: str = Field(validation_alias=AliasChoices("attempt_id", "id"))
    quiz_id: str
    nick: str


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    question_id: int = Field(validation_alias=AliasChoices("question_id", "id"))
    position: int
    question_count: int
    text: str
    category: str
    difficulty: str
    options: list[str]


class AnswerRequest(BaseModel):
    question_id: int
    selected_index: int


class AnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_correct: bool
    correct_index: int
    finished: bool


class ResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: str
    quiz_id: str
    nick: str
    score: int
    question_count: int
    duration_seconds: float | None
