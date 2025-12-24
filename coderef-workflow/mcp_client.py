"""
MCP-to-MCP Client for inter-server communication.

Allows coderef-workflow MCP to call tools from coderef-context MCP.
Implements JSON-RPC 2.0 protocol over stdio transport.
"""

import subprocess
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPToolClient:
    """
    Lightweight MCP client for calling coderef-context tools from coderef-workflow.

    Uses JSON-RPC 2.0 protocol over stdio subprocess communication.
    Supports retries, timeouts, and graceful error handling.
    """

    # Class-level singleton instance
    _instance: Optional['MCPToolClient'] = None
    _lock = asyncio.Lock()

    def __init__(self, server_script_path: Optional[str] = None):
        """
        Initialize MCP client.

        Args:
            server_script_path: Path to coderef-context server.py.
                              If None, uses default location.
        """
        if server_script_path is None:
            # Default to coderef-context server
            server_script_path = str(Path(__file__).parent.parent / "coderef-context" / "server.py")

        self.server_script_path = server_script_path
        self.process: Optional[subprocess.Popen] = None
        self.message_id = 0
        self.timeout_seconds = 30
        self.max_retries = 3

        logger.debug(f"Initialized MCPToolClient with server: {server_script_path}")

    async def connect(self) -> bool:
        """
        Start the MCP server subprocess.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            if self.process and self.process.poll() is None:
                logger.debug("MCP server already running")
                return True

            # Start server process
            self.process = subprocess.Popen(
                ["python", self.server_script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            logger.info(f"Started MCP server process (PID: {self.process.pid})")
            await asyncio.sleep(0.5)  # Give server time to start

            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            return False

    async def call_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Call an MCP tool in coderef-context server.

        Args:
            tool_name: Name of tool to call (e.g., "coderef_scan")
            tool_args: Arguments to pass to tool
            retry_count: Internal retry counter (0-max_retries)

        Returns:
            Dict with tool response data and success status

        Raises:
            ConnectionError: If unable to connect to server
            TimeoutError: If tool call exceeds timeout
            RuntimeError: If tool execution fails
        """
        # Ensure connected
        if not self.process or self.process.poll() is not None:
            connected = await self.connect()
            if not connected:
                raise ConnectionError("Failed to connect to MCP server")

        try:
            # Build JSON-RPC request
            self.message_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self.message_id,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": tool_args
                }
            }

            # Send request
            request_json = json.dumps(request)
            logger.debug(f"Sending MCP request: {request_json[:100]}...")

            self.process.stdin.write(request_json + "\n")
            self.process.stdin.flush()

            # Read response with timeout
            try:
                loop = asyncio.get_event_loop()
                response_line = await asyncio.wait_for(
                    loop.run_in_executor(None, self.process.stdout.readline),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Tool call '{tool_name}' exceeded {self.timeout_seconds}s timeout")

            if not response_line:
                raise RuntimeError(f"MCP server closed connection unexpectedly")

            # Parse response
            try:
                response = json.loads(response_line)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MCP response: {response_line}")
                raise RuntimeError(f"Invalid JSON response from MCP server: {str(e)}")

            # Check for errors
            if "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                logger.warning(f"MCP tool error: {error_msg}")

                # Retry on transient errors
                if retry_count < self.max_retries and self._is_retryable(error_msg):
                    logger.info(f"Retrying tool call {retry_count + 1}/{self.max_retries}")
                    await asyncio.sleep(0.5)  # Brief backoff
                    return await self.call_tool(tool_name, tool_args, retry_count + 1)

                raise RuntimeError(f"MCP tool '{tool_name}' failed: {error_msg}")

            # Extract result
            if "result" not in response:
                raise RuntimeError("MCP response missing 'result' field")

            result = response["result"]
            logger.debug(f"Tool '{tool_name}' completed successfully")

            return {
                "success": True,
                "data": result,
                "tool_name": tool_name
            }

        except (ConnectionError, TimeoutError, RuntimeError) as e:
            # Re-raise known errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling tool '{tool_name}': {str(e)}")
            raise RuntimeError(f"Tool call failed: {str(e)}")

    def _is_retryable(self, error_msg: str) -> bool:
        """Check if error is likely transient and worth retrying."""
        retryable_patterns = [
            "timeout",
            "temporary",
            "busy",
            "try again",
            "connection reset"
        ]
        return any(pattern in error_msg.lower() for pattern in retryable_patterns)

    async def disconnect(self):
        """Gracefully shutdown MCP server."""
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=5)
                logger.info("MCP server disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting MCP server: {str(e)}")
                self.process.kill()

    @classmethod
    async def get_instance(cls, server_path: Optional[str] = None) -> 'MCPToolClient':
        """
        Get singleton instance of MCP client (thread-safe).

        Args:
            server_path: Optional custom path to server.py

        Returns:
            Singleton MCPToolClient instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(server_path)
                    await cls._instance.connect()

        return cls._instance


# Convenience function for async code
async def call_coderef_tool(
    tool_name: str,
    tool_args: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to call a coderef tool.

    Args:
        tool_name: Name of tool to call
        tool_args: Arguments to pass to tool

    Returns:
        Dict with tool response

    Raises:
        ConnectionError, TimeoutError, RuntimeError on failure
    """
    client = await MCPToolClient.get_instance()
    return await client.call_tool(tool_name, tool_args)
