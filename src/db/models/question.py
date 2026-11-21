from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.engine import Base

if TYPE_CHECKING:
    from src.db.models.quiz import Quiz


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column()
    text: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String)
    options: Mapped[list[str]] = mapped_column(JSON)
    correct_index: Mapped[int] = mapped_column()

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")

    __table_args__ = (
        UniqueConstraint("quiz_id", "position", name="uq_questions_quiz_id_position"),
    )
