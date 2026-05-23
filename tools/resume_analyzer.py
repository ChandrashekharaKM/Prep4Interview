"""
tools/resume_analyzer.py
Core AI engine for candidate resume analysis, job suitability scoring,
predicted interview prep, and tailored resume building.
"""

import os
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

SUITABILITY_SYSTEM_PROMPT = """You are an elite corporate recruiter and resume consultant.
Compare the candidate's resume text against the provided Job Description (JD).
Score their compatibility objectively from 0 to 100 and extract exact matching strengths and key missing skill/keyword gaps.

You MUST respond with a single valid JSON object. Do not include any markdown formatting (like ```json), HTML, or preambles.

Required JSON format:
{
  "score": <integer from 0 to 100>,
  "matches": ["<strength 1>", "<strength 2>", ...],
  "gaps": ["<gap 1 (missing skill or keyword)>", "<gap 2>", ...],
  "recommendations": ["<actionable resume optimization tip 1>", "<tip 2>", ...],
  "detailed_analysis": "<markdown formatted textual summary of fit and core observations>"
}
"""

QUESTIONS_SYSTEM_PROMPT = """You are a senior hiring manager and tech lead.
Analyze the candidate's resume text and the optional Job Description (JD).
Generate 5 highly relevant interview questions (mix of technical deep dives and behavioral) that are specifically tailored to this candidate's projects, experience, and the target role.
For each question, provide a detailed, high-quality model answer in the STAR framework (Situation, Task, Action, Result).

You MUST respond with a single valid JSON object. Do not include any markdown formatting (like ```json), HTML, or preambles.

Required JSON format:
{
  "questions": [
    {
      "id": 1,
      "question": "<the tailored interview question>",
      "category": "<Technical | Behavioral | System Design>",
      "model_answer": "<the exact, professional, first-person (I/me/my) spoken response the candidate should give. It MUST contain ONLY the recommended answer itself following STAR methodology, with absolutely NO intro, NO outro, NO meta-commentary, and NO wrapper text. Only the actual recommended response content should be there.>"
    },
    ...
  ]
}
"""

BUILDER_SYSTEM_PROMPT = """You are an expert resume writer and career coach.
Suggest how the user can build and optimize their resume for a specific target role.
Analyze their current experience (provided as CURRENT CANDIDATE RESUME) and generate:
1. High-impact STAR-format bullet points customized to the role.
2. A checklist of high-demand skills (Hard and Soft skills).
3. Strategic structure advice (what sections to emphasize).
4. A FULLY COMPILED, professional resume representing the tailored resume structure!

You MUST respond with a single valid JSON object. Do not include any markdown formatting (like ```json), HTML, or preambles.

Required JSON format:
{
  "recommended_structure": ["<section 1>", "<section 2>", ...],
  "must_have_skills": ["<skill 1>", ...],
  "tailored_bullet_points": ["<bullet 1>", ...],
  "strategic_advice": "<markdown advice>",
  "compiled_resume": {
    "name": "<Candidate's Full Name, default to CHANDRASHEKHARA K M if found in context, else use a placeholder>",
    "contact_info": {
      "location": "<City, State>",
      "phone": "<Phone>",
      "email": "<Email>",
      "linkedin": "<LinkedIn profile link / username>",
      "github": "<GitHub profile link / username>"
    },
    "professional_summary": "<A highly tailored, quantified professional summary with bold keywords like **Python Developer**, **FastAPI**>",
    "education": [
      {
        "degree": "<e.g., Master of Computer Applications (MCA) or Bachelor of Computer Applications (BCA)>",
        "institution": "<e.g., Dayananda Sagar University, Bengaluru>",
        "date": "<e.g., 2024 - 2026 (Exp.)>",
        "score": "<e.g., CGPA: 9.14/10 or 85.83%>"
      }
    ],
    "work_experience": [
      {
        "company": "<Company Name>",
        "role": "<Role Title>",
        "location": "<Location or Remote>",
        "date": "<e.g., Dec 2025 - Apr 2026>",
        "bullets": [
          "<Highly quantified STAR bullet point starting with a strong verb, e.g., Engineered an HR Automation System using Python to automate candidate parsing, reducing manual entries by 15+ hours...>",
          "<Quantified STAR bullet point 2>"
        ]
      }
    ],
    "skills": {
      "languages": "<Piped or comma-separated languages, e.g. Python, Java, JavaScript>",
      "tools": "<e.g. Git, GitHub, Docker, Postman>",
      "python_ecosystem": "<e.g. FastAPI, Flask, Scikit-learn, Pandas>",
      "core_concepts": "<e.g. Data Structures & Algorithms (DSA), System Design>"
    },
    "featured_projects": [
      {
        "title": "<Project Title>",
        "tech_stack": "<Piped or comma-separated tech list, e.g. Python, FastAPI, Hugging Face>",
        "bullets": [
          "<Quantified action bullet 1>",
          "<Quantified action bullet 2>"
        ]
      }
    ],
    "additional_projects": [
      {
        "title": "<Project Title, e.g. Water Quality Prediction>",
        "description": "<Bullet point summary description, e.g. ML model (87% accuracy) for water safety classification using Python and Scikit-learn.>"
      }
    ],
    "certifications_and_achievements": [
      {
        "category": "<e.g. Problem Solving or Certifications>",
        "details": "<e.g. Solved 50+ problems on competitive programming platforms focusing on DSA. or Certified Secure Computer User (CSCU).>"
      }
    ]
  }
}
"""

