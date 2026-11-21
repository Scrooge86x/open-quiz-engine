from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.engine import Base


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    selected_index: Mapped[int] = mapped_column()
    is_correct: Mapped[bool] = mapped_column()

    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_answers_attempt_id_question_id"),
    )
