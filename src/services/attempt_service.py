import uuid
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.attempt import Attempt
from src.db.models.question import Question
from src.db.models.quiz import Quiz
from src.errors.conflict import AttemptFinishedError
from src.errors.not_found import AttemptNotFoundError, QuizNotFoundError


class AttemptService:
    def __init__(
        self,
        session: Session,
        clock: Callable[[], datetime],
    ) -> None:
        self._session = session
        self._clock = clock

    def start_attempt(self, quiz_id: str, nick: str) -> Attempt:
        quiz = self._session.get(Quiz, quiz_id)
        if quiz is None:
            raise QuizNotFoundError()

        attempt = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz_id,
            nick=nick,
            current_position=0,
            score=0,
            started_at=self._clock(),
        )
        self._session.add(attempt)
        self._session.commit()
        return attempt

    def get_attempt(self, attempt_id: str) -> Attempt:
        attempt = self._session.get(Attempt, attempt_id)
        if attempt is None:
            raise AttemptNotFoundError()
        return attempt

    def get_current_question(self, attempt_id: str) -> Question:
        attempt = self.get_attempt(attempt_id)
        if attempt.is_finished:
            raise AttemptFinishedError()

        statement = select(Question).where(
            Question.quiz_id == attempt.quiz_id,
            Question.position == attempt.current_position,
        )
        question = self._session.scalars(statement).first()
        if question is None:
            raise QuizNotFoundError()
        return question
