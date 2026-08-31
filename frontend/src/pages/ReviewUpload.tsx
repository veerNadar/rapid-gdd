import { type ChangeEvent, type FormEvent, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { describeApiError, submitReview } from '../api/client'
import Spinner from '../components/Spinner'
import { btnPrimary, card, inputClass, labelClass } from '../styles'

export default function ReviewUpload() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
      navigate(`/projects/${projectId}/reviews/${uploaded.review.id}`)
    } catch (err) {
      setError(describeApiError(err, 'Failed to submit review.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Upload for Review</h1>
      <p className="mt-1 text-sm text-slate-500">
        Paste an existing GDD, or upload a .txt/.docx file. Gemini will sort it into Rapid
        GDD's sections and critique each one.
      </p>

      <form onSubmit={handleSubmit} className={`${card} mt-8 space-y-5`}>
        <div>
          <label htmlFor="file" className={labelClass}>
            Upload a file
          </label>
          <input
            id="file"
            type="file"
            accept=".txt,.docx"
            onChange={handleFileChange}
            disabled={submitting}
            className="mt-1 w-full text-sm text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-indigo-700 hover:file:bg-indigo-100 disabled:opacity-40"
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
          <label htmlFor="content" className={labelClass}>
            GDD content
          </label>
          <textarea
            id="content"
            value={content}
            onChange={handleContentChange}
            disabled={submitting || file !== null}
            rows={10}
            placeholder="Paste your game design document here…"
            className={`${inputClass} disabled:opacity-40`}
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button type="submit" disabled={submitting || !canSubmit} className={btnPrimary}>
          {submitting && <Spinner className="border-indigo-300 border-t-white" />}
          {submitting ? 'Parsing & critiquing with Gemini…' : 'Submit for Review'}
        </button>
      </form>
    </div>
  )
}
