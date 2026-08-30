import { type FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject } from '../api/client'

export default function Home() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [genre, setGenre] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const project = await createProject({
        title,
        intake_data: { genre },
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-12">
      <h1 className="text-2xl font-semibold text-slate-900">New Project</h1>
      <p className="mt-1 text-sm text-slate-500">
        Answer a few questions and Rapid GDD will scaffold your game design document.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-slate-700">
            Project title
          </label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Hollow Spire"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </div>

        <div>
          <label htmlFor="genre" className="block text-sm font-medium text-slate-700">
            Genre
          </label>
          <input
            id="genre"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g. metroidvania"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          />
        </div>

        {/* TODO: dimension, perspective, multiplayer, core hook, scope/team
            size, target platform, reference games, target feeling */}
        <p className="text-xs text-slate-400">
          More intake fields (dimension, perspective, scope, references, target
          feeling…) go here.
        </p>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting || !title}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
        >
          {submitting ? 'Creating…' : 'Create Project'}
        </button>
      </form>
    </div>
  )
}
