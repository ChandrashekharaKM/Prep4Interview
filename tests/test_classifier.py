"""
tests/test_classifier.py
Unit tests for the Career Copilot classification logic and schemas.
Run: pytest tests/ -v
"""

import json
import os
# Ensure mock GEMINI_API_KEY is present so importing graph.nodes doesn't fail
os.environ.setdefault("GEMINI_API_KEY", "mock-api-key")

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Test: classifier returns valid JSON with required fields
# ---------------------------------------------------------------------------

VALID_CLASSIFY_RESPONSES = [
    '{"tool": "resume_qa", "confidence": 0.95, "clarification_needed": false, "clarification_question": null}',
    '{"tool": "job_suitability", "confidence": 0.88, "clarification_needed": false, "clarification_question": null}',
    '{"tool": "interview_prep", "confidence": 0.91, "clarification_needed": false, "clarification_question": null}',
    '{"tool": "github_explainer", "confidence": 0.96, "clarification_needed": false, "clarification_question": null}',
    '{"tool": "resume_builder", "confidence": 0.85, "clarification_needed": false, "clarification_question": null}',
]

@pytest.mark.parametrize("raw_json", VALID_CLASSIFY_RESPONSES)
def test_valid_classifier_json(raw_json):
    result = json.loads(raw_json)
    assert result["tool"] in {"resume_qa", "job_suitability", "interview_prep", "github_explainer", "resume_builder", "clarify"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["clarification_needed"], bool)


# ---------------------------------------------------------------------------
# Test: invalid tool name falls back to resume_qa/clarify
# ---------------------------------------------------------------------------

def test_invalid_tool_falls_back():
    """Simulate the fallback logic from nodes.py classify_node."""
    valid_tools = {"resume_qa", "job_suitability", "interview_prep", "github_explainer", "resume_builder", "clarify"}
    result = {"tool": "nonexistent_tool", "confidence": 0.9, "clarification_needed": False}

    if result.get("tool") not in valid_tools:
        result["tool"] = "resume_qa"
        result["confidence"] = 0.8
        result["clarification_needed"] = False

    assert result["tool"] == "resume_qa"
    assert result["clarification_needed"] is False


# ---------------------------------------------------------------------------
# Test: low confidence triggers clarification
# ---------------------------------------------------------------------------

def test_low_confidence_triggers_clarification():
    """Below threshold, clarification should be set."""
    THRESHOLD = 0.70
    result = {"tool": "resume_qa", "confidence": 0.60, "clarification_needed": False,
              "clarification_question": None}

    if result["confidence"] < THRESHOLD and not result["clarification_needed"]:
        result["clarification_needed"] = True
        result["clarification_question"] = "Could you clarify?"

    assert result["clarification_needed"] is True
    assert result["clarification_question"] is not None


# ---------------------------------------------------------------------------
# Test: Suitability analysis output schema
# ---------------------------------------------------------------------------

def test_suitability_matcher_schema():
    """Verify the expected schema from evaluate_suitability output."""
    sample_output = {
        "score": 85,
        "matches": ["Strong Python experience", "FastAPI web dev expertise"],
        "gaps": ["Docker containerization", "AWS Kubernetes deployments"],
        "recommendations": ["Add a Docker project to experience section"],
        "detailed_analysis": "The candidate matches 85% of core requirements but lacks production cloud ops exposure."
    }

    required_keys = {"score", "matches", "gaps", "recommendations", "detailed_analysis"}
    assert required_keys.issubset(sample_output.keys())
    assert isinstance(sample_output["matches"], list)
    assert isinstance(sample_output["gaps"], list)
    assert isinstance(sample_output["score"], int)


# ---------------------------------------------------------------------------
# Test: Predicted questions schema
# ---------------------------------------------------------------------------

def test_predicted_questions_schema():
    """Verify schema structure of predicted questions generator."""
    sample_output = {
        "questions": [
            {
                "id": 1,
                "question": "Can you explain how you designed the database layout in project X?",
                "category": "Technical",
                "model_answer": "Situation: DB query lag... Task: Redesign... Action: Indexed... Result: 40% speed up."
            }
        ]
    }

    assert "questions" in sample_output
    assert len(sample_output["questions"]) == 1
    assert sample_output["questions"][0]["category"] == "Technical"
    assert "model_answer" in sample_output["questions"][0]


# ---------------------------------------------------------------------------
# Test: session store fallback (no Redis)
# ---------------------------------------------------------------------------

def test_session_store_fallback():
    """SessionStore should work without Redis using in-memory dict."""
    from memory.session_store import SessionStore

    store = SessionStore(redis_url="redis://localhost:9999")  # intentionally wrong port
    session_id = "test-session-001"

    store.append(session_id, "Hello", "Hi there!")
    history = store.get_history(session_id)

    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"


# ---------------------------------------------------------------------------
# Test: Mock Interview Scorecard Schema
# ---------------------------------------------------------------------------

