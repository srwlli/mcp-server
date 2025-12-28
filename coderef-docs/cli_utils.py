"""
CLI utilities for calling @coderef/core CLI from coderef-docs MCP server.

Provides subprocess utilities for executing the @coderef/core command-line tool
and parsing its JSON output. Handles errors gracefully with logging.

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 1.
"""

import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from logger_config import logger

# Default CLI path - can be overridden via environment variable
DEFAULT_CLI_PATH = r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli\dist\cli.js"


def get_cli_path() -> str:
    """
    Get path to @coderef/core CLI binary.

    Returns:
        str: Absolute path to CLI executable (Node.js script)

    Example:
        >>> path = get_cli_path()
        >>> print(path)
        'C:\\Users\\willh\\Desktop\\projects\\coderef-system\\packages\\cli\\dist\\cli.js'
    """
    # TODO: Support environment variable override (CODEREF_CLI_PATH)
    return DEFAULT_CLI_PATH


def validate_cli_available() -> bool:
    """
    Check if @coderef/core CLI exists and is accessible.

    Verifies that:
    1. First checks if 'coderef' command is available in PATH (global install)
    2. Falls back to checking hardcoded CLI path
    3. Verifies file is readable

    Returns:
        bool: True if CLI is available, False otherwise

    Example:
        >>> if validate_cli_available():
        ...     print("CLI ready")
        ... else:
        ...     print("CLI not found - running in degraded mode")
    """
    # First, check if 'coderef' is available in PATH (global npm install)
    try:
        result = subprocess.run(
            ["coderef", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info(f"CLI found in PATH (global install): coderef --version = {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"Global 'coderef' command not found in PATH: {e}")

    # Fallback: Check hardcoded CLI path
    cli_path = get_cli_path()
    cli_file = Path(cli_path)

    if not cli_file.exists():
        logger.warning(f"CLI not found at {cli_path} and not in PATH")
        return False

    if not cli_file.is_file():
        logger.warning(f"CLI path exists but is not a file: {cli_path}")
        return False

    # Check if file is readable
    try:
        with open(cli_file, 'r', encoding='utf-8', errors='ignore') as f:
            f.read(1)  # Read 1 byte to verify access
        logger.info(f"CLI found at hardcoded path: {cli_path}")
        return True
    except (PermissionError, OSError) as e:
        logger.warning(f"CLI file not readable: {e}")
        return False


def run_coderef_command(command: str, args: Optional[List[str]] = None, timeout: int = 120) -> Dict[str, Any]:
    """
    Execute @coderef/core CLI command and return parsed JSON output.

    Runs the CLI as a subprocess, captures stdout/stderr, and parses the JSON response.
    Handles common errors gracefully with logging.

    Args:
        command: CLI command to run (e.g., "scan", "query", "analyze")
        args: Optional list of command arguments
        timeout: Command timeout in seconds (default: 120)

    Returns:
        dict: Parsed JSON output from CLI, or empty dict on error with 'error' key

    Example:
        >>> result = run_coderef_command("scan", ["--project", "/path/to/project"])
        >>> if "error" not in result:
        ...     print(f"Found {len(result.get('elements', []))} code elements")

    Error Handling:
        - FileNotFoundError: CLI not found (logs warning, returns {"error": "..."})
        - subprocess.TimeoutExpired: Command timed out (logs warning, returns {"error": "..."})
        - json.JSONDecodeError: Invalid JSON response (logs warning, returns {"error": "..."})
        - Exception: Any other error (logs warning, returns {"error": "..."})
    """
    if args is None:
        args = []

    cli_path = get_cli_path()

    # Build full command: node <cli_path> <command> <args>
    full_command = ["node", cli_path, command] + args

    logger.info(f"Running CLI command: {command} with {len(args)} args")

    try:
        # Execute command with timeout
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # Don't raise on non-zero exit codes
        )

        # Log stderr if present (warnings, errors)
        if result.stderr:
            logger.debug(f"CLI stderr: {result.stderr[:200]}")  # First 200 chars

        # Check for empty stdout
        if not result.stdout.strip():
            logger.warning(f"CLI command '{command}' returned empty output")
            return {"error": "Empty output from CLI"}

        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            logger.info(f"CLI command '{command}' completed successfully")
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"CLI output is not valid JSON: {e}")
            logger.debug(f"Raw output (first 500 chars): {result.stdout[:500]}")
            return {"error": f"Invalid JSON from CLI: {str(e)}"}

    except FileNotFoundError as e:
        logger.warning(f"CLI not found at {cli_path}: {e}")
        return {"error": f"CLI not found: {str(e)}"}

    except subprocess.TimeoutExpired as e:
        logger.warning(f"CLI command '{command}' timed out after {timeout}s")
        return {"error": f"Command timed out after {timeout}s"}

    except Exception as e:
        logger.warning(f"Unexpected error running CLI command '{command}': {e}")
        return {"error": f"Unexpected error: {str(e)}"}


# Module-level test function (for manual verification)
def _test_cli() -> None:
    """
    Test CLI utilities (manual verification only).

    This function is for development/debugging purposes.
    Run with: python -c "from cli_utils import _test_cli; _test_cli()"
    """
    print("Testing CLI utilities...")

    # Test 1: Get CLI path
    cli_path = get_cli_path()
    print(f"✓ CLI path: {cli_path}")

    # Test 2: Validate CLI availability
    is_available = validate_cli_available()
    print(f"✓ CLI available: {is_available}")

    if is_available:
        # Test 3: Run simple command (version check or help)
        result = run_coderef_command("--version")
        if "error" not in result:
            print(f"✓ CLI command executed successfully")
        else:
            print(f"✗ CLI command failed: {result['error']}")
    else:
        print("⚠ Skipping command test - CLI not available")


if __name__ == "__main__":
    # Allow running as script for quick tests
    _test_cli()
