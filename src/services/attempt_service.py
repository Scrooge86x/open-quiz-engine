import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models.answer import Answer
from src.db.models.attempt import Attempt
from src.db.models.question import Question
from src.db.models.quiz import Quiz
from src.errors.conflict import AttemptFinishedError, WrongQuestionError
from src.errors.not_found import AttemptNotFoundError, QuizNotFoundError
from src.logic.answer_checker import is_answer_correct


@dataclass(frozen=True)
class AnswerOutcome:
    is_correct: bool
    correct_index: int
    finished: bool


@dataclass(frozen=True)
class AttemptResult:
    attempt_id: str
    quiz_id: str
    nick: str
    score: int
    question_count: int
    duration_seconds: float | None


def _calculate_duration(
    started_at: datetime,
    finished_at: datetime | None,
) -> float | None:
    if finished_at is None:
        return None
    return round((finished_at - started_at).total_seconds(), 1)


class AttemptService:
    def __init__(
        self,
        session: Session,
        clock: Callable[[], datetime],
    ) -> None:
        self._session = session
        self._clock = clock

    def start_attempt(self, quiz_id: str, nick: str) -> Attempt:
        quiz = self._get_quiz(quiz_id)

        attempt = Attempt(
            id=str(uuid.uuid4()),
            quiz_id=quiz.id,
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
        return self._get_question_by_position(attempt.quiz_id, attempt.current_position)

    def submit_answer(
        self,
        attempt_id: str,
        question_id: int,
        selected_index: int,
    ) -> AnswerOutcome:
        attempt = self.get_attempt(attempt_id)
        if attempt.is_finished:
            raise AttemptFinishedError()

        current_question = self._get_question_by_position(attempt.quiz_id, attempt.current_position)
        if question_id != current_question.id:
            raise WrongQuestionError()

        is_correct = is_answer_correct(selected_index, current_question.correct_index)
        answer = Answer(
            attempt_id=attempt.id,
            question_id=question_id,
            selected_index=selected_index,
            is_correct=is_correct,
        )
        self._session.add(answer)

        if is_correct:
            attempt.score += 1

        attempt.current_position += 1
        quiz = self._get_quiz(attempt.quiz_id)
        if attempt.current_position >= quiz.question_count:
            attempt.finished_at = self._clock()

        self._session.commit()
        return AnswerOutcome(
            is_correct=is_correct,
            correct_index=current_question.correct_index,
            finished=attempt.is_finished,
        )

    def get_result(self, attempt_id: str) -> AttemptResult:
        attempt = self.get_attempt(attempt_id)
        quiz = self._get_quiz(attempt.quiz_id)
        duration_seconds = _calculate_duration(attempt.started_at, attempt.finished_at)

        return AttemptResult(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            nick=attempt.nick,
            score=attempt.score,
            question_count=quiz.question_count,
            duration_seconds=duration_seconds,
        )

    def _get_quiz(self, quiz_id: str) -> Quiz:
        quiz = self._session.get(Quiz, quiz_id)
        if quiz is None:
            raise QuizNotFoundError()
        return quiz

    def _get_question_by_position(self, quiz_id: str, position: int) -> Question:
        statement = select(Question).where(
            Question.quiz_id == quiz_id,
            Question.position == position,
        )
        question = self._session.scalars(statement).first()
        if question is None:
            raise QuizNotFoundError()
        return question
