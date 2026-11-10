from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash"

def generate_text(api_key: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not api_key:
        raise ValueError("Missing Gemini API key.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=7000,
        ),
    )
    text = response.text
    if not text:
        raise RuntimeError("Gemini returned an empty response. Try again.")
    return text.strip()
