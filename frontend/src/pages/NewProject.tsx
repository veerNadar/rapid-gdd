import { type FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject, describeApiError } from '../api/client'
import type { Dimension, MultiplayerMode, Perspective } from '../api/types'
import Spinner from '../components/Spinner'
import TagInput from '../components/TagInput'
import { btnPrimary, card, inputClass, labelClass } from '../styles'

const PERSPECTIVE_OPTIONS: { value: Perspective; label: string }[] = [
  { value: 'first_person', label: 'First-person' },
  { value: 'third_person', label: 'Third-person' },
  { value: 'top_down', label: 'Top-down' },
  { value: 'isometric', label: 'Isometric' },
  { value: 'side_scrolling', label: 'Side-scrolling' },
]

const FEELING_OPTIONS = [
  { value: 'cozy', label: 'Cozy' },
  { value: 'tense', label: 'Tense' },
  { value: 'competitive', label: 'Competitive' },
  { value: 'relaxing', label: 'Relaxing' },
  { value: 'chaotic', label: 'Chaotic' },
  { value: 'eerie', label: 'Eerie' },
  { value: 'other', label: 'Other…' },
]

export default function NewProject() {
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [genre, setGenre] = useState('')
  const [dimension, setDimension] = useState<Dimension | ''>('')
  const [perspective, setPerspective] = useState<Perspective | ''>('')
  const [multiplayer, setMultiplayer] = useState<MultiplayerMode | ''>('')
  const [coreHook, setCoreHook] = useState('')
  const [scopeTeamSize, setScopeTeamSize] = useState('')
  const [targetPlatform, setTargetPlatform] = useState<string[]>([])
  const [referenceGames, setReferenceGames] = useState<string[]>([])
  const [targetFeeling, setTargetFeeling] = useState('')
  const [targetFeelingOther, setTargetFeelingOther] = useState('')

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const referenceGamesValid = referenceGames.length >= 1 && referenceGames.length <= 3
  const feelingValid = targetFeeling !== 'other' || targetFeelingOther.trim() !== ''
  const canSubmit =
    title.trim() !== '' && coreHook.trim() !== '' && referenceGamesValid && feelingValid

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    setError(null)
    try {
      const project = await createProject({
        title,
        intake_data: {
          genre: genre || undefined,
          dimension: dimension || undefined,
          perspective: perspective || undefined,
          multiplayer: multiplayer || undefined,
          core_hook: coreHook,
          scope_team_size: scopeTeamSize || undefined,
          target_platform: targetPlatform,
          reference_games: referenceGames,
          target_feeling:
            targetFeeling === 'other' ? targetFeelingOther : targetFeeling || undefined,
        },
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(describeApiError(err, 'Failed to create project.'))
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

      <form onSubmit={handleSubmit} className={`${card} mt-8 space-y-6`}>
        <div>
          <label htmlFor="title" className={labelClass}>
            Project title
          </label>
          <input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Hollow Spire"
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="genre" className={labelClass}>
            Genre
          </label>
          <input
            id="genre"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            placeholder="e.g. metroidvania"
            className={inputClass}
          />
        </div>

        <fieldset>
          <legend className={labelClass}>Dimension</legend>
          <div className="mt-1 flex gap-4">
            {(['2D', '3D'] as const).map((option) => (
              <label key={option} className="flex items-center gap-1.5 text-sm text-slate-700">
                <input
                  type="radio"
                  name="dimension"
                  value={option}
                  checked={dimension === option}
                  onChange={() => setDimension(option)}
                  className="accent-indigo-600"
                />
                {option}
              </label>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="perspective" className={labelClass}>
            Perspective
          </label>
          <select
            id="perspective"
            value={perspective}
            onChange={(e) => setPerspective(e.target.value as Perspective)}
            className={inputClass}
          >
            <option value="">Select a perspective…</option>
            {PERSPECTIVE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <fieldset>
          <legend className={labelClass}>Players</legend>
          <div className="mt-1 flex gap-4">
            {(
              [
                { value: 'singleplayer', label: 'Single-player' },
                { value: 'multiplayer', label: 'Multiplayer' },
              ] as const
            ).map((option) => (
              <label
                key={option.value}
                className="flex items-center gap-1.5 text-sm text-slate-700"
              >
                <input
                  type="radio"
                  name="multiplayer"
                  value={option.value}
                  checked={multiplayer === option.value}
                  onChange={() => setMultiplayer(option.value)}
                  className="accent-indigo-600"
                />
                {option.label}
              </label>
            ))}
          </div>
        </fieldset>

        <div>
          <label htmlFor="coreHook" className={labelClass}>
            The Hook <span className="text-red-500">*</span>
          </label>
          <p className="mt-0.5 text-xs text-slate-400">
            One sentence: what makes someone keep playing this?
          </p>
          <textarea
            id="coreHook"
            value={coreHook}
            onChange={(e) => setCoreHook(e.target.value)}
            required
            rows={2}
            placeholder="e.g. you play as the dungeon, not the hero"
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="scope" className={labelClass}>
            Scope
          </label>
          <p className="mt-0.5 text-xs text-slate-400">
            Solo developer, or team size (e.g. "solo", "team of 4").
          </p>
          <input
            id="scope"
            value={scopeTeamSize}
            onChange={(e) => setScopeTeamSize(e.target.value)}
            placeholder="e.g. solo, 6 months"
            className={inputClass}
          />
        </div>

        <div>
          <label htmlFor="platforms" className={labelClass}>
            Target platform(s)
          </label>
          <TagInput
            id="platforms"
            value={targetPlatform}
            onChange={setTargetPlatform}
            placeholder="e.g. PC (Steam), Nintendo Switch…"
          />
        </div>

        <div>
          <label htmlFor="referenceGames" className={labelClass}>
            Reference games <span className="text-red-500">*</span>
          </label>
          <p className="mt-0.5 text-xs text-slate-400">1 to 3 games this is closest to.</p>
          <TagInput
            id="referenceGames"
            value={referenceGames}
            onChange={setReferenceGames}
            placeholder="e.g. Hollow Knight…"
            max={3}
          />
          {referenceGames.length > 0 && !referenceGamesValid && (
            <p className="mt-1 text-xs text-red-600">Add at least 1 game (up to 3).</p>
          )}
        </div>

        <div>
          <label htmlFor="targetFeeling" className={labelClass}>
            Target feeling
          </label>
          <select
            id="targetFeeling"
            value={targetFeeling}
            onChange={(e) => setTargetFeeling(e.target.value)}
            className={inputClass}
          >
            <option value="">Select a feeling…</option>
            {FEELING_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {targetFeeling === 'other' && (
            <input
              value={targetFeelingOther}
              onChange={(e) => setTargetFeelingOther(e.target.value)}
              placeholder="Describe the feeling…"
              className={`${inputClass} mt-2`}
            />
          )}
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button type="submit" disabled={submitting || !canSubmit} className={btnPrimary}>
          {submitting && <Spinner className="border-indigo-300 border-t-white" />}
          {submitting ? 'Creating…' : 'Create Project'}
        </button>
      </form>
    </div>
  )
}
