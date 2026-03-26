"""LLM client for intent classification and tool use."""

import os
import json
from typing import List, Dict, Any, Optional

import httpx
from dotenv import load_dotenv
from pathlib import Path


def _load_env():
    """Load .env.bot.secret from bot directory or parent directory."""
    env_path = Path(__file__).parent.parent / ".env.bot.secret"
    if not env_path.exists():
        env_path = Path(__file__).parent.parent.parent / ".env.bot.secret"
    if env_path.exists():
        load_dotenv(env_path)


_load_env()


class LLMClient:
    """Client for LLM API with tool use support."""

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        model: str = None,
    ):
        """Initialize the LLM client.

        Args:
            base_url: LLM API base URL. Defaults to LLM_API_BASE_URL env var.
            api_key: API key for authentication. Defaults to LLM_API_KEY env var.
            model: Model name. Defaults to LLM_API_MODEL env var.
        """
        self.base_url = (base_url or os.getenv("LLM_API_BASE_URL", "")).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_API_MODEL", "qwen3-coder-plus")
        self.client = httpx.Client(timeout=60.0)

    def _headers(self) -> Dict[str, str]:
        """Return headers with Bearer authentication."""
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        system_prompt: str = None,
    ) -> Dict[str, Any]:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool schemas for function calling.
            system_prompt: Optional system prompt to prepend.

        Returns:
            LLM response dict with 'content' and/or 'tool_calls'.
        """
        # Build messages with system prompt
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self.client.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from LLM response.

        Args:
            response: LLM response dict.

        Returns:
            List of tool calls with 'name', 'arguments', and 'id'.
        """
        choices = response.get("choices", [])
        if not choices:
            return []

        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])

        result = []
        for tc in tool_calls:
            func = tc.get("function", {})
            try:
                arguments = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}

            result.append({
                "id": tc.get("id"),
                "name": func.get("name"),
                "arguments": arguments,
            })

        return result

    def get_response_text(self, response: Dict[str, Any]) -> str:
        """Extract text content from LLM response.

        Args:
            response: LLM response dict.

        Returns:
            Text content or empty string.
        """
        choices = response.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")
