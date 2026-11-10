import streamlit as st
from core.gemini_client import generate_text
from core.prompts import build_creator_prompt, build_rewrite_prompt
from core.video_engine import render_video, make_srt
from core.storage import safe_filename

from core.gemini_client import generate_text

if st.button("Test Gemini connection"):
    try:
        result = generate_text(
            st.secrets["GEMINI_API_KEY"],
            "Reply with exactly: VYRON ONLINE"
        )
        st.success(result)
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        
st.set_page_config(page_title="VYRON AI Studio", page_icon="🎬", layout="wide")
st.markdown("""
<style>
.stApp {background: radial-gradient(circle at top right,#24202a 0,#101116 42%,#090a0d 100%); color:#f5f5f5;}
section[data-testid="stSidebar"] {background:#121318;}
div[data-testid="stMetric"] {background:#1b1c23;padding:14px;border:1px solid #39323b;border-radius:14px;}
.stButton>button {border-radius:10px;border:1px solid #bd8d3c;background:linear-gradient(90deg,#8f1d25,#b88735);color:white;font-weight:700;}
h1,h2,h3 {letter-spacing:.2px;}
</style>
""", unsafe_allow_html=True)

if "project" not in st.session_state:
    st.session_state.project = None
if "script" not in st.session_state:
    st.session_state.script = ""

def get_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return os.environ.get("GEMINI_API_KEY", "")

import os
key = get_key()

with st.sidebar:
    st.title("🎬 VYRON")
    st.caption("AI STUDIO • ENTERTAINMENT WITHOUT LIMITS")
    st.divider()
    st.markdown("**Studio status**")
    st.success("Gemini key detected") if key else st.warning("Add GEMINI_API_KEY in Streamlit Secrets")
    st.markdown("**Workflow**")
    st.markdown("1. Create a concept\n2. Generate script + scenes\n3. Edit the narration\n4. Render a video\n5. Export captions")
    st.divider()
    st.caption("VYRON AI Studio • MVP 1.0")

st.title("VYRON AI Studio")
st.write("Turn a video idea into a structured script, scene plan, captions and a vertical or landscape MP4.")
st.caption("Gemini generates the creative material. The built-in renderer creates a cinematic text-and-scene video; it does not generate photorealistic AI footage.")

tab_create, tab_edit, tab_render, tab_help = st.tabs(["✨ Creator", "✍️ Script editor", "🎞️ Video renderer", "📘 Guide"])

with tab_create:
    left, right = st.columns([1.2, 0.8])
    with left:
        topic = st.text_area("What should the video be about?", "What if the Sun disappeared for 24 hours?", height=100)
        style = st.selectbox("Video format", ["What If / science explainer", "AI short story", "Comedy sketch", "African mystery", "History / facts"])
        platform = st.selectbox("Target platform", ["YouTube Shorts / TikTok", "YouTube video"])
        duration = st.slider("Target duration (minutes)", 1, 8, 2)
        tone = st.selectbox("Narration tone", ["Cinematic and suspenseful", "Funny and energetic", "Documentary", "Mysterious", "Simple and educational"])
        audience = st.selectbox("Audience", ["General audience", "Teens and young adults", "Family-friendly"])
        if st.button("Generate full video plan", type="primary", use_container_width=True):
            if not key:
                st.error("Add your Gemini API key in Streamlit Secrets before generating.")
            elif not topic.strip():
                st.error("Enter a video idea first.")
            else:
                with st.spinner("VYRON is writing your video plan..."):
                    try:
                        prompt = build_creator_prompt(topic, style, platform, duration, tone, audience)
                        result = generate_text(key, prompt)
                        st.session_state.script = result
                        st.session_state.project = {"topic": topic, "style": style, "platform": platform, "duration": duration}
                        st.success("Your video plan is ready. Open Script editor to review it.")
                    except Exception as e:
                        st.error(f"Generation failed: {e}")
    with right:
        st.subheader("What the studio creates")
        st.markdown("- Strong opening hook\n- Narration script\n- Scene-by-scene visual directions\n- On-screen text suggestions\n- Sound and pacing notes\n- Video title and description\n- Hashtags and thumbnail concept")
        st.info("For reliable results, ask for one clear idea per video. Verify factual claims before publishing.")

