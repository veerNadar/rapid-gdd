import { type KeyboardEvent, useState } from 'react'

interface TagInputProps {
  value: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
  max?: number
  id?: string
}

/** A small chip/tag input: type a value and press Enter or "," to add it,
 * Backspace on an empty field removes the last tag. Used for reference
 * games and target platforms. */
export default function TagInput({ value, onChange, placeholder, max, id }: TagInputProps) {
  const [draft, setDraft] = useState('')
  const atMax = max !== undefined && value.length >= max

  function addTag() {
    const tag = draft.trim()
    if (!tag || atMax) {
      setDraft('')
      return
    }
    if (!value.includes(tag)) {
      onChange([...value, tag])
    }
    setDraft('')
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault()
      addTag()
    } else if (event.key === 'Backspace' && !draft && value.length > 0) {
      onChange(value.slice(0, -1))
    }
  }

  return (
    <div className="mt-1 flex flex-wrap items-center gap-2 rounded-md border border-slate-300 px-2 py-1.5 focus-within:border-slate-500">
      {value.map((tag) => (
        <span
          key={tag}
          className="flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700"
        >
          {tag}
          <button
            type="button"
            onClick={() => onChange(value.filter((t) => t !== tag))}
            className="text-slate-400 hover:text-slate-700"
            aria-label={`Remove ${tag}`}
          >
            ×
          </button>
        </span>
      ))}
      {!atMax && (
        <input
          id={id}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={addTag}
          placeholder={value.length === 0 ? placeholder : ''}
          className="min-w-[8ch] flex-1 border-0 py-1 text-sm focus:outline-none"
        />
      )}
    </div>
  )
}
