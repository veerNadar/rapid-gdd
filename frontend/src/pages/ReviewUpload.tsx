import { type ChangeEvent, type FormEvent, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { describeApiError, submitReview } from '../api/client'
import type { ReviewWithSections } from '../api/types'
import Spinner from '../components/Spinner'
import { SECTION_LABELS, SECTION_ORDER } from '../sectionLabels'

export default function ReviewUpload() {
  const { projectId } = useParams<{ projectId: string }>()
  const [content, setContent] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ReviewWithSections | null>(null)

  const canSubmit = content.trim() !== '' || file !== null

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null
    setFile(selected)
    if (selected) setContent('')
  }

  function handleContentChange(event: ChangeEvent<HTMLTextAreaElement>) {
    setContent(event.target.value)
    if (event.target.value) setFile(null)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!projectId || !canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      const uploaded = await submitReview(projectId, file ? { file } : { content })
      setResult(uploaded)
    } catch (err) {
      setError(describeApiError(err, 'Failed to submit review.'))
    } finally {
      setSubmitting(false)
    }
  }

  if (result) {
    const populatedTypes = new Set(result.sections.map((s) => s.section_type))
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <h1 className="text-2xl font-semibold text-slate-900">Uploaded</h1>
        <p className="mt-1 text-sm text-slate-500">
          Gemini sorted your document into {result.sections.length} of {SECTION_ORDER.length}{' '}
          sections. Anything it couldn't place landed under "Unmapped Content" in Additional
          Design Specifications.
        </p>

        <div className="mt-6 space-y-2">
          {SECTION_ORDER.map((sectionType) => (
            <div
              key={sectionType}
              className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 text-sm"
            >
              <span className="text-slate-700">{SECTION_LABELS[sectionType]}</span>
              {populatedTypes.has(sectionType) ? (
                <span className="text-xs text-emerald-600">Parsed</span>
              ) : (
                <span className="text-xs text-slate-400">No content found</span>
              )}
            </div>
          ))}
        </div>

        <Link
          to={`/projects/${projectId}`}
          className="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white"
        >
          View project →
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Upload for Review</h1>
      <p className="mt-1 text-sm text-slate-500">
        Paste an existing GDD, or upload a .txt/.docx file, and Gemini will sort it into
        Rapid GDD's sections.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="file" className="block text-sm font-medium text-slate-700">
            Upload a file
          </label>
          <input
            id="file"
            type="file"
            accept=".txt,.docx"
            onChange={handleFileChange}
            disabled={submitting}
            className="mt-1 w-full text-sm text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm disabled:opacity-40"
          />
          <p className="mt-1 text-xs text-slate-400">.txt or .docx.</p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center" aria-hidden>
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative flex justify-center">
            <span className="bg-white px-2 text-xs text-slate-400">or paste text</span>
          </div>
        </div>

        <div>
          <label htmlFor="content" className="block text-sm font-medium text-slate-700">
            GDD content
          </label>
          <textarea
            id="content"
            value={content}
            onChange={handleContentChange}
            disabled={submitting || file !== null}
            rows={10}
            placeholder="Paste your game design document here…"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none disabled:opacity-40"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !canSubmit}
          className="flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting && <Spinner className="border-slate-500 border-t-white" />}
          {submitting ? 'Parsing with Gemini…' : 'Submit for Review'}
        </button>
      </form>
    </div>
  )
}
