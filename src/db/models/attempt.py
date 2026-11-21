from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.engine import Base

if TYPE_CHECKING:
    from src.db.models.answer import Answer


def _generate_uuid() -> str:
    return str(uuid4())


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_generate_uuid)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    nick: Mapped[str] = mapped_column(String)
    current_position: Mapped[int] = mapped_column(default=0)
    score: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime] = mapped_column()
    finished_at: Mapped[datetime | None] = mapped_column(default=None)

    answers: Mapped[list["Answer"]] = relationship(cascade="all, delete-orphan")

    @property
    def is_finished(self) -> bool:
        return self.finished_at is not None
