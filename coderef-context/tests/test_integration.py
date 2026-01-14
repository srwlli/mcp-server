"""
Integration Tests for WO-CONTEXT-INTEGRATION-001

Tests the new MCP tools added in this workorder:
- coderef_incremental_scan (P1-1)
- validate_coderef_outputs (P2-3)

Note: generate_foundation_docs (P2-2) was removed in WO-FOUNDATION-DOCS-CLEANUP-001
      and consolidated to coderef-docs server.
"""

import json
import pytest
from pathlib import Path
from src.handlers_refactored import (
    handle_coderef_incremental_scan,
    handle_validate_coderef_outputs,
)


@pytest.mark.asyncio
async def test_incremental_scan_with_drift():
    """Test incremental_scan detects drift and returns changed files"""
    # Use current project as test subject
    project_path = str(Path(__file__).parent.parent)

    result = await handle_coderef_incremental_scan({"project_path": project_path})

    # Parse response
    assert len(result) > 0, "No result returned"
    assert result[0].text, "Empty response text"
    response = json.loads(result[0].text)

    # Should succeed (drift.json exists)
    assert response.get("success") == True or response.get("drift_detected") == False

    # Should have changed_files array
    assert "changed_files" in response
    assert isinstance(response["changed_files"], list)


@pytest.mark.asyncio
async def test_incremental_scan_no_coderef():
    """Test incremental_scan handles missing .coderef/ gracefully"""
    # Use /tmp directory (no .coderef/)
    import tempfile
    temp_dir = tempfile.mkdtemp()

    result = await handle_coderef_incremental_scan({"project_path": temp_dir})

    # Parse response
    assert len(result) > 0, "No result returned"
    assert result[0].text, "Empty response text"

    # Error response might be plain text or JSON
    response_text = result[0].text
    if response_text.startswith("Error"):
        # Plain text error
        assert "No drift data found" in response_text or "error" in response_text.lower()
    else:
        # JSON error
        response = json.loads(response_text)
        assert response.get("success") == False
        assert "error" in response


@pytest.mark.asyncio
async def test_validate_coderef_outputs_valid():
    """Test validate_coderef_outputs with valid .coderef/ directory"""
    project_path = str(Path(__file__).parent.parent)

    result = await handle_validate_coderef_outputs({"project_path": project_path})

    # Parse response
    response = json.loads(result[0].text)

    # Should succeed if .coderef/ exists
    if ".coderef" in str(Path(project_path).iterdir()):
        assert "average_score" in response
        assert "validation_results" in response
        assert isinstance(response["validation_results"], list)


@pytest.mark.asyncio
async def test_validate_coderef_outputs_missing():
    """Test validate_coderef_outputs handles missing .coderef/"""
    import tempfile
    temp_dir = tempfile.mkdtemp()

    result = await handle_validate_coderef_outputs({"project_path": temp_dir})

    # Parse response
    response = json.loads(result[0].text)

    # Should fail gracefully
    assert response.get("success") == False
    assert "error" in response


@pytest.mark.asyncio
async def test_validate_coderef_outputs_structure():
    """Test validate_coderef_outputs returns expected structure"""
    project_path = str(Path(__file__).parent.parent)

    result = await handle_validate_coderef_outputs({"project_path": project_path})

    # Parse response
    response = json.loads(result[0].text)

    # Should have expected fields
    assert "success" in response

    if response.get("success"):
        assert "average_score" in response
        assert isinstance(response["average_score"], int)
        assert 0 <= response["average_score"] <= 100

        assert "validation_results" in response
        assert isinstance(response["validation_results"], list)

        # Each validation result should have file, score, exists
        for result_item in response["validation_results"]:
            assert "file" in result_item
            assert "score" in result_item
            assert "exists" in result_item


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
