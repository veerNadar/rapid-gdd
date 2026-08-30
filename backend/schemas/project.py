import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IntakeData(BaseModel):
    """Answers collected by the project intake form. Extra fields are
    allowed so the form can evolve without a schema migration here."""

    model_config = ConfigDict(extra="allow")

    genre: str | None = None
    dimension: str | None = None  # "2D" or "3D"
    perspective: str | None = None
    multiplayer: str | None = None  # e.g. "singleplayer" / "multiplayer"
    core_hook: str | None = None
    scope_team_size: str | None = None
    target_platform: str | None = None
    reference_games: list[str] = Field(default_factory=list)
    target_feeling: str | None = None


class ProjectBase(BaseModel):
    title: str
    intake_data: IntakeData = Field(default_factory=IntakeData)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    intake_data: IntakeData | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
