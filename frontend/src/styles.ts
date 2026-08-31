// Shared Tailwind class strings so buttons, inputs, and cards look the
// same everywhere rather than being redefined ad hoc per page.

export const inputClass =
  'mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500'

export const labelClass = 'block text-sm font-medium text-slate-700'

export const btnPrimary =
  'inline-flex items-center justify-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40'

export const btnSecondary =
  'inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'

export const btnDanger =
  'inline-flex items-center justify-center gap-2 rounded-md border border-red-300 bg-white px-2.5 py-1 text-xs font-medium text-red-700 transition-colors hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-40'

export const btnSuccess =
  'inline-flex items-center justify-center gap-2 rounded-md border border-emerald-300 bg-white px-2.5 py-1 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-40'

export const card = 'rounded-lg border border-slate-200 bg-white p-4 shadow-sm'
