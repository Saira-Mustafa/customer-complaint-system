"""Initial AI risk assessment for logged/edited complaints."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.llm import get_groq_llm
from app.schemas.complaint import Complaint, ComplaintUpdate, InitialRiskAssessment
from app.services import complaint_store

RISK_SYSTEM_PROMPT = """
You provide an INITIAL AI-recommended risk assessment for a pharmaceutical
customer complaint.

This is NOT a final QA or regulatory decision. It is only a first suggestion
for human reviewers.

Guidance:
- Possible contamination, wrong product, labeling that could affect dosing,
  or patient-safety concerns → higher severity and priority.
- Minor packaging/cosmetic issues without safety impact → lower concern.
- Be conservative when uncertain, but do not invent facts not in the complaint.

Return:
- initial_severity (e.g. Low, Medium, High, Critical)
- priority (e.g. Low, Medium, High)
- recommended_next_action (short next step for QA/staff)
""".strip()


def generate_initial_risk_assessment(complaint: Complaint) -> InitialRiskAssessment:
    """Ask Groq for an initial risk assessment and save severity/priority on the complaint."""
    llm = get_groq_llm(temperature=0)
    structured = llm.with_structured_output(InitialRiskAssessment)

    complaint_text = complaint.model_dump_json()
    result = structured.invoke(
        [
            SystemMessage(content=RISK_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "Assess this complaint for an INITIAL AI recommendation only:\n"
                    f"{complaint_text}"
                )
            ),
        ]
    )

    if isinstance(result, InitialRiskAssessment):
        assessment = result
    else:
        assessment = InitialRiskAssessment.model_validate(result)

    # Ensure the disclaimer label stays clear
    assessment.label = (
        "AI-recommended initial assessment (not a final pharmaceutical QA decision)"
    )

    # Persist severity/priority onto the complaint record
    complaint_store.update_complaint(
        complaint.id,
        ComplaintUpdate(
            initial_severity=assessment.initial_severity,
            priority=assessment.priority,
        ),
    )

    return assessment
