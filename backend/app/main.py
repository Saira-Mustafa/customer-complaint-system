# Customer Complaint System — Backend

from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.ai.complaint_agent import run_complaint_agent
from app.ai.document_extractor import run_document_complaint_pipeline
from app.db.session import get_db
from app.schemas.complaint import (
    AIComplaintRequest,
    AIComplaintResponse,
    Complaint,
    ComplaintCreate,
    ComplaintUpdate,
    DocumentComplaintResponse,
    LedgerSaveRequest,
    LedgerSaveResponse,
)
from app.services import complaint_store
from app.services.ledger_service import (
    get_ledger_complaint,
    list_ledger_complaints,
    save_complaint_to_ledger,
)
from app.services.pdf_extractor import PdfExtractionError, extract_text_from_pdf

app = FastAPI(
    title="Customer Complaint System",
    description="AI-powered Customer Complaint Management System for pharmaceutical manufacturing.",
    version="0.1.0",
)

# Allow the Vite frontend during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Customer Complaint System API is running."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/complaints", response_model=list[Complaint])
def list_complaints(db: Session = Depends(get_db)):
    """Return complaints saved to the QMS ledger (PostgreSQL)."""
    return list_ledger_complaints(db)


@app.get("/complaints/{complaint_id}", response_model=Complaint)
def get_complaint(complaint_id: UUID, db: Session = Depends(get_db)):
    """Return one ledger complaint, falling back to the in-memory working copy."""
    saved = get_ledger_complaint(db, complaint_id)
    if saved is not None:
        return saved
    working = complaint_store.get_complaint(complaint_id)
    if working is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return working


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


@app.post("/complaints/{complaint_id}/ledger", response_model=LedgerSaveResponse)
def save_to_qms_ledger(
    complaint_id: UUID,
    body: LedgerSaveRequest | None = None,
    db: Session = Depends(get_db),
):
    """Persist the current working complaint into the PostgreSQL QMS ledger."""
    try:
        return save_complaint_to_ledger(
            db,
            complaint_id,
            recommended_next_action=(body.recommended_next_action if body else None),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Complaint not found") from None
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to save complaint to QMS Ledger: {exc}",
        ) from exc


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
