from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.engine import Base

if TYPE_CHECKING:
    from src.db.models.question import Question


def _generate_uuid() -> str:
    return str(uuid4())


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_generate_uuid)
    difficulty: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column()

    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz",
        order_by="Question.position",
        cascade="all, delete-orphan",
    )

    @property
    def question_count(self) -> int:
        return len(self.questions)
