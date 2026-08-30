interface SpinnerProps {
  className?: string
}

export default function Spinner({ className = '' }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={`inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-600 ${className}`}
    />
  )
}
