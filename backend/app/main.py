# Customer Complaint System — Backend

from uuid import UUID

from fastapi import FastAPI, File, HTTPException, UploadFile

from app.ai.complaint_agent import run_complaint_agent
from app.ai.document_extractor import run_document_complaint_pipeline
from app.schemas.complaint import (
    AIComplaintRequest,
    AIComplaintResponse,
    Complaint,
    ComplaintCreate,
    ComplaintUpdate,
    DocumentComplaintResponse,
)
from app.services import complaint_store
from app.services.pdf_extractor import PdfExtractionError, extract_text_from_pdf

app = FastAPI(
    title="Customer Complaint System",
    description="AI-powered Customer Complaint Management System for pharmaceutical manufacturing.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Customer Complaint System API is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/complaints", response_model=list[Complaint])
def list_complaints():
    """Return all stored complaints (empty list until some are created)."""
    return complaint_store.list_complaints()


@app.post("/complaints", response_model=Complaint)
def create_complaint(complaint: ComplaintCreate):
    """Accept a complaint JSON body, store it in memory, and return it."""
    return complaint_store.create_complaint(complaint)


@app.patch("/complaints/{complaint_id}", response_model=Complaint)
def update_complaint(complaint_id: UUID, updates: ComplaintUpdate):
    """Update only the fields provided in the request body."""
    try:
        return complaint_store.update_complaint(complaint_id, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail="Complaint not found") from None


@app.post("/ai/complaint", response_model=AIComplaintResponse)
def ai_complaint_agent(request: AIComplaintRequest):
    """Run the complaint agent (log or edit via LangGraph tools)."""
    try:
        result = run_complaint_agent(
            message=request.message,
            complaint_id=request.complaint_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI agent failed: {exc}",
        ) from exc

    return AIComplaintResponse(
        message=request.message,
        action=result.action,
        complaint_id=result.complaint_id,
        complaint=result.complaint,
        risk_assessment=result.risk_assessment,
        clarification=result.clarification,
        assistant_message=result.assistant_message,
    )


@app.post("/ai/complaint/document", response_model=DocumentComplaintResponse)
async def ai_complaint_from_document(file: UploadFile = File(...)):
    """Upload a PDF, extract text, structure fields with AI, and log the complaint."""
    filename = file.filename or "upload.pdf"
    content_type = (file.content_type or "").lower()

    if not filename.lower().endswith(".pdf") and content_type not in {
        "application/pdf",
        "application/x-pdf",
    }:
        raise HTTPException(
            status_code=400,
            detail="Only PDF uploads are supported. Please upload a .pdf file.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        pdf_text = extract_text_from_pdf(file_bytes)
    except PdfExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        result = run_document_complaint_pipeline(pdf_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Document AI extraction failed: {exc}",
        ) from exc

    return DocumentComplaintResponse(
        action=result.action,
        complaint_id=result.complaint_id,
        complaint=result.complaint,
        risk_assessment=result.risk_assessment,
        filename=filename,
        extracted_text=result.extracted_text,
        extracted_complaint=result.extracted_complaint,
    )
