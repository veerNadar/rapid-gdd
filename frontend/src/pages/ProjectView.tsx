import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { describeApiError, getProject, listSections } from '../api/client'
import type { GDDSection, Project, SectionType } from '../api/types'
import SectionCard from '../components/SectionCard'
import SectionCardSkeleton from '../components/SectionCardSkeleton'
import { SECTION_LABELS } from '../sectionLabels'

export default function ProjectView() {
  const { projectId } = useParams<{ projectId: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [sections, setSections] = useState<Partial<Record<SectionType, GDDSection>>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    Promise.all([getProject(projectId), listSections(projectId)])
      .then(([loadedProject, loadedSections]) => {
        setProject(loadedProject)
        const byType: Partial<Record<SectionType, GDDSection>> = {}
        for (const section of loadedSections) {
          byType[section.section_type] = section
        }
        setSections(byType)
      })
      .catch((err) => setError(describeApiError(err, 'Failed to load project')))
      .finally(() => setLoading(false))
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

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <div className="mt-8 space-y-4">
        {loading
          ? Object.keys(SECTION_LABELS).map((sectionType) => (
              <SectionCardSkeleton key={sectionType} />
            ))
          : projectId &&
            (Object.entries(SECTION_LABELS) as [SectionType, string][]).map(
              ([sectionType, label]) => (
                <SectionCard
                  key={sectionType}
                  projectId={projectId}
                  sectionType={sectionType}
                  label={label}
                  section={sections[sectionType]}
                />
              ),
            )}
      </div>
    </div>
  )
}
