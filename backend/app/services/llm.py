from collections.abc import Iterator

from openai import OpenAI


class LLMClient:
    """Thin wrapper around the OpenAI Chat Completions API."""

    def __init__(self, api_key: str, model: str, temperature: float | None, max_tokens: int):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = (
            OpenAI(api_key=api_key, timeout=30.0, max_retries=2) if api_key else None
        )

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def _params(self, system_prompt: str, user_prompt: str) -> dict:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY is not set")
        params = {
            "model": self.model,
            "max_completion_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        # Some models only accept the default temperature; leave it unset for them
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return params

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Whole answer at once."""
        response = self.client.chat.completions.create(**self._params(system_prompt, user_prompt))
        return response.choices[0].message.content or ""

    def stream(self, system_prompt: str, user_prompt: str) -> Iterator[str]:
        """Answer piece by piece, as OpenAI writes it."""
        params = self._params(system_prompt, user_prompt)
        params["stream"] = True
        for chunk in self.client.chat.completions.create(**params):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content