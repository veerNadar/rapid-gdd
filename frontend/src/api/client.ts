// Thin API client for the Rapid GDD backend. Every function below is a
// placeholder wired to the real endpoint shape — the backend routes it
// calls are currently stubs (see backend/routers/), so these will start
// returning real data as those are implemented, with no changes needed
// here.

import type {
  GDDSection,
  Project,
  ProjectCreateInput,
  Review,
  ReviewSource,
  SectionType,
} from './types'

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })

  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new ApiError(res.status, body || res.statusText)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

/** Create a new project from intake form answers. */
export function createProject(input: ProjectCreateInput): Promise<Project> {
  return request<Project>('/projects/', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

/** Fetch a single project by id. */
export function getProject(projectId: string): Promise<Project> {
  return request<Project>(`/projects/${projectId}`)
}

/** Ask the backend to generate a fresh draft of one GDD section. */
export function generateSection(
  projectId: string,
  sectionType: SectionType,
): Promise<GDDSection> {
  return request<GDDSection>('/sections/generate', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, section_type: sectionType }),
  })
}

/** Ask the backend to regenerate an existing section, optionally steered
 * by free-form instructions (e.g. "make it punchier"). */
export function regenerateSection(
  sectionId: string,
  instructions?: string,
): Promise<GDDSection> {
  return request<GDDSection>(`/sections/${sectionId}/regenerate`, {
    method: 'POST',
    body: JSON.stringify({ instructions }),
  })
}

/** Submit a GDD (uploaded file text, or a generated draft) for review. */
export function submitReview(
  projectId: string,
  source: ReviewSource,
  content?: string,
): Promise<Review> {
  return request<Review>('/reviews/', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, source, content }),
  })
}

export { ApiError }
