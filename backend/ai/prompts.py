"""Structured prompt templates for generating GDD sections with Gemini.

Each section type gets its own `ChatPromptTemplate` keyed by
`models.enums.SectionType` in `SECTION_PROMPTS`. Only "Game Overview" is
implemented for now — the pipeline is being validated end-to-end on this
one section before the rest are added.
"""

from langchain_core.prompts import ChatPromptTemplate

from models.enums import SectionType

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

GAME_OVERVIEW_HUMAN_TEMPLATE = """\
Write the Game Overview section for this project.

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

GAME_OVERVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", GAME_OVERVIEW_SYSTEM_PROMPT),
        ("human", GAME_OVERVIEW_HUMAN_TEMPLATE),
    ]
)

# Maps each section type to its prompt template. Sections not yet present
# here are not implemented — `generate_section` raises a clear error for
# them rather than silently producing nothing.
SECTION_PROMPTS: dict[SectionType, ChatPromptTemplate] = {
    SectionType.OVERVIEW: GAME_OVERVIEW_PROMPT,
}
