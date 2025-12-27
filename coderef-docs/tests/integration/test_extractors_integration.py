"""
Integration tests for extractors module with real CLI calls.

Tests actual CLI execution and output transformation with real coderef-docs project.
Verifies graceful error handling with invalid paths.

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 3 (TEST-002).
"""

import pytest
import os
import json
from pathlib import Path

# Import functions to test
from extractors import extract_apis, extract_schemas, extract_components


class TestExtractorsIntegration:
    """Integration tests with real coderef CLI calls."""

    @pytest.fixture
    def test_project_path(self):
        """Use actual coderef-docs project for testing."""
        # Get absolute path to coderef-docs project root
        return str(Path(__file__).parent.parent.parent)

    def setup_method(self):
        """Clear LRU caches before each test."""
        extract_apis.cache_clear()
        extract_schemas.cache_clear()
        extract_components.cache_clear()

    def test_extract_apis_real_project(self, test_project_path):
        """Test API extraction with real coderef-docs project."""
        result = extract_apis(test_project_path)

        # Verify result structure
        assert isinstance(result, dict)
        assert "endpoints" in result or "error" in result
        assert "timestamp" in result
        assert "source" in result

        # Verify timestamp is ISO8601-like
        assert "T" in result["timestamp"]

        # If successful, verify endpoints format
        if "error" not in result or result["error"] is None:
            endpoints = result.get("endpoints", [])
            assert isinstance(endpoints, list)

            # Each endpoint should have required fields
            for endpoint in endpoints:
                assert isinstance(endpoint, dict)
                assert "method" in endpoint
                assert "path" in endpoint
                # Optional fields: params, response, description

    def test_extract_schemas_real_project(self, test_project_path):
        """Test schema extraction with real coderef-docs project."""
        result = extract_schemas(test_project_path)

        # Verify result structure
        assert isinstance(result, dict)
        assert "entities" in result or "error" in result
        assert "timestamp" in result
        assert "source" in result

        # Verify timestamp
        assert "T" in result["timestamp"]

        # If successful, verify entities format
        if "error" not in result or result["error"] is None:
            entities = result.get("entities", [])
            assert isinstance(entities, list)

            # Each entity should have required fields
            for entity in entities:
                assert isinstance(entity, dict)
                assert "name" in entity
                assert "fields" in entity
                # Optional field: relationships

    def test_extract_components_real_project(self, test_project_path):
        """Test component extraction with real coderef-docs project."""
        result = extract_components(test_project_path)

        # Verify result structure
        assert isinstance(result, dict)
        assert "components" in result or "error" in result
        assert "timestamp" in result
        assert "source" in result

        # Verify timestamp
        assert "T" in result["timestamp"]

        # If successful, verify components format
        if "error" not in result or result["error"] is None:
            components = result.get("components", [])
            assert isinstance(components, list)

            # Each component should have required fields
            for component in components:
                assert isinstance(component, dict)
                assert "name" in component
                assert "type" in component
                # Optional fields: props, children, description

    def test_all_extractions_have_timestamps(self, test_project_path):
        """Verify all extractions include ISO8601 timestamps."""
        apis = extract_apis(test_project_path)
        schemas = extract_schemas(test_project_path)
        components = extract_components(test_project_path)

        # All should have timestamps
        for result in [apis, schemas, components]:
            assert "timestamp" in result
            # Verify timestamp is ISO8601-like (contains 'T' separator)
            assert "T" in result["timestamp"]

    def test_extractions_handle_nonexistent_path(self):
        """Test extractions gracefully handle invalid project path."""
        bad_path = "/nonexistent/path/that/does/not/exist/xyz123"

        apis = extract_apis(bad_path)
        schemas = extract_schemas(bad_path)
        components = extract_components(bad_path)

        # All should handle gracefully (return error or placeholder)
        for result in [apis, schemas, components]:
            assert isinstance(result, dict)
            assert "timestamp" in result
            assert "error" in result
            # Should not crash - either error or placeholder

    def test_extract_apis_caching_works(self, test_project_path):
        """Test that API extraction results are cached correctly."""
        # First call
        result1 = extract_apis(test_project_path)

        # Second call (should be cached)
        result2 = extract_apis(test_project_path)

        # Results should be identical (same timestamp indicates cache hit)
        assert result1["timestamp"] == result2["timestamp"]
        assert result1["source"] == result2["source"]

    def test_extract_schemas_caching_works(self, test_project_path):
        """Test that schema extraction results are cached correctly."""
        # First call
        result1 = extract_schemas(test_project_path)

        # Second call (should be cached)
        result2 = extract_schemas(test_project_path)

        # Results should be identical
        assert result1["timestamp"] == result2["timestamp"]
        assert result1["source"] == result2["source"]

    def test_extract_components_caching_works(self, test_project_path):
        """Test that component extraction results are cached correctly."""
        # First call
        result1 = extract_components(test_project_path)

        # Second call (should be cached)
        result2 = extract_components(test_project_path)

        # Results should be identical
        assert result1["timestamp"] == result2["timestamp"]
        assert result1["source"] == result2["source"]

    def test_all_extractors_have_source_field(self, test_project_path):
        """Verify all extractors return a source field."""
        apis = extract_apis(test_project_path)
        schemas = extract_schemas(test_project_path)
        components = extract_components(test_project_path)

        # All should have source field
        for result in [apis, schemas, components]:
            assert "source" in result
            # Source should be one of: coderef-cli, placeholder, error
            assert result["source"] in ["coderef-cli", "placeholder", "error"]

    def test_extractors_return_empty_lists_on_error(self):
        """Verify extractors return empty lists (not None) on error."""
        bad_path = "/this/path/does/not/exist"

        apis = extract_apis(bad_path)
        schemas = extract_schemas(bad_path)
        components = extract_components(bad_path)

        # All should return empty lists, not None
        assert apis.get("endpoints") is not None
        assert isinstance(apis.get("endpoints"), list)

        assert schemas.get("entities") is not None
        assert isinstance(schemas.get("entities"), list)

        assert components.get("components") is not None
        assert isinstance(components.get("components"), list)
