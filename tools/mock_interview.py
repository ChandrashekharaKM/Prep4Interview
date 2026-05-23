"""
tools/mock_interview.py
AI engine for the premium Interactive Mock Interview Simulator.
Handles persona-based question generation, multi-turn response evaluation,
and compiles a final recruiter performance scorecard.
"""

import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

MOCK_INTERVIEW_SYSTEM_PROMPT = """You are an elite, expert interviewer acting in a professional candidate mock interview.
Your role is to simulate a highly realistic job interview.

You must adapt your tone and interviewing style to the chosen persona:
1. "Tough Tech Lead": Highly analytical, direct, skeptical, asks deep technical follow-ups, and expects precise, optimized solutions.
2. "Friendly Mentor": Extremely encouraging, supportive, guides the user with hints, focuses on learning and problem-solving patterns.
3. "Fast-Paced Recruiter": Focuses on high-level impact, quick summaries, communication style, cultural fit, and behavioral metrics.

The interview type is: {interview_type} (e.g., Technical, Behavioral, System Design).
The candidate's resume is:
{resume_text}

--- INTERVIEW RULES ---
1. You must act strictly in-character as the selected persona.
2. Ask exactly ONE question at a time.
3. You will receive the conversation history. Do not repeat previous questions.
4. Keep questions challenging and tailored directly to the candidate's resume, projects, and target role if provided.
5. If the user answers a question, provide a brief 2-3 sentence constructive, persona-appropriate micro-feedback on their response, and then ask the NEXT question.
6. When the user has answered {max_questions} questions, do not ask a new question. Instead, indicate that the interview is complete, and we are ready for the evaluation scorecard.

--- OUTPUT FORMAT ---
Your output for each turn must be a clean markdown response containing:
1. **[Feedback]**: Brief, constructive persona-appropriate reaction to their last answer (if not the first question).
2. **[Question]**: The next clear, focused interview question.
"""

SCORECARD_SYSTEM_PROMPT = """You are a senior talent acquisition specialist and engineering director.
Analyze the complete transcript of the mock interview and generate a comprehensive performance scorecard.

The interview transcript is:
{transcript}

The target role was: {target_role}
The candidate's resume was:
{resume_text}

You MUST respond with a single valid JSON object. Do not include any markdown formatting (like ```json), HTML, or preambles.

Required JSON format:
{{
  "grade": "<A+ | A | B | C | D | F>",
  "overall_summary": "<a high-impact summary of their overall interview performance, communication style, and readiness>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "gaps": ["<weak spot 1>", "<weak spot 2>", ...],
  "answers_review": [
    {{
      "question_number": <int>,
      "question": "<the question asked>",
      "user_answer": "<the user's actual answer>",
      "critique": "<constructive critique on structure, depth, or delivery>",
      "model_answer": "<the exact, professional, first-person (I/me/my) spoken response the candidate should have given. It MUST contain ONLY the recommended answer itself, with absolutely NO intro, NO outro, NO meta-commentary, and NO wrapper text. Only the actual recommended response content should be there.>"
    }},
    ...
  ]
}}
"""

class MockInterviewSimulator:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    def get_next_turn(
        self,
        resume_text: str,
        interview_type: str,
        persona: str,
        history: list[dict],
        max_questions: int = 3
    ) -> str:
        """
        Generates the next interview question and potential feedback based on conversation history.
        `history` format: list of {"role": "user"|"assistant", "content": str}
        """
        system_instruction = MOCK_INTERVIEW_SYSTEM_PROMPT.format(
            interview_type=interview_type,
            resume_text=resume_text if resume_text else "(No resume provided)",
            max_questions=max_questions
        )

        # Convert simple history format to Gemini parts format
        chat_history = []
        for turn in history:
            role = "user" if turn["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [turn["content"]]})

        # Start chat with the system prompt context
        prompt = (
            f"{system_instruction}\n\n"
            f"Active Persona: {persona}\n"
            f"History count: {len(history)} turns out of {max_questions * 2} max.\n"
        )
        
        # If history is empty, ask the first question
        if not history:
            prompt += "Please begin the interview by introducing yourself briefly as the persona and asking the first question."
        else:
            prompt += "Please analyze the candidate's last response, give micro-feedback, and ask the next question."

        try:
            # We start a chat session to retain memory if helpful, or pass it in context
            chat = self._model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.exception("Error in MockInterviewSimulator.get_next_turn")
            return f"❌ **Error generating next question**: {e}"

    def get_next_turn_stream(
        self,
        resume_text: str,
        interview_type: str,
        persona: str,
        history: list[dict],
        max_questions: int = 3
    ):
        """
        Generates the next interview question and potential feedback based on conversation history as a stream.
        """
        system_instruction = MOCK_INTERVIEW_SYSTEM_PROMPT.format(
            interview_type=interview_type,
            resume_text=resume_text if resume_text else "(No resume provided)",
            max_questions=max_questions
        )

        chat_history = []
        for turn in history:
            role = "user" if turn["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [turn["content"]]})

        prompt = (
            f"{system_instruction}\n\n"
            f"Active Persona: {persona}\n"
            f"History count: {len(history)} turns out of {max_questions * 2} max.\n"
        )
        
        if not history:
            prompt += "Please begin the interview by introducing yourself briefly as the persona and asking the first question."
        else:
            prompt += "Please analyze the candidate's last response, give micro-feedback, and ask the next question."

        try:
            chat = self._model.start_chat(history=chat_history)
            response = chat.send_message(prompt, stream=True)
            for chunk in response:
                yield chunk.text
        except Exception as e:
            logger.exception("Error in MockInterviewSimulator.get_next_turn_stream")
            yield f"❌ **Error generating next question**: {e}"

    def generate_scorecard(
        self,
        resume_text: str,
        target_role: str,
        history: list[dict]
    ) -> dict:
        """
        Analyzes the full interview history and outputs a professional performance scorecard.
        """
        # Build raw transcript for the AI
        transcript_lines = []
        for i, turn in enumerate(history):
            speaker = "Interviewer" if turn["role"] == "assistant" else "Candidate"
            transcript_lines.append(f"{speaker}: {turn['content']}")
        transcript = "\n".join(transcript_lines)

        prompt = SCORECARD_SYSTEM_PROMPT.format(
            transcript=transcript,
            target_role=target_role,
            resume_text=resume_text if resume_text else "(No resume provided)"
        )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2
                )
            )
            raw = response.text.strip()
            
            # Clean possible markdown JSON wrappers
            if raw.startswith("```"):
                lines = raw.split("\n")
                if lines[0].startswith("```json") or lines[0].startswith("```"):
                    raw = "\n".join(lines[1:-1])
                else:
                    raw = raw.replace("```json", "").replace("```", "")
            raw = raw.strip()
            
            return json.loads(raw)
        except Exception as e:
            logger.exception("Error compiling mock interview scorecard")
            return {
                "grade": "B",
                "overall_summary": f"Could not compile structured scorecard due to an error: {e}",
                "strengths": ["Completed all rounds of the mock interview simulator."],
                "gaps": ["Error parsing response JSON from generative engine."],
                "answers_review": []
            }
