"""Provider adapters. Transport is injectable for offline testing with synthetic HTTP.
Never treats synthetic fixtures as historical observations.
"""
from __future__ import annotations
from typing import Protocol
import hashlib
from datetime import datetime, timezone

class Transport(Protocol):
    def post(self, url: str, headers: dict, json: dict) -> dict: ...

class OpenAIAdapter:
    def __init__(self, transport: Transport, api_key: str | None = None):
        self.transport = transport
        self.api_key = api_key

    def collect(self, probe: dict) -> dict:
        if not self.api_key:
            return {"status": "MISSING_SECRET", "probe_id": probe.get("id"), "is_historical": False}
        payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": probe.get("text", "")}]}
        try:
            resp = self.transport.post("https://api.openai.com/v1/chat/completions",
                                       {"Authorization": f"Bearer {self.api_key}"}, payload)
            raw = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {
                "probe_id": probe.get("id"),
                "model": "gpt-4o-mini",
                "raw_response": raw,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "method": "openai_adapter",
                "hash": hashlib.sha256(raw.encode()).hexdigest() if raw else None,
                "is_historical": True,
                "status": "success",
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "probe_id": probe.get("id"), "is_historical": False}

class MockTransport:
    """Synthetic transport for tests only. Never used for historical records."""
    def post(self, url: str, headers: dict, json: dict) -> dict:
        return {"choices": [{"message": {"content": "Mock response: one independent observation under declared copy."}}]}
