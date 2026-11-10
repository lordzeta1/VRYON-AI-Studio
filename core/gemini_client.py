
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-3.8-flash"

def generate_text(api_key: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not api_key:
        raise ValueError("Gemini API key is missing.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=30000
        )
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()

    finally:
        client.close()
        
