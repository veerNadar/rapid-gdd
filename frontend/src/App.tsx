import { Link, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import ProjectView from './pages/ProjectView'
import ReviewResults from './pages/ReviewResults'
import ReviewUpload from './pages/ReviewUpload'

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <header className="border-b border-slate-200">
        <nav className="mx-auto flex max-w-3xl items-center gap-6 px-4 py-4">
          <Link to="/" className="text-sm font-semibold text-slate-900">
            Rapid GDD
          </Link>
          <Link to="/" className="text-sm text-slate-500 hover:text-slate-900">
            New Project
          </Link>
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/projects/:projectId" element={<ProjectView />} />
        <Route path="/projects/:projectId/review" element={<ReviewUpload />} />
        <Route
          path="/projects/:projectId/reviews/:reviewId"
          element={<ReviewResults />}
        />
      </Routes>
    </div>
  )
}
