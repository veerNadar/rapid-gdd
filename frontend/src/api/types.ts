// Mirrors backend/schemas — kept minimal and hand-in-sync for now.

export type SectionType =
  | 'overview'
  | 'gameplay_mechanics'
  | 'story_narrative'
  | 'characters'
  | 'world_building'
  | 'progression'
  | 'additional'

export type ReviewSource = 'uploaded' | 'generated'

export type FeedbackStatus = 'pending' | 'accepted' | 'rejected' | 'edited'

export type Dimension = '2D' | '3D'

export type Perspective =
  | 'first_person'
  | 'third_person'
  | 'top_down'
  | 'isometric'
  | 'side_scrolling'

export type MultiplayerMode = 'singleplayer' | 'multiplayer'

export interface IntakeData {
  genre?: string
  dimension?: Dimension
  perspective?: Perspective
  multiplayer?: MultiplayerMode
  core_hook?: string
  scope_team_size?: string
  target_platform?: string[]
  reference_games?: string[]
  // A fixed set of options plus a free-text "other" choice both land here.
  target_feeling?: string
}

export interface Project {
  id: string
  title: string
  intake_data: IntakeData
  created_at: string
}

export interface ProjectCreateInput {
  title: string
  intake_data: IntakeData
}

export interface GDDSection {
  id: string
  project_id: string
  section_type: SectionType
  content: string
  version: number
  created_at: string
  updated_at: string
}

export interface Review {
  id: string
  project_id: string
  source: ReviewSource
  raw_content: string | null
  created_at: string
}

export interface ReviewSectionFeedback {
  id: string
  review_id: string
  section_type: SectionType
  critique: string
  suggested_rewrite: string | null
  status: FeedbackStatus
}

export interface ReviewWithSections {
  review: Review
  sections: GDDSection[]
  feedback: ReviewSectionFeedback[]
}

export interface ReviewWithFeedback {
  review: Review
  feedback: ReviewSectionFeedback[]
}

export interface ProjectWithSections {
  project: Project
  sections: GDDSection[]
}
