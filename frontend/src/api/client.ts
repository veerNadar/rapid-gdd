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
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    // fetch itself threw: the network is down, the backend isn't
    // running, CORS blocked it, etc. — there's no HTTP response at all.
    throw new ApiError(0, 'Could not reach the server. Is the backend running?')
  }

  if (!res.ok) {
    const rawBody = await res.text().catch(() => '')
    // FastAPI error responses are {"detail": "..."} — surface just the
    // detail message when present, rather than the raw JSON blob.
    let message = rawBody || res.statusText
    if (rawBody) {
      try {
        const parsed: unknown = JSON.parse(rawBody)
        if (
          parsed &&
          typeof parsed === 'object' &&
          'detail' in parsed &&
          typeof parsed.detail === 'string'
        ) {
          message = parsed.detail
        }
      } catch {
        // Not JSON — keep the raw text as the message.
      }
    }
    throw new ApiError(res.status, message)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return (await res.json()) as T
}

/** Turn a caught error into a short, user-facing message. Recognizes
 * known ApiError status codes — especially 429, Gemini's free-tier rate
 * limit — and falls back to the error's own message otherwise. */
export function describeApiError(err: unknown, fallback: string): string {
  if (err instanceof ApiError) {
    if (err.status === 429) {
      return err.message || "Gemini's free-tier rate limit was hit. Wait a bit and try again."
    }
    if (err.status === 0) {
      return err.message
    }
    return err.message || fallback
  }
  if (err instanceof Error) {
    return err.message || fallback
  }
  return fallback
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

/** The latest version of each section already generated for a project. */
export function listSections(projectId: string): Promise<GDDSection[]> {
  return request<GDDSection[]>(`/sections/?project_id=${encodeURIComponent(projectId)}`)
}

/** Ask the backend to (re)generate one GDD section. Generating a section
 * that already has content creates a new version rather than overwriting
 * the old one — call this the same way for both the initial "Generate"
 * and a later "Regenerate". */
export function generateSection(
  projectId: string,
  sectionType: SectionType,
): Promise<GDDSection> {
  return request<GDDSection>(`/projects/${projectId}/sections/${sectionType}/generate`, {
    method: 'POST',
  })
}

/** Generate every section of a project's GDD in sequence. */
export function generateFullGdd(projectId: string): Promise<GDDSection[]> {
  return request<GDDSection[]>(`/projects/${projectId}/generate`, {
    method: 'POST',
  })
}

/** Manually edit a section's content in place (does not create a new
 * version — that's reserved for AI (re)generation). */
export function updateSection(sectionId: string, content: string): Promise<GDDSection> {
  return request<GDDSection>(`/sections/${sectionId}`, {
    method: 'PATCH',
    body: JSON.stringify({ content }),
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
