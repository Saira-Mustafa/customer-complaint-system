export default function FieldDisplay({ label, value, multiline = false }) {
  const display =
    value === null || value === undefined || String(value).trim() === ''
      ? '—'
      : String(value)

  const isEmpty = display === '—'

  if (multiline) {
    return (
      <div className="space-y-1.5">
        <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">
          {label}
        </label>
        <textarea
          readOnly
          rows={4}
          value={display}
          className={`w-full resize-none rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none ${
            isEmpty ? 'text-slate-400 italic' : 'text-slate-800'
          }`}
        />
      </div>
    )
  }

  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </label>
      <input
        readOnly
        value={display}
        className={`w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none ${
          isEmpty ? 'text-slate-400 italic' : 'text-slate-800'
        }`}
      />
    </div>
  )
}
