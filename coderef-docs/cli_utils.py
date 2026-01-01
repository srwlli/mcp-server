"""
CLI utilities for calling @coderef/core CLI from coderef-docs MCP server.

Provides subprocess utilities for executing the @coderef/core command-line tool
and parsing its JSON output. Handles errors gracefully with logging.

CLI Path Configuration:
    The CLI path is resolved in the following priority order:
    1. CODEREF_CLI_PATH environment variable (recommended)
    2. Global 'coderef' command in PATH (npm install -g @coderef/cli)
    3. Hardcoded DEFAULT_CLI_PATH (deprecated, shows warning)

    Example configuration:
        # Windows
        set CODEREF_CLI_PATH=C:\\path\\to\\coderef\\packages\\cli\\dist\\cli.js

        # Linux/Mac
        export CODEREF_CLI_PATH=/path/to/coderef/packages/cli/dist/cli.js

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 1 + WO-ENV-VAR-CLI-PATH-001.
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

    Resolution order:
    1. CODEREF_CLI_PATH environment variable (explicit override)
    2. Check if 'coderef' in PATH (global npm install)
    3. Fallback to DEFAULT_CLI_PATH (local development)

    Returns:
        str: Absolute path to CLI executable

    Raises:
        FileNotFoundError: If CLI not found in any location

    Example:
        >>> # Using environment variable
        >>> os.environ['CODEREF_CLI_PATH'] = '/custom/path/cli.js'
        >>> path = get_cli_path()
        >>> print(path)
        '/custom/path/cli.js'
    """
    import os
    import shutil

    # Priority 1: Environment variable (explicit override)
    env_path = os.getenv("CODEREF_CLI_PATH")
    if env_path:
        env_path_obj = Path(env_path)
        if env_path_obj.exists() and env_path_obj.is_file():
            logger.info(f"Using CLI from CODEREF_CLI_PATH: {env_path}")
            return str(env_path_obj.absolute())
        else:
            logger.warning(f"CODEREF_CLI_PATH set but invalid: {env_path}")

    # Priority 2: Fallback to hardcoded path first (most reliable)
    default_path = Path(DEFAULT_CLI_PATH)
    if default_path.exists():
        logger.info(f"Using hardcoded CLI path: {DEFAULT_CLI_PATH}")
        return DEFAULT_CLI_PATH

    # Priority 3: Check PATH for global install (may be broken)
    global_cli = shutil.which("coderef")
    if global_cli:
        logger.warning(f"Using global CLI from PATH: {global_cli} (may be broken)")
        return global_cli

    # No CLI found anywhere
    raise FileNotFoundError(
        "Could not find @coderef/core CLI. "
        "Set CODEREF_CLI_PATH environment variable or install globally with: "
        "npm install -g @coderef/cli"
    )


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

    # Fallback: Use get_cli_path() which checks all sources
    try:
        cli_path = get_cli_path()
        cli_file = Path(cli_path)

        if not cli_file.exists():
            logger.warning(f"CLI not found at {cli_path}")
            return False

        if not cli_file.is_file():
            logger.warning(f"CLI path exists but is not a file: {cli_path}")
            return False

        # Check if file is readable
        try:
            with open(cli_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.read(1)  # Read 1 byte to verify access
            logger.info(f"CLI validated successfully: {cli_path}")
            return True
        except (PermissionError, OSError) as e:
            logger.warning(f"CLI file not readable: {e}")
            return False

    except FileNotFoundError as e:
        logger.warning(f"CLI not found: {e}")
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

    # Build full command based on CLI type
    # If CLI is a .CMD/.BAT file (Windows npm wrapper), run directly
    # If CLI is a .js file, run with node
    if cli_path.lower().endswith(('.cmd', '.bat')):
        # Windows batch wrapper - run directly
        full_command = [cli_path, command] + args
    elif cli_path.lower().endswith('.js'):
        # Node.js file - run with node
        full_command = ["node", cli_path, command] + args
    else:
        # Assume executable (global install or direct path)
        full_command = [cli_path, command] + args

    logger.info(f"Running CLI command: {command} with {len(args)} args (cli_type: {Path(cli_path).suffix})")

    try:
        # Execute command with timeout
        # Use utf-8 encoding to handle emoji and non-ASCII characters
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid chars instead of crashing
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
        # Strip progress indicators (lines starting with emoji or "🔍")
        output_lines = result.stdout.strip().split('\n')
        json_start = 0
        for i, line in enumerate(output_lines):
            if line.strip().startswith('[') or line.strip().startswith('{'):
                json_start = i
                break

        json_output = '\n'.join(output_lines[json_start:])

        try:
            data = json.loads(json_output)
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
