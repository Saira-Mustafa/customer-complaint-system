"""LangGraph workflow: extract structured complaint fields from free text.

Kept for learning/reference. The main AI endpoint now uses the tool-calling agent.
"""

from __future__ import annotations

from typing import Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.ai.llm import get_groq_llm
from app.schemas.complaint import ComplaintExtraction

EXTRACTION_SYSTEM_PROMPT = """
You extract structured pharmaceutical customer-complaint information
from a short natural-language message.

Rules:
1. Only fill a field when the message clearly contains that information.
2. If a value is not present, leave it as null. Do NOT invent or guess.
3. Do not invent batch numbers, quantities, manufacturing dates, expiry dates,
   severity, or priority when they are not mentioned.
4. detailed_complaint_description should briefly capture what the user reported.
5. complaint_type should be a short label when you can reasonably infer one
   from the described problem (for example: "Product Quality", "Packaging Defect").
   If you cannot infer a type, leave it null.
""".strip()


class ComplaintGraphState(TypedDict):
    """Shared memory that flows through the LangGraph workflow."""

    message: str
    extracted_complaint: Optional[ComplaintExtraction]
    error: Optional[str]


def extract_complaint_node(state: ComplaintGraphState) -> ComplaintGraphState:
    """AI extraction node: call Groq and fill structured complaint fields."""
    llm = get_groq_llm()
    structured_llm = llm.with_structured_output(ComplaintExtraction)

    result = structured_llm.invoke(
        [
            SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=state["message"]),
        ]
    )

    if isinstance(result, ComplaintExtraction):
        extracted = result
    else:
        extracted = ComplaintExtraction.model_validate(result)

    return {
        "message": state["message"],
        "extracted_complaint": extracted,
        "error": None,
    }


def build_complaint_extraction_graph():
    """Build: Input → AI extraction node → Structured output."""
    graph = StateGraph(ComplaintGraphState)
    graph.add_node("extract_complaint", extract_complaint_node)
    graph.add_edge(START, "extract_complaint")
    graph.add_edge("extract_complaint", END)
    return graph.compile()


complaint_extraction_graph = build_complaint_extraction_graph()


def run_complaint_extraction(message: str) -> ComplaintExtraction:
    """Run the extraction-only LangGraph workflow."""
    final_state = complaint_extraction_graph.invoke(
        {
            "message": message,
            "extracted_complaint": None,
            "error": None,
        }
    )

    extracted = final_state.get("extracted_complaint")
    if extracted is None:
        raise RuntimeError("The AI workflow finished without producing an extraction result.")

    if isinstance(extracted, ComplaintExtraction):
        return extracted
    return ComplaintExtraction.model_validate(extracted)
