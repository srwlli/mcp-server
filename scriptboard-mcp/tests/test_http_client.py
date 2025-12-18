"""
Tests for Scriptboard HTTP Client.

Tests the async HTTP client with mocked httpx responses.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from http_client import (
    ScriptboardClient,
    ScriptboardResponse,
    get_client,
    SCRIPTBOARD_URL,
    TIMEOUT
)


class TestScriptboardResponse:
    """Tests for ScriptboardResponse dataclass."""

    def test_success_response(self):
        """Should create successful response with data."""
        response = ScriptboardResponse(
            success=True,
            data={"id": "123", "status": "ok"}
        )

        assert response.success is True
        assert response.data == {"id": "123", "status": "ok"}
        assert response.error is None

    def test_error_response(self):
        """Should create error response with message."""
        response = ScriptboardResponse(
            success=False,
            error="Connection refused"
        )

        assert response.success is False
        assert response.data is None
        assert response.error == "Connection refused"


class TestScriptboardClientInit:
    """Tests for ScriptboardClient initialization."""

    def test_default_base_url(self):
        """Should use default localhost URL."""
        client = ScriptboardClient()
        assert client.base_url == "http://localhost:8000"

    def test_custom_base_url(self):
        """Should accept custom base URL."""
        client = ScriptboardClient("http://custom:9000/")
        assert client.base_url == "http://custom:9000"  # trailing slash stripped

    def test_client_starts_none(self):
        """HTTP client should be None until first request."""
        client = ScriptboardClient()
        assert client._client is None


class TestScriptboardClientSetPrompt:
    """Tests for set_prompt method."""

    @pytest.mark.asyncio
    async def test_set_prompt_success(self):
        """Should send POST request with text payload."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.set_prompt("Review this code")

        assert result.success is True
        assert result.data == {"status": "ok"}
        mock_http.request.assert_called_once_with(
            method="POST",
            url="/prompt",
            json={"text": "Review this code"}
        )

    @pytest.mark.asyncio
    async def test_set_prompt_http_error(self):
        """Should return error response on HTTP error."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.set_prompt("test")

        assert result.success is False
        assert "500" in result.error


class TestScriptboardClientClearPrompt:
    """Tests for clear_prompt method."""

    @pytest.mark.asyncio
    async def test_clear_prompt_success(self):
        """Should send DELETE request to /prompt."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "cleared"}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.clear_prompt()

        assert result.success is True
        mock_http.request.assert_called_once_with(
            method="DELETE",
            url="/prompt",
            json=None
        )


class TestScriptboardClientAddAttachment:
    """Tests for add_attachment method."""

    @pytest.mark.asyncio
    async def test_add_attachment_with_filename(self):
        """Should send text and filename in payload."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "att_123"}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.add_attachment("code content", "main.py")

        assert result.success is True
        mock_http.request.assert_called_once_with(
            method="POST",
            url="/attachments/text",
            json={"text": "code content", "suggested_name": "main.py"}
        )

    @pytest.mark.asyncio
    async def test_add_attachment_without_filename(self):
        """Should send text only when filename is None."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "att_456"}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.add_attachment("some content", None)

        mock_http.request.assert_called_once_with(
            method="POST",
            url="/attachments/text",
            json={"text": "some content"}  # No suggested_name
        )


class TestScriptboardClientClearAttachments:
    """Tests for clear_attachments method."""

    @pytest.mark.asyncio
    async def test_clear_attachments_success(self):
        """Should send DELETE request to /attachments."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "cleared"}

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.clear_attachments()

        assert result.success is True
        mock_http.request.assert_called_once_with(
            method="DELETE",
            url="/attachments",
            json=None
        )


class TestScriptboardClientErrorHandling:
    """Tests for HTTP error handling."""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Should return friendly message on connection error."""
        client = ScriptboardClient()

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.side_effect = httpx.ConnectError("Connection refused")
            mock_get.return_value = mock_http

            result = await client.set_prompt("test")

        assert result.success is False
        assert "not running" in result.error
        assert "localhost:8000" in result.error

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Should return timeout message on timeout."""
        client = ScriptboardClient()

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.side_effect = httpx.TimeoutException("Timeout")
            mock_get.return_value = mock_http

            result = await client.set_prompt("test")

        assert result.success is False
        assert "timed out" in result.error

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        """Should catch and wrap generic exceptions."""
        client = ScriptboardClient()

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.side_effect = Exception("Something went wrong")
            mock_get.return_value = mock_http

            result = await client.set_prompt("test")

        assert result.success is False
        assert "Something went wrong" in result.error

    @pytest.mark.asyncio
    async def test_non_json_response(self):
        """Should handle non-JSON response body."""
        client = ScriptboardClient()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Plain text response"

        with patch.object(client, '_get_client') as mock_get:
            mock_http = AsyncMock()
            mock_http.request.return_value = mock_response
            mock_get.return_value = mock_http

            result = await client.set_prompt("test")

        assert result.success is True
        assert result.data == {"text": "Plain text response"}


class TestGetClient:
    """Tests for get_client singleton."""

    def test_get_client_returns_singleton(self):
        """Should return same client instance."""
        # Reset singleton
        import http_client
        http_client._client = None

        client1 = get_client()
        client2 = get_client()

        assert client1 is client2

    def test_get_client_creates_scriptboard_client(self):
        """Should create ScriptboardClient instance."""
        import http_client
        http_client._client = None

        client = get_client()

        assert isinstance(client, ScriptboardClient)


class TestClientClose:
    """Tests for client cleanup."""

    @pytest.mark.asyncio
    async def test_close_cleans_up(self):
        """Should close HTTP client and reset to None."""
        client = ScriptboardClient()

        # Create mock HTTP client
        mock_http = AsyncMock()
        client._client = mock_http

        await client.close()

        mock_http.aclose.assert_called_once()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_when_no_client(self):
        """Should handle close when client is None."""
        client = ScriptboardClient()
        client._client = None

        # Should not raise
        await client.close()

        assert client._client is None
