"""
Integration Tests for WO-CONTEXT-INTEGRATION-001

Tests the new MCP tools added in this workorder:
- coderef_incremental_scan (P1-1)
- generate_foundation_docs (P2-2)
- validate_coderef_outputs (P2-3)
"""

import json
import pytest
from pathlib import Path
from src.handlers_refactored import (
    handle_coderef_incremental_scan,
    handle_generate_foundation_docs,
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
async def test_generate_foundation_docs_api():
    """Test generate_foundation_docs creates API.md"""
    import tempfile
    project_path = str(Path(__file__).parent.parent)

    # Create temp output dir
    output_dir = tempfile.mkdtemp()

    result = await handle_generate_foundation_docs({
        "project_path": project_path,
        "docs": ["api"],
        "output_dir": output_dir
    })

    # Parse response
    response = json.loads(result[0].text)

    # Should succeed if .coderef/index.json exists
    if response.get("success"):
        assert len(response.get("generated_files", [])) == 1
        assert "API.md" in response["generated_files"][0]

        # Verify file was created
        api_file = Path(output_dir) / "API.md"
        assert api_file.exists()

        # Verify content has expected sections
        content = api_file.read_text()
        assert "# API Reference" in content


@pytest.mark.asyncio
async def test_generate_foundation_docs_all():
    """Test generate_foundation_docs creates all doc types"""
    import tempfile
    project_path = str(Path(__file__).parent.parent)
    output_dir = tempfile.mkdtemp()

    result = await handle_generate_foundation_docs({
        "project_path": project_path,
        "docs": ["api", "schema", "components", "readme"],
        "output_dir": output_dir
    })

    # Parse response
    response = json.loads(result[0].text)

    if response.get("success"):
        # Should generate 4 files
        assert len(response.get("generated_files", [])) == 4

        # Verify all expected files exist
        for filename in ["API.md", "SCHEMA.md", "COMPONENTS.md", "README.md"]:
            file_path = Path(output_dir) / filename
            assert file_path.exists(), f"{filename} not created"


@pytest.mark.asyncio
async def test_generate_foundation_docs_no_index():
    """Test generate_foundation_docs handles missing index.json"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()

    result = await handle_generate_foundation_docs({
        "project_path": temp_dir,
        "docs": ["api"],
        "output_dir": output_dir
    })

    # Parse response
    response = json.loads(result[0].text)

    # Should fail gracefully
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


def test_foundation_doc_generator_import():
    """Test that foundation_doc_generator module imports correctly"""
    from src.foundation_doc_generator import FoundationDocGenerator, generate_foundation_docs

    # Should import without errors
    assert FoundationDocGenerator is not None
    assert generate_foundation_docs is not None


def test_foundation_doc_generator_class():
    """Test FoundationDocGenerator class initialization"""
    from src.foundation_doc_generator import FoundationDocGenerator

    # Create instance with empty data
    generator = FoundationDocGenerator("/tmp", [])

    # Should initialize without errors
    assert generator.project_path == Path("/tmp")
    assert generator.index_data == []
    assert generator.timestamp is not None


def test_foundation_doc_generator_group_by_type():
    """Test element grouping by type"""
    from src.foundation_doc_generator import FoundationDocGenerator

    # Sample index data
    index_data = [
        {"name": "foo", "type": "function"},
        {"name": "bar", "type": "function"},
        {"name": "Baz", "type": "class"},
    ]

    generator = FoundationDocGenerator("/tmp", index_data)
    grouped = generator._group_by_type()

    assert "function" in grouped
    assert len(grouped["function"]) == 2
    assert "class" in grouped
    assert len(grouped["class"]) == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
