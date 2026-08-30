import type { SectionType } from './api/types'

export const SECTION_LABELS: Record<SectionType, string> = {
  overview: 'Game Overview',
  gameplay_mechanics: 'Gameplay & Mechanics',
  story_narrative: 'Story & Narrative',
  characters: 'Characters',
  world_building: 'World-Building',
  progression: 'Progression Systems',
  additional: 'Additional Design Specifications',
}

// Mirrors backend ai.prompts.SECTION_ORDER.
export const SECTION_ORDER: SectionType[] = [
  'overview',
  'gameplay_mechanics',
  'story_narrative',
  'characters',
  'world_building',
  'progression',
  'additional',
]
