"""
tools/streaming_agent.py
Direct streaming agent for Career Coach Chat.
Streams responses from Gemini 2.5-Flash and persists history on completion.
"""

import os
import logging
from pypdf import PdfReader
import google.generativeai as genai
from memory.session_store import SessionStore

logger = logging.getLogger(__name__)

RESUME_QA_SYSTEM = """You are a highly supportive and expert Career Coach and Interview Preparation Mentor.
You are helping the candidate prepare for interviews and refine their profile.

If they have uploaded a resume (provided below), use it to ground your answers, suggest refinements, and point out relevant strengths.
Always write structured, encouraging, and detailed responses in clean GitHub Markdown.

--- CANDIDATE RESUME ---
{resume_text}
"""

class StreamingAgent:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self._model = genai.GenerativeModel("gemini-2.5-flash")
        self._session_store = SessionStore()

    def _get_resume_text(self, uploaded_file_path: str | None) -> str:
        if not uploaded_file_path:
            return ""
        try:
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

    def stream_chat(self, session_id: str, user_input: str, uploaded_file_path: str | None):
        history = self._session_store.get_history(session_id)
        resume_text = self._get_resume_text(uploaded_file_path)

        conversation_history = []
        for msg in history:
            if msg["role"] == "user":
                conversation_history.append({"role": "user", "parts": [msg["content"]]})
            else:
                conversation_history.append({"role": "model", "parts": [msg["content"]]})

        try:
            chat = self._model.start_chat(history=conversation_history)
            system_msg = RESUME_QA_SYSTEM.format(resume_text=resume_text if resume_text else "(No resume uploaded yet)")
            
            prompt = f"{system_msg}\n\nCandidate Question: {user_input}"
            response = chat.send_message(prompt, stream=True)
            
            full_response = []
            for chunk in response:
                text = chunk.text
                full_response.append(text)
                yield text
                
            # Persist to session memory upon successful completion of stream
            self._session_store.append(
                session_id=session_id,
                user_msg=user_input,
                assistant_msg="".join(full_response)
            )
        except Exception as e:
            logger.exception("Error in stream_chat")
            yield f"❌ **Error generating response**: {e}"
