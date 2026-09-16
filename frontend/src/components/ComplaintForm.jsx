import { useDispatch, useSelector } from 'react-redux'
import { BookMarked, CheckCircle2, ClipboardList, LoaderCircle, Sparkles } from 'lucide-react'
import ComplaintSection from './ComplaintSection'
import FieldDisplay from './FieldDisplay'
import RiskAssessment from './RiskAssessment'
import {
  setLedgerError,
  setLedgerSaved,
  setSavingToLedger,
} from '../store/complaintSlice'
import { getFriendlyApiError, saveComplaintToLedger } from '../services/api'

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const {
    complaint,
    complaintId,
    riskAssessment,
    ledgerStatus,
    savingToLedger,
    ledgerError,
    ledgerMessage,
  } = useSelector((state) => state.complaint)

  const canSave =
    Boolean(complaintId) &&
    !savingToLedger &&
    ledgerStatus !== 'saved'

  const buttonLabel =
    ledgerStatus === 'saving'
      ? 'Saving...'
      : ledgerStatus === 'saved'
        ? 'Saved to QMS Ledger'
        : ledgerStatus === 'unsaved_changes'
          ? 'Save Updates to QMS Ledger'
          : 'Save to QMS Ledger'

  async function handleSaveToLedger() {
    if (!complaintId || savingToLedger) {
      return
    }

    dispatch(setSavingToLedger(true))
    try {
      const result = await saveComplaintToLedger(
        complaintId,
        riskAssessment?.recommended_next_action || complaint?.recommended_next_action,
      )
      dispatch(
        setLedgerSaved({
          complaint: result.complaint,
          message: result.message || 'Complaint saved to QMS Ledger.',
        }),
      )
    } catch (error) {
      dispatch(
        setLedgerError(
          getFriendlyApiError(error) || 'Unable to save complaint to QMS Ledger.',
        ),
      )
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex shrink-0 items-start justify-between gap-3 border-b border-slate-200 px-5 py-3">
        <div>
          <div className="flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-teal-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-slate-900">
              Customer Complaint Form
            </h2>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Structured fields are populated by the AI Copilot — not filled manually.
          </p>
        </div>
        <div className="inline-flex items-center gap-1.5 rounded-md bg-teal-50 px-2.5 py-1 text-xs font-medium text-teal-800">
          <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          AI-driven
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-6 overflow-y-auto px-5 py-5">
        {complaintId ? (
          <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-xs text-slate-600">
            Complaint ID: {complaintId}
          </p>
        ) : (
          <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-3 py-2 text-sm text-slate-500">
            No complaint loaded yet. Describe an issue in the AI Copilot to begin.
          </p>
        )}

        <ComplaintSection title="1. Origin & Customer Details">
          <FieldDisplay label="Complaint Source" value={complaint?.complaint_source} />
          <FieldDisplay label="Customer Name" value={complaint?.customer_name} />
        </ComplaintSection>

        <ComplaintSection title="2. Product & Batch Identification">
          <FieldDisplay label="Product Name" value={complaint?.product_name} />
          <FieldDisplay
            label="Product Strength / Grade"
            value={complaint?.product_strength_grade}
          />
          <FieldDisplay label="Batch / Lot Number" value={complaint?.batch_lot_number} />
          <FieldDisplay label="Affected Quantity" value={complaint?.affected_quantity} />
          <FieldDisplay label="Manufacturing Date" value={complaint?.manufacturing_date} />
          <FieldDisplay label="Expiry Date" value={complaint?.expiry_date} />
        </ComplaintSection>

        <ComplaintSection title="3. Complaint Details">
          <FieldDisplay label="Complaint Type" value={complaint?.complaint_type} />
          <FieldDisplay label="Complaint Date" value={complaint?.complaint_date} />
          <div className="sm:col-span-2">
            <FieldDisplay
              label="Detailed Complaint Description"
              value={complaint?.detailed_complaint_description}
              multiline
            />
          </div>
        </ComplaintSection>

        <ComplaintSection title="4. Initial Assessment & Priority">
          <FieldDisplay label="Initial Severity" value={complaint?.initial_severity} />
          <FieldDisplay label="Priority" value={complaint?.priority} />
        </ComplaintSection>

        <RiskAssessment />

        <div className="border-t border-slate-200 pt-4">
          <div className="flex flex-wrap items-center gap-4">
            <button
              type="button"
              disabled={!canSave}
              onClick={handleSaveToLedger}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-teal-700 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
            >
              {savingToLedger ? (
                <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
              ) : ledgerStatus === 'saved' ? (
                <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
              ) : (
                <BookMarked className="h-4 w-4" aria-hidden="true" />
              )}
              {buttonLabel}
            </button>

            {ledgerMessage && ledgerStatus === 'saved' && (
              <p className="inline-flex items-center gap-1.5 text-xs text-emerald-700">
                <CheckCircle2 className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                {ledgerMessage}
              </p>
            )}
          </div>

          {ledgerStatus === 'unsaved_changes' && (
            <p className="mt-2 text-xs text-amber-700">
              Complaint changed after the last ledger save. Save again to update PostgreSQL.
            </p>
          )}

          {ledgerError && (
            <p className="mt-2 text-xs text-red-700">{ledgerError}</p>
          )}
        </div>
      </div>
    </div>
  )
}
