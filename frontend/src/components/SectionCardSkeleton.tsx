/** Placeholder shown in place of a SectionCard while a project's
 * sections are first loading. */
export default function SectionCardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg border border-slate-200 p-4">
      <div className="flex items-center justify-between">
        <div className="h-4 w-40 rounded bg-slate-200" />
        <div className="h-6 w-24 rounded bg-slate-100" />
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 w-full rounded bg-slate-100" />
        <div className="h-3 w-11/12 rounded bg-slate-100" />
        <div className="h-3 w-3/4 rounded bg-slate-100" />
      </div>
    </div>
  )
}