REVISER_SYSTEM_PROMPT = """You are an expert resume writer and career coach.
You are helping the candidate revise and refine a previously generated tailored resume guide.
You are given:
1. The target professional role.
2. The candidate's older/current resume context (if any).
3. The previously generated tailored resume guide in JSON format.
4. The candidate's specific request for changes/revisions.

Apply the revision request to update the previous guide.
Make sure you modify the recommended structure, must-have skills, tailored bullet points, strategic advice, and specifically compile a fresh "compiled_resume" incorporating the candidate's exact feedback, while preserving and maintaining all other correct sections.

You MUST respond with a single valid JSON object. Do not include any markdown formatting (like ```json), HTML, or preambles.

Required JSON format:
{
  "recommended_structure": ["<section 1>", "<section 2>", ...],
  "must_have_skills": ["<skill 1>", ...],
  "tailored_bullet_points": ["<bullet 1>", ...],
  "strategic_advice": "<markdown advice>",
  "compiled_resume": {
    "name": "<Candidate's Full Name>",
    "contact_info": {
      "location": "<City, State>",
      "phone": "<Phone>",
      "email": "<Email>",
      "linkedin": "<LinkedIn profile link>",
      "github": "<GitHub profile link>"
    },
    "professional_summary": "<A highly tailored, quantified professional summary with bold keywords>",
    "education": [
      {
        "degree": "<Degree>",
        "institution": "<Institution>",
        "date": "<Dates>",
        "score": "<Score>"
      }
    ],
    "work_experience": [
      {
        "company": "<Company>",
        "role": "<Role>",
        "location": "<Location>",
        "date": "<Dates>",
        "bullets": [
          "<Revised STAR bullet point 1>",
          "<Revised STAR bullet point 2>"
        ]
      }
    ],
    "skills": {
      "languages": "<languages>",
      "tools": "<tools>",
      "python_ecosystem": "<python_ecosystem>",
      "core_concepts": "<core_concepts>"
    },
    "featured_projects": [
      {
        "title": "<Project Title>",
        "tech_stack": "<Tech Stack>",
        "bullets": [
          "<bullet 1>",
          "<bullet 2>"
        ]
      }
    ],
    "additional_projects": [
      {
        "title": "<Project Title>",
        "description": "<Description>"
      }
    ],
    "certifications_and_achievements": [
      {
        "category": "<Category>",
        "details": "<Details>"
      }
    ]
  }
}
"""

