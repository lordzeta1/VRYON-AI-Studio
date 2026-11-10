
from google import genai

DEFAULT_MODEL = "gemini-3.8-flash"


def generate_text(api_key: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not api_key:
        raise ValueError("Missing Gemini API key.")

    client = genai.Client(api_key=api_key)

    interaction = client.interactions.create(
        model=model,
        input=prompt,
    )

    result = interaction.output_text

    if not result:
        raise RuntimeError("Gemini returned an empty response.")

    return result.strip()
    
