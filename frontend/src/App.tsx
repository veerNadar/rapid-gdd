import { Link, NavLink, Route, Routes } from 'react-router-dom'
import Landing from './pages/Landing'
import Metrics from './pages/Metrics'
import NewProject from './pages/NewProject'
import ProjectView from './pages/ProjectView'
import ReviewResults from './pages/ReviewResults'
import ReviewUpload from './pages/ReviewUpload'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm font-medium transition-colors ${
    isActive ? 'text-indigo-600' : 'text-slate-500 hover:text-slate-900'
  }`

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <nav className="mx-auto flex max-w-5xl items-center gap-6 px-4 py-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-600 text-xs font-bold text-white">
              R
            </span>
            <span className="text-sm font-semibold text-slate-900">Rapid GDD</span>
          </Link>
          <div className="flex flex-1 items-center gap-6">
            <NavLink to="/new" className={navLinkClass}>
              New Project
            </NavLink>
            <NavLink to="/admin/metrics" className={navLinkClass}>
              Metrics
            </NavLink>
          </div>
        </nav>
      </header>

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/new" element={<NewProject />} />
          <Route path="/projects/:projectId" element={<ProjectView />} />
          <Route path="/projects/:projectId/review" element={<ReviewUpload />} />
          <Route
            path="/projects/:projectId/reviews/:reviewId"
            element={<ReviewResults />}
          />
          <Route path="/admin/metrics" element={<Metrics />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-200 bg-white py-6">
        <p className="mx-auto max-w-5xl px-4 text-xs text-slate-400">
          Rapid GDD — AI-assisted game design documentation, powered by Gemini.
        </p>
      </footer>
    </div>
  )
}
