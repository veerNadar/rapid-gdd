import { Link } from 'react-router-dom'
import { btnPrimary, card } from '../styles'

const FEATURES = [
  {
    title: 'Answer a few questions',
    body: 'Genre, perspective, scope, reference games, and the one hook that makes your game worth playing. Five minutes, not a blank page.',
  },
  {
    title: 'Get a structured GDD',
    body: "Gemini drafts all seven sections — Overview, Mechanics, Story, Characters, World, Progression, and more — consistent with each other, not seven disconnected pages.",
  },
  {
    title: 'Review, edit, iterate',
    body: 'Regenerate any section, edit inline, or upload a GDD you already wrote and get section-by-section critique with suggested rewrites you accept, edit, or reject.',
  },
]

export default function Landing() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-16 sm:py-24">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-sm font-semibold text-indigo-600">For indie & solo developers</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
          Design the game.
          <br />
          Let AI handle the document.
        </h1>
        <p className="mt-5 text-base text-slate-600 sm:text-lg">
          Rapid GDD turns a short intake into a structured, editable Game Design Document —
          and reviews the one you've already written. Spend your time on the design decisions
          that make your game good, not on formatting a doc nobody reads.
        </p>
        <div className="mt-8 flex justify-center">
          <Link to="/new" className={`${btnPrimary} px-6 py-3 text-base`}>
            Start a New Project →
          </Link>
        </div>
      </div>

      <div className="mt-20 grid grid-cols-1 gap-6 sm:grid-cols-3">
        {FEATURES.map((feature, i) => (
          <div key={feature.title} className={card}>
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-50 text-sm font-semibold text-indigo-600">
              {i + 1}
            </span>
            <h2 className="mt-3 text-sm font-semibold text-slate-900">{feature.title}</h2>
            <p className="mt-1.5 text-sm text-slate-600">{feature.body}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
