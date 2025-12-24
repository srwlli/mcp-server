"""
Tests for Scriptboard MCP Server.

Tests the MCP tool handlers with mocked HTTP client.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from http_client import ScriptboardResponse


class TestListTools:
    """Tests for list_tools() function."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_four_tools(self):
        """Should return all 4 Scriptboard tools."""
        from server import list_tools

        tools = await list_tools()

        assert len(tools) == 4
        tool_names = [t.name for t in tools]
        assert "mcp__scriptboard__set_prompt" in tool_names
        assert "mcp__scriptboard__clear_prompt" in tool_names
        assert "mcp__scriptboard__add_attachment" in tool_names
        assert "mcp__scriptboard__clear_attachments" in tool_names

    @pytest.mark.asyncio
    async def test_set_prompt_schema(self):
        """set_prompt should require text parameter."""
        from server import list_tools

        tools = await list_tools()
        set_prompt = next(t for t in tools if t.name == "mcp__scriptboard__set_prompt")

        assert set_prompt.inputSchema["required"] == ["text"]
        assert "text" in set_prompt.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_add_attachment_schema(self):
        """add_attachment should require text, optional filename."""
        from server import list_tools

        tools = await list_tools()
        add_attachment = next(t for t in tools if t.name == "mcp__scriptboard__add_attachment")

        assert add_attachment.inputSchema["required"] == ["text"]
        assert "text" in add_attachment.inputSchema["properties"]
        assert "filename" in add_attachment.inputSchema["properties"]


class TestSetPrompt:
    """Tests for set_prompt tool handler."""

    @pytest.mark.asyncio
    async def test_set_prompt_success(self):
        """Should return success when prompt is set."""
        from server import call_tool

        mock_response = ScriptboardResponse(
            success=True,
            data={"status": "ok"}
        )

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.set_prompt.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__set_prompt",
                {"text": "Review this code"}
            )

        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        assert response_data["message"] == "Prompt set in Scriptboard"

    @pytest.mark.asyncio
    async def test_set_prompt_empty_text(self):
        """Should return error when text is empty."""
        from server import call_tool

        result = await call_tool(
            "mcp__scriptboard__set_prompt",
            {"text": ""}
        )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is False
        assert "text parameter is required" in response_data["error"]

    @pytest.mark.asyncio
    async def test_set_prompt_missing_text(self):
        """Should return error when text parameter is missing."""
        from server import call_tool

        result = await call_tool(
            "mcp__scriptboard__set_prompt",
            {}
        )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is False

    @pytest.mark.asyncio
    async def test_set_prompt_backend_error(self):
        """Should return error message when backend fails."""
        from server import call_tool

        mock_response = ScriptboardResponse(
            success=False,
            error="Scriptboard not running. Start backend at localhost:8000"
        )

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.set_prompt.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__set_prompt",
                {"text": "test prompt"}
            )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is False
        assert "not running" in response_data["message"]


class TestClearPrompt:
    """Tests for clear_prompt tool handler."""

    @pytest.mark.asyncio
    async def test_clear_prompt_success(self):
        """Should return success when prompt is cleared."""
        from server import call_tool

        mock_response = ScriptboardResponse(success=True)

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.clear_prompt.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__clear_prompt",
                {}
            )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        assert response_data["message"] == "Prompt cleared"


class TestAddAttachment:
    """Tests for add_attachment tool handler."""

    @pytest.mark.asyncio
    async def test_add_attachment_with_filename(self):
        """Should add attachment with filename."""
        from server import call_tool

        mock_response = ScriptboardResponse(
            success=True,
            data={"id": "att_123", "filename": "auth.py"}
        )

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.add_attachment.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__add_attachment",
                {"text": "def login():\n    pass", "filename": "auth.py"}
            )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        assert "auth.py" in response_data["message"]
        mock_client.add_attachment.assert_called_once_with(
            "def login():\n    pass",
            "auth.py"
        )

    @pytest.mark.asyncio
    async def test_add_attachment_without_filename(self):
        """Should add attachment without filename (unnamed)."""
        from server import call_tool

        mock_response = ScriptboardResponse(success=True, data={"id": "att_456"})

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.add_attachment.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__add_attachment",
                {"text": "some code content"}
            )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        assert "unnamed" in response_data["message"]
        mock_client.add_attachment.assert_called_once_with("some code content", None)

    @pytest.mark.asyncio
    async def test_add_attachment_empty_text(self):
        """Should return error when text is empty."""
        from server import call_tool

        result = await call_tool(
            "mcp__scriptboard__add_attachment",
            {"text": "", "filename": "empty.py"}
        )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is False
        assert "text parameter is required" in response_data["error"]


class TestClearAttachments:
    """Tests for clear_attachments tool handler."""

    @pytest.mark.asyncio
    async def test_clear_attachments_success(self):
        """Should return success when attachments are cleared."""
        from server import call_tool

        mock_response = ScriptboardResponse(success=True)

        with patch('server.get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.clear_attachments.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = await call_tool(
                "mcp__scriptboard__clear_attachments",
                {}
            )

        response_data = json.loads(result[0].text)
        assert response_data["success"] is True
        assert response_data["message"] == "All attachments cleared"


class TestUnknownTool:
    """Tests for unknown tool handling."""

    @pytest.mark.asyncio
    async def test_unknown_tool_raises_error(self):
        """Should raise ValueError for unknown tool names."""
        from server import call_tool

        with pytest.raises(ValueError) as exc_info:
            await call_tool("mcp__scriptboard__unknown_tool", {})

        assert "Unknown tool" in str(exc_info.value)
