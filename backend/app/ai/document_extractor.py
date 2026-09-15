"""LangGraph workflow: extract complaint fields from PDF document text."""

from __future__ import annotations

from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.ai.llm import get_groq_llm
from app.ai.risk_assessment import generate_initial_risk_assessment
from app.ai.tools import log_complaint_from_extraction
from app.schemas.complaint import (
    Complaint,
    ComplaintExtraction,
    DocumentComplaintResult,
    InitialRiskAssessment,
)

DOCUMENT_EXTRACTION_PROMPT = """
You extract structured pharmaceutical customer-complaint information
from text that was taken from an uploaded PDF document.

Rules:
1. Only fill a field when the document text clearly contains that information.
2. If a value is not present, leave it as null. Do NOT invent or guess.
3. Do not invent batch numbers, quantities, manufacturing dates, expiry dates,
   customer names, or product details.
4. You may infer a reasonable complaint_type from the described problem.
5. detailed_complaint_description should summarize the complaint text that appears
   in the document.
6. Dates must use ISO format YYYY-MM-DD when present.
""".strip()


class DocumentGraphState(TypedDict):
    """State for the document extraction LangGraph workflow."""

    pdf_text: str
    extracted_complaint: Optional[ComplaintExtraction]
    error: Optional[str]


def extract_from_document_node(state: DocumentGraphState) -> DocumentGraphState:
    """AI node: send PDF text to Groq and fill ComplaintExtraction fields."""
    llm = get_groq_llm(temperature=0)
    structured_llm = llm.with_structured_output(ComplaintExtraction)

    result = structured_llm.invoke(
        [
            SystemMessage(content=DOCUMENT_EXTRACTION_PROMPT),
            HumanMessage(
                content=(
                    "Extract complaint fields from this PDF text. "
                    "Leave unknown fields null.\n\n"
                    f"{state['pdf_text']}"
                )
            ),
        ]
    )

    if isinstance(result, ComplaintExtraction):
        extracted = result
    else:
        extracted = ComplaintExtraction.model_validate(result)

    return {
        "pdf_text": state["pdf_text"],
        "extracted_complaint": extracted,
        "error": None,
    }


def build_document_extraction_graph():
    """Build: PDF text → AI extraction → structured complaint fields."""
    graph = StateGraph(DocumentGraphState)
    graph.add_node("extract_from_document", extract_from_document_node)
    graph.add_edge(START, "extract_from_document")
    graph.add_edge("extract_from_document", END)
    return graph.compile()


document_extraction_graph = build_document_extraction_graph()


def run_document_complaint_pipeline(pdf_text: str) -> DocumentComplaintResult:
    """Extract structured fields from PDF text, log the complaint, assess risk."""
    final_state = document_extraction_graph.invoke(
        {
            "pdf_text": pdf_text,
            "extracted_complaint": None,
            "error": None,
        }
    )

    extracted = final_state.get("extracted_complaint")
    if extracted is None:
        raise RuntimeError("Document AI workflow finished without an extraction result.")

    if not isinstance(extracted, ComplaintExtraction):
        extracted = ComplaintExtraction.model_validate(extracted)

    complaint: Complaint = log_complaint_from_extraction(extracted)
    risk: InitialRiskAssessment = generate_initial_risk_assessment(complaint)
    # Reload after severity/priority were saved by risk assessment
    from app.services import complaint_store

    refreshed = complaint_store.get_complaint(complaint.id) or complaint

    return DocumentComplaintResult(
        action="document_extraction",
        complaint_id=refreshed.id,
        complaint=refreshed,
        risk_assessment=risk,
        extracted_text=pdf_text,
        extracted_complaint=extracted,
    )