with tab_edit:
    st.subheader("Script workspace")
    if st.session_state.script:
        st.session_state.script = st.text_area("Generated plan (you can edit it)", st.session_state.script, height=480)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download script (.md)", st.session_state.script, file_name="vyron_video_plan.md", use_container_width=True)
        with col2:
            if st.button("Improve this script", use_container_width=True):
                if not key:
                    st.error("Gemini key is missing.")
                else:
                    with st.spinner("Improving your script..."):
                        try:
                            st.session_state.script = generate_text(key, build_rewrite_prompt(st.session_state.script))
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
    else:
        st.info("Generate a video plan in the Creator tab first.")

with tab_render:
    st.subheader("Create an MP4 from your scenes")
    st.write("Paste your narration or scene text below. The renderer creates animated title/scene cards with transitions.")
    render_text = st.text_area("Video content", st.session_state.script, height=250, placeholder="Paste your script or scene breakdown here...")
    c1, c2, c3 = st.columns(3)
    with c1:
        layout = st.selectbox("Canvas", ["Vertical 9:16", "Landscape 16:9"])
    with c2:
        seconds = st.slider("Seconds per scene", 3, 10, 5)
    with c3:
        fps = st.selectbox("Frame rate", [12, 15, 24], index=1)
    uploaded_audio = st.file_uploader("Optional narration audio (MP3 or WAV)", type=["mp3", "wav", "m4a"])
    if st.button("Render MP4", type="primary", use_container_width=True):
        if not render_text.strip():
            st.error("Paste a script or generate a plan first.")
        else:
            with st.spinner("Rendering video. Longer scripts take more time..."):
                try:
                    audio_bytes = uploaded_audio.getvalue() if uploaded_audio else None
                    audio_name = uploaded_audio.name if uploaded_audio else None
                    video_path = render_video(render_text, layout, seconds, fps, audio_bytes, audio_name)
                    with open(video_path, "rb") as f:
                        st.session_state["rendered_video"] = f.read()
                    st.success("Video rendered.")
                except Exception as e:
                    st.error(f"Could not render video: {e}")
    if st.session_state.get("rendered_video"):
        st.video(st.session_state["rendered_video"])
        st.download_button("Download MP4", st.session_state["rendered_video"], file_name="vyron_video.mp4", mime="video/mp4", use_container_width=True)
    if render_text.strip():
        try:
            srt = make_srt(render_text, seconds)
            st.download_button("Download basic subtitles (.srt)", srt, file_name="vyron_captions.srt")
        except Exception:
            pass

with tab_help:
    st.subheader("Setup")
    st.markdown("""
1. Upload the project files to your GitHub repository.
2. Open Streamlit Community Cloud and create an app from that repository.
3. Set the main file path to `app.py`.
4. In Advanced settings → Secrets, add:
""")
    st.code('GEMINI_API_KEY = "YOUR_PRIVATE_KEY"', language="toml")
    st.warning("Never put your real API key in app.py, README, GitHub, screenshots or messages.")
    st.markdown("**Current capabilities**")
    st.markdown("- Gemini-powered video concepts, scripts and production plans.\n- Editable scripts and Markdown export.\n- MP4 rendering from animated text/scene cards.\n- Optional uploaded narration audio.\n- Basic SRT caption export.")
    st.markdown("**Not included yet**")
    st.markdown("- Automatic cinematic AI footage generation.\n- Automatic voice cloning or music generation.\n- Direct publishing to YouTube or TikTok.")
    st.markdown("**Useful official documentation**")
    st.markdown("- [Google Gen AI Python SDK](https://googleapis.github.io/python-genai/)\n- [Streamlit deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)\n- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)")
