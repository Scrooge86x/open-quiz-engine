import random
import uuid
from collections.abc import Callable
from datetime import datetime

from sqlalchemy.orm import Session

from src.clients.trivia_client import TriviaClient, TriviaQuestion
from src.db.models.question import Question
from src.db.models.quiz import Quiz
from src.errors.not_found import QuizNotFoundError
from src.errors.validation import NotEnoughQuestionsError
from src.logic.option_shuffler import build_options
from src.logic.text_utils import decode_html_text


def _convert_trivia_question(
    trivia_question: TriviaQuestion,
    quiz_id: str,
    position: int,
    rng: random.Random,
) -> Question:
    decoded_text = decode_html_text(trivia_question.text)
    decoded_correct = decode_html_text(trivia_question.correct_answer)
    decoded_incorrect = [decode_html_text(answer) for answer in trivia_question.incorrect_answers]
    decoded_category = decode_html_text(trivia_question.category)

    options, correct_index = build_options(
        question_type=trivia_question.question_type,
        correct_answer=decoded_correct,
        incorrect_answers=decoded_incorrect,
        rng=rng,
    )

    return Question(
        quiz_id=quiz_id,
        position=position,
        text=decoded_text,
        category=decoded_category,
        difficulty=trivia_question.difficulty,
        options=options,
        correct_index=correct_index,
    )


class QuizService:
    def __init__(
        self,
        session: Session,
        trivia_client: TriviaClient,
        rng: random.Random,
        clock: Callable[[], datetime],
    ) -> None:
        self._session = session
        self._trivia_client = trivia_client
        self._rng = rng
        self._clock = clock

    def create_quiz(
        self,
        question_count: int,
        difficulty: str | None = None,
    ) -> Quiz:
        trivia_questions = self._trivia_client.fetch_questions(
            question_count=question_count,
            difficulty=difficulty,
        )
        if not trivia_questions:
            raise NotEnoughQuestionsError()

        quiz_id = str(uuid.uuid4())
        quiz = Quiz(
            id=quiz_id,
            difficulty=difficulty,
            created_at=self._clock(),
        )

        for position, trivia_question in enumerate(trivia_questions):
            question = _convert_trivia_question(
                trivia_question=trivia_question,
                quiz_id=quiz_id,
                position=position,
                rng=self._rng,
            )
            quiz.questions.append(question)

        self._session.add(quiz)
        self._session.commit()
        return quiz

    def get_quiz(self, quiz_id: str) -> Quiz:
        quiz = self._session.get(Quiz, quiz_id)
        if quiz is None:
            raise QuizNotFoundError()
        return quiz
