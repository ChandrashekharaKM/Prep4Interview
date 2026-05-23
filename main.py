"""
main.py
FastAPI application for HR-Copilot.
Exposes REST endpoints consumed by the Streamlit frontend.
"""

import os
import uuid
import logging
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Set up logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Monkey Patch Gemini API to automatically retry on 429 Quota/Rate Limit Errors
# ---------------------------------------------------------------------------
def patch_gemini_with_retry():
    try:
        import google.generativeai as genai
        from google.api_core.exceptions import ResourceExhausted

        orig_generate_content = genai.GenerativeModel.generate_content
        orig_send_message = genai.ChatSession.send_message

        def retry_on_429(func, *args, **kwargs):
            max_retries = 3
            delay = 2.0
            backoff = 2.0
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Detect 429 / resource exhausted / quota exceeded / rate limit errors
                    is_429 = isinstance(e, ResourceExhausted) or "429" in str(e) or "quota" in str(e).lower() or "limit" in str(e).lower()
                    if is_429 and attempt < max_retries:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"Gemini API rate limit hit (429/quota). Retrying in {wait_time:.1f}s "
                            f"(Attempt {attempt+1}/{max_retries}). Error: {e}"
                        )
                        time.sleep(wait_time)
                    else:
                        raise e

        def patched_generate_content(self, *args, **kwargs):
            return retry_on_429(orig_generate_content, self, *args, **kwargs)

        def patched_send_message(self, *args, **kwargs):
            return retry_on_429(orig_send_message, self, *args, **kwargs)

        genai.GenerativeModel.generate_content = patched_generate_content
        genai.ChatSession.send_message = patched_send_message
        logger.info("Successfully monkey-patched google.generativeai for automatic 429 rate limit retries.")
    except Exception as patch_err:
        logger.error(f"Failed to monkey-patch google.generativeai: {patch_err}")

patch_gemini_with_retry()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from graph.agent import hr_graph
from graph.state import initial_state, AgentState
from tools.mock_interview import MockInterviewSimulator
from tools.streaming_agent import StreamingAgent


