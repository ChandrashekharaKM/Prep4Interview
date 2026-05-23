"""
graph/state.py
Shared state schema for the LangGraph agent.
All nodes read from and write to this TypedDict.
"""

from typing import TypedDict, Optional, Literal, Any
from datetime import datetime


ToolName = Literal["resume_qa", "job_suitability", "interview_prep", "github_explainer", "resume_builder", "clarify"]

ReviewDecision = Literal["approved", "edited", "rejected", "pending"]


class AgentState(TypedDict):
    # --- Input ---
    session_id: str
    user_id: str
    raw_input: str
    uploaded_file_path: Optional[str]   # path to uploaded PDF if any
    older_resume_text: Optional[str]    # text content of older resume if direct input

    # --- Classification ---
    tool: Optional[ToolName]
    confidence: float
    clarification_needed: bool
    clarification_question: Optional[str]

    # --- Tool output ---
    draft_output: Optional[str]          # raw text draft
    structured_output: Optional[dict]    # JSON output from doc_summarizer
    citations: Optional[list[str]]       # sources from policy_qa

    # --- Review gate ---
    review_decision: ReviewDecision
    edited_output: Optional[str]         # HR staff's edited version
    reject_reason: Optional[str]

    # --- Metadata ---
    timestamp: str
    iteration: int                       # loop counter for safety
    error: Optional[str]


def initial_state(session_id: str, user_id: str, raw_input: str,
                  uploaded_file_path: Optional[str] = None,
                  older_resume_text: Optional[str] = None) -> AgentState:
    return AgentState(
        session_id=session_id,
        user_id=user_id,
        raw_input=raw_input,
        uploaded_file_path=uploaded_file_path,
        older_resume_text=older_resume_text,
        tool=None,
        confidence=0.0,
        clarification_needed=False,
        clarification_question=None,
        draft_output=None,
        structured_output=None,
        citations=None,
        review_decision="pending",
        edited_output=None,
        reject_reason=None,
        timestamp=datetime.utcnow().isoformat(),
        iteration=0,
        error=None,
    )
