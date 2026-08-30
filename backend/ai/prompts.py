"""Structured prompt templates for generating GDD sections with Gemini.

Each section type gets its own `ChatPromptTemplate` keyed by
`models.enums.SectionType` in `SECTION_PROMPTS`, all sharing the same
input variables: the project's intake fields, plus a `context` block
that carries the content of already-generated sections this section
depends on (see `SECTION_DEPENDENCIES`), so e.g. Characters can stay
consistent with an existing Story & Narrative section.

`SECTION_ORDER` is the sequence "Generate Full GDD" walks: each section
only depends on sections earlier in this list.
"""

from langchain_core.prompts import ChatPromptTemplate

from models.enums import SectionType

# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------

SECTION_LABELS: dict[SectionType, str] = {
    SectionType.OVERVIEW: "Game Overview",
    SectionType.GAMEPLAY_MECHANICS: "Gameplay & Mechanics",
    SectionType.STORY_NARRATIVE: "Story & Narrative",
    SectionType.CHARACTERS: "Characters",
    SectionType.WORLD_BUILDING: "World-Building",
    SectionType.PROGRESSION: "Progression Systems",
    SectionType.ADDITIONAL: "Additional Design Specifications",
}

# The sequence "Generate Full GDD" generates sections in. Each entry only
# depends (per SECTION_DEPENDENCIES below) on sections earlier in this list.
SECTION_ORDER: list[SectionType] = [
    SectionType.OVERVIEW,
    SectionType.GAMEPLAY_MECHANICS,
    SectionType.STORY_NARRATIVE,
    SectionType.CHARACTERS,
    SectionType.WORLD_BUILDING,
    SectionType.PROGRESSION,
    SectionType.ADDITIONAL,
]

# Which already-generated sections (if present) get included as context
# when generating a given section, for narrative/design consistency.
SECTION_DEPENDENCIES: dict[SectionType, list[SectionType]] = {
    SectionType.OVERVIEW: [],
    SectionType.GAMEPLAY_MECHANICS: [SectionType.OVERVIEW],
    SectionType.STORY_NARRATIVE: [SectionType.OVERVIEW],
    SectionType.CHARACTERS: [SectionType.OVERVIEW, SectionType.STORY_NARRATIVE],
    SectionType.WORLD_BUILDING: [
        SectionType.OVERVIEW,
        SectionType.STORY_NARRATIVE,
        SectionType.CHARACTERS,
    ],
    SectionType.PROGRESSION: [SectionType.OVERVIEW, SectionType.GAMEPLAY_MECHANICS],
    SectionType.ADDITIONAL: [
        SectionType.OVERVIEW,
        SectionType.GAMEPLAY_MECHANICS,
        SectionType.STORY_NARRATIVE,
        SectionType.CHARACTERS,
        SectionType.WORLD_BUILDING,
        SectionType.PROGRESSION,
    ],
}

_INTAKE_SUMMARY_BLOCK = """\
Project title: {title}
Genre: {genre}
Dimension: {dimension}
Perspective: {perspective}
Players: {multiplayer}
The Hook: {core_hook}
Scope / team size: {scope_team_size}
Target platform(s): {target_platform}
Reference games: {reference_games}
Target feeling: {target_feeling}\
"""

_CONTEXT_BLOCK = """\
Already-generated sections, provided for consistency — do not repeat \
them verbatim, but keep names, tone, and established facts aligned with \
them:
{context}\
"""


def _human_template(instruction: str) -> str:
    """Build a section's human message: its task instruction, the shared
    intake summary, and the shared already-generated-sections context."""
    return f"{instruction.strip()}\n\n{_INTAKE_SUMMARY_BLOCK}\n\n{_CONTEXT_BLOCK}"


def _build_prompt(system_prompt: str, instruction: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt.strip()),
            ("human", _human_template(instruction)),
        ]
    )


