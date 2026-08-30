import enum


class SectionType(str, enum.Enum):
    """The GDD sections a project can have, and the section a piece of
    review feedback applies to."""

    OVERVIEW = "overview"
    GAMEPLAY_MECHANICS = "gameplay_mechanics"
    STORY_NARRATIVE = "story_narrative"
    CHARACTERS = "characters"
    WORLD_BUILDING = "world_building"
    PROGRESSION = "progression"
    ADDITIONAL = "additional"


class ReviewSource(str, enum.Enum):
    """Where the GDD content being reviewed came from."""

    UPLOADED = "uploaded"
    GENERATED = "generated"


class FeedbackStatus(str, enum.Enum):
    """Lifecycle of a single piece of review feedback."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"
