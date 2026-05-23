"""
graph/nodes.py
Individual node functions for the LangGraph state machine.
Each node receives AgentState and returns a partial update dict.
"""

import json
import os
import logging
import re
from typing import Any

import google.generativeai as genai

from graph.state import AgentState, ToolName
from memory.session_store import SessionStore
from tools.github_explainer import GitHubExplainer
from tools.resume_analyzer import ResumeAnalyzer

logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# Using gemini-2.5-flash as supported by the API key and service
_model = genai.GenerativeModel("gemini-2.5-flash")
_session_store = SessionStore()
_github_explainer = GitHubExplainer()
_resume_analyzer = ResumeAnalyzer()

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))
MAX_ITERATIONS = 5

# ---------------------------------------------------------------------------
# Helper: PDF Text Extractor
# ---------------------------------------------------------------------------

def _get_resume_text(uploaded_file_path: str | None) -> str:
    """Extract raw text from a PDF resume if available."""
    if not uploaded_file_path:
        return ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        return "\n\n".join(pages)
    except Exception as e:
        logger.error("Failed to parse PDF resume at %s: %s", uploaded_file_path, e)
        return ""

# ---------------------------------------------------------------------------
# Node 1: Classify
# ---------------------------------------------------------------------------

CLASSIFY_SYSTEM = """You are an advanced Career Copilot and Interview Prep classifier. Given a user request, decide which tool to invoke.

Available tools:
- resume_qa          : use for general conversation, asking questions about the uploaded resume, general interview advice, or generic greet/chat.
- job_suitability    : use when the user asks if their resume matches or is suitable for a specific job/role, or pastes a Job Description (JD) to match.
- interview_prep     : use when the user requests practice questions, predicted interview questions, or mock interviews.
- github_explainer   : use when the user provides a GitHub repository link or asks to explain/pitch their git project.
- resume_builder     : use when the user asks for tips on how to build, improve, format, or write achievements/bullet points for a specific target role.
- clarify            : use ONLY when the request is extremely short, ambiguous, or lacks context to choose any tool.

Respond ONLY with valid JSON, no markdown formatting (like ```json), no preamble:
{
  "tool": "<tool_name>",
  "confidence": <float 0.0-1.0>,
  "clarification_needed": <bool>,
  "clarification_question": "<question to ask user, or null>"
}"""


def classify_node(state: AgentState) -> dict:
    """Classify user intent and select a career tool."""
    iteration = state.get("iteration", 0)
    if iteration >= MAX_ITERATIONS:
        return {"error": "Max iterations reached", "tool": "clarify"}

    raw_input = state["raw_input"]

    # Programmatic bypass fast-paths to guarantee routing accuracy & eliminate LLM classification latency
    if raw_input.startswith("BUILD_RESUME_FOR:") or raw_input.startswith("REVISE_RESUME:"):
        return {
            "tool": "resume_builder",
            "confidence": 1.0,
            "clarification_needed": False,
            "clarification_question": None,
            "iteration": iteration + 1,
        }
    elif raw_input.startswith("Compare my resume against this Job Description:"):
        return {
            "tool": "job_suitability",
            "confidence": 1.0,
            "clarification_needed": False,
            "clarification_question": None,
            "iteration": iteration + 1,
        }
    elif raw_input.startswith("Generate predicted interview questions and answers based on my resume."):
        return {
            "tool": "interview_prep",
            "confidence": 1.0,
            "clarification_needed": False,
            "clarification_question": None,
            "iteration": iteration + 1,
        }

    # Pull conversation history for context
    history = _session_store.get_history(state["session_id"])
    messages = history + [{"role": "user", "content": state["raw_input"]}]

    # Nudge if file uploaded or text pasted
    if state.get("uploaded_file_path") or state.get("older_resume_text"):
        messages[-1]["content"] += "\n[Note: User has provided a Resume]"

    # Convert to Gemini format
    conversation_history = []
    for msg in messages:
        if msg["role"] == "user":
            conversation_history.append({"role": "user", "parts": [msg["content"]]})
        else:
            conversation_history.append({"role": "model", "parts": [msg["content"]]})

    # Classify intent
    try:
        chat = _model.start_chat(history=conversation_history[:-1])
        response = chat.send_message(
            f"{CLASSIFY_SYSTEM}\n\nUser Request:\n{conversation_history[-1]['parts'][0]}",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=256,
                temperature=0.2,
            ),
        )
        raw = response.text.strip()
        # Strip potential markdown fences
        if raw.startswith("```"):
            lines = raw.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                raw = "\n".join(lines[1:-1])
            else:
                raw = raw.replace("```json", "").replace("```", "")
        raw = raw.strip()
        result = json.loads(raw)
    except Exception as e:
        logger.warning("Classifier failed: %s", e)
        # Fallback to general resume Q&A if it looks like a chat, or git if it has github.com
        if "github.com" in state["raw_input"].lower():
            result = {"tool": "github_explainer", "confidence": 0.9, "clarification_needed": False, "clarification_question": None}
        else:
            result = {"tool": "resume_qa", "confidence": 0.8, "clarification_needed": False, "clarification_question": None}

    # Validate tool name
    valid_tools: set[ToolName] = {"resume_qa", "job_suitability", "interview_prep", "github_explainer", "resume_builder", "clarify"}
    if result.get("tool") not in valid_tools:
        logger.warning("Invalid tool name %s, falling back to resume_qa", result.get("tool"))
        result["tool"] = "resume_qa"
        result["confidence"] = 0.8
        result["clarification_needed"] = False

    # Enforce confidence threshold
    if result["confidence"] < CONFIDENCE_THRESHOLD and not result["clarification_needed"]:
        result["clarification_needed"] = True
        result["clarification_question"] = (
            "I want to make sure I help you best! Are you trying to "
            "(a) practice interview questions, (b) check your resume suitability for a job description, "
            "(c) get resume bullet points for a role, or (d) explain a GitHub repository?"
        )

    return {
        "tool": result["tool"],
        "confidence": result["confidence"],
        "clarification_needed": result["clarification_needed"],
        "clarification_question": result.get("clarification_question"),
        "iteration": iteration + 1,
    }


