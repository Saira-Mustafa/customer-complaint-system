import { Activity } from 'lucide-react'

export default function Header() {
  return (
    <header className="shrink-0 border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2 sm:px-6">
        <div className="min-w-0">
          <h1 className="text-base font-semibold tracking-tight text-slate-900 sm:text-lg">
            Customer Complaint Management System
          </h1>
          <p className="text-xs text-slate-500 sm:text-sm">
            AI-powered pharmaceutical complaint intake &amp; initial assessment
          </p>
        </div>

        <div className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-800 sm:text-sm">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
          </span>
          <Activity className="h-3.5 w-3.5" aria-hidden="true" />
          AI Copilot Online
        </div>
      </div>
    </header>
  )
}
