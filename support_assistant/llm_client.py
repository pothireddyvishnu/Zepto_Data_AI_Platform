import os
import json
from groq import Groq
from pydantic import ValidationError
from schemas import AskResponse

import dotenv

dotenv.load_dotenv()

MAX_RETRIES = 2
GROQ_MODEL = "qwen/qwen3.6-27b"

_groq_client = None


def _get_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set. Required When MOCK_LLM=0"
            )

        _groq_client = Groq(api_key=api_key)
    return _groq_client


def _clean_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def llm_call(prompt):
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        reasoning_format="hidden",
        reasoning_effort="none"
    )
    return response.choices[0].message.content


def llm_call_structured(prompt):
    client = _get_client()
    current_prompt = prompt
    last_error = None

    for attempt in range(MAX_RETRIES + 1):

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": current_prompt}],
            temperature=0.0,
            reasoning_format="hidden",
            reasoning_effort="none"
        )
        raw_text = response.choices[0].message.content
        cleaned_text = _clean_text(raw_text)

        try:
            parsed_json = json.loads(cleaned_text)
            validate = AskResponse(**parsed_json)
            return validate.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            current_prompt = f""""
                {prompt}\n\n
                Your previous repose was invalid: {e}\n
                Your previous raw output was: {raw_text}\n

                Respond again with ONLY a single valid JSON object matching the exact schema described above 
                (fields: answer [string], sources [list of strings], confidence [float between 0 and 1]).

                Do not include any text, explanation or markdown formatting outside the JSON object.
            """

    return {
        "answer": f"""
            Error: LLM failed to produce a valid structured response after {MAX_RETRIES} attempts.
            Last validation error: {last_error}
        """,
        "sources": [],
        "confidence": 0.0
    }