# ---------------------------------------------------------------------------
# Node 2: Act — dispatch to the right career tool
# ---------------------------------------------------------------------------

RESUME_QA_SYSTEM = """You are a highly supportive and expert Career Coach and Interview Preparation Mentor.
You are helping the candidate prepare for interviews and refine their profile.

If they have uploaded a resume (provided below), use it to ground your answers, suggest refinements, and point out relevant strengths.
Always write structured, encouraging, and detailed responses in clean GitHub Markdown.

--- CANDIDATE RESUME ---
{resume_text}
"""

def act_node(state: AgentState) -> dict:
    """Invoke the selected career helper tool."""
    tool = state["tool"]
    user_input = state["raw_input"]
    history = _session_store.get_history(state["session_id"])
    resume_text = state.get("older_resume_text") or _get_resume_text(state.get("uploaded_file_path"))

    try:
        if tool == "resume_qa":
            # Convert history to Gemini format
            conversation_history = []
            for msg in history:
                if msg["role"] == "user":
                    conversation_history.append({"role": "user", "parts": [msg["content"]]})
                else:
                    conversation_history.append({"role": "model", "parts": [msg["content"]]})

            chat = _model.start_chat(history=conversation_history)
            system_msg = RESUME_QA_SYSTEM.format(resume_text=resume_text if resume_text else "(No resume uploaded yet)")
            response = chat.send_message(f"{system_msg}\n\nCandidate Question: {user_input}")
            return {"draft_output": response.text, "error": None}

        elif tool == "job_suitability":
            if not resume_text:
                return {
                    "draft_output": "⚠️ **Please upload your resume PDF in the sidebar first** before comparing suitability with a job description.",
                    "error": None
                }
            res = _resume_analyzer.evaluate_suitability(resume_text, user_input)
            matches = "\n".join([f"- {m}" for m in res.get("matches", [])])
            gaps = "\n".join([f"- {g}" for g in res.get("gaps", [])])
            recs = "\n".join([f"- {r}" for r in res.get("recommendations", [])])
            detailed = res.get("detailed_analysis", "")
            
            markdown_out = f"""## 📊 Suitability Match: **{res.get('score', 0)}%**

### 🎯 Key Strengths & Match Points
{matches}

### ⚠️ Missing Keywords & Skill Gaps
{gaps}

### 💡 Actionable Resume Optimization Recommendations
{recs}

---

### 🔍 Recruiter's Deep-Dive Analysis
{detailed}"""
            return {
                "draft_output": markdown_out,
                "structured_output": res,
                "error": None
            }

        elif tool == "interview_prep":
            if not resume_text:
                return {
                    "draft_output": "⚠️ **Please upload your resume PDF in the sidebar first** before predicting customized interview questions.",
                    "error": None
                }
            # user_input can be a target job description or role
            res = _resume_analyzer.generate_questions(resume_text, user_input)
            
            formatted_q = ["## ❓ Custom Predicted Interview Questions & Answers\n"]
            for q in res.get("questions", []):
                formatted_q.append(f"### {q.get('id')}. {q.get('question')}")
                formatted_q.append(f"**Category**: *{q.get('category')}*")
                formatted_q.append(f"**Suggested STAR Model Answer**:\n{q.get('model_answer')}\n")
                formatted_q.append("---")
            
            return {
                "draft_output": "\n".join(formatted_q),
                "structured_output": res,
                "error": None
            }

        elif tool == "github_explainer":
            # Extract git URL from user input using regex
            git_pattern = r"(https?://(?:www\.)?github\.com/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+)"
            match = re.search(git_pattern, user_input)
            if not match:
                # If they didn't supply a full link, maybe it's in the text or they just typed username/repo
                backup_pattern = r"([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-\.]+)"
                match_backup = re.search(backup_pattern, user_input)
                if match_backup and "/" in match_backup.group(1):
                    git_url = f"https://github.com/{match_backup.group(1)}"
                else:
                    return {
                        "draft_output": "⚠️ **Please provide a public GitHub URL** (e.g. `https://github.com/owner/repository`) for me to fetch and explain your project.",
                        "error": None
                    }
            else:
                git_url = match.group(1)

            explanation = _github_explainer.explain_project(git_url)
            return {"draft_output": explanation, "error": None}

        elif tool == "resume_builder":
            target_role = ""
            custom_instructions = ""
            is_revision = False
            revision_request = ""
            previous_output = ""

            if user_input.startswith("BUILD_RESUME_FOR:"):
                lines = user_input.split("\n")
                target_role = lines[0].replace("BUILD_RESUME_FOR:", "").strip()
                
                # Robust multiline parser for instructions
                inst_idx = -1
                for i, line in enumerate(lines):
                    if line.startswith("INSTRUCTIONS:"):
                        inst_idx = i
                        break
                if inst_idx != -1:
                    custom_instructions = "\n".join(lines[inst_idx:]).replace("INSTRUCTIONS:", "").strip()

            elif user_input.startswith("REVISE_RESUME:"):
                is_revision = True
                lines = user_input.split("\n")
                revision_request = lines[0].replace("REVISE_RESUME:", "").strip()
                
                # Parse target role
                for line in lines:
                    if line.startswith("TARGET_ROLE:"):
                        target_role = line.replace("TARGET_ROLE:", "").strip()
                        break
                
                # Parse previous output
                prev_idx = -1
                for i, line in enumerate(lines):
                    if line.startswith("PREVIOUS_OUTPUT:"):
                        prev_idx = i
                        break
                if prev_idx != -1:
                    previous_output = "\n".join(lines[prev_idx:]).replace("PREVIOUS_OUTPUT:", "").strip()

            res = _resume_analyzer.suggest_resume_build(
                target_role=target_role,
                current_resume=resume_text,
                custom_instructions=custom_instructions,
                is_revision=is_revision,
                revision_request=revision_request,
                previous_output=previous_output
            )
            
            structure = "\n".join([f"- {s}" for s in res.get("recommended_structure", [])])
            skills = "\n".join([f"- {sk}" for sk in res.get("must_have_skills", [])])
            bullets = "\n".join([f"- {b}" for b in res.get("tailored_bullet_points", [])])
            advice = res.get("strategic_advice", "")

            # If there's compiled resume info, append brief explanation in markdown
            compiled_part = ""
            if "compiled_resume" in res:
                compiled_part = "\n\n🎉 **A Pixel-Perfect, Printable PDF-ready Resume has been compiled below matching your styling layout!**"

            markdown_out = f"""## ✍️ Resume Tailoring Guide for **{target_role}**
 
### 📁 Recommended Section Layout
{structure}
 
### 🛠️ High-Demand Technical & Soft Skills
{skills}
 
### 🚀 Optimized STAR Impact Achievements (Copy-Paste Ready!)
{bullets}
 
---
 
### 💡 Strategic Recruiter Advice
{advice}{compiled_part}"""
            return {
                "draft_output": markdown_out,
                "structured_output": res,
                "error": None
            }

        else:
            return {"error": f"Unknown career tool: {tool}"}

    except Exception as exc:
        logger.exception("Career Tool %s encountered an error", tool)
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Node 3: Save to session memory
# ---------------------------------------------------------------------------

def memory_node(state: AgentState) -> dict:
    """Persist the exchange to session memory."""
    output = state.get("edited_output") or state.get("draft_output", "")
    _session_store.append(
        session_id=state["session_id"],
        user_msg=state["raw_input"],
        assistant_msg=output,
    )
    return {}


# ---------------------------------------------------------------------------
# Node 4: Audit log
# ---------------------------------------------------------------------------

def audit_node(state: AgentState) -> dict:
    """Append a record to the append-only audit log."""
    import json as _json
    from datetime import datetime

    record = {
        "ts": datetime.utcnow().isoformat(),
        "session_id": state["session_id"],
        "user_id": state["user_id"],
        "tool": state.get("tool"),
        "confidence": state.get("confidence"),
        "review_decision": state.get("review_decision"),
        "reject_reason": state.get("reject_reason"),
    }
    log_path = os.getenv("AUDIT_LOG_PATH", "./data/audit_log.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(_json.dumps(record) + "\n")
    return {}
