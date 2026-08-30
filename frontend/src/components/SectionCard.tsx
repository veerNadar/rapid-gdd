import { useState } from 'react'
import { ApiError, describeApiError, generateSection, updateSection } from '../api/client'
import type { GDDSection, SectionType } from '../api/types'
import Spinner from './Spinner'

interface SectionCardProps {
  projectId: string
  sectionType: SectionType
  label: string
  section: GDDSection | undefined
}

export default function SectionCard({
  projectId,
  sectionType,
  label,
  section: initialSection,
}: SectionCardProps) {
  const [section, setSection] = useState(initialSection)
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isRateLimit, setIsRateLimit] = useState(false)

  const busy = generating || saving

  function startEditing() {
    setDraft(section?.content ?? '')
    setIsEditing(true)
    setError(null)
  }

  function cancelEditing() {
    setIsEditing(false)
    setError(null)
  }

  async function handleSave() {
    if (!section) return
    setSaving(true)
    setError(null)
    setIsRateLimit(false)
    try {
      const updated = await updateSection(section.id, draft)
      setSection(updated)
      setIsEditing(false)
    } catch (err) {
      setError(describeApiError(err, 'Failed to save this edit.'))
      setIsRateLimit(err instanceof ApiError && err.status === 429)
    } finally {
      setSaving(false)
    }
  }

  async function handleGenerate() {
    setGenerating(true)
    setError(null)
    setIsRateLimit(false)
    try {
      const generated = await generateSection(projectId, sectionType)
      setSection(generated)
      setIsEditing(false)
    } catch (err) {
      setError(describeApiError(err, 'Failed to generate this section.'))
      setIsRateLimit(err instanceof ApiError && err.status === 429)
    } finally {
      setGenerating(false)
    }
  }

  const generateLabel = generating
    ? 'Generating…'
    : error
      ? 'Retry'
      : section
        ? 'Regenerate'
        : 'Generate'

  return (
    <section className="rounded-lg border border-slate-200 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-800">{label}</h2>
          {section && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
              v{section.version}
            </span>
          )}
          {generating && (
            <span className="flex items-center gap-1.5 text-xs text-slate-400">
              <Spinner /> Generating…
            </span>
          )}
        </div>
        <div className="flex gap-2">
          {section && !isEditing && (
            <button
              type="button"
              onClick={startEditing}
              disabled={busy}
              className="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
            >
              Edit
            </button>
          )}
          <button
            type="button"
            onClick={handleGenerate}
            disabled={busy}
            className={`rounded-md border px-2.5 py-1 text-xs font-medium disabled:opacity-40 ${
              error
                ? 'border-red-300 text-red-700 hover:bg-red-50'
                : 'border-slate-300 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {generateLabel}
          </button>
        </div>
      </div>

      {error && (
        <div
          className={`mt-2 flex items-start gap-2 rounded-md border px-3 py-2 text-xs ${
            isRateLimit
              ? 'border-amber-200 bg-amber-50 text-amber-800'
              : 'border-red-200 bg-red-50 text-red-700'
          }`}
        >
          <span aria-hidden>{isRateLimit ? '⏳' : '⚠️'}</span>
          <span>{error}</span>
        </div>
      )}

      <div className="mt-3">
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              disabled={saving}
              rows={12}
              className="w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs focus:border-slate-500 focus:outline-none"
            />
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleSave}
                disabled={saving}
                className="flex items-center gap-1.5 rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40"
              >
                {saving && <Spinner className="border-slate-500 border-t-white" />}
                {saving ? 'Saving…' : 'Save'}
              </button>
              <button
                type="button"
                onClick={cancelEditing}
                disabled={saving}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : section ? (
          <p className="whitespace-pre-wrap text-sm text-slate-700">{section.content}</p>
        ) : generating ? (
          <div className="animate-pulse space-y-2">
            <div className="h-3 w-full rounded bg-slate-100" />
            <div className="h-3 w-11/12 rounded bg-slate-100" />
            <div className="h-3 w-3/4 rounded bg-slate-100" />
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">Not generated yet.</p>
        )}
      </div>
    </section>
  )
}
