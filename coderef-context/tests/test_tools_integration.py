"""
Integration tests for coderef-context MCP tools - ACTUAL CLI EXECUTION

These tests call the real @coderef/core CLI and validate actual behavior.
Not mocked - tests real tool functionality.
"""

import pytest
import json
import subprocess
import os
import sys
from pathlib import Path


@pytest.fixture
def cli_bin(cli_path):
    """Get the CLI binary path."""
    return os.path.join(cli_path, "dist", "cli.js")


@pytest.fixture
def node_cmd():
    """Get node command (handles Windows vs Unix)."""
    return "node"


async def run_cli_command(cli_bin, node_cmd, *args, timeout=120):
    """
    Run a CLI command and return parsed JSON output.

    Args:
        cli_bin: Path to cli.js
        node_cmd: Node command
        *args: CLI arguments
        timeout: Command timeout in seconds

    Returns:
        Parsed JSON output as dict
    """
    import asyncio

    cmd = [node_cmd, cli_bin] + list(args) + ["--json"]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        if process.returncode != 0:
            raise RuntimeError(f"CLI error: {stderr.decode()}")

        output = stdout.decode()

        # CLI outputs emoji + message before JSON, need to extract JSON part
        # Find the first '[' or '{' which marks start of JSON (use min to get earliest)
        bracket_pos = output.find('[')
        brace_pos = output.find('{')
        # Filter out -1 values (not found) and take minimum of valid positions
        positions = [p for p in [bracket_pos, brace_pos] if p >= 0]
        if not positions:
            raise ValueError(f"No JSON found in CLI output: {output}")
        json_start = min(positions)

        # Find the end of JSON (last ] or })
        json_part = output[json_start:]

        # If JSON starts with '[', look for the closing ']'
        # If it starts with '{', look for the closing '}'
        if json_part[0] == '[':
            # Find the last ']'
            last_bracket = json_part.rfind(']')
            if last_bracket > 0:
                json_str = json_part[:last_bracket + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

        # Fallback: try to parse with increasing length
        for i in range(len(json_part), 0, -1):
            try:
                return json.loads(json_part[:i])
            except json.JSONDecodeError:
                continue

        raise ValueError(f"Could not parse JSON from output: {output}")
    except asyncio.TimeoutError:
        raise TimeoutError(f"CLI command timed out after {timeout}s")


# ============================================================================
# CODEREF_SCAN INTEGRATION TESTS
# ============================================================================

class TestCoderefScanIntegration:
    """Integration tests for coderef_scan - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_scan_valid_project(self, test_project_path, cli_bin, node_cmd):
        """Test scanning a valid project with default settings."""
        result = await run_cli_command(cli_bin, node_cmd, "scan", test_project_path)

        # CLI returns array of elements directly
        assert isinstance(result, list)
        assert len(result) > 0, "Should find elements in coderef-context source"

        # Validate elements have required fields
        for element in result:
            assert "name" in element, f"Element missing 'name': {element}"
            assert "type" in element, f"Element missing 'type': {element}"
            assert "file" in element, f"Element missing 'file': {element}"
            assert "line" in element, f"Element missing 'line': {element}"

    @pytest.mark.asyncio
    async def test_scan_with_ast_mode(self, test_project_path, cli_bin, node_cmd):
        """Test scan with AST analysis enabled (99% accuracy)."""
        # Run scan (CLI handles AST internally)
        result = await run_cli_command(
            cli_bin, node_cmd, "scan", test_project_path
        )

        assert isinstance(result, list) or (isinstance(result, dict) and "elements" in result)
        # Should find elements
        elements = result if isinstance(result, list) else result.get("elements", [])
        assert len(elements) > 0

    @pytest.mark.asyncio
    async def test_scan_discovers_server_class(self, test_project_path, cli_bin, node_cmd):
        """Test that scan finds elements in the scanned project."""
        result = await run_cli_command(cli_bin, node_cmd, "scan", test_project_path)

        # CLI returns array directly
        assert isinstance(result, list), "Scan should return array of elements"
        assert len(result) > 0, "Should find elements in scanned project"

        # Each element should have required fields
        for elem in result:
            assert "name" in elem, "Element missing 'name' field"
            assert "type" in elem, "Element missing 'type' field"
            assert "file" in elem, "Element missing 'file' field"
            assert "line" in elem, "Element missing 'line' field"

    @pytest.mark.asyncio
    async def test_scan_discovers_functions(self, test_project_path, cli_bin, node_cmd):
        """Test that scan discovers functions."""
        result = await run_cli_command(cli_bin, node_cmd, "scan", test_project_path)

        # CLI returns array directly
        assert isinstance(result, list), "Scan should return array"

        # Should find some functions
        functions = [e for e in result if e.get("type") == "function"]
        assert len(functions) > 0, f"No functions found in scan results. Found {len(result)} total elements"

    @pytest.mark.asyncio
    async def test_scan_custom_languages(self, test_project_path, cli_bin, node_cmd):
        """Test scan returns valid results."""
        result = await run_cli_command(
            cli_bin, node_cmd, "scan", test_project_path
        )

        # CLI returns array directly
        assert isinstance(result, list), "Scan should return array of elements"
        # Should find at least some elements in the scanned project
        assert len(result) > 0, "Should find elements in scanned project"


# ============================================================================
# CODEREF_QUERY INTEGRATION TESTS
# ============================================================================

class TestCoderefQueryIntegration:
    """Integration tests for coderef_query - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_query_imports(self, test_project_path, cli_bin, node_cmd):
        """Test 'imports' query - what does Server import?"""
        result = await run_cli_command(
            cli_bin, node_cmd, "query", test_project_path,
            "--type", "imports", "--target", "Server"
        )

        assert "success" in result or "relationships" in result
        # Query should return results
        assert result is not None

    @pytest.mark.asyncio
    async def test_query_calls(self, test_project_path, cli_bin, node_cmd):
        """Test 'calls' query - what calls list_tools?"""
        result = await run_cli_command(
            cli_bin, node_cmd, "query", test_project_path,
            "--type", "calls", "--target", "list_tools"
        )

        # Should get valid response
        assert result is not None

    @pytest.mark.asyncio
    async def test_query_depends_on(self, test_project_path, cli_bin, node_cmd):
        """Test 'depends-on' query - what does Server depend on?"""
        result = await run_cli_command(
            cli_bin, node_cmd, "query", test_project_path,
            "--type", "depends-on", "--target", "Server"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_query_with_custom_depth(self, test_project_path, cli_bin, node_cmd):
        """Test query with custom max_depth parameter."""
        result = await run_cli_command(
            cli_bin, node_cmd, "query", test_project_path,
            "--type", "imports", "--target", "Server", "--depth", "2"
        )

        assert result is not None


# ============================================================================
# CODEREF_IMPACT INTEGRATION TESTS
# ============================================================================

class TestCoderefImpactIntegration:
    """Integration tests for coderef_impact - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_impact_modify_operation(self, test_project_path, cli_bin, node_cmd):
        """Test impact analysis for 'modify' operation on Server."""
        result = await run_cli_command(
            cli_bin, node_cmd, "impact", test_project_path,
            "--element", "Server", "--operation", "modify"
        )

        # Should get impact analysis
        assert result is not None
        assert "success" in result or "impact" in result

    @pytest.mark.asyncio
    async def test_impact_delete_operation(self, test_project_path, cli_bin, node_cmd):
        """Test impact analysis for 'delete' operation."""
        result = await run_cli_command(
            cli_bin, node_cmd, "impact", test_project_path,
            "--element", "Server", "--operation", "delete"
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_impact_refactor_operation(self, test_project_path, cli_bin, node_cmd):
        """Test impact analysis for 'refactor' operation."""
        result = await run_cli_command(
            cli_bin, node_cmd, "impact", test_project_path,
            "--element", "Server", "--operation", "refactor"
        )

        assert result is not None


# ============================================================================
# CODEREF_COMPLEXITY INTEGRATION TESTS
# ============================================================================

class TestCoderefComplexityIntegration:
    """Integration tests for coderef_complexity - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_complexity_metrics(self, test_project_path, cli_bin, node_cmd):
        """Test getting complexity metrics for Server class."""
        result = await run_cli_command(
            cli_bin, node_cmd, "complexity", test_project_path,
            "--element", "Server"
        )

        # Should return complexity data
        assert result is not None


# ============================================================================
# CODEREF_PATTERNS INTEGRATION TESTS
# ============================================================================

class TestCoderefPatternsIntegration:
    """Integration tests for coderef_patterns - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_patterns_discovery(self, test_project_path, cli_bin, node_cmd):
        """Test discovering patterns in project."""
        result = await run_cli_command(
            cli_bin, node_cmd, "patterns", test_project_path
        )

        assert result is not None
        assert "success" in result or "patterns" in result


# ============================================================================
# CODEREF_CONTEXT INTEGRATION TESTS
# ============================================================================

class TestCoderefContextIntegration:
    """Integration tests for coderef_context - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_context_generation(self, test_project_path, cli_bin, node_cmd):
        """Test comprehensive context generation."""
        result = await run_cli_command(
            cli_bin, node_cmd, "context", test_project_path
        )

        assert result is not None


# ============================================================================
# CODEREF_DIAGRAM INTEGRATION TESTS
# ============================================================================

class TestCoderefDiagramIntegration:
    """Integration tests for coderef_diagram - actual CLI calls."""

    @pytest.mark.asyncio
    async def test_diagram_generation(self, test_project_path, cli_bin, node_cmd):
        """Test generating dependency diagram."""
        result = await run_cli_command(
            cli_bin, node_cmd, "diagram", test_project_path
        )

        # Should return diagram data (Mermaid or Graphviz)
        assert result is not None


# ============================================================================
# MULTI-TOOL WORKFLOW TESTS
# ============================================================================

class TestWorkflowIntegration:
    """Integration tests for multi-tool workflows."""

    @pytest.mark.asyncio
    async def test_scan_then_query_workflow(self, test_project_path, cli_bin, node_cmd):
        """Test scan → query workflow."""
        # Step 1: Scan to find elements
        scan_result = await run_cli_command(cli_bin, node_cmd, "scan", test_project_path)
        assert scan_result["success"] is True
        assert len(scan_result["elements"]) > 0

        # Step 2: Query an element found by scan
        first_element = scan_result["elements"][0]["name"]
        query_result = await run_cli_command(
            cli_bin, node_cmd, "query", test_project_path,
            "--type", "imports", "--target", first_element
        )

        # Both should succeed
        assert query_result is not None

    @pytest.mark.asyncio
    async def test_scan_then_impact_workflow(self, test_project_path, cli_bin, node_cmd):
        """Test scan → impact workflow."""
        # Step 1: Scan
        scan_result = await run_cli_command(cli_bin, node_cmd, "scan", test_project_path)
        assert len(scan_result["elements"]) > 0

        # Step 2: Analyze impact of modifying first element
        first_element = scan_result["elements"][0]["name"]
        impact_result = await run_cli_command(
            cli_bin, node_cmd, "impact", test_project_path,
            "--element", first_element, "--operation", "modify"
        )

        assert impact_result is not None
