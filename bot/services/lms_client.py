"""LMS API client for making authenticated requests to the backend."""

import os
from typing import List, Dict, Any, Optional

import httpx
from dotenv import load_dotenv
from pathlib import Path


def _load_env():
    """Load .env.bot.secret from bot directory or parent directory."""
    # Try bot/.env.bot.secret first
    env_path = Path(__file__).parent.parent / ".env.bot.secret"
    if not env_path.exists():
        # Try root/.env.bot.secret
        env_path = Path(__file__).parent.parent.parent / ".env.bot.secret"
    if env_path.exists():
        load_dotenv(env_path)


# Load environment variables on module import
_load_env()


class LMSClient:
    """Client for the LMS backend API.

    Uses Bearer token authentication with the LMS_API_KEY.
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS API. Defaults to LMS_API_BASE_URL env var.
            api_key: API key for authentication. Defaults to LMS_API_KEY env var.
        """
        self.base_url = base_url or os.getenv("LMS_API_BASE_URL", "http://localhost:42002")
        self.api_key = api_key or os.getenv("LMS_API_KEY")
        self.client = httpx.Client(timeout=10.0)

    def _headers(self) -> Dict[str, str]:
        """Return headers with Bearer authentication."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_items(self) -> List[Dict[str, Any]]:
        """Fetch all items from the LMS API."""
        response = self.client.get(
            f"{self.base_url}/items/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def get_labs(self) -> List[Dict[str, Any]]:
        """Fetch only lab items (filter by type)."""
        items = self.get_items()
        return [item for item in items if item.get("type") == "lab"]

    def get_pass_rates(self, lab: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., 'lab-04').

        Returns:
            List of pass rate data per task, or None if lab not found.
        """
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def health_check(self) -> Dict[str, Any]:
        """Check if the backend is healthy.

        Returns:
            Dict with 'healthy' bool and optional 'message' or 'error'.
        """
        try:
            response = self.client.get(
                f"{self.base_url}/items/",
                headers=self._headers(),
                timeout=5.0
            )
            if response.status_code == 200:
                items = response.json()
                return {"healthy": True, "item_count": len(items)}
            else:
                return {"healthy": False, "error": f"HTTP {response.status_code}"}
        except httpx.ConnectError as e:
            return {"healthy": False, "error": f"connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "error": f"HTTP {e.response.status_code} {e.response.status_phrase}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}

    def get_learners(self) -> List[Dict[str, Any]]:
        """Fetch all learners from the LMS API."""
        response = self.client.get(
            f"{self.base_url}/learners/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch score distribution for a specific lab."""
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/scores",
                params={"lab": lab},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_timeline(self, lab: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch submission timeline for a specific lab."""
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/timeline",
                params={"lab": lab},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_groups(self, lab: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch per-group performance for a specific lab."""
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/groups",
                params={"lab": lab},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_top_learners(self, lab: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Fetch top learners for a specific lab."""
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/top-learners",
                params={"lab": lab, "limit": limit},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_completion_rate(self, lab: str) -> Optional[Dict[str, Any]]:
        """Fetch completion rate for a specific lab."""
        try:
            response = self.client.get(
                f"{self.base_url}/analytics/completion-rate",
                params={"lab": lab},
                headers=self._headers()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def trigger_sync(self) -> Dict[str, Any]:
        """Trigger ETL sync to refresh data from autochecker API."""
        response = self.client.post(
            f"{self.base_url}/pipeline/sync",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