class ResumeAnalyzer:
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self._model = genai.GenerativeModel("gemini-2.5-flash")

    def _clean_json_response(self, text: str) -> dict:
        """Strip possible markdown wrappers and load JSON securely."""
        raw = text.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                # Join lines excluding the first and last line fences
                raw = "\n".join(lines[1:-1])
            else:
                raw = raw.replace("```json", "").replace("```", "")
        
        # Strip potential leading/trailing quotes
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.exception("Failed to parse JSON from AI: %s", raw)
            raise RuntimeError(f"Failed to generate structured response from Gemini: {e}")

    def evaluate_suitability(self, resume_text: str, job_description: str) -> dict:
        """Compare resume against JD and extract scores, gaps, and improvements."""
        if not resume_text or not job_description:
            return {
                "score": 0,
                "matches": ["Upload a resume and paste a Job Description first."],
                "gaps": ["Missing inputs"],
                "recommendations": ["Ensure both fields are filled"],
                "detailed_analysis": "Please provide both your resume and the job description to run this analyzer."
            }

        prompt = (
            f"{SUITABILITY_SYSTEM_PROMPT}\n\n"
            f"--- CANDIDATE RESUME ---\n{resume_text}\n\n"
            f"--- JOB DESCRIPTION ---\n{job_description}"
        )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            return self._clean_json_response(response.text)
        except Exception as e:
            logger.exception("Error evaluating suitability")
            return {
                "score": 50,
                "matches": [f"Error occurred: {str(e)}"],
                "gaps": ["Error parsing request"],
                "recommendations": ["Check environment/keys and try again"],
                "detailed_analysis": f"An error occurred during matching: {str(e)}"
            }

    def generate_questions(self, resume_text: str, job_description: str = "") -> dict:
        """Create resume-specific custom interview questions and STAR answers."""
        if not resume_text:
            return {
                "questions": [
                    {
                        "id": 1,
                        "question": "Could you upload your resume to get customized questions?",
                        "category": "Behavioral",
                        "model_answer": "Once you upload a resume, I will extract questions from your actual experience."
                    }
                ]
            }

        jd_context = f"\n\n--- JOB DESCRIPTION ---\n{job_description}" if job_description else ""
        prompt = (
            f"{QUESTIONS_SYSTEM_PROMPT}\n\n"
            f"--- CANDIDATE RESUME ---\n{resume_text}"
            f"{jd_context}"
        )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )
            return self._clean_json_response(response.text)
        except Exception as e:
            logger.exception("Error generating questions")
            return {
                "questions": [
                    {
                        "id": 1,
                        "question": f"Error loading questions: {str(e)}",
                        "category": "Error",
                        "model_answer": "Please make sure your resume PDF contains readable text."
                    }
                ]
            }

    def suggest_resume_build(self, target_role: str, current_resume: str = "", custom_instructions: str = "",
                             is_revision: bool = False, revision_request: str = "", previous_output: str = "") -> dict:
        """Suggest resume layout, high-demand skills, and action bullets for a target role."""
        if not target_role:
            return {
                "recommended_structure": [],
                "must_have_skills": [],
                "tailored_bullet_points": [],
                "strategic_advice": "Please select or type a target role to get optimization tips."
            }

        if is_revision:
            resume_context = f"\n\n--- CURRENT CANDIDATE RESUME ---\n{current_resume}" if current_resume else ""
            prompt = (
                f"{REVISER_SYSTEM_PROMPT}\n\n"
                f"TARGET ROLE: {target_role}\n"
                f"REVISION REQUEST: {revision_request}\n"
                f"PREVIOUS OUTPUT: {previous_output}"
                f"{resume_context}"
            )
        else:
            resume_context = f"\n\n--- CURRENT CANDIDATE RESUME ---\n{current_resume}" if current_resume else ""
            instructions_context = f"\n\n--- ADDITIONAL CANDIDATE REQUESTS / SPECIFIC CHANGES ---\n{custom_instructions}" if custom_instructions else ""
            prompt = (
                f"{BUILDER_SYSTEM_PROMPT}\n\n"
                f"TARGET ROLE: {target_role}"
                f"{resume_context}"
                f"{instructions_context}"
            )

        try:
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )
            return self._clean_json_response(response.text)
        except Exception as e:
            logger.exception("Error suggesting resume edits")
            return {
                "recommended_structure": ["Professional Summary", "Experience", "Skills"],
                "must_have_skills": [target_role, "Technical Skills"],
                "tailored_bullet_points": ["Achieved X by implementing Y, resulting in a Z% improvement."],
                "strategic_advice": f"An error occurred while generating resume build suggestions: {str(e)}"
            }
