import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Dimension = Literal["2D", "3D"]
Perspective = Literal[
    "first_person", "third_person", "top_down", "isometric", "side_scrolling"
]
MultiplayerMode = Literal["singleplayer", "multiplayer"]


class IntakeData(BaseModel):
    """Answers collected by the project intake form. Extra fields are
    allowed so the form can evolve without a schema migration here.

    ``target_feeling`` is a free string rather than a Literal: the intake
    form offers a fixed set of options plus an "other" choice that lets
    the user type their own, and both land in this same field.
    """

    model_config = ConfigDict(extra="allow")

    genre: str | None = None
    dimension: Dimension | None = None
    perspective: Perspective | None = None
    multiplayer: MultiplayerMode | None = None
    core_hook: str | None = None
    scope_team_size: str | None = None
    target_platform: list[str] = Field(default_factory=list)
    reference_games: list[str] = Field(default_factory=list, min_length=1, max_length=3)
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
