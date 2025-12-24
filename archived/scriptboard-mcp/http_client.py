"""
Async HTTP client for Scriptboard REST API.

Provides methods to interact with Scriptboard FastAPI backend
running at localhost:8000.
"""

import httpx
from typing import Optional
from dataclasses import dataclass


SCRIPTBOARD_URL = "http://localhost:8000"
CODEREF_URL = "http://localhost:8042"
TIMEOUT = 10.0


@dataclass
class ScriptboardResponse:
    """Standardized response from Scriptboard operations."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class ScriptboardClient:
    """Async HTTP client for Scriptboard API."""

    def __init__(self, base_url: str = SCRIPTBOARD_URL):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> ScriptboardResponse:
        """Make HTTP request with error handling."""
        try:
            client = await self._get_client()
            response = await client.request(
                method=method,
                url=endpoint,
                json=json_data
            )

            if response.status_code >= 400:
                return ScriptboardResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}"
                )

            try:
                data = response.json()
            except Exception:
                data = {"text": response.text}

            return ScriptboardResponse(success=True, data=data)

        except httpx.ConnectError:
            return ScriptboardResponse(
                success=False,
                error="Scriptboard not running. Start backend at localhost:8000"
            )
        except httpx.TimeoutException:
            return ScriptboardResponse(
                success=False,
                error=f"Request timed out after {TIMEOUT}s"
            )
        except Exception as e:
            return ScriptboardResponse(
                success=False,
                error=f"Request failed: {str(e)}"
            )

    # === Tool Methods ===

    async def set_prompt(self, text: str) -> ScriptboardResponse:
        """Set the current prompt text in Scriptboard."""
        return await self._request("POST", "/prompt", json_data={"text": text})

    async def clear_prompt(self) -> ScriptboardResponse:
        """Clear the current prompt."""
        return await self._request("DELETE", "/prompt")

    async def add_attachment(self, text: str, filename: Optional[str] = None) -> ScriptboardResponse:
        """Add a text attachment. Can be called multiple times."""
        payload = {"text": text}
        if filename:
            payload["suggested_name"] = filename
        return await self._request("POST", "/attachments/text", json_data=payload)

    async def clear_attachments(self) -> ScriptboardResponse:
        """Clear all attachments."""
        return await self._request("DELETE", "/attachments")

    # === CodeRef Methods ===

    async def _coderef_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[dict] = None
    ) -> ScriptboardResponse:
        """Make HTTP request to CodeRef API (port 8042)."""
        try:
            async with httpx.AsyncClient(
                base_url=CODEREF_URL,
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"}
            ) as client:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    json=json_data
                )

                if response.status_code >= 400:
                    return ScriptboardResponse(
                        success=False,
                        error=f"HTTP {response.status_code}: {response.text}"
                    )

                try:
                    data = response.json()
                except Exception:
                    data = {"text": response.text}

                return ScriptboardResponse(success=True, data=data)

        except httpx.ConnectError:
            return ScriptboardResponse(
                success=False,
                error="CodeRef backend not running. Start backend at localhost:8042"
            )
        except httpx.TimeoutException:
            return ScriptboardResponse(
                success=False,
                error=f"Request timed out after {TIMEOUT}s"
            )
        except Exception as e:
            return ScriptboardResponse(
                success=False,
                error=f"Request failed: {str(e)}"
            )

    async def coderef_status(self) -> ScriptboardResponse:
        """Check if CodeRef CLI is available."""
        return await self._coderef_request("GET", "/coderef/status")

    async def coderef_scan(
        self,
        source_dir: str,
        languages: Optional[list[str]] = None,
        use_ast: bool = False
    ) -> ScriptboardResponse:
        """Scan a directory for code elements."""
        payload = {
            "source_dir": source_dir,
            "use_ast": use_ast
        }
        if languages:
            payload["languages"] = languages
        return await self._coderef_request("POST", "/coderef/scan", json_data=payload)

    async def coderef_query(
        self,
        target: str,
        source_dir: Optional[str] = None
    ) -> ScriptboardResponse:
        """Query element dependencies."""
        payload = {"target": target}
        if source_dir:
            payload["source_dir"] = source_dir
        return await self._coderef_request("POST", "/coderef/query", json_data=payload)

    async def coderef_impact(
        self,
        target: str,
        source_dir: Optional[str] = None,
        depth: int = 3
    ) -> ScriptboardResponse:
        """Analyze impact of changing a code element."""
        payload = {"target": target, "depth": depth}
        if source_dir:
            payload["source_dir"] = source_dir
        return await self._coderef_request("POST", "/coderef/impact", json_data=payload)


# Singleton client instance
_client: Optional[ScriptboardClient] = None


def get_client() -> ScriptboardClient:
    """Get or create singleton client."""
    global _client
    if _client is None:
        _client = ScriptboardClient()
    return _client
