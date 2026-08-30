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


class CallType(str, enum.Enum):
    """Which kind of Gemini call a `GenerationMetric` row is for."""

    SECTION_GENERATION = "section_generation"
    REVIEW_PARSE = "review_parse"
    CRITIQUE = "critique"


class GenerationStatus(str, enum.Enum):
    """Outcome of a single Gemini call attempt, for metrics."""

    OK = "ok"
    INVALID = "invalid"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
