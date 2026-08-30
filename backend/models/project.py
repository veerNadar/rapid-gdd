import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Project(Base):
    """A single game design document project, seeded by an intake form.

    ``intake_data`` holds the free-form intake answers as JSON, e.g.::

        {
            "genre": "metroidvania",
            "dimension": "2D",
            "perspective": "side-scrolling",
            "multiplayer": "singleplayer",
            "core_hook": "you play as the dungeon, not the hero",
            "scope_team_size": "solo, 6 months",
            "target_platform": "PC (Steam)",
            "reference_games": ["Hollow Knight", "Dead Cells"],
            "target_feeling": "tense but rewarding exploration"
        }
    """

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    intake_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    gdd_sections: Mapped[list["GDDSection"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r}>"
