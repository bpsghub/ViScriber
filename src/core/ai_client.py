from __future__ import annotations
from typing import Optional, Protocol, runtime_checkable

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore

try:
    import openai
except ImportError:
    openai = None  # type: ignore

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore


@runtime_checkable
class AIClient(Protocol):
    def summarize(self, transcript: str, prompt: str) -> str: ...


class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        if anthropic is None:
            raise ImportError("anthropic package is required: pip install anthropic")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def summarize(self, transcript: str, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            messages=[{"role": "user", "content": f"{prompt}\n\n---\n\n{transcript}"}],
        )
        return response.content[0].text


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if openai is None:
            raise ImportError("openai package is required: pip install openai")
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model

    def summarize(self, transcript: str, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript},
            ],
        )
        return response.choices[0].message.content


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3", timeout: float = 120.0):
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def summarize(self, transcript: str, prompt: str) -> str:
        if httpx is None:
            raise ImportError("httpx package is required: pip install httpx")
        response = httpx.post(
            f"{self._base_url}/api/generate",
            json={"model": self._model, "prompt": f"{prompt}\n\n---\n\n{transcript}", "stream": False},
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        if "response" not in data:
            raise RuntimeError(data.get("error", "Unexpected Ollama response"))
        return data["response"]


def get_client(provider: str, api_key: str, base_url: str) -> Optional[AIClient]:
    p = provider.lower().strip()
    if p in ("", "none"):
        return None
    if p == "claude":
        return ClaudeClient(api_key=api_key)
    if p == "openai":
        return OpenAIClient(api_key=api_key)
    if p == "ollama":
        return OllamaClient(base_url=base_url or "http://localhost:11434")
    return None
