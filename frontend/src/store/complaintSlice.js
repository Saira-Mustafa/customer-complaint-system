import { createSlice } from '@reduxjs/toolkit'

const initialMessages = [
  {
    id: 'welcome',
    role: 'assistant',
    content:
      'Hello. I can help you log or update a customer complaint. Describe the complaint or upload a complaint document.',
  },
]

const initialState = {
  complaint: null,
  complaintId: null,
  riskAssessment: null,
  messages: initialMessages,
  loading: false,
  uploading: false,
  error: null,
  ledgerStatus: 'not_saved', // not_saved | saving | saved | unsaved_changes | error
  savingToLedger: false,
  ledgerError: null,
  ledgerMessage: null,
}

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    setComplaint(state, action) {
      const complaint = action.payload
      state.complaint = complaint
      state.complaintId = complaint?.id ?? state.complaintId
      if (state.ledgerStatus === 'saved') {
        state.ledgerStatus = 'unsaved_changes'
        state.ledgerMessage = null
      }
    },
    updateComplaint(state, action) {
      // Authoritative full complaint from the backend — do not shallow-merge fields.
      const complaint = action.payload
      state.complaint = complaint
      if (complaint?.id) {
        state.complaintId = complaint.id
      }
      if (state.ledgerStatus === 'saved') {
        state.ledgerStatus = 'unsaved_changes'
        state.ledgerMessage = null
      }
    },
    setRiskAssessment(state, action) {
      state.riskAssessment = action.payload
      if (state.ledgerStatus === 'saved') {
        state.ledgerStatus = 'unsaved_changes'
        state.ledgerMessage = null
      }
    },
    addMessage(state, action) {
      state.messages.push(action.payload)
    },
    setLoading(state, action) {
      state.loading = action.payload
    },
    setUploading(state, action) {
      state.uploading = action.payload
    },
    setError(state, action) {
      state.error = action.payload
    },
    setSavingToLedger(state, action) {
      state.savingToLedger = action.payload
      if (action.payload) {
        state.ledgerStatus = 'saving'
        state.ledgerError = null
      }
    },
    setLedgerSaved(state, action) {
      state.savingToLedger = false
      state.ledgerStatus = 'saved'
      state.ledgerError = null
      state.ledgerMessage =
        action.payload?.message || 'Complaint saved to QMS Ledger.'
      if (action.payload?.complaint) {
        state.complaint = action.payload.complaint
        state.complaintId = action.payload.complaint.id
      }
    },
    setLedgerError(state, action) {
      state.savingToLedger = false
      state.ledgerStatus = 'error'
      state.ledgerError = action.payload
      state.ledgerMessage = null
    },
    clearComplaint(state) {
      state.complaint = null
      state.complaintId = null
      state.riskAssessment = null
      state.error = null
      state.loading = false
      state.uploading = false
      state.messages = initialMessages
      state.ledgerStatus = 'not_saved'
      state.savingToLedger = false
      state.ledgerError = null
      state.ledgerMessage = null
    },
  },
})

export const {
  setComplaint,
  updateComplaint,
  setRiskAssessment,
  addMessage,
  setLoading,
  setUploading,
  setError,
  setSavingToLedger,
  setLedgerSaved,
  setLedgerError,
  clearComplaint,
} = complaintSlice.actions

export default complaintSlice.reducer