# ---------------------------------------------------------------------------
# Game Overview
# ---------------------------------------------------------------------------

GAME_OVERVIEW_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Game Overview" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you. If a detail \
is missing ("Not specified"), do not invent one; either omit it or note \
that it still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Concept Summary (2-3 sentences capturing the game at a glance)
- Genre & Platform
- Core Hook (why a player keeps playing — expand on the developer's hook,
  don't just repeat it verbatim)
- Player Experience (the target feeling, and how the stated perspective /
  dimension / multiplayer mode serve it)
- Inspirations (how the reference games inform this game, and what makes
  it different from them)
- Scope Notes (what the stated team size / timeline implies for what's
  achievable)

Keep the whole section to roughly 300-450 words.\
"""

GAME_OVERVIEW_PROMPT = _build_prompt(
    GAME_OVERVIEW_SYSTEM_PROMPT,
    'Write the "Game Overview" section for this project.',
)

# ---------------------------------------------------------------------------
# Gameplay & Mechanics
# ---------------------------------------------------------------------------

GAMEPLAY_MECHANICS_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Gameplay & Mechanics" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you, and stay \
consistent with anything shown to you from already-generated sections. \
If a detail is missing ("Not specified"), do not invent one; either omit \
it or note that it still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Core Gameplay Loop (the minute-to-minute cycle of player actions)
- Primary Mechanics (a bulleted list of the game's core mechanics, each
  with a one- or two-sentence description)
- Controls & Player Actions (informed by the stated dimension and
  perspective)
- Systems & Interactions (how the mechanics reinforce each other and the
  core hook)
- Difficulty & Balance Notes
- Open Questions (mechanics that still need prototyping or a decision)

Keep the whole section to roughly 350-500 words.\
"""

GAMEPLAY_MECHANICS_PROMPT = _build_prompt(
    GAMEPLAY_MECHANICS_SYSTEM_PROMPT,
    'Write the "Gameplay & Mechanics" section for this project.',
)

# ---------------------------------------------------------------------------
# Story & Narrative
# ---------------------------------------------------------------------------

STORY_NARRATIVE_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Story & Narrative" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you, and stay \
consistent with anything shown to you from already-generated sections. \
If a detail is missing ("Not specified"), do not invent one; either omit \
it or note that it still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Premise (a one-paragraph logline)
- Setting (time period, place, and the tone implied by the target
  feeling)
- Narrative Structure (linear, branching, environmental, etc. — pick
  something realistic for the stated scope / team size)
- Key Story Beats (3-5 major beats from opening to ending)
- Themes & Tone
- Narrative Delivery (how the story reaches the player — dialogue,
  cutscenes, environmental storytelling — appropriate to the team's
  scope)

Keep the whole section to roughly 350-500 words.\
"""

STORY_NARRATIVE_PROMPT = _build_prompt(
    STORY_NARRATIVE_SYSTEM_PROMPT,
    'Write the "Story & Narrative" section for this project.',
)

# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

CHARACTERS_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Characters" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you. If a "Story \
& Narrative" section is provided below, this cast MUST fit its premise, \
setting, and story beats — reuse its names, roles, and motivations \
rather than introducing a disconnected cast. If a detail is missing \
("Not specified"), do not invent one; either omit it or note that it \
still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Protagonist (who the player is or controls, their motivation, and how
  this ties to the Hook)
- Key Supporting Characters (2-4 characters: allies, antagonists, or
  other roles)
- Character Roles in Gameplay (how each named character connects to a
  mechanic — grants an ability, gates content, etc.)
- Consistency Notes (briefly note how this cast lines up with the Story
  & Narrative section, if one was provided)

Keep the whole section to roughly 350-500 words.\
"""

CHARACTERS_PROMPT = _build_prompt(
    CHARACTERS_SYSTEM_PROMPT,
    'Write the "Characters" section for this project.',
)

# ---------------------------------------------------------------------------
# World-Building
# ---------------------------------------------------------------------------

WORLD_BUILDING_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "World-Building" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you. If "Story & \
Narrative" and/or "Characters" sections are provided below, this world \
MUST be consistent with them — the same setting, timeline, and named \
characters/locations, not a contradicting one. If a detail is missing \
("Not specified"), do not invent one; either omit it or note that it \
still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- World Overview (scale and tone of the setting)
- Key Locations (3-5 locations, each with a one- to two-sentence
  description tied to the stated dimension/perspective)
- Lore & History (background that supports the story, kept brief)
- Rules & Constraints (world logic that shapes gameplay — e.g. a magic
  system's limits, technology level)
- Consistency Notes (how this ties back to Story & Narrative /
  Characters, if provided)

Keep the whole section to roughly 350-500 words.\
"""

WORLD_BUILDING_PROMPT = _build_prompt(
    WORLD_BUILDING_SYSTEM_PROMPT,
    'Write the "World-Building" section for this project.',
)

# ---------------------------------------------------------------------------
# Progression Systems
# ---------------------------------------------------------------------------

PROGRESSION_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Progression Systems" section of their Game Design Document (GDD).

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you, and keep \
progression systems consistent with the mechanics described in the \
"Gameplay & Mechanics" section, if provided below. If a detail is \
missing ("Not specified"), do not invent one; either omit it or note \
that it still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Progression Philosophy (what growth is meant to feel like, tied to the
  target feeling)
- Player Progression (leveling, unlocks, skill trees, or equivalent —
  tied to the mechanics already established)
- Content / World Progression (pacing and gating across the game's
  length)
- Reward Loops (short-, mid-, and long-term rewards)
- Scope-Appropriate Cuts (what to trim first if the stated team
  size/timeline runs short)

Keep the whole section to roughly 350-500 words.\
"""

PROGRESSION_PROMPT = _build_prompt(
    PROGRESSION_SYSTEM_PROMPT,
    'Write the "Progression Systems" section for this project.',
)

# ---------------------------------------------------------------------------
# Additional Design Specifications
# ---------------------------------------------------------------------------

ADDITIONAL_SYSTEM_PROMPT = """\
You are a seasoned game designer helping an indie or solo developer write \
the "Additional Design Specifications" section of their Game Design \
Document (GDD) — a catch-all for details that don't fit elsewhere.

Write clearly and concretely — avoid generic marketing language. Ground \
every claim in the specific details the developer gave you, and stay \
consistent with anything shown to you from already-generated sections \
below. If a detail is missing ("Not specified"), do not invent one; \
either omit it or note that it still needs to be decided.

Output clean Markdown with the following subsections, each as a "##" \
heading:
- Audio & Art Direction (informed by the target feeling and genre)
- UI/UX Considerations
- Technical & Platform Considerations (informed by the target platforms)
- Monetization & Release Notes (write "Not applicable" if nothing was
  specified rather than guessing)
- Risks & Open Questions

Keep the whole section to roughly 300-450 words.\
"""

ADDITIONAL_PROMPT = _build_prompt(
    ADDITIONAL_SYSTEM_PROMPT,
    'Write the "Additional Design Specifications" section for this project.',
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SECTION_PROMPTS: dict[SectionType, ChatPromptTemplate] = {
    SectionType.OVERVIEW: GAME_OVERVIEW_PROMPT,
    SectionType.GAMEPLAY_MECHANICS: GAMEPLAY_MECHANICS_PROMPT,
    SectionType.STORY_NARRATIVE: STORY_NARRATIVE_PROMPT,
    SectionType.CHARACTERS: CHARACTERS_PROMPT,
    SectionType.WORLD_BUILDING: WORLD_BUILDING_PROMPT,
    SectionType.PROGRESSION: PROGRESSION_PROMPT,
    SectionType.ADDITIONAL: ADDITIONAL_PROMPT,
}
