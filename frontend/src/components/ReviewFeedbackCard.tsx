import { useState } from 'react'
import { describeApiError, updateReviewFeedback } from '../api/client'
import type { FeedbackStatus, ReviewSectionFeedback } from '../api/types'
import { btnDanger, btnSecondary, btnSuccess, card } from '../styles'
import Spinner from './Spinner'

const STATUS_STYLES: Record<FeedbackStatus, string> = {
  pending: 'bg-slate-100 text-slate-600',
  accepted: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-700',
  edited: 'bg-blue-100 text-blue-700',
}

interface ReviewFeedbackCardProps {
  label: string
  originalContent: string | undefined
  feedback: ReviewSectionFeedback
  onUpdate: (updated: ReviewSectionFeedback) => void
}

export default function ReviewFeedbackCard({
  label,
  originalContent,
  feedback,
  onUpdate,
}: ReviewFeedbackCardProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(feedback.suggested_rewrite ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function setStatus(status: FeedbackStatus) {
    setSaving(true)
    setError(null)
    try {
      const updated = await updateReviewFeedback(feedback.id, { status })
      onUpdate(updated)
    } catch (err) {
      setError(describeApiError(err, 'Failed to update this section.'))
    } finally {
      setSaving(false)
    }
  }

  function startEditing() {
    setDraft(feedback.suggested_rewrite ?? '')
    setIsEditing(true)
    setError(null)
  }

  async function handleSaveEdit() {
    setSaving(true)
    setError(null)
    try {
      const updated = await updateReviewFeedback(feedback.id, {
        status: 'edited',
        suggested_rewrite: draft,
      })
      onUpdate(updated)
      setIsEditing(false)
    } catch (err) {
      setError(describeApiError(err, 'Failed to save your edit.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className={card}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-800">{label}</h2>
          <span
            className={`rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_STYLES[feedback.status]}`}
          >
            {feedback.status}
          </span>
        </div>
        <div className="flex gap-2">
          <button type="button" onClick={() => setStatus('accepted')} disabled={saving} className={btnSuccess}>
            Accept
          </button>
          <button
            type="button"
            onClick={startEditing}
            disabled={saving}
            className={`${btnSecondary} px-2.5 py-1 text-xs`}
          >
            Edit
          </button>
          <button type="button" onClick={() => setStatus('rejected')} disabled={saving} className={btnDanger}>
            Reject
          </button>
        </div>
      </div>

      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}

      <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <h3 className="text-xs font-semibold tracking-wide text-slate-400 uppercase">
            Original
          </h3>
          <p className="mt-1 max-h-72 overflow-y-auto text-xs whitespace-pre-wrap text-slate-600">
            {originalContent || 'Original content not found.'}
          </p>
        </div>

        <div>
          <h3 className="text-xs font-semibold tracking-wide text-slate-400 uppercase">
            Critique
          </h3>
          <p className="mt-1 max-h-72 overflow-y-auto text-xs whitespace-pre-wrap text-slate-600">
            {feedback.critique}
          </p>
        </div>

        <div>
          <h3 className="text-xs font-semibold tracking-wide text-slate-400 uppercase">
            Suggested Rewrite
          </h3>
          {isEditing ? (
            <div className="mt-1 space-y-2">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                disabled={saving}
                rows={12}
                className="w-full rounded-md border border-slate-300 px-2 py-1.5 font-mono text-xs focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleSaveEdit}
                  disabled={saving}
                  className="flex items-center gap-1.5 rounded-md bg-indigo-600 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {saving && <Spinner className="border-indigo-300 border-t-white" />}
                  {saving ? 'Saving…' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  disabled={saving}
                  className={`${btnSecondary} px-3 py-1 text-xs`}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <p className="mt-1 max-h-72 overflow-y-auto text-xs whitespace-pre-wrap text-slate-600">
              {feedback.suggested_rewrite || '—'}
            </p>
          )}
        </div>
      </div>
    </section>
  )
}
