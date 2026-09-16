import { ShieldAlert } from 'lucide-react'
import { useSelector } from 'react-redux'

export default function RiskAssessment() {
  const riskAssessment = useSelector((state) => state.complaint.riskAssessment)

  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50/70 p-4">
      <div className="mb-3 flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 text-amber-700" aria-hidden="true" />
        <h3 className="text-sm font-semibold text-amber-950">
          Initial AI Risk Assessment
        </h3>
      </div>

      {!riskAssessment ? (
        <p className="text-sm text-amber-900/70">No assessment available yet.</p>
      ) : (
        <div className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-800/70">
                Severity
              </p>
              <p className="mt-1 text-sm font-medium text-amber-950">
                {riskAssessment.initial_severity || '—'}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-amber-800/70">
                Priority
              </p>
              <p className="mt-1 text-sm font-medium text-amber-950">
                {riskAssessment.priority || '—'}
              </p>
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-amber-800/70">
              Recommended Next Action
            </p>
            <p className="mt-1 text-sm text-amber-950">
              {riskAssessment.recommended_next_action || '—'}
            </p>
          </div>

          <p className="rounded-md border border-amber-200 bg-white/70 px-2.5 py-2 text-xs text-amber-900">
            {riskAssessment.label ||
              'AI-recommended initial assessment — not a final pharmaceutical QA decision.'}
          </p>
        </div>
      )}
    </section>
  )
}
