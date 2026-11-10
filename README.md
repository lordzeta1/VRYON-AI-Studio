# VYRON AI Studio

A Streamlit-based AI video-planning and scene-card renderer for VYRON Studios.

## Features
- Gemini-powered video concepts, hooks, narration and storyboards.
- Script editing and Markdown export.
- MP4 renderer for vertical 9:16 and landscape 16:9 formats.
- Optional narration audio upload (MP3/WAV/M4A).
- Basic SRT caption export.
- Streamlit Secrets support for API-key safety.

## Important limitation
This version creates animated text/scene-card videos. It does **not** automatically create photorealistic AI footage, clone voices, generate music, or publish to social platforms. Gemini API access and quotas depend on the account, model, region and current Google terms.

## Deploy on Streamlit Community Cloud
1. Upload all files and folders in this project to your GitHub repository.
2. Open https://share.streamlit.io/ and create an app.
3. Select your repository and branch.
4. Set **Main file path** to `app.py`.
5. Open Advanced settings → Secrets and paste:

```toml
GEMINI_API_KEY = "YOUR_PRIVATE_GEMINI_API_KEY"
```

6. Deploy.

Never place your real key in `app.py`, README, GitHub, screenshots or chat messages. If a key is accidentally exposed, revoke it and create a replacement.

## Local run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project structure
```text
vyron-ai-studio/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── core/
    ├── __init__.py
    ├── gemini_client.py
    ├── prompts.py
    ├── storage.py
    └── video_engine.py
```

## Official references
- Google Gen AI Python SDK: https://googleapis.github.io/python-genai/
- Streamlit deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
