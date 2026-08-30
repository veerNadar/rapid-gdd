import { type FormEvent, useState } from 'react'
import { useParams } from 'react-router-dom'
import { describeApiError, submitReview } from '../api/client'
import Spinner from '../components/Spinner'

export default function ReviewUpload() {
  const { projectId } = useParams<{ projectId: string }>()
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!projectId) return
    setSubmitting(true)
    setError(null)
    try {
      await submitReview(projectId, 'uploaded', content)
      setSubmitted(true)
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
        Paste an existing GDD, or upload a file, to get section-by-section
        critique and suggested rewrites.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="file" className="block text-sm font-medium text-slate-700">
            Upload a file
          </label>
          <input
            id="file"
            type="file"
            disabled
            className="mt-1 w-full text-sm text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm"
          />
          <p className="mt-1 text-xs text-slate-400">File parsing not wired up yet.</p>
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
            onChange={(e) => setContent(e.target.value)}
            rows={10}
            placeholder="Paste your game design document here…"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}
        {submitted && <p className="text-sm text-emerald-600">Review submitted.</p>}

        <button
          type="submit"
          disabled={submitting || !content}
          className="flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting && <Spinner className="border-slate-500 border-t-white" />}
          {submitting ? 'Submitting…' : 'Submit for Review'}
        </button>
      </form>
    </div>
  )
}
