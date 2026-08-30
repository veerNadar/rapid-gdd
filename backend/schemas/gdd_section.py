import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import SectionType


class GDDSectionBase(BaseModel):
    section_type: SectionType
    content: str = ""


class GDDSectionCreate(GDDSectionBase):
    project_id: uuid.UUID


class GDDSectionUpdate(BaseModel):
    content: str | None = None


class GDDSectionRead(GDDSectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
