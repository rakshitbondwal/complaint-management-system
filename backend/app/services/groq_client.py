import json
import re
from groq import Groq

from app.config import settings

_client = Groq(api_key=settings.groq_api_key)


def _extract_json(text: str) -> dict:
    """Groq models sometimes wrap JSON in prose or code fences - strip that off."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def chat(system_prompt: str, user_prompt: str, model: str | None = None, temperature: float = 0.2) -> str:
    """Plain text completion via Groq."""
    response = _client.chat.completions.create(
        model=model or settings.groq_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def chat_json(system_prompt: str, user_prompt: str, model: str | None = None, temperature: float = 0.1) -> dict:
    """
    Completion where we force the model to reply with JSON only.
    Falls back to the larger llama model once if gemma2-9b-it returns malformed JSON.
    """
    strict_system = (
        system_prompt
        + "\n\nRespond with ONLY valid JSON. No markdown fences, no preamble, no explanation outside the JSON."
    )
    raw = chat(strict_system, user_prompt, model=model, temperature=temperature)
    try:
        return _extract_json(raw)
    except (json.JSONDecodeError, AttributeError):
        # retry once with the more capable fallback model
        raw_fallback = chat(strict_system, user_prompt, model=settings.groq_fallback_model, temperature=temperature)
        try:
            return _extract_json(raw_fallback)
        except (json.JSONDecodeError, AttributeError):
            return {"error": "Failed to parse model output", "raw": raw_fallback}
