from typing import Any

import httpx


class DriftClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_token: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._model = model
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_seconds),
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def create_conversation(self, title: str) -> int:
        response = await self._client.post("/conversations", json={"title": title})
        response.raise_for_status()
        payload = response.json()
        return int(payload["id"])

    async def send_message(self, *, prompt: str, conversation_id: int) -> str:
        response = await self._client.post(
            "/chat/completions",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "conversation_id": conversation_id,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return _extract_content(payload)


def _extract_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    return str(content or "").strip()