app = FastAPI(title="HR-Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class MockTurnRequest(BaseModel):
    resume_text: str
    interview_type: str
    persona: str
    history: list[dict]
    max_questions: int = 3
    api_key: Optional[str] = None

class MockScorecardRequest(BaseModel):
    resume_text: str
    target_role: str
    history: list[dict]
    api_key: Optional[str] = None

class RunRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: str = "anonymous"
    user_input: str
    uploaded_file_path: Optional[str] = None
    older_resume_text: Optional[str] = None
    api_key: Optional[str] = None


class ChatStreamRequest(BaseModel):
    session_id: str
    user_input: str
    uploaded_file_path: Optional[str] = None
    api_key: Optional[str] = None


class ReviewRequest(BaseModel):
    session_id: str
    decision: str          # "approved" | "edited" | "rejected"
    edited_output: Optional[str] = None
    reject_reason: Optional[str] = None


class RunResponse(BaseModel):
    session_id: str
    tool: Optional[str]
    confidence: float
    clarification_needed: bool
    clarification_question: Optional[str]
    draft_output: Optional[str]
    citations: Optional[list[str]]
    structured_output: Optional[dict]
    error: Optional[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

_mock_simulator = MockInterviewSimulator()
_streaming_agent = StreamingAgent()

@app.post("/mock_interview/next_stream")
def mock_interview_next_stream(req: MockTurnRequest):
    """Generate the next question/feedback for the mock interview simulator as a stream."""
    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    try:
        def event_generator():
            for chunk in _mock_simulator.get_next_turn_stream(
                resume_text=req.resume_text,
                interview_type=req.interview_type,
                persona=req.persona,
                history=req.history,
                max_questions=req.max_questions
            ):
                yield chunk
        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        logger.exception("Error in /mock_interview/next_stream")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
def chat_stream(req: ChatStreamRequest):
    """Generate the next career coach response as a stream."""
    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    try:
        def event_generator():
            for chunk in _streaming_agent.stream_chat(
                session_id=req.session_id,
                user_input=req.user_input,
                uploaded_file_path=req.uploaded_file_path
            ):
                yield chunk
        return StreamingResponse(event_generator(), media_type="text/plain")
    except Exception as e:
        logger.exception("Error in /chat/stream")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mock_interview/next")
def mock_interview_next(req: MockTurnRequest):
    """Generate the next question/feedback for the mock interview simulator."""
    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    try:
        output = _mock_simulator.get_next_turn(
            resume_text=req.resume_text,
            interview_type=req.interview_type,
            persona=req.persona,
            history=req.history,
            max_questions=req.max_questions
        )
        return {"output": output}
    except Exception as e:
        logger.exception("Error in /mock_interview/next")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mock_interview/scorecard")
def mock_interview_scorecard(req: MockScorecardRequest):
    """Generate the final evaluation scorecard for the mock interview session."""
    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
    try:
        scorecard = _mock_simulator.generate_scorecard(
            resume_text=req.resume_text,
            target_role=req.target_role,
            history=req.history
        )
        return scorecard
    except Exception as e:
        logger.exception("Error in /mock_interview/scorecard")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def run_agent(req: RunRequest):
    """
    Main endpoint. Runs the LangGraph agent for a given user input.
    Returns the draft output and metadata for the review gate.
    """
    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

    session_id = req.session_id or str(uuid.uuid4())

    state = initial_state(
        session_id=session_id,
        user_id=req.user_id,
        raw_input=req.user_input,
        uploaded_file_path=req.uploaded_file_path,
        older_resume_text=req.older_resume_text,
    )

    try:
        result: AgentState = hr_graph.invoke(state)
    except Exception as exc:
        logger.exception("Graph invocation failed")
        raise HTTPException(status_code=500, detail=str(exc))

    return RunResponse(
        session_id=session_id,
        tool=result.get("tool"),
        confidence=result.get("confidence", 0.0),
        clarification_needed=result.get("clarification_needed", False),
        clarification_question=result.get("clarification_question"),
        draft_output=result.get("draft_output"),
        citations=result.get("citations"),
        structured_output=result.get("structured_output"),
        error=result.get("error"),
    )


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF or XLSX document and extract text if PDF."""
    allowed_extensions = {".pdf", ".xlsx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only PDF and XLSX files are supported.")

    dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()
    dest.write_bytes(content)
    logger.info("Uploaded file saved to %s", dest)

    extracted_text = ""
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(dest)
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            extracted_text = "\n\n".join(pages)
            logger.info("Extracted %d characters from PDF resume", len(extracted_text))
        except Exception as e:
            logger.error("Failed to extract text from uploaded PDF: %s", e)

    return {
        "file_path": str(dest),
        "filename": file.filename,
        "extracted_text": extracted_text
    }


@app.post("/review")
def submit_review(req: ReviewRequest):
    """
    Record the HR staff review decision.
    In production this would update a database record.
    Here it logs to the audit trail.
    """
    import json
    from datetime import datetime

    record = {
        "ts": datetime.utcnow().isoformat(),
        "session_id": req.session_id,
        "decision": req.decision,
        "has_edit": bool(req.edited_output),
        "reject_reason": req.reject_reason,
    }

    log_path = Path(os.getenv("AUDIT_LOG_PATH", "./data/audit_log.jsonl"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    return {"status": "recorded", "decision": req.decision}


@app.get("/audit")
def get_audit_log(limit: int = 50):
    """Return the last N audit log entries."""
    import json
    log_path = Path(os.getenv("AUDIT_LOG_PATH", "./data/audit_log.jsonl"))
    if not log_path.exists():
        return {"entries": []}
    lines = log_path.read_text().strip().splitlines()
    entries = [json.loads(l) for l in lines[-limit:]]
    return {"entries": list(reversed(entries))}
