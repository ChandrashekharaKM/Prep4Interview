"""
frontend/app.py
Streamlit UI for the Career Copilot & Interview Prep Suite.
Run with: streamlit run frontend/app.py
"""

import uuid
import os
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

# Set premium page layout and configuration
st.set_page_config(
    page_title="Prep4Interview",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject modern, premium dark-theme CSS style rules for maximum aesthetic appeal
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* Global Overrides */
    html, body, [data-testid="stAppViewContainer"], .main {
        font-family: 'Inter', sans-serif !important;
        background-color: #080A10 !important;
        color: #E2E8F0 !important;
    }
    
    /* Gradient Headers */
    .main-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.05em !important;
        background: linear-gradient(135deg, #A78BFA 0%, #4E65FF 50%, #06B6D4 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 0.1rem;
        text-shadow: 0 10px 40px rgba(124, 58, 237, 0.15);
    }
    .subtitle {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.15rem !important;
        color: #94A3B8 !important;
        margin-bottom: 2rem !important;
        font-weight: 400 !important;
    }
    
    /* Sidebar frosted glass effect */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 13, 22, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #E2E8F0 !important;
    }
    
    /* Premium card components */
    .metric-card {
        background: rgba(17, 24, 39, 0.5) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    .metric-card:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(167, 139, 250, 0.4) !important;
        box-shadow: 0 12px 40px rgba(124, 58, 237, 0.25) !important;
    }
    
    .strength-header {
        color: #10B981 !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.02em;
    }
    .gap-header {
        color: #F43F5E !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.02em;
    }
    .rec-header {
        color: #F59E0B !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.02em;
    }
    
    /* Custom styled buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    /* Primary buttons */
    .stButton>button[p-button="true"], .stButton>button[class*="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #4E65FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    .stButton>button[class*="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5) !important;
        filter: brightness(1.1) !important;
    }
    .stButton>button[class*="primary"]:active {
        transform: translateY(1px) !important;
    }
    /* Secondary/standard buttons */
    .stButton>button:not([class*="primary"]) {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #E2E8F0 !important;
    }
    .stButton>button:not([class*="primary"]):hover {
        background: rgba(30, 41, 59, 0.7) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* Modern Glass Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background-color: rgba(15, 22, 42, 0.4) !important;
        padding: 8px !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 18px !important;
        color: #94A3B8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #C084FC !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%) !important;
        color: #C084FC !important;
        border: 1px solid rgba(167, 139, 250, 0.3) !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight-spinner"] {
        display: none !important;
    }
    
    /* Input & Area Elements */
    .stTextArea textarea, .stTextInput input, .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(167, 139, 250, 0.6) !important;
        box-shadow: 0 0 12px rgba(124, 58, 237, 0.25) !important;
    }

    /* Retro Hacker Grilling Console */
    .hacker-terminal {
        background-color: #05070A !important;
        border: 1px solid #00F0FF !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #00F0FF !important;
        box-shadow: 0 4px 20px rgba(0, 240, 255, 0.15) !important;
        margin-top: 1rem;
        position: relative;
    }
    .hacker-terminal::before {
        content: "⚡ CODEBASE DEFENSE SIMULATOR v1.0";
        display: block;
        font-size: 0.75rem;
        color: rgba(0, 240, 255, 0.5);
        border-bottom: 1px solid rgba(0, 240, 255, 0.2);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        letter-spacing: 0.1em;
    }

    /* Custom Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
        margin: 2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []  # general prep chat history
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""
if "builder_result" not in st.session_state:
    st.session_state.builder_result = None
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""


# ---------------------------------------------------------------------------
# Dynamic Premium Error & Quota Exceeded Handler Component
# ---------------------------------------------------------------------------
def show_premium_error(error_msg: str):
    """
    Renders a stunning, premium dark-themed caution alert box for handling rate limits,
    invalid API keys, and server-side errors with detailed recovery actions.
    """
    err_str = str(error_msg)
    
    # 1. Detect if it's a Quota/Rate Limit (429) error
    if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower() or "resourceexhausted" in err_str.lower():
        st.markdown(
            f"""
            <div class="metric-card" style="border: 2px solid #F43F5E; background: rgba(244, 63, 94, 0.05) !important; padding: 1.5rem !important;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.75rem;">⚠️</span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700; color: #F43F5E;">
                        Gemini API Quota Exceeded (429)
                    </span>
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #E2E8F0; line-height: 1.6;">
                    <p style="margin-top: 0; color: #E2E8F0;">You have exceeded your Gemini API rate limit or daily free tier allocation.</p>
                    <div style="background: rgba(0, 0, 0, 0.4); border-radius: 8px; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #FDA4AF; overflow-x: auto;">
                        {err_str}
                    </div>
                    <h4 style="color: #F87171; font-family: 'Outfit', sans-serif; margin: 1rem 0 0.5rem 0; font-weight: 600;">💡 How to Fix and Improve This:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #CBD5E1;">
                        <li style="margin-bottom: 0.5rem;">
                            <b>Wait 60 Seconds:</b> The free-tier has a 15 Requests-Per-Minute (RPM) limit. Wait a brief moment and retry your action.
                        </li>
                        <li style="margin-bottom: 0.5rem;">
                            <b>Set up Billing in Google AI Studio:</b> Go to <a href="https://aistudio.google.com/" target="_blank" style="color: #38BDF8; text-decoration: none; font-weight: 500;">Google AI Studio</a>. By enabling a Pay-As-You-Go billing plan, you get vast quotas with generous, free monthly usage tiers!
                        </li>
                        <li style="margin-bottom: 0.5rem;">
                            <b>Use a Custom API Key:</b> Paste your own unique API Key inside the <b>⚙️ API Settings</b> in the sidebar to prevent sharing limits with other users.
                        </li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # 2. Detect if it's an Invalid API Key error
    elif "api key" in err_str.lower() or "invalid key" in err_str.lower() or "unauthorized" in err_str.lower() or "api_key" in err_str.lower() or "400" in err_str or "403" in err_str:
        st.markdown(
            f"""
            <div class="metric-card" style="border: 2px solid #F59E0B; background: rgba(245, 158, 11, 0.05) !important; padding: 1.5rem !important;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;">
                    <span style="font-size: 1.75rem;">🔑</span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700; color: #F59E0B;">
                        Invalid or Inactive API Key
                    </span>
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #E2E8F0; line-height: 1.6;">
                    <p style="margin-top: 0; color: #E2E8F0;">The Gemini API Key provided is either invalid, expired, or has not been activated yet.</p>
                    <div style="background: rgba(0, 0, 0, 0.4); border-radius: 8px; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #FDE047; overflow-x: auto;">
                        {err_str}
                    </div>
                    <h4 style="color: #FBBF24; font-family: 'Outfit', sans-serif; margin: 1rem 0 0.5rem 0; font-weight: 600;">💡 How to Fix:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #CBD5E1;">
                        <li style="margin-bottom: 0.5rem;">
                            Go to <a href="https://aistudio.google.com/" target="_blank" style="color: #38BDF8; text-decoration: none; font-weight: 500;">Google AI Studio</a>, generate a fresh API key, and paste it into the <b>⚙️ API Settings</b> section in the sidebar.
                        </li>
                        <li style="margin-bottom: 0.5rem;">
                            Ensure there are no leading or trailing whitespace characters in the pasted key.
                        </li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # 3. Generic Error Card
    st.markdown(
        f"""
        <div class="metric-card" style="border: 2px solid #F43F5E; background: rgba(244, 63, 94, 0.05) !important; padding: 1.5rem !important;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.75rem;">
                <span style="font-size: 1.75rem;">❌</span>
                <span style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700; color: #F43F5E;">
                    Execution Error
                </span>
            </div>
            <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #E2E8F0; line-height: 1.6;">
                <p style="margin-top: 0; color: #E2E8F0;">An error occurred while executing the request:</p>
                <div style="background: rgba(0, 0, 0, 0.4); border-radius: 8px; padding: 0.75rem; border: 1px solid rgba(255, 255, 255, 0.05); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #FDA4AF; overflow-x: auto;">
                    {err_str}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------------
# Sidebar UI & Resume Uploading
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="font-family:'Outfit', sans-serif; font-size:2.0rem; font-weight:900; background: linear-gradient(135deg, #A78BFA 0%, #4E65FF 50%, #06B6D4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; text-shadow: 0 4px 15px rgba(124, 58, 237, 0.2);">
            Prep4Interview 🚀
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption(f"Session ID: `{st.session_state.session_id[:8]}...`")

    st.divider()
    st.markdown("#### 📄 Upload Your Resume")
    uploaded = st.file_uploader("Select Resume PDF", type=["pdf"])
    
    if uploaded:
        if st.session_state.resume_name != uploaded.name:
            with st.spinner("Processing & Parsing PDF..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/upload",
                        files={"file": (uploaded.name, uploaded.read(), "application/pdf")},
                    )
                    if resp.ok:
                        data = resp.json()
                        st.session_state.uploaded_file_path = data["file_path"]
                        st.session_state.resume_text = data.get("extracted_text", "")
                        st.session_state.resume_name = uploaded.name
                        st.success(f"✅ {uploaded.name} loaded successfully!")
                    else:
                        st.error("Failed to parse and upload resume.")
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

    # Resume Load Badge
    if st.session_state.resume_text:
        st.markdown(
            f"""
            <div class="metric-card" style="padding:0.75rem; margin-top:1rem; border-color:#00E676;">
                <span style="color:#00E676; font-weight:bold;">🟢 RESUME CONNECTED</span><br/>
                <span style="font-size:0.85rem; color:#A0AEC0;">File: {st.session_state.resume_name}</span><br/>
                <span style="font-size:0.85rem; color:#A0AEC0;">Length: {len(st.session_state.resume_text)} characters</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🗑️ Clear Resume"):
            st.session_state.uploaded_file_path = None
            st.session_state.resume_text = ""
            st.session_state.resume_name = ""
            st.session_state.builder_result = None
            st.rerun()

    st.divider()
    st.markdown("#### ⚙️ API Settings")
    api_key_input = st.text_input(
        "Gemini API Key:",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIzaSy...",
        help="Your API key is stored securely in your browser's session state and is never logged or saved to the server filesystem."
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input.strip()
    else:
        st.session_state.gemini_api_key = ""

    if st.session_state.gemini_api_key:
        st.success("🔑 API Key configured!")
    else:
        st.warning("⚠️ Using backend default key.")

    st.divider()
    with st.expander("❓ How to Run & Use the LLM", expanded=False):
        st.markdown(
            """
            Follow these instructions to configure and run the **Prep4Interview** LLM:
            
            1. **Obtain Gemini API Key**: Go to [Google AI Studio](https://aistudio.google.com/) to get a free API Key.
            2. **Enter the API Key**: Paste the key into the **⚙️ API Settings** section above. It is fully masked and secure.
            3. **Upload Your Resume**: Select a PDF copy of your resume to initialize your candidate profile.
            4. **Explore Prep4Interview**:
               - 🎭 **Mock Interview**: Practice persona-based mock interviews.
               - 💬 **Coach Chat**: Ask career/technical questions.
               - 🎯 **Job Fit Matcher**: Match compatibility against a JD.
               - ✍ **Resume Tailoring**: Quantify achievements and re-route your resume.
            """
        )

    st.divider()
    if st.button("🔄 Reset Current Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.history = []
        st.session_state.uploaded_file_path = None
        st.session_state.resume_text = ""
        st.session_state.resume_name = ""
        st.session_state.builder_result = None
        st.session_state.gemini_api_key = ""
        st.success("Session reset!")
        st.rerun()

# ---------------------------------------------------------------------------
# Main Header Layout
# ---------------------------------------------------------------------------
st.markdown('<div class="main-title">Prep4Interview</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Prepare for mock interviews, analyze job suitability, explain git repos, and optimize your resume for target roles.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Application Workspaces (Tabs)
# ---------------------------------------------------------------------------
tab_mock, tab_chat, tab_suitability, tab_questions, tab_github, tab_builder = st.tabs([
    "🎭 Interactive Mock Interview",
    "💬 Interview Coach Chat",
    "🎯 Job Fit Matcher",
    "❓ Predicted Q&A Cards",
    "📁 GitHub Project Pitcher",
    "✍️ Resume Tailoring Builder"
])

# ---------------------------------------------------------------------------
# Tab 0: Interactive Mock Interview Simulator
# ---------------------------------------------------------------------------
with tab_mock:
    st.markdown("### 🎭 Timed Interactive Mock Interview Simulator")
    st.markdown(
        "Simulate a live, challenging job interview. Choose your interviewer's persona, role focus, "
        "and get a detailed performance scorecard with a grade and optimized STAR rewrites at the end!"
    )

    # Initialize mock session state variables
    if "mock_active" not in st.session_state:
        st.session_state.mock_active = False
    if "mock_history" not in st.session_state:
        st.session_state.mock_history = []
    if "mock_question_count" not in st.session_state:
        st.session_state.mock_question_count = 0
    if "mock_scorecard" not in st.session_state:
        st.session_state.mock_scorecard = None
    if "mock_persona" not in st.session_state:
        st.session_state.mock_persona = "Tough Tech Lead"
    if "mock_type" not in st.session_state:
        st.session_state.mock_type = "Technical"
    if "mock_role" not in st.session_state:
        st.session_state.mock_role = "Backend Engineer"
    if "mock_max_q" not in st.session_state:
        st.session_state.mock_max_q = 3

    if not st.session_state.resume_text:
        st.warning("⚠️ **No resume uploaded.** Please upload a resume PDF in the sidebar to start a simulated mock interview.")
    else:
        if not st.session_state.mock_active and st.session_state.mock_scorecard is None:
            # Interview Setup Panel
            st.markdown("#### ⚙️ Configure Your Simulation")
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.mock_persona = st.selectbox(
                    "Interviewer Persona:",
                    ["Tough Tech Lead", "Friendly Mentor", "Fast-Paced Recruiter"],
                    help="Tough Tech Lead asks granular technical details. Friendly Mentor guides you with hints. Fast-Paced Recruiter looks for high-level impact and behavioral fit."
                )
                st.session_state.mock_type = st.selectbox(
                    "Interview Mode:",
                    ["Technical", "Behavioral", "System Design"],
                    help="Technical focuses on coding/algorithms, Behavioral on STAR achievements, and System Design on scaling architectures."
                )
            with col2:
                st.session_state.mock_role = st.text_input(
                    "Target Role Name:",
                    value="Backend Engineer",
                    placeholder="e.g. Frontend Engineer, Product Manager..."
                )
                st.session_state.mock_max_q = st.slider(
                    "Number of Questions:",
                    min_value=2,
                    max_value=5,
                    value=3,
                    help="Select how many questions the interviewer should ask you."
                )
            if st.button("🚀 Start Mock Interview", type="primary", use_container_width=True):
                st.session_state.mock_active = True
                st.session_state.mock_history = []
                st.session_state.mock_question_count = 0
                st.session_state.mock_scorecard = None
                st.rerun()

        elif st.session_state.mock_active:
            # Active Simulation Console
            st.markdown(f"#### 🎙️ Live Mock Interview — Round {st.session_state.mock_question_count + 1} of {st.session_state.mock_max_q}")
            
            st.markdown(
                f"""
                <span style="background-color:#1A1F2C; border: 1px solid #4E65FF; color:#66FCF1; padding: 4px 10px; border-radius: 4px; font-size:0.85rem; font-weight:bold;">
                    👤 {st.session_state.mock_persona} · {st.session_state.mock_type} · Role: {st.session_state.mock_role}
                </span>
                """,
                unsafe_allow_html=True
            )
            st.write("")

            # Render full conversation flow
            for turn in st.session_state.mock_history:
                with st.chat_message(turn["role"]):
                    st.markdown(turn["content"])

            # If history is empty, stream the first question
            if not st.session_state.mock_history:
                with st.chat_message("assistant"):
                    payload = {
                        "resume_text": st.session_state.resume_text,
                        "interview_type": st.session_state.mock_type,
                        "persona": st.session_state.mock_persona,
                        "history": [],
                        "max_questions": st.session_state.mock_max_q,
                        "api_key": st.session_state.gemini_api_key
                    }
                    def stream_first_q():
                        try:
                            resp = requests.post(f"{API_BASE}/mock_interview/next_stream", json=payload, stream=True, timeout=90)
                            resp.raise_for_status()
                            for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    yield chunk
                        except Exception as e:
                            yield f"❌ **Failed to start simulator**: {e}"
                    
                    full_ans = st.write_stream(stream_first_q())
                    if "❌" in full_ans or "ERROR:" in full_ans or "429" in full_ans:
                        st.session_state.mock_active = False
                        st.session_state.mock_history = []
                        st.session_state.mock_question_count = 0
                        show_premium_error(full_ans)
                    else:
                        st.session_state.mock_history.append({"role": "assistant", "content": full_ans})
                        st.rerun()

            # If the last message was user response, stream follow-up or finish
            elif st.session_state.mock_history[-1]["role"] == "user":
                if st.session_state.mock_question_count + 1 >= st.session_state.mock_max_q:
                    # Time to score the interview!
                    st.session_state.mock_active = False
                    with st.spinner("🎉 All rounds complete! Composing your performance scorecard & custom reviews..."):
                        payload = {
                            "resume_text": st.session_state.resume_text,
                            "target_role": st.session_state.mock_role,
                            "history": st.session_state.mock_history,
                            "api_key": st.session_state.gemini_api_key
                        }
                        try:
                            resp = requests.post(f"{API_BASE}/mock_interview/scorecard", json=payload, timeout=120)
                            resp.raise_for_status()
                            st.session_state.mock_scorecard = resp.json()
                            st.rerun()
                        except Exception as e:
                            st.session_state.mock_active = False
                            st.session_state.mock_history = []
                            st.session_state.mock_question_count = 0
                            show_premium_error(f"Failed to compile scorecard: {e}")
                else:
                    st.session_state.mock_question_count += 1
                    with st.chat_message("assistant"):
                        payload = {
                            "resume_text": st.session_state.resume_text,
                            "interview_type": st.session_state.mock_type,
                            "persona": st.session_state.mock_persona,
                            "history": st.session_state.mock_history,
                            "max_questions": st.session_state.mock_max_q,
                            "api_key": st.session_state.gemini_api_key
                        }
                        def stream_next_q():
                            try:
                                resp = requests.post(f"{API_BASE}/mock_interview/next_stream", json=payload, stream=True, timeout=90)
                                resp.raise_for_status()
                                for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                                    if chunk:
                                        yield chunk
                            except Exception as e:
                                yield f"❌ **Failed to load next turn**: {e}"
                        
                        full_ans = st.write_stream(stream_next_q())
                        if "❌" in full_ans or "ERROR:" in full_ans or "429" in full_ans:
                            st.session_state.mock_active = False
                            st.session_state.mock_history = []
                            st.session_state.mock_question_count = 0
                            show_premium_error(full_ans)
                        else:
                            st.session_state.mock_history.append({"role": "assistant", "content": full_ans})
                            st.rerun()

            # Chat input at bottom
            if st.session_state.mock_history and st.session_state.mock_history[-1]["role"] == "assistant":
                user_ans = st.chat_input("Write your response to the interviewer's question...")
                if user_ans:
                    st.session_state.mock_history.append({"role": "user", "content": user_ans})
                    st.rerun()

            # Safety restart button
            st.write("")
            if st.button("🚪 Quit Simulation", type="secondary", use_container_width=True):
                st.session_state.mock_active = False
                st.session_state.mock_history = []
                st.session_state.mock_question_count = 0
                st.session_state.mock_scorecard = None
                st.rerun()

        elif st.session_state.mock_scorecard is not None:
            # Scorecard Render Panel
            sc = st.session_state.mock_scorecard
            grade = sc.get("grade", "B")
            grade_colors = {
                "A+": "#00E676", "A": "#00E676",
                "B+": "#FFD740", "B": "#FFD740",
                "C+": "#FF8F00", "C": "#FF8F00",
                "D": "#FF5252", "F": "#FF5252"
            }
            color = grade_colors.get(grade[:2].strip(), "#66FCF1")

            st.markdown("### 🏆 Performance Scorecard")
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; border-color: {color};">
                    <span style="font-size: 1.2rem; color: #A0AEC0; font-weight: 500;">MOCK INTERVIEW GRADE</span><br/>
                    <span style="font-size: 5rem; font-weight: 800; color: {color}; line-height: 1;">{grade}</span><br/>
                    <span style="font-size: 0.95rem; color: #C5C6C7;">Simulated for {st.session_state.mock_role}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### 🎯 Overall Evaluation Summary")
            st.info(sc.get("overall_summary", "Excellent effort during the interview simulation."))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<span class="strength-header">👍 Communication & Skill Strengths</span>', unsafe_allow_html=True)
                for s in sc.get("strengths", []):
                    st.markdown(f"- {s}")
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<span class="gap-header">👎 Core Improvement Areas & Gaps</span>', unsafe_allow_html=True)
                for g in sc.get("gaps", []):
                    st.markdown(f"- {g}")
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("### 📝 Granular Answer Critiques & Model STAR Rewrites")
            for rev in sc.get("answers_review", []):
                q_num = rev.get("question_number", 1)
                with st.expander(f"⭐ Turn {q_num}: {rev.get('question')[:80]}..."):
                    st.markdown(f"**Question Asked:**\n*{rev.get('question')}*\n")
                    st.markdown(f"**Your Response:**\n_{rev.get('user_answer')}_\n")
                    st.divider()
                    st.markdown(f"**💡 Constructive Critique:**\n{rev.get('critique')}\n")
                    st.markdown('<div style="background-color:#1A1F2C; border-left: 4px solid #66FCF1; padding: 15px; border-radius: 4px;">', unsafe_allow_html=True)
                    st.markdown(f"**🚀 Flawless STAR Rewrite:**\n{rev.get('model_answer')}")
                    st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            if st.button("🔄 Start a New Mock Interview", type="primary", use_container_width=True):
                st.session_state.mock_active = False
                st.session_state.mock_history = []
                st.session_state.mock_question_count = 0
                st.session_state.mock_scorecard = None
                st.rerun()

# ---------------------------------------------------------------------------
# Tab 1: Interview Coach Chat
# ---------------------------------------------------------------------------
with tab_chat:
    st.markdown("### 💬 Chat with your Personal Career Coach")
    st.markdown(
        "Ask questions about your career, practice interview topics, or ask detailed questions about "
        "your uploaded resume. If you mention a GitHub link, the AI will explain your project code!"
    )

    # Historical messages
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New chat input
    user_query = st.chat_input("Ask a question, practice a topic, or request feedback...")
    if user_query:
        st.session_state.history.append({"role": "user", "content": user_query})
        st.rerun()

    # If the last message was a user query, stream the coach's response!
    if st.session_state.history and st.session_state.history[-1]["role"] == "user":
        with st.chat_message("assistant"):
            payload = {
                "session_id": st.session_state.session_id,
                "user_input": st.session_state.history[-1]["content"],
                "uploaded_file_path": st.session_state.uploaded_file_path,
                "api_key": st.session_state.gemini_api_key
            }
            def stream_coach():
                try:
                    resp = requests.post(f"{API_BASE}/chat/stream", json=payload, stream=True, timeout=90)
                    resp.raise_for_status()
                    for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            yield chunk
                except Exception as e:
                    yield f"❌ **Failed to load response**: {e}"
            
            full_ans = st.write_stream(stream_coach())
            if "❌" in full_ans or "ERROR:" in full_ans or "429" in full_ans:
                if st.session_state.history:
                    st.session_state.history.pop()  # remove failed question from view
                show_premium_error(full_ans)
            else:
                st.session_state.history.append({"role": "assistant", "content": full_ans})
                st.rerun()
# ---------------------------------------------------------------------------
# Tab 2: Job Fit Matcher
# ---------------------------------------------------------------------------
with tab_suitability:
    st.markdown("### 🎯 Resume-to-Job Fit Compatibility Matcher")
    st.markdown(
        "Paste the Job Description (JD) of a role you are interested in below. The AI will evaluate "
        "your resume, calculate a matching score, map keywords, and identify exactly what gaps to fix."
    )

    if not st.session_state.resume_text:
        st.warning("⚠️ **No resume uploaded.** Please upload a resume PDF in the sidebar to use the Suitability Matcher.")
    else:
        job_desc_input = st.text_area(
            "Paste Target Job Description (JD) here:",
            height=250,
            placeholder="We are looking for a Software Engineer with 3+ years experience in Python, FastAPI, and cloud systems..."
        )
        
        if st.button("🚀 Evaluate Job Compatibility", type="primary", use_container_width=True):
            if not job_desc_input.strip():
                st.error("Please paste a valid Job Description first.")
            else:
                with st.spinner("Analyzing compatibility and mapping keywords..."):
                    payload = {
                        "session_id": st.session_state.session_id,
                        "user_id": "candidate",
                        "user_input": f"Compare my resume against this Job Description:\n{job_desc_input}",
                        "uploaded_file_path": st.session_state.uploaded_file_path,
                        "api_key": st.session_state.gemini_api_key
                    }
                    try:
                        resp = requests.post(f"{API_BASE}/run", json=payload, timeout=90)
                        resp.raise_for_status()
                        data = resp.json()
                        
                        if data.get("error"):
                            show_premium_error(data['error'])
                        else:
                            # Try to extract the structured metadata returned
                            structured = data.get("structured_output") or {}
                            
                            # Render Compatibility Score Gauge
                            score = structured.get("score", 0)
                            score_color = "#FF5252" if score < 50 else ("#FFD740" if score < 75 else "#00E676")
                            
                            st.markdown(
                                f"""
                                <div class="metric-card" style="text-align: center; border-color: {score_color};">
                                    <span style="font-size: 1.2rem; color: #A0AEC0; font-weight: 500;">COMPATIBILITY MATCH SCORE</span><br/>
                                    <span style="font-size: 4rem; font-weight: 800; color: {score_color};">{score}%</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Render Columns for Strengths, Gaps, and Tips
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.markdown('<span class="strength-header">🎯 Strengths & Job Match Points</span>', unsafe_allow_html=True)
                                for match in structured.get("matches", []):
                                    st.markdown(f"- {match}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                            with col2:
                                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                                st.markdown('<span class="gap-header">⚠️ Skill Gaps & Missing Keywords</span>', unsafe_allow_html=True)
                                for gap in structured.get("gaps", []):
                                    st.markdown(f"- {gap}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.markdown('<span class="rec-header">💡 Actionable Resume Improvements</span>', unsafe_allow_html=True)
                            for rec in structured.get("recommendations", []):
                                st.markdown(f"- {rec}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.subheader("🔍 Recruiter's Deep-Dive Analysis")
                            st.markdown(structured.get("detailed_analysis", "No text explanation available."))
                    except Exception as e:
                        show_premium_error(f"Connection failed: {e}")

# ---------------------------------------------------------------------------
# Tab 3: Predicted Q&A Cards
# ---------------------------------------------------------------------------
with tab_questions:
    st.markdown("### ❓ Predicted Interview Questions & STAR Answer Guides")
    st.markdown(
        "Generate custom behavioral, system design, and deep technical questions targeted specifically "
        "to your experiences. Paste an optional job description to tailor the interview focus."
    )

    if not st.session_state.resume_text:
        st.warning("⚠️ **No resume uploaded.** Please upload a resume PDF in the sidebar to generate mock questions.")
    else:
        tailor_jd = st.text_area(
            "Paste Job Description to tailor questions (Optional):",
            height=120,
            placeholder="Leave empty for general questions based strictly on your resume..."
        )
        
        if st.button("🔍 Predict Customized Questions", type="primary", use_container_width=True):
            with st.spinner("Analyzing project experience and generating STAR guides..."):
                user_msg = "Generate predicted interview questions and answers based on my resume."
                if tailor_jd.strip():
                    user_msg += f"\nTailor questions to this job description:\n{tailor_jd}"
                    
                payload = {
                    "session_id": st.session_state.session_id,
                    "user_id": "candidate",
                    "user_input": user_msg,
                    "uploaded_file_path": st.session_state.uploaded_file_path,
                    "api_key": st.session_state.gemini_api_key
                }
                try:
                    resp = requests.post(f"{API_BASE}/run", json=payload, timeout=90)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    if data.get("error"):
                        show_premium_error(data['error'])
                    else:
                        structured = data.get("structured_output") or {}
                        questions = structured.get("questions", [])
                        
                        if not questions:
                            st.warning("Could not extract structured questions. Displaying text response instead:")
                            st.markdown(data.get("draft_output", ""))
                        else:
                            st.markdown("### 📚 Tailored Practice Cards")
                            st.caption("Click on any predicted question to reveal the recommended STAR format answer guide.")
                            
                            for q in questions:
                                q_id = q.get("id", 1)
                                q_text = q.get("question", "")
                                category = q.get("category", "Technical")
                                model_ans = q.get("model_answer", "")
                                
                                with st.expander(f"🛡️ {category} · Question {q_id}: {q_text}"):
                                    st.markdown(f"**Best Practice STAR Answer:**")
                                    st.markdown(model_ans)
                except Exception as e:
                    show_premium_error(f"Connection failed: {e}")

# ---------------------------------------------------------------------------
# Tab 4: GitHub Project Pitcher
# ---------------------------------------------------------------------------
with tab_github:
    st.markdown("### 📁 GitHub Project Explainer & Pitch Assistant")
    st.markdown(
        "Enter the public URL of one of your GitHub repositories. The AI will parse the codebase README, "
        "break down its stack, formulate an interview pitch, and prepare you to present it."
    )

    # Initialize GitHub Mock Session variables
    if "git_analysis" not in st.session_state:
        st.session_state.git_analysis = ""
    if "git_repo_name" not in st.session_state:
        st.session_state.git_repo_name = ""
    if "git_mock_active" not in st.session_state:
        st.session_state.git_mock_active = False
    if "git_mock_history" not in st.session_state:
        st.session_state.git_mock_history = []
    if "git_mock_round" not in st.session_state:
        st.session_state.git_mock_round = 0
    if "git_mock_scorecard" not in st.session_state:
        st.session_state.git_mock_scorecard = None

    git_url_input = st.text_input(
        "Enter Public GitHub Repository Link:",
        placeholder="https://github.com/username/project-repository"
    )

    if st.button("💡 Analyze Repository & Build Pitch", type="primary", use_container_width=True):
        if not git_url_input.strip():
            st.error("Please enter a valid GitHub URL.")
        else:
            with st.spinner("Fetching README.md content and running code diagnostics..."):
                payload = {
                    "session_id": st.session_state.session_id,
                    "user_id": "candidate",
                    "user_input": f"Analyze this GitHub link and explain the project: {git_url_input}",
                    "uploaded_file_path": None,
                    "api_key": st.session_state.gemini_api_key
                }
                try:
                    resp = requests.post(f"{API_BASE}/run", json=payload, timeout=90)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    if data.get("error"):
                        show_premium_error(data['error'])
                    else:
                        st.session_state.git_analysis = data.get("draft_output", "")
                        # Simple extraction of repo name from URL
                        parts = git_url_input.rstrip("/").split("/")
                        st.session_state.git_repo_name = parts[-1].replace(".git", "") if parts else "Repository"
                        
                        # Reset any active project mock sessions
                        st.session_state.git_mock_active = False
                        st.session_state.git_mock_history = []
                        st.session_state.git_mock_round = 0
                        st.session_state.git_mock_scorecard = None
                        st.rerun()
                except Exception as e:
                    show_premium_error(f"Connection failed: {e}")

    # Render results & simulator if analysis exists
    if st.session_state.git_analysis:
        st.markdown(st.session_state.git_analysis)
        st.divider()
        
        # -------------------------------------------------------------------
        # "Grill Me on My Code" Sub-Console
        # -------------------------------------------------------------------
        st.markdown("### 🎮 'Grill Me on My Code' Codebase Defense Simulator")
        st.markdown(
            "Ready to present this repository in a real interview? A **Tough Tech Lead** will ask you 3 customized questions "
            "challenging your architecture decisions, database queries, and stack implementations."
        )
        
        if not st.session_state.git_mock_active and st.session_state.git_mock_scorecard is None:
            if st.button("🎙️ Start Codebase Mastery Grilling", type="primary", use_container_width=True):
                st.session_state.git_mock_active = True
                st.session_state.git_mock_history = []
                st.session_state.git_mock_round = 0
                st.session_state.git_mock_scorecard = None
                st.rerun()
                
        elif st.session_state.git_mock_active:
            st.markdown(f"#### 🎙️ Codebase Grilling — Question {st.session_state.git_mock_round + 1} of 3")
            
            for turn in st.session_state.git_mock_history:
                with st.chat_message(turn["role"]):
                    st.markdown(turn["content"])

            # If history is empty, stream the first question
            if not st.session_state.git_mock_history:
                with st.chat_message("assistant"):
                    payload = {
                        "resume_text": st.session_state.git_analysis,
                        "interview_type": "GitHub Codebase Technical Q&A",
                        "persona": "Tough Tech Lead",
                        "history": [],
                        "max_questions": 3,
                        "api_key": st.session_state.gemini_api_key
                    }
                    def stream_first_git_q():
                        try:
                            resp = requests.post(f"{API_BASE}/mock_interview/next_stream", json=payload, stream=True, timeout=90)
                            resp.raise_for_status()
                            for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                                if chunk:
                                    yield chunk
                        except Exception as e:
                            yield f"❌ **Failed to start project grilling**: {e}"
                    
                    full_ans = st.write_stream(stream_first_git_q())
                    if "❌" in full_ans or "error" in full_ans.lower() or "failed" in full_ans.lower():
                        st.session_state.git_mock_active = False
                        st.session_state.git_mock_history = []
                        st.session_state.git_mock_round = 0
                        show_premium_error(full_ans)
                    else:
                        st.session_state.git_mock_history.append({"role": "assistant", "content": full_ans})
                        st.rerun()

            # If the last message was a user answer, stream next question or scorecard
            elif st.session_state.git_mock_history[-1]["role"] == "user":
                if st.session_state.git_mock_round + 1 >= 3:
                    st.session_state.git_mock_active = False
                    with st.spinner("Evaluating your codebase defense and formulating scorecard..."):
                        payload = {
                            "resume_text": st.session_state.git_analysis,
                            "target_role": f"Developer of {st.session_state.git_repo_name}",
                            "history": st.session_state.git_mock_history,
                            "api_key": st.session_state.gemini_api_key
                        }
                        try:
                            resp = requests.post(f"{API_BASE}/mock_interview/scorecard", json=payload, timeout=120)
                            resp.raise_for_status()
                            st.session_state.git_mock_scorecard = resp.json()
                            st.rerun()
                        except Exception as e:
                            st.session_state.git_mock_active = False
                            st.session_state.git_mock_history = []
                            st.session_state.git_mock_round = 0
                            show_premium_error(f"Failed to compile scorecard: {e}")
                else:
                    st.session_state.git_mock_round += 1
                    with st.chat_message("assistant"):
                        payload = {
                            "resume_text": st.session_state.git_analysis,
                            "interview_type": "GitHub Codebase Technical Q&A",
                            "persona": "Tough Tech Lead",
                            "history": st.session_state.git_mock_history,
                            "max_questions": 3,
                            "api_key": st.session_state.gemini_api_key
                        }
                        def stream_next_git_q():
                            try:
                                resp = requests.post(f"{API_BASE}/mock_interview/next_stream", json=payload, stream=True, timeout=90)
                                resp.raise_for_status()
                                for chunk in resp.iter_content(chunk_size=None, decode_unicode=True):
                                    if chunk:
                                        yield chunk
                            except Exception as e:
                                yield f"❌ **Failed to load next grilling question**: {e}"
                        
                        full_ans = st.write_stream(stream_next_git_q())
                        if "❌" in full_ans or "error" in full_ans.lower() or "failed" in full_ans.lower():
                            st.session_state.git_mock_active = False
                            st.session_state.git_mock_history = []
                            st.session_state.git_mock_round = 0
                            show_premium_error(full_ans)
                        else:
                            st.session_state.git_mock_history.append({"role": "assistant", "content": full_ans})
                            st.rerun()

            # Input at bottom
            if st.session_state.git_mock_history and st.session_state.git_mock_history[-1]["role"] == "assistant":
                user_ans = st.chat_input("Explain your codebase decisions to the Tech Lead...")
                if user_ans:
                    st.session_state.git_mock_history.append({"role": "user", "content": user_ans})
                    st.rerun()
                            
            st.write("")
            if st.button("Aborted Grilling Session", type="secondary", use_container_width=True):
                st.session_state.git_mock_active = False
                st.session_state.git_mock_history = []
                st.session_state.git_mock_round = 0
                st.session_state.git_mock_scorecard = None
                st.rerun()
                
        elif st.session_state.git_mock_scorecard is not None:
            sc = st.session_state.git_mock_scorecard
            grade = sc.get("grade", "B")
            grade_colors = {
                "A+": "#00E676", "A": "#00E676",
                "B+": "#FFD740", "B": "#FFD740",
                "C+": "#FF8F00", "C": "#FF8F00",
                "D": "#FF5252", "F": "#FF5252"
            }
            color = grade_colors.get(grade[:2].strip(), "#66FCF1")
            
            st.markdown(
                f"""
                <div class="metric-card" style="text-align: center; border-color: {color};">
                    <span style="font-size: 1.1rem; color: #A0AEC0; font-weight: 500;">CODEBASE DEFENSE GRADE</span><br/>
                    <span style="font-size: 4rem; font-weight: 800; color: {color}; line-height: 1;">{grade}</span><br/>
                    <span style="font-size: 0.85rem; color: #C5C6C7;">Project: {st.session_state.git_repo_name}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("#### 🎯 Codebase Defense Summary")
            st.info(sc.get("overall_summary", "Review complete."))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<span class="strength-header">👍 Correct Architectural Decisions</span>', unsafe_allow_html=True)
                for s in sc.get("strengths", []):
                    st.markdown(f"- {s}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<span class="gap-header">👎 Design Vulnerabilities & Gaps</span>', unsafe_allow_html=True)
                for g in sc.get("gaps", []):
                    st.markdown(f"- {g}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            st.markdown("### 📝 Granular Critiques & Perfect Design STAR Rewrites")
            for rev in sc.get("answers_review", []):
                q_num = rev.get("question_number", 1)
                with st.expander(f"⭐ Question {q_num}: {rev.get('question')[:80]}..."):
                    st.markdown(f"**Question Asked:**\n*{rev.get('question')}*\n")
                    st.markdown(f"**Your Answer:**\n_{rev.get('user_answer')}_\n")
                    st.divider()
                    st.markdown(f"**💡 Recruiter Critique:**\n{rev.get('critique')}\n")
                    st.markdown('<div style="background-color:#1A1F2C; border-left: 4px solid #66FCF1; padding: 15px; border-radius: 4px;">', unsafe_allow_html=True)
                    st.markdown(f"**🚀 Perfect Architectural Pitch:**\n{rev.get('model_answer')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            st.write("")
            if st.button("🔄 Try Codebase Grilling Again", type="primary", use_container_width=True):
                st.session_state.git_mock_active = False
                st.session_state.git_mock_history = []
                st.session_state.git_mock_round = 0
                st.session_state.git_mock_scorecard = None
                st.rerun()

# ---------------------------------------------------------------------------
# Tab 5 Helper Functions: Pixel-Perfect Resume Renderers
# ---------------------------------------------------------------------------

def render_resume_inner(resume_data: dict) -> str:
    name = resume_data.get("name", "CHANDRASHEKHARA K M")
    contact = resume_data.get("contact_info", {})
    summary = resume_data.get("professional_summary", "")
    education = resume_data.get("education", [])
    experience = resume_data.get("work_experience", [])
    skills = resume_data.get("skills", {})
    projects = resume_data.get("featured_projects", [])
    additional_projects = resume_data.get("additional_projects", [])
    certifications = resume_data.get("certifications_and_achievements", [])
    
    # Helper to build contact string
    contact_parts = []
    if contact.get("location"): contact_parts.append(contact["location"])
    if contact.get("phone"): contact_parts.append(contact["phone"])
    if contact.get("email"): contact_parts.append(contact["email"])
    if contact.get("linkedin"): contact_parts.append(f"LinkedIn: {contact['linkedin']}")
    if contact.get("github"): contact_parts.append(f"GitHub: {contact['github']}")
    contact_str = " | ".join(contact_parts)
    
    # CSS rules scoped to a single container to prevent global styles pollution
    css = """
        <style>
            .resume-preview-container {
                font-family: 'Times New Roman', Times, Georgia, serif !important;
                background-color: #ffffff !important;
                color: #111111 !important;
                padding: 40px !important;
                line-height: 1.35 !important;
                font-size: 13.5px !important;
            }
            .resume-preview-container h1, .resume-preview-container h2, .resume-preview-container h3 {
                color: #111111 !important;
                font-family: 'Times New Roman', Times, Georgia, serif !important;
                margin: 0 !important;
            }
            .resume-preview-container .header {
                text-align: center;
                margin-bottom: 12px;
            }
            .resume-preview-container .name {
                font-size: 26px !important;
                font-weight: bold !important;
                letter-spacing: 0.02em !important;
                margin: 0 0 3px 0 !important;
                text-transform: uppercase !important;
            }
            .resume-preview-container .contact {
                font-size: 11.5px !important;
                color: #222222 !important;
                margin: 0 !important;
            }
            .resume-preview-container .section {
                margin-top: 14px !important;
            }
            .resume-preview-container .section-title {
                font-size: 13.5px !important;
                font-weight: bold !important;
                text-transform: uppercase !important;
                margin: 0 0 4px 0 !important;
                letter-spacing: 0.05em !important;
                border-bottom: 1.5px solid #222222 !important;
                padding-bottom: 1px !important;
            }
            .resume-preview-container .row-split {
                display: flex !important;
                justify-content: space-between !important;
                align-items: baseline !important;
                margin-top: 3px !important;
            }
            .resume-preview-container .bold {
                font-weight: bold !important;
            }
            .resume-preview-container .italic {
                font-style: italic !important;
            }
            .resume-preview-container .summary-text {
                margin: 4px 0 0 0 !important;
                text-align: justify !important;
            }
            .resume-preview-container ul {
                margin: 3px 0 0 0 !important;
                padding-left: 20px !important;
                list-style-type: disc !important;
            }
            .resume-preview-container li {
                margin-bottom: 2px !important;
                text-align: justify !important;
                color: #111111 !important;
                display: list-item !important;
            }
            .resume-preview-container .skills-grid {
                margin-top: 4px !important;
            }
            .resume-preview-container .skills-line {
                margin-bottom: 3px !important;
            }
        </style>
    """
    
    html = css + f"""
    <div class="resume-preview-container">
        <div class="header">
            <h1 class="name">{name}</h1>
            <p class="contact">{contact_str}</p>
        </div>
    """
    
    if summary:
        html += f"""
        <div class="section">
            <h2 class="section-title">Professional Summary</h2>
            <p class="summary-text">{summary}</p>
        </div>
        """
        
    if education:
        html += """
        <div class="section">
            <h2 class="section-title">Education</h2>
        """
        for edu in education:
            degree = edu.get("degree", "")
            inst = edu.get("institution", "")
            dt = edu.get("date", "")
            score = edu.get("score", "")
            
            html += f"""
            <div class="row-split">
                <span class="bold">{degree}</span>
                <span class="bold">{dt}</span>
            </div>
            <div class="row-split" style="margin-top: 0px;">
                <span class="italic">{inst}</span>
                <span class="bold">{score}</span>
            </div>
            """
        html += "</div>"
        
    if experience:
        html += """
        <div class="section">
            <h2 class="section-title">Work Experience</h2>
        """
        for exp in experience:
            company = exp.get("company", "")
            role = exp.get("role", "")
            loc = exp.get("location", "")
            dt = exp.get("date", "")
            bullets = exp.get("bullets", [])
            
            html += f"""
            <div class="row-split">
                <span class="bold">{company}</span>
                <span class="bold">{loc}</span>
            </div>
            <div class="row-split" style="margin-top: 0px; margin-bottom: 1px;">
                <span class="italic">{role}</span>
                <span class="italic">{dt}</span>
            </div>
            """
            if bullets:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"
        html += "</div>"
        
    if skills:
        html += """
        <div class="section">
            <h2 class="section-title">Technical Skills</h2>
            <div class="skills-grid">
        """
        if skills.get("languages"):
            html += f'<div class="skills-line"><span class="bold">Languages:</span> {skills["languages"]}</div>'
        if skills.get("tools"):
            html += f'<div class="skills-line"><span class="bold">Tools:</span> {skills["tools"]}</div>'
        if skills.get("python_ecosystem"):
            html += f'<div class="skills-line"><span class="bold">Python Ecosystem:</span> {skills["python_ecosystem"]}</div>'
        if skills.get("core_concepts"):
            html += f'<div class="skills-line"><span class="bold">Core Concepts:</span> {skills["core_concepts"]}</div>'
        html += """
            </div>
        </div>
        """
        
    if projects:
        html += """
        <div class="section">
            <h2 class="section-title">Featured Projects</h2>
        """
        for proj in projects:
            title = proj.get("title", "")
            stack = proj.get("tech_stack", "")
            bullets = proj.get("bullets", [])
            
            html += f"""
            <div class="row-split">
                <span class="bold">{title}</span>
                <span class="italic">{stack}</span>
            </div>
            """
            if bullets:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"
        html += "</div>"
        
    if additional_projects:
        html += """
        <div class="section">
            <h2 class="section-title">Additional Projects</h2>
            <ul>
        """
        for proj in additional_projects:
            title = proj.get("title", "")
            desc = proj.get("description", "")
            html += f"<li><span class='bold'>{title}:</span> {desc}</li>"
        html += """
            </ul>
        </div>
        """
        
    if certifications:
        html += """
        <div class="section">
            <h2 class="section-title">Certifications & Achievements</h2>
        """
        for cert in certifications:
            cat = cert.get("category", "")
            det = cert.get("details", "")
            html += f'<div style="margin-top: 3px;"><span class="bold">{cat}:</span> {det}</div>'
        html += "</div>"
        
    html += "</div>"
    return html


def render_resume_full_document(resume_data: dict) -> str:
    name = resume_data.get("name", "CHANDRASHEKHARA K M")
    contact = resume_data.get("contact_info", {})
    summary = resume_data.get("professional_summary", "")
    education = resume_data.get("education", [])
    experience = resume_data.get("work_experience", [])
    skills = resume_data.get("skills", {})
    projects = resume_data.get("featured_projects", [])
    additional_projects = resume_data.get("additional_projects", [])
    certifications = resume_data.get("certifications_and_achievements", [])
    
    # Helper to build contact string
    contact_parts = []
    if contact.get("location"): contact_parts.append(contact["location"])
    if contact.get("phone"): contact_parts.append(contact["phone"])
    if contact.get("email"): contact_parts.append(contact["email"])
    if contact.get("linkedin"): contact_parts.append(f"LinkedIn: {contact['linkedin']}")
    if contact.get("github"): contact_parts.append(f"GitHub: {contact['github']}")
    contact_str = " | ".join(contact_parts)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{name} - Tailored Resume</title>
    <style>
        body {{
            font-family: 'Times New Roman', Times, Georgia, serif;
            background-color: #ffffff;
            color: #111111;
            margin: 0 auto;
            max-width: 800px;
            padding: 30px;
            line-height: 1.35;
            font-size: 13.5px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 12px;
        }}
        .name {{
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 0.02em;
            margin: 0 0 3px 0;
            text-transform: uppercase;
        }}
        .contact {{
            font-size: 11.5px;
            color: #222222;
            margin: 0;
        }}
        .section {{
            margin-top: 14px;
        }}
        .section-title {{
            font-size: 13.5px;
            font-weight: bold;
            text-transform: uppercase;
            margin: 0 0 4px 0;
            letter-spacing: 0.05em;
            border-bottom: 1.5px solid #222222;
            padding-bottom: 1px;
        }}
        .row-split {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-top: 3px;
        }}
        .bold {{
            font-weight: bold;
        }}
        .italic {{
            font-style: italic;
        }}
        .summary-text {{
            margin: 4px 0 0 0;
            text-align: justify;
        }}
        ul {{
            margin: 3px 0 0 0;
            padding-left: 20px;
            list-style-type: disc;
        }}
        li {{
            margin-bottom: 2px;
            text-align: justify;
            color: #111111;
        }}
        .skills-grid {{
            margin-top: 4px;
        }}
        .skills-line {{
            margin-bottom: 3px;
        }}
        @media print {{
            body {{
                padding: 0 !important;
                margin: 0.5in !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="name">{name}</h1>
        <p class="contact">{contact_str}</p>
    </div>
"""

    if summary:
        html += f"""
    <div class="section">
        <h2 class="section-title">Professional Summary</h2>
        <p class="summary-text">{summary}</p>
    </div>
    """
        
    if education:
        html += """
    <div class="section">
        <h2 class="section-title">Education</h2>
    """
        for edu in education:
            degree = edu.get("degree", "")
            inst = edu.get("institution", "")
            dt = edu.get("date", "")
            score = edu.get("score", "")
            
            html += f"""
        <div class="row-split">
            <span class="bold">{degree}</span>
            <span class="bold">{dt}</span>
        </div>
        <div class="row-split" style="margin-top: 0px;">
            <span class="italic">{inst}</span>
            <span class="bold">{score}</span>
        </div>
        """
        html += "</div>"
        
    if experience:
        html += """
    <div class="section">
        <h2 class="section-title">Work Experience</h2>
    """
        for exp in experience:
            company = exp.get("company", "")
            role = exp.get("role", "")
            loc = exp.get("location", "")
            dt = exp.get("date", "")
            bullets = exp.get("bullets", [])
            
            html += f"""
        <div class="row-split">
            <span class="bold">{company}</span>
            <span class="bold">{loc}</span>
        </div>
        <div class="row-split" style="margin-top: 0px; margin-bottom: 1px;">
            <span class="italic">{role}</span>
            <span class="italic">{dt}</span>
        </div>
        """
            if bullets:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"
        html += "</div>"
        
    if skills:
        html += """
    <div class="section">
        <h2 class="section-title">Technical Skills</h2>
        <div class="skills-grid">
    """
        if skills.get("languages"):
            html += f'<div class="skills-line"><span class="bold">Languages:</span> {skills["languages"]}</div>'
        if skills.get("tools"):
            html += f'<div class="skills-line"><span class="bold">Tools:</span> {skills["tools"]}</div>'
        if skills.get("python_ecosystem"):
            html += f'<div class="skills-line"><span class="bold">Python Ecosystem:</span> {skills["python_ecosystem"]}</div>'
        if skills.get("core_concepts"):
            html += f'<div class="skills-line"><span class="bold">Core Concepts:</span> {skills["core_concepts"]}</div>'
        html += """
        </div>
    </div>
    """
        
    if projects:
        html += """
    <div class="section">
        <h2 class="section-title">Featured Projects</h2>
    """
        for proj in projects:
            title = proj.get("title", "")
            stack = proj.get("tech_stack", "")
            bullets = proj.get("bullets", [])
            
            html += f"""
        <div class="row-split">
            <span class="bold">{title}</span>
            <span class="italic">{stack}</span>
        </div>
        """
            if bullets:
                html += "<ul>"
                for b in bullets:
                    html += f"<li>{b}</li>"
                html += "</ul>"
        html += "</div>"
        
    if additional_projects:
        html += """
    <div class="section">
        <h2 class="section-title">Additional Projects</h2>
        <ul>
    """
        for proj in additional_projects:
            title = proj.get("title", "")
            desc = proj.get("description", "")
            html += f"<li><span class='bold'>{title}:</span> {desc}</li>"
        html += """
        </ul>
    </div>
    """
        
    if certifications:
        html += """
    <div class="section">
        <h2 class="section-title">Certifications & Achievements</h2>
    """
        for cert in certifications:
            cat = cert.get("category", "")
            det = cert.get("details", "")
            html += f'<div style="margin-top: 3px;"><span class="bold">{cat}:</span> {det}</div>'
        html += "</div>"
        
    html += """
    <script>
        window.onload = function() {
            window.print();
        }
    </script>
</body>
</html>
"""
    return html

# ---------------------------------------------------------------------------
# Tab 5: Resume Tailoring Builder & Exporter
# ---------------------------------------------------------------------------
with tab_builder:
    st.markdown("### ✍️ Role-Specific Resume Tailoring Builder & Exporter")
    st.markdown(
        "Specify your target professional role and review the **compiled professional resume live preview** below. "
        "Use the **Live Revision** card to customize details, add skills, or reword sentences, then click to download or print your clean, high-standard resume!"
    )

    # Sync with sidebar PDF text if a new file is uploaded
    if "prev_resume_text" not in st.session_state:
        st.session_state.prev_resume_text = st.session_state.resume_text
    
    if st.session_state.resume_text != st.session_state.prev_resume_text:
        st.session_state.builder_older_resume = st.session_state.resume_text
        st.session_state.prev_resume_text = st.session_state.resume_text

    older_resume_input = st.text_area(
        "📄 Your Current/Older Resume Text:",
        value=st.session_state.resume_text,
        placeholder="Paste your existing resume here, or upload a PDF in the sidebar to auto-fill...",
        height=200,
        key="builder_older_resume",
        help="Feel free to edit this text directly! The builder will use it as the source for your tailored resume."
    )

    col_role, col_instr = st.columns([1, 1])
    with col_role:
        target_role_input = st.selectbox(
            "Select or Type Target Professional Role:",
            options=[
                "Frontend Engineer",
                "Backend Engineer",
                "Fullstack Software Developer",
                "Machine Learning / AI Engineer",
                "Data Scientist",
                "Product Manager",
                "DevOps / SRE Specialist",
                "Other (Custom Role Name)"
            ],
            key="builder_role_select"
        )
        
        custom_role = ""
        if target_role_input == "Other (Custom Role Name)":
            custom_role = st.text_input("Enter Target Role Name:", key="builder_role_custom")
            
        final_role = custom_role if target_role_input == "Other (Custom Role Name)" else target_role_input

    with col_instr:
        # Added custom user request area as requested by user
        additional_instructions = st.text_area(
            "💡 Specific Focus, Gaps, or Changes (Optional):",
            placeholder="e.g. Focus heavily on cloud native scalability with AWS, highlight my pythonic backend experience, or customize achievements to show leadership skills...",
            height=100,
            key="builder_custom_instructions"
        )

    if st.button("🛠️ Generate Resume Optimization Guide", type="primary", use_container_width=True, key="builder_submit"):
        if not final_role.strip():
            st.error("Please enter a valid role name.")
        else:
            with st.spinner("Consulting recruiting databases & composing STAR action points..."):
                # Programmatically prefix user_input so the classifier routes perfectly
                user_msg = f"BUILD_RESUME_FOR: {final_role}"
                if additional_instructions.strip():
                    user_msg += f"\nINSTRUCTIONS: {additional_instructions}"

                payload = {
                    "session_id": st.session_state.session_id,
                    "user_id": "candidate",
                    "user_input": user_msg,
                    "uploaded_file_path": st.session_state.uploaded_file_path,
                    "older_resume_text": older_resume_input,
                    "api_key": st.session_state.gemini_api_key
                }
                try:
                    resp = requests.post(f"{API_BASE}/run", json=payload, timeout=90)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    if data.get("error"):
                        show_premium_error(data['error'])
                    else:
                        st.session_state.builder_result = data.get("structured_output") or {}
                        st.success("🎉 Tailored Resume generated successfully!")
                except Exception as e:
                    show_premium_error(f"Connection failed: {e}")

    # Display results if generated
    if st.session_state.builder_result:
        structured = st.session_state.builder_result
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card" style="border-color:#4E65FF;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#66FCF1; margin-top:0;">💡 Strategic Optimization Suggestions (~10 lines)</h3>', unsafe_allow_html=True)
        st.markdown(structured.get("strategic_advice", ""))
        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # "Anything you want to change?" Revision Box
        # -------------------------------------------------------------------
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card" style="border-color:#A78BFA; background: rgba(124, 58, 237, 0.05) !important;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color:#C084FC; margin:0 0 5px 0;">💬 Live Custom Revision & Refinement</h3>', unsafe_allow_html=True)
        st.markdown("Ask the AI to change, rephrase, customize, or refine anything in the resume preview below!")
        
        revision_request = st.text_input(
            "What would you like me to change or adjust? (e.g. 'Translate to Spanish', 'Change SwipeGen to remote', 'Emphasize cloud deployments'):",
            placeholder="e.g. 'Translate to Spanish', 'Change SwipeGen to remote', 'Emphasize cloud deployments'...",
            key="builder_revision_input"
        )
        
        if st.button("⚡ Apply Revision", type="primary", use_container_width=True, key="builder_revision_submit"):
            if not revision_request.strip():
                st.error("Please enter what you want to change.")
            else:
                with st.spinner("Applying custom edits and rebuilding your resume..."):
                    import json
                    user_msg = f"REVISE_RESUME: {revision_request}\nTARGET_ROLE: {final_role}\nPREVIOUS_OUTPUT: {json.dumps(structured)}"
                    payload = {
                        "session_id": st.session_state.session_id,
                        "user_id": "candidate",
                        "user_input": user_msg,
                        "uploaded_file_path": st.session_state.uploaded_file_path,
                        "older_resume_text": older_resume_input,
                        "api_key": st.session_state.gemini_api_key
                    }
                    try:
                        resp = requests.post(f"{API_BASE}/run", json=payload, timeout=90)
                        resp.raise_for_status()
                        data = resp.json()
                        
                        if data.get("error"):
                            show_premium_error(data['error'])
                        else:
                            st.session_state.builder_result = data.get("structured_output") or {}
                            st.success("✅ Custom revision successfully applied!")
                            st.rerun()
                    except Exception as e:
                        show_premium_error(f"Connection failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # Compiled Resume Live Preview matching image style
        # -------------------------------------------------------------------
        if "compiled_resume" in structured:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📄 Compiled Professional Resume Live Preview")
            st.caption("Scroll down or click the download button below to print or save this as a high-standard PDF!")
            
            compiled_data = structured["compiled_resume"]
            inner_html = render_resume_inner(compiled_data).replace("\n", " ")
            
            # Render a physical-sheet look with shadow without splitting HTML blocks
            st.markdown(
                f'<div style="background-color: white; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.25); border: 1px solid #E2E8F0; margin-bottom: 25px; overflow: hidden;">{inner_html}</div>',
                unsafe_allow_html=True
            )
            
            # Print/Export Button
            full_html = render_resume_full_document(compiled_data)
            candidate_name = compiled_data.get("name", "Tailored").replace(" ", "_")
            
            st.download_button(
                label="📥 Download Printable HTML Resume (Open to Print / Save as PDF)",
                data=full_html,
                file_name=f"{candidate_name}_Tailored_Resume.html",
                mime="text/html",
                use_container_width=True
            )