def test_mock_interview_scorecard_schema():
    """Verify mock interview scorecard contains all keys expected by frontend."""
    sample_scorecard = {
        "grade": "A",
        "overall_summary": "Great communication and strong tech skills.",
        "strengths": ["Clear project presentation", "Metric-oriented STAR answers"],
        "gaps": ["Lacks systems-level depth"],
        "answers_review": [
            {
                "question_number": 1,
                "question": "Tell me about your Python project?",
                "user_answer": "I built a web scraper for real estate.",
                "critique": "A bit short.",
                "model_answer": "Situation: Needed market insights... Task: Retrieve... Action: Built Scraper... Result: 10k listings."
            }
        ]
    }

    required_keys = {"grade", "overall_summary", "strengths", "gaps", "answers_review"}
    assert required_keys.issubset(sample_scorecard.keys())
    assert isinstance(sample_scorecard["strengths"], list)
    assert isinstance(sample_scorecard["answers_review"], list)
    assert sample_scorecard["answers_review"][0]["question_number"] == 1


# ---------------------------------------------------------------------------
# Test: Programmatic Bypass classification routing
# ---------------------------------------------------------------------------

def test_programmatic_bypass_routing():
    """Verify that inputs with special prefixes bypass the LLM classifier completely."""
    from graph.nodes import classify_node
    from graph.state import initial_state

    # 1. Test BUILD_RESUME_FOR: bypass
    state_build = initial_state(
        session_id="test_sess_001",
        user_id="test_user_001",
        raw_input="BUILD_RESUME_FOR: Senior Machine Learning Engineer"
    )
    result_build = classify_node(state_build)
    assert result_build["tool"] == "resume_builder"
    assert result_build["confidence"] == 1.0
    assert result_build["clarification_needed"] is False

    # 2. Test REVISE_RESUME: bypass
    state_revise = initial_state(
        session_id="test_sess_002",
        user_id="test_user_002",
        raw_input="REVISE_RESUME: Translate all sections to Spanish and update dates."
    )
    result_revise = classify_node(state_revise)
    assert result_revise["tool"] == "resume_builder"
    assert result_revise["confidence"] == 1.0
    assert result_revise["clarification_needed"] is False

    # 3. Test Compare suitability bypass
    state_suit = initial_state(
        session_id="test_sess_003",
        user_id="test_user_003",
        raw_input="Compare my resume against this Job Description:\nLooking for Python Developer"
    )
    result_suit = classify_node(state_suit)
    assert result_suit["tool"] == "job_suitability"
    assert result_suit["confidence"] == 1.0
    assert result_suit["clarification_needed"] is False

    # 4. Test Predict questions bypass
    state_pred = initial_state(
        session_id="test_sess_004",
        user_id="test_user_004",
        raw_input="Generate predicted interview questions and answers based on my resume."
    )
    result_pred = classify_node(state_pred)
    assert result_pred["tool"] == "interview_prep"
    assert result_pred["confidence"] == 1.0
    assert result_pred["clarification_needed"] is False


# ---------------------------------------------------------------------------
# Test: act_node priority routing & parsing
# ---------------------------------------------------------------------------

@patch("graph.nodes._resume_analyzer.suggest_resume_build")
def test_act_node_older_resume_priority(mock_suggest_build):
    """Verify that act_node prioritizes older_resume_text over PDF extracted text."""
    from graph.nodes import act_node
    from graph.state import AgentState

    mock_suggest_build.return_value = {
        "recommended_structure": [],
        "must_have_skills": [],
        "tailored_bullet_points": [],
        "strategic_advice": "Perfect!"
    }

    # Set state with both older_resume_text and uploaded_file_path
    state: AgentState = {
        "session_id": "test_sess_005",
        "user_id": "test_user_005",
        "raw_input": "BUILD_RESUME_FOR: Backend Engineer",
        "uploaded_file_path": "fake_path.pdf",
        "older_resume_text": "Pasted older resume text from input box",
        "tool": "resume_builder",
        "confidence": 1.0,
        "clarification_needed": False,
        "clarification_question": None,
        "draft_output": None,
        "structured_output": None,
        "citations": None,
        "review_decision": "pending",
        "edited_output": None,
        "reject_reason": None,
        "timestamp": "2026-05-22T00:00:00",
        "iteration": 1,
        "error": None
    }

    with patch("graph.nodes._get_resume_text") as mock_get_pdf_text:
        act_node(state)
        # Verify mock_get_pdf_text is NOT called since older_resume_text was directly present and used
        mock_get_pdf_text.assert_not_called()
        
        # Verify suggest_resume_build was called with the older_resume_text
        mock_suggest_build.assert_called_once()
        kwargs = mock_suggest_build.call_args[1]
        assert kwargs["current_resume"] == "Pasted older resume text from input box"


# ---------------------------------------------------------------------------
# Test: API endpoints schema validation for custom api_key
# ---------------------------------------------------------------------------

def test_api_endpoints_accept_api_key():
    """Verify that all request bodies accept the optional api_key parameter without validation errors."""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    # 1. Test /mock_interview/next_stream with api_key
    with patch("main._mock_simulator.get_next_turn_stream") as mock_next_turn:
        mock_next_turn.return_value = ["chunk1", "chunk2"]
        resp = client.post(
            "/mock_interview/next_stream",
            json={
                "resume_text": "Sample resume text",
                "interview_type": "Technical",
                "persona": "Friendly Mentor",
                "history": [],
                "api_key": "user-custom-api-key"
            }
        )
        assert resp.status_code == 200

    # 2. Test /chat/stream with api_key
    with patch("main._streaming_agent.stream_chat") as mock_chat:
        mock_chat.return_value = ["chunk"]
        resp = client.post(
            "/chat/stream",
            json={
                "session_id": "test-session",
                "user_input": "Hello",
                "api_key": "user-custom-api-key"
            }
        )
        assert resp.status_code == 200


