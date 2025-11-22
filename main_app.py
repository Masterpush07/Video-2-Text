import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from backend.processing_logic import process_video_insights, CommunicationAnalysis

# --- Configuration & Initialization ---

# 1. Load environment variables (API Key)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check for API Key and initialize client
if GEMINI_API_KEY:
    try:
        # Ensure the client is only initialized once
        @st.cache_resource
        def get_gemini_client():
            # Removed the problematic line: genai.logging.set_verbosity("DEBUG")
            return genai.Client(api_key=GEMINI_API_KEY)
        
        gemini_client = get_gemini_client()
        st.session_state['client_ready'] = True
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        st.session_state['client_ready'] = False
else:
    st.session_state['client_ready'] = False
    
# --- Streamlit UI Components ---

st.set_page_config(
    page_title="Video Insight Analyzer",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("📹 Video Insight Analyzer")
st.markdown(
    """
    A simple backend-focused tool to extract communication insights from a public video URL 
    (e.g., YouTube, Loom). This tool fulfills the **Python Assessment** requirements.
    """
)

# 1. API Key Warning
if not st.session_state.get('client_ready'):
    st.warning("🚨 **API Key Missing!** Please ensure you have set the `GEMINI_API_KEY` in your `.env` file and restarted the application.")
    st.stop()


# 2. User Input
video_url = st.text_input(
    "Enter Public Video URL",
    placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    key="video_url_input"
)

# 3. Processing Button
if st.button("Analyze Video Insights", type="primary") and video_url:
    
    # Simple URL validation (can be more robust, but this is fine for an assessment)
    if not video_url.startswith(("http://", "https://")):
        st.error("Please enter a valid URL starting with http:// or https://")
        st.stop()
        
    try:
        # Use a status indicator to show progress
        with st.status("Analyzing Video...", expanded=True) as status:
            status.write("Starting video analysis pipeline...")
            
            # Step 1: Extract Audio (Handled by process_video_insights function)
            status.write("Extracting and preparing audio from URL...")
            
            # Step 2: Transcribe & Analyze with Gemini
            status.write("Sending audio to Gemini for transcription and LLM analysis...")
            
            # The main backend call
            analysis: CommunicationAnalysis = process_video_insights(
                video_url=video_url, 
                client=gemini_client
            )
            
            status.write("Analysis complete. Structuring results.")
            status.update(label="Analysis Complete!", state="complete", expanded=False)

        # 4. Display Outputs (Required Deliverables)
        
        st.subheader("✅ Analysis Results")
        
        # Clarity Score (Required Output 1)
        st.metric(
            label="Clarity Score", 
            value=f"{analysis.clarity_score}%",
            delta_color="off"
        )
        
        # Communication Focus (Required Output 2)
        st.info(f"**Communication Focus:** {analysis.communication_focus}")
        
        # Optional: Display the Transcript (Required Output for analysis but good for user validation)
        with st.expander("View Full Transcript", expanded=False):
            st.code(analysis.transcript, language="text")
            
    except ConnectionError as e:
        st.error(f"**API Error:** {e}")
        st.markdown("Please verify your Gemini API key is correct and ensure network connectivity.")
    except ValueError as e:
        st.error(f"**Processing Error:** {e}")
        st.markdown("This usually means `yt-dlp` couldn't process the video URL. Ensure the link is public and accessible.")
    except Exception as e:
        st.exception(e)
        st.error(f"An unexpected error occurred during processing: {e}")

# Footer for context
st.markdown("---")
st.caption("Backend powered by Python, yt-dlp, and Google Gemini. UI via Streamlit.")