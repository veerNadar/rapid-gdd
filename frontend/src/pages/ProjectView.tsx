import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getProject } from '../api/client'
import type { Project, SectionType } from '../api/types'

const SECTION_LABELS: Record<SectionType, string> = {
  overview: 'Overview',
  gameplay_mechanics: 'Gameplay Mechanics',
  story_narrative: 'Story & Narrative',
  characters: 'Characters',
  world_building: 'World Building',
  progression: 'Progression',
  additional: 'Additional Notes',
}

export default function ProjectView() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    getProject(projectId)
      .then(setProject)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load project'))
  }, [projectId])

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">
        {project?.title ?? `Project ${projectId}`}
      </h1>
      <p className="mt-1 text-sm text-slate-500">
        Generate, edit, and version each section of your game design document.
      </p>

      <Link
        to={`/projects/${projectId}/review`}
        className="mt-3 inline-block text-sm text-slate-500 underline hover:text-slate-900"
      >
        Submit this GDD for review →
      </Link>

      {error && (
        <p className="mt-4 text-sm text-red-600">
          {error} (expected until the backend endpoints are implemented)
        </p>
      )}

      <div className="mt-8 space-y-4">
        {Object.entries(SECTION_LABELS).map(([sectionType, label]) => (
          <section
            key={sectionType}
            className="rounded-lg border border-slate-200 p-4"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-800">{label}</h2>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                >
                  Generate
                </button>
                <button
                  type="button"
                  className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                >
                  Regenerate
                </button>
              </div>
            </div>
            <p className="mt-2 text-sm text-slate-400 italic">
              No content yet — placeholder section body.
            </p>
          </section>
        ))}
      </div>
    </div>
  )
}
