import asyncio
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

# --- Page Config ---
st.set_page_config(
    page_title="Singapore Travel Maestro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3.5rem;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #334155 !important;
        border: 1px solid #475569;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #1e293b !important;
        border: 1px solid #334155;
    }
    .sidebar-content {
        padding: 1.5rem;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 15px;
        border: 1px solid #334155;
    }
    /* Streamlit overrides */
    div.stButton > button {
        background-color: #38bdf8;
        color: #0f172a;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #7dd3fc;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(56, 189, 248, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="main-title">Singapore Travel Maestro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-powered journey planning across the Lion City. Get the perfect balance of cost and time.</p>', unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_service" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
if "session_created" not in st.session_state:
    st.session_state.session_created = False

APP_NAME = "my_travel_agent_app"
USER_ID = "traveler_one"
SESSION_ID = "current_planning_session"

async def ensure_session():
    """Ensure the ADK session is initialized."""
    if not st.session_state.session_created:
        await st.session_state.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        st.session_state.session_created = True

async def fetch_agent_response(query: str) -> str:
    """Invokes the root agent and returns the synthesized response."""
    await ensure_session()

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=st.session_state.session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=query)])
    response_text = "I'm sorry, I couldn't generate a recommendation."

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
            break
    
    return response_text

def process_query(query: str) -> str:
    """Wrapper for async agent call."""
    return asyncio.run(fetch_agent_response(query))

# --- Chat Interface ---
# Container for messages for better layout control
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Where are we heading? (e.g., Woodlands to Orchard Road)"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # Agent Response
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Consulting specialized agents..."):
                response_content = process_query(prompt)
                st.markdown(response_content)
    
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🗺️ Travel Intelligence")
    st.markdown("""
    <div class="sidebar-content">
        Our system employs multiple specialized AI agents:
        <br><br>
        💰 <b>Cost Specialist</b><br>
        Analyzes MRT, Bus, and Taxi fares to find the best value.
        <br><br>
        ⏱️ <b>Time Specialist</b><br>
        Estimates real-time travel durations and identifies bottlenecks.
        <br><br>
        🤖 <b>Coordinator</b><br>
        Synthesizes all data into a premium recommendation.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🚀 New Trip", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_created = False
        st.rerun()

    st.markdown("---")
    st.caption("Built with Gemini AI & Google ADK")
