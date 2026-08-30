import { type FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { describeApiError, getReview, listSections, promoteReview } from '../api/client'
import type { GDDSection, Review, ReviewSectionFeedback, SectionType } from '../api/types'
import ReviewFeedbackCard from '../components/ReviewFeedbackCard'
import SectionCardSkeleton from '../components/SectionCardSkeleton'
import Spinner from '../components/Spinner'
import { SECTION_LABELS } from '../sectionLabels'

export default function ReviewResults() {
  const { projectId, reviewId } = useParams<{ projectId: string; reviewId: string }>()
  const navigate = useNavigate()

  const [review, setReview] = useState<Review | null>(null)
  const [feedbackList, setFeedbackList] = useState<ReviewSectionFeedback[]>([])
  const [originalSections, setOriginalSections] = useState<Partial<Record<SectionType, GDDSection>>>(
    {},
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [promoteTitle, setPromoteTitle] = useState('')
  const [promoting, setPromoting] = useState(false)
  const [promoteError, setPromoteError] = useState<string | null>(null)

  useEffect(() => {
    if (!reviewId || !projectId) return
    Promise.all([getReview(reviewId), listSections(projectId)])
      .then(([reviewData, sections]) => {
        setReview(reviewData.review)
        setFeedbackList(reviewData.feedback)
        const byType: Partial<Record<SectionType, GDDSection>> = {}
        for (const section of sections) {
          byType[section.section_type] = section
        }
        setOriginalSections(byType)
      })
      .catch((err) => setError(describeApiError(err, 'Failed to load review')))
      .finally(() => setLoading(false))
  }, [reviewId, projectId])

  function handleFeedbackUpdate(updated: ReviewSectionFeedback) {
    setFeedbackList((prev) => prev.map((f) => (f.id === updated.id ? updated : f)))
  }

  const promotableCount = feedbackList.filter(
    (f) => f.status === 'accepted' || f.status === 'edited',
  ).length

  async function handlePromote(event: FormEvent) {
    event.preventDefault()
    if (!reviewId) return
    setPromoting(true)
    setPromoteError(null)
    try {
      const result = await promoteReview(reviewId, promoteTitle)
      navigate(`/projects/${result.project.id}`)
    } catch (err) {
      setPromoteError(describeApiError(err, 'Failed to create the new project.'))
    } finally {
      setPromoting(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">Review Results</h1>
      <p className="mt-1 text-sm text-slate-500">
        Accept, edit, or reject each section's suggested rewrite, then optionally promote your
        accepted changes into a new project.
      </p>
      {review && (
        <p className="mt-1 text-xs text-slate-400">
          Uploaded {new Date(review.created_at).toLocaleString()}
        </p>
      )}
      <Link
        to={`/projects/${projectId}`}
        className="mt-3 inline-block text-sm text-slate-500 underline hover:text-slate-900"
      >
        ← Back to project
      </Link>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <form
        onSubmit={handlePromote}
        className="mt-8 flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4"
      >
        <div className="flex-1">
          <label htmlFor="promoteTitle" className="block text-sm font-medium text-slate-700">
            Promote to a new project
          </label>
          <p className="mt-0.5 text-xs text-slate-500">
            {promotableCount === 0
              ? 'Accept or edit at least one section to enable this.'
              : `${promotableCount} section${promotableCount === 1 ? '' : 's'} ready to promote.`}
          </p>
          <input
            id="promoteTitle"
            value={promoteTitle}
            onChange={(e) => setPromoteTitle(e.target.value)}
            placeholder="New project title (optional)"
            disabled={promoting}
            className="mt-2 w-full max-w-sm rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none disabled:opacity-40"
          />
        </div>
        <button
          type="submit"
          disabled={promoting || promotableCount === 0}
          className="flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {promoting && <Spinner className="border-slate-500 border-t-white" />}
          {promoting ? 'Creating…' : 'Promote to New Project'}
        </button>
      </form>
      {promoteError && <p className="mt-2 text-sm text-red-600">{promoteError}</p>}

      <div className="mt-8 space-y-4">
        {loading ? (
          <>
            <SectionCardSkeleton />
            <SectionCardSkeleton />
          </>
        ) : feedbackList.length === 0 ? (
          <p className="text-sm text-slate-400 italic">No critique feedback for this review.</p>
        ) : (
          feedbackList.map((feedback) => (
            <ReviewFeedbackCard
              key={feedback.id}
              label={SECTION_LABELS[feedback.section_type]}
              originalContent={originalSections[feedback.section_type]?.content}
              feedback={feedback}
              onUpdate={handleFeedbackUpdate}
            />
          ))
        )}
      </div>
    </div>
  )
}
