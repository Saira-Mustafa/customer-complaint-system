import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

/**
 * POST /ai/complaint
 * Backend expects: { message, complaint_id? }
 */
export async function sendAIMessage(message, complaintId) {
  const payload = { message }
  if (complaintId) {
    payload.complaint_id = complaintId
  }
  const response = await api.post('/ai/complaint', payload)
  return response.data
}

/**
 * POST /ai/complaint/document
 * Backend expects multipart field name: file
 */
export async function uploadComplaintDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  // Do not set Content-Type manually — the browser adds the multipart boundary.
  const response = await api.post('/ai/complaint/document', formData)
  return response.data
}

/** GET /complaints */
export async function getComplaints() {
  const response = await api.get('/complaints')
  return response.data
}

/** GET /complaints — find one by id from the ledger list */
export async function getComplaint(id) {
  try {
    const response = await api.get(`/complaints/${id}`)
    return response.data
  } catch {
    const complaints = await getComplaints()
    return complaints.find((item) => item.id === id) ?? null
  }
}

/**
 * POST /complaints/{complaintId}/ledger
 * Persist the working complaint into PostgreSQL QMS ledger.
 */
export async function saveComplaintToLedger(complaintId, recommendedNextAction) {
  const payload = {}
  if (recommendedNextAction) {
    payload.recommended_next_action = recommendedNextAction
  }
  const response = await api.post(`/complaints/${complaintId}/ledger`, payload)
  return response.data
}

export function getFriendlyApiError(error) {
  if (!error.response) {
    return 'Unable to connect to the backend. Make sure the FastAPI server is running.'
  }

  const detail = error.response.data?.detail
  if (typeof detail === 'string') {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(' ')
  }

  return 'Something went wrong while talking to the AI service. Please try again.'
}

export default api
