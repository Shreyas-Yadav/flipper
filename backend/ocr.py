import base64
import os

from openai import OpenAI

_client: OpenAI | None = None

_PROMPT = (
    "You are an OCR engine. Extract all text from this book page exactly as written. "
    "Preserve paragraph structure and line breaks. Output only the extracted text, no commentary."
)


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ["OCR_API_KEY"],
            base_url=os.environ.get("OCR_BASE_URL", "https://api.featherless.ai/v1"),
        )
    return _client


def extract_text(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    model = os.environ.get("OCR_MODEL", "Qwen/Qwen3.5-397B-A17B")
    response = _get_client().chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
    )
    return response.choices[0].message.content
