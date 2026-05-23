# 🚀 Career Copilot & Interview Prep Suite

A premium, interactive AI-powered suite designed for candidates and job seekers to ace their tech interviews and optimize their resumes.

Built with **FastAPI**, **Streamlit**, and **LangGraph**, powered by **Gemini Pro**.

---

## ✨ Features

1. **💬 Interview Coach Chat**: Real-time mock interview prep chat powered by Gemini. Discuss your background, ask general career coaching questions, or practice custom behavioral skills with active resume context.
2. **🎯 Job Fit Matcher**: Objective resume-to-job compatibility analysis. Paste a Job Description to calculate a compatibility match percentage, extract key strengths, map keyword gaps, and get recommendations to optimize your resume.
3. **❓ Predicted Q&A Cards**: Generate custom behavioral and technical interview questions based strictly on your resume and optional job descriptions, complete with detailed STAR format answer guides in expander cards.
4. **📁 GitHub Project Pitcher**: Auto-analyze public GitHub codebases. Fetches `README.md` files (no token required) and generates elevator pitches, tech stack architectural breakdowns, and customized interview pitches.
5. **✍️ Resume Tailoring Builder**: Customize your resume for any target role (e.g. Frontend Engineer, Product Manager). Outlines optimal section layouts, lists high-demand skills, and writes copy-paste ready, quantified STAR achievement bullet points.

---

## 🛠️ Tech Stack & Architecture

* **Frontend**: Streamlit (Premium dark-theme visual console with progress gauges and interactive accordions)
* **Backend**: FastAPI (Restful endpoints for document upload, parsing, and graph execution)
* **LLM Engine**: Google Gemini Pro
* **State Machine**: LangGraph (Dynamic routing, classifier nodes, and fallback handlers)
* **Session Store**: local dict session memory with Redis support

```
        User Dashboard (Streamlit Frontend)
                       ↕
               FastAPI Backend (main.py)
                       ↕
         LangGraph Orchestrator (graph/agent.py)
                       ↕
  Intent Classifier node → Dispatches to specialist tools:
     • resume_qa          • job_suitability
     • interview_prep     • github_explainer
     • resume_builder
```

---

## 🚀 Setup & Execution

### 1. Environment Configuration
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
CONFIDENCE_THRESHOLD=0.70
API_BASE=http://localhost:8000
```

### 2. Install Dependencies
Ensure you have Python 3.10+ installed. In your terminal, run:
```bash
pip install -r requirements.txt
```

### 3. Launch FastAPI Backend
Start the backend server on port 8000:
```bash
uvicorn main:app --reload --port 8000
```

### 4. Launch Streamlit Frontend
Start the web application:
```bash
streamlit run frontend/app.py --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501) in your browser to start your prep session!

---

## 🧪 Running Tests
Verify tool routing, schemas, and fallback boundaries using the Pytest test suite:
```bash
pytest tests/ -v
```
