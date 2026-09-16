import { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Bot, LoaderCircle, Paperclip, Send } from 'lucide-react'
import ChatMessage from './ChatMessage'
import {
  addMessage,
  setError,
  setLoading,
  setRiskAssessment,
  setUploading,
  updateComplaint,
} from '../store/complaintSlice'
import {
  getFriendlyApiError,
  sendAIMessage,
  uploadComplaintDocument,
} from '../services/api'

function buildAssistantSummary(data, { fromDocument = false } = {}) {
  if (data.clarification && !data.complaint) {
    return data.clarification
  }

  if (data.assistant_message) {
    return data.assistant_message
  }

  if (fromDocument && data.complaint) {
    return 'Document processed successfully. I extracted the available complaint details, logged the complaint, and generated an initial risk assessment.'
  }

  if (data.action === 'edit_complaint' && data.complaint) {
    return 'Complaint updated successfully. I applied your corrections and refreshed the initial risk assessment.'
  }

  if (data.action === 'log_complaint' && data.complaint) {
    return 'Complaint logged successfully. I extracted the available product and complaint details and generated an initial risk assessment.'
  }

  if (data.action === 'document_extraction' && data.complaint) {
    return 'Document processed successfully. I extracted the available complaint details, logged the complaint, and generated an initial risk assessment.'
  }

  return 'I processed your request. Review the complaint form and risk assessment for details.'
}

export default function AICopilot() {
  const dispatch = useDispatch()
  const { messages, loading, uploading, error, complaintId } = useSelector(
    (state) => state.complaint,
  )

  const [draft, setDraft] = useState('')
  const [selectedFileName, setSelectedFileName] = useState('')
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, uploading])

  async function handleSend(event) {
    event.preventDefault()
    const message = draft.trim()
    if (!message || loading || uploading) {
      return
    }

    dispatch(setError(null))
    dispatch(addMessage({ id: crypto.randomUUID(), role: 'user', content: message }))
    setDraft('')
    dispatch(setLoading(true))

    try {
      const data = await sendAIMessage(message, complaintId)

      if (data.complaint) {
        // Use the backend complaint as the authoritative state (no client-side field merge).
        dispatch(updateComplaint(data.complaint))
      }

      if (data.risk_assessment) {
        dispatch(setRiskAssessment(data.risk_assessment))
      }

      dispatch(
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: buildAssistantSummary(data),
        }),
      )
    } catch (err) {
      const friendly = getFriendlyApiError(err)
      dispatch(setError(friendly))
      dispatch(
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: friendly,
        }),
      )
    } finally {
      dispatch(setLoading(false))
    }
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0]
    event.target.value = ''

    if (!file) {
      return
    }

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      const message = 'Only PDF files are supported. Please choose a .pdf document.'
      dispatch(setError(message))
      dispatch(
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: message,
        }),
      )
      return
    }

    setSelectedFileName(file.name)
    dispatch(setError(null))
    dispatch(
      addMessage({
        id: crypto.randomUUID(),
        role: 'user',
        content: `Uploaded document: ${file.name}`,
      }),
    )
    dispatch(setUploading(true))

    try {
      const data = await uploadComplaintDocument(file)

      if (data.complaint) {
        dispatch(updateComplaint(data.complaint))
      }

      if (data.risk_assessment) {
        dispatch(setRiskAssessment(data.risk_assessment))
      }

      dispatch(
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: buildAssistantSummary(data, { fromDocument: true }),
        }),
      )
    } catch (err) {
      const friendly = getFriendlyApiError(err)
      dispatch(setError(friendly))
      dispatch(
        addMessage({
          id: crypto.randomUUID(),
          role: 'assistant',
          content: friendly,
        }),
      )
    } finally {
      dispatch(setUploading(false))
    }
  }

  const busy = loading || uploading

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="shrink-0 border-b border-slate-200 px-5 py-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-teal-700" aria-hidden="true" />
          <h2 className="text-lg font-semibold text-slate-900">AI Copilot</h2>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Describe a complaint, update an existing complaint, or upload a complaint document.
        </p>
      </div>

      {/* Scrollable conversation only — composer stays outside this region */}
      <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
        <div className="space-y-3 rounded-lg border border-slate-100 bg-slate-50/60 p-3">
          {messages.map((message) => (
            <ChatMessage key={message.id} role={message.role} content={message.content} />
          ))}

          {(loading || uploading) && (
            <div className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600">
              <LoaderCircle className="h-4 w-4 animate-spin text-teal-700" aria-hidden="true" />
              {uploading ? 'Extracting complaint...' : 'AI is processing...'}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Fixed composer at bottom of the chat panel */}
      <div className="shrink-0 border-t border-slate-200 bg-white px-5 py-3">
        {error && (
          <div className="mb-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSend}>
          <div className="flex min-w-0 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-2 py-1.5 focus-within:border-teal-600 focus-within:ring-2 focus-within:ring-teal-100">
            <button
              type="button"
              aria-label="Attach complaint document"
              disabled={busy}
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Paperclip className="h-4 w-4" aria-hidden="true" />
            </button>

            <input
              type="text"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Describe the customer complaint..."
              disabled={busy}
              className="min-w-0 flex-1 border-0 bg-transparent px-1 py-1.5 text-sm text-slate-800 outline-none placeholder:text-slate-400 disabled:bg-transparent"
            />

            <button
              type="submit"
              disabled={busy || !draft.trim()}
              aria-label={busy ? 'Processing' : 'Send'}
              className="inline-flex h-9 min-w-[4.5rem] shrink-0 items-center justify-center gap-1.5 rounded-md bg-teal-700 px-3 text-sm font-medium text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            >
              {busy ? (
                <LoaderCircle className="h-4 w-4 animate-spin" aria-hidden="true" />
              ) : (
                <>
                  <Send className="h-4 w-4" aria-hidden="true" />
                  Send
                </>
              )}
            </button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={handleFileChange}
          />

          {selectedFileName && uploading && (
            <p className="mt-1.5 truncate text-xs text-slate-500">
              Extracting: {selectedFileName}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
