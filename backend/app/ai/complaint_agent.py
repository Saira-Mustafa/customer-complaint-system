"""LangGraph complaint agent with tool calling (log / edit)."""

from __future__ import annotations

import json
from typing import Optional
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from app.ai.llm import get_groq_llm
from app.ai.risk_assessment import generate_initial_risk_assessment
from app.ai.tools import COMPLAINT_TOOLS
from app.schemas.complaint import AgentComplaintResult, Complaint
from app.services import complaint_store

AGENT_SYSTEM_PROMPT = """
You are a pharmaceutical customer-complaint assistant.

You can take actions using tools:
1) log_complaint — create a NEW complaint
2) edit_complaint — update an EXISTING complaint by complaint_id

Rules:
- Decide which tool to call based on the user's intent. Do not rely on fixed keyword checks alone.
- If the user reports a new problem, call log_complaint.
- If the user corrects or updates an existing complaint, call edit_complaint.
- For edits you MUST have a real complaint_id. If no complaint_id is available, do NOT invent one.
  Ask the user to provide the complaint ID.
- Never invent pharmaceutical facts (batch numbers, quantities, manufacturing/expiry dates).
  Omit fields that are unknown.
- You may infer a reasonable complaint_type from the description.
- After tools run, briefly confirm what you did in natural language.
""".strip()


def _build_agent():
    llm = get_groq_llm(temperature=0)
    return create_react_agent(
        model=llm,
        tools=COMPLAINT_TOOLS,
        prompt=AGENT_SYSTEM_PROMPT,
    )


def _parse_tool_payload(content: str) -> Optional[dict]:
    try:
        data = json.loads(content)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def _final_assistant_text(messages: list) -> Optional[str]:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content and not message.tool_calls:
            content = message.content
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    else:
                        parts.append(str(item))
                return "\n".join(parts).strip() or None
            return str(content).strip() or None
    return None


def run_complaint_agent(
    message: str,
    complaint_id: Optional[UUID] = None,
) -> AgentComplaintResult:
    """Run the tool-calling complaint agent and return a structured API result."""
    agent = _build_agent()

    user_content = message
    if complaint_id is not None:
        user_content += (
            f"\n\n[System note: A complaint_id was provided with this request: {complaint_id}. "
            "If the user is correcting an existing complaint, use this ID with edit_complaint.]"
        )

    result = agent.invoke({"messages": [HumanMessage(content=user_content)]})
    messages = result.get("messages", [])

    tool_payloads: list[dict] = []
    for message_item in messages:
        if isinstance(message_item, ToolMessage):
            payload = _parse_tool_payload(message_item.content)
            if payload:
                tool_payloads.append(payload)

    assistant_text = _final_assistant_text(messages)

    # Prefer the last successful tool result
    success_payload = None
    clarification_payload = None
    for payload in tool_payloads:
        status = payload.get("status")
        if status == "success":
            success_payload = payload
        elif status in {"needs_clarification", "error"}:
            clarification_payload = payload

    if success_payload:
        action = success_payload.get("action")
        cid_raw = success_payload.get("complaint_id")
        complaint: Optional[Complaint] = None
        cid: Optional[UUID] = None

        if cid_raw:
            try:
                cid = UUID(str(cid_raw))
                complaint = complaint_store.get_complaint(cid)
            except ValueError:
                cid = None

        risk = None
        if complaint is not None:
            risk = generate_initial_risk_assessment(complaint)
            # Reload after severity/priority were saved
            complaint = complaint_store.get_complaint(complaint.id)

        return AgentComplaintResult(
            action=action,
            complaint_id=cid,
            complaint=complaint,
            risk_assessment=risk,
            clarification=None,
            assistant_message=assistant_text,
        )

    clarification_text = None
    if clarification_payload:
        clarification_text = clarification_payload.get("message")
    elif assistant_text:
        # Model asked for info without calling a tool (e.g. missing complaint ID)
        clarification_text = assistant_text
    else:
        clarification_text = (
            "I could not complete the request. "
            "If you want to edit a complaint, please provide the complaint ID. "
            "If you want to log a new complaint, please describe the issue."
        )

    return AgentComplaintResult(
        action="clarification",
        complaint_id=None,
        complaint=None,
        risk_assessment=None,
        clarification=clarification_text,
        assistant_message=assistant_text,
    )
