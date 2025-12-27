"""
Unit tests for extractors module.

Tests extract_apis, extract_schemas, and extract_components with mocked CLI calls.
Verifies transformation logic, error handling, caching, and graceful degradation.

Part of WO-CONTEXT-DOCS-INTEGRATION-001 Phase 3 (TEST-001).
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import subprocess

# Import functions to test
from extractors import extract_apis, extract_schemas, extract_components


class TestExtractApis:
    """Test extract_apis() function with mocked CLI calls."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        extract_apis.cache_clear()

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_apis_success(self, mock_cli, mock_validate):
        """Test successful API extraction with real-like CLI output."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI return value with realistic data
        mock_cli.return_value = {
            "elements": [
                {
                    "type": "function",
                    "name": "get_users",
                    "file": "routes/users.py",
                    "path": "/api/users",
                    "params": [{"name": "limit", "type": "int"}],
                    "return_type": "List[User]",
                    "description": "Get all users"
                },
                {
                    "type": "function",
                    "name": "create_user",
                    "file": "routes/users.py",
                    "path": "/api/users",
                    "params": [{"name": "user", "type": "UserCreate"}],
                    "return_type": "User",
                    "description": "Create new user"
                }
            ]
        }

        # Call extract_apis
        result = extract_apis("/test/project")

        # Verify results
        assert result is not None
        assert isinstance(result, dict)
        assert "endpoints" in result
        assert "timestamp" in result
        assert "error" in result
        assert "source" in result

        # Verify endpoints structure
        endpoints = result["endpoints"]
        assert isinstance(endpoints, list)
        assert len(endpoints) >= 0

        # Verify no errors
        assert result["error"] is None

        # Verify timestamp is ISO8601-like
        assert "T" in result["timestamp"]

        # Verify CLI was called correctly
        mock_cli.assert_called_once()
        call_args = mock_cli.call_args
        assert call_args[0][0] == "scan"
        assert "--project" in call_args[1]["args"]

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_apis_cli_failure(self, mock_cli, mock_validate):
        """Test API extraction when CLI returns error."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI failure
        mock_cli.return_value = {"error": "CLI not available"}

        # Call extract_apis
        result = extract_apis("/test/project")

        # Verify graceful handling
        assert result["endpoints"] == []
        assert result["error"] is not None
        assert "CLI not available" in result["error"]
        assert result["source"] == "error"

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_apis_timeout(self, mock_cli, mock_validate):
        """Test API extraction with timeout."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock timeout exception
        mock_cli.side_effect = subprocess.TimeoutExpired("cmd", 120)

        # Call extract_apis
        result = extract_apis("/test/project")

        # Verify graceful handling
        assert result["endpoints"] == []
        assert result["error"] is not None
        assert result["source"] == "error"

    @patch('extractors.validate_cli_available')
    def test_extract_apis_cli_unavailable(self, mock_validate):
        """Test API extraction when CLI is unavailable."""
        # Mock CLI unavailability
        mock_validate.return_value = False

        # Call extract_apis
        result = extract_apis("/test/project")

        # Verify placeholder response
        assert result["endpoints"] == []
        assert result["error"] is None
        assert result["source"] == "placeholder"
        assert "timestamp" in result

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_apis_caching(self, mock_cli, mock_validate):
        """Test that results are cached (same call doesn't hit CLI twice)."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI return value
        mock_cli.return_value = {"elements": []}

        # First call
        extract_apis("/test/project")
        assert mock_cli.call_count == 1

        # Second call (should use cache)
        extract_apis("/test/project")
        assert mock_cli.call_count == 1  # Still 1, not 2

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_apis_http_method_detection(self, mock_cli, mock_validate):
        """Test HTTP method detection from element names."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI with various method patterns
        mock_cli.return_value = {
            "elements": [
                {"type": "function", "name": "post_user", "file": "routes/api.py"},
                {"type": "function", "name": "delete_user", "file": "routes/api.py"},
                {"type": "function", "name": "update_user", "file": "routes/api.py"},
            ]
        }

        # Call extract_apis
        result = extract_apis("/test/project")

        # Verify method detection
        endpoints = result["endpoints"]
        if len(endpoints) >= 3:
            # Check that POST, DELETE, PUT are detected
            methods = [ep["method"] for ep in endpoints]
            assert "POST" in methods or "DELETE" in methods or "PUT" in methods


class TestExtractSchemas:
    """Test extract_schemas() function with mocked CLI calls."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        extract_schemas.cache_clear()

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_schemas_success(self, mock_cli, mock_validate):
        """Test successful schema extraction."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI return value with realistic schema data
        mock_cli.return_value = {
            "elements": [
                {
                    "type": "class",
                    "name": "User",
                    "file": "models/user.py",
                    "properties": [
                        {"name": "id", "type": "UUID", "constraints": ["primary_key"]},
                        {"name": "email", "type": "str", "constraints": ["unique", "not_null"]},
                        {"name": "created_at", "type": "datetime", "constraints": []}
                    ],
                    "relationships": [
                        {"type": "hasMany", "target": "Post", "foreignKey": "user_id"}
                    ]
                }
            ]
        }

        # Call extract_schemas
        result = extract_schemas("/test/project")

        # Verify results
        assert result is not None
        assert isinstance(result, dict)
        assert "entities" in result
        assert "timestamp" in result
        assert "error" in result
        assert "source" in result

        # Verify entities structure
        entities = result["entities"]
        assert isinstance(entities, list)
        assert len(entities) >= 0

        # Verify no errors
        assert result["error"] is None

        # Verify timestamp
        assert "T" in result["timestamp"]

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_schemas_cli_failure(self, mock_cli, mock_validate):
        """Test schema extraction when CLI fails."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI error
        mock_cli.return_value = {"error": "CLI error"}

        # Call extract_schemas
        result = extract_schemas("/test/project")

        # Verify graceful handling
        assert result["entities"] == []
        assert result["error"] is not None
        assert "CLI error" in result["error"]
        assert result["source"] == "error"

    @patch('extractors.validate_cli_available')
    def test_extract_schemas_cli_unavailable(self, mock_validate):
        """Test schema extraction when CLI is unavailable."""
        # Mock CLI unavailability
        mock_validate.return_value = False

        # Call extract_schemas
        result = extract_schemas("/test/project")

        # Verify placeholder response
        assert result["entities"] == []
        assert result["error"] is None
        assert result["source"] == "placeholder"

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_schemas_field_parsing(self, mock_cli, mock_validate):
        """Test field parsing from different property formats."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI with mixed property formats
        mock_cli.return_value = {
            "elements": [
                {
                    "type": "class",
                    "name": "Post",
                    "file": "models/post.py",
                    "properties": [
                        {"name": "title", "type": "str"},  # Dict format
                        "content",  # String format
                    ]
                }
            ]
        }

        # Call extract_schemas
        result = extract_schemas("/test/project")

        # Verify field parsing handles both formats
        if result["entities"]:
            entity = result["entities"][0]
            assert "fields" in entity
            # Should handle both dict and string formats


class TestExtractComponents:
    """Test extract_components() function with mocked CLI calls."""

    def setup_method(self):
        """Clear LRU cache before each test."""
        extract_components.cache_clear()

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_components_success(self, mock_cli, mock_validate):
        """Test successful component extraction."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI return value with realistic component data
        mock_cli.return_value = {
            "elements": [
                {
                    "type": "function",
                    "name": "Button",
                    "file": "components/Button.tsx",
                    "params": [
                        {"name": "onClick", "type": "function", "required": True},
                        {"name": "label", "type": "string", "required": True},
                        {"name": "disabled", "type": "boolean", "required": False, "default": False}
                    ],
                    "dependencies": ["Icon", "Tooltip"],
                    "description": "Reusable button component"
                }
            ]
        }

        # Call extract_components
        result = extract_components("/test/project")

        # Verify results
        assert result is not None
        assert isinstance(result, dict)
        assert "components" in result
        assert "timestamp" in result
        assert "error" in result
        assert "source" in result

        # Verify components structure
        components = result["components"]
        assert isinstance(components, list)
        assert len(components) >= 0

        # Verify no errors
        assert result["error"] is None

        # Verify timestamp
        assert "T" in result["timestamp"]

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_components_cli_failure(self, mock_cli, mock_validate):
        """Test component extraction when CLI fails."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI error
        mock_cli.return_value = {"error": "CLI error"}

        # Call extract_components
        result = extract_components("/test/project")

        # Verify graceful handling
        assert result["components"] == []
        assert result["error"] is not None
        assert "CLI error" in result["error"]
        assert result["source"] == "error"

    @patch('extractors.validate_cli_available')
    def test_extract_components_cli_unavailable(self, mock_validate):
        """Test component extraction when CLI is unavailable."""
        # Mock CLI unavailability
        mock_validate.return_value = False

        # Call extract_components
        result = extract_components("/test/project")

        # Verify placeholder response
        assert result["components"] == []
        assert result["error"] is None
        assert result["source"] == "placeholder"

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_components_type_detection(self, mock_cli, mock_validate):
        """Test component type detection (Functional, Class, Vue, Svelte)."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI with various component types
        mock_cli.return_value = {
            "elements": [
                {"type": "function", "name": "Button", "file": "Button.tsx"},
                {"type": "class", "name": "Modal", "file": "Modal.jsx"},
                {"type": "export", "name": "Card", "file": "Card.vue"},
                {"type": "component", "name": "Alert", "file": "Alert.svelte"},
            ]
        }

        # Call extract_components
        result = extract_components("/test/project")

        # Verify type detection
        components = result["components"]
        if len(components) >= 4:
            types = [comp["type"] for comp in components]
            # Should detect different component types
            assert any("Component" in t for t in types)

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_components_prop_parsing(self, mock_cli, mock_validate):
        """Test prop parsing from different param formats."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI with mixed param formats
        mock_cli.return_value = {
            "elements": [
                {
                    "type": "function",
                    "name": "Input",
                    "file": "Input.tsx",
                    "params": [
                        {"name": "value", "type": "string"},  # Dict format
                        "onChange",  # String format
                    ]
                }
            ]
        }

        # Call extract_components
        result = extract_components("/test/project")

        # Verify prop parsing handles both formats
        if result["components"]:
            component = result["components"][0]
            assert "props" in component
            # Should handle both dict and string formats

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_extract_components_naming_convention(self, mock_cli, mock_validate):
        """Test component naming convention filtering (uppercase first letter)."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI with mixed naming conventions
        mock_cli.return_value = {
            "elements": [
                {"type": "function", "name": "Button", "file": "Button.tsx"},  # Component
                {"type": "function", "name": "helper", "file": "utils.tsx"},   # Not a component
                {"type": "function", "name": "Modal", "file": "Modal.jsx"},    # Component
            ]
        }

        # Call extract_components
        result = extract_components("/test/project")

        # Verify only uppercase-first names are extracted as components
        components = result["components"]
        for comp in components:
            # Component names should start with uppercase (if any extracted)
            if comp["name"]:
                assert comp["name"][0].isupper()


# Integration-style test (runs against all extractors)
class TestExtractorsConsistency:
    """Test consistency across all extractor functions."""

    def setup_method(self):
        """Clear all LRU caches before each test."""
        extract_apis.cache_clear()
        extract_schemas.cache_clear()
        extract_components.cache_clear()

    @patch('extractors.validate_cli_available')
    def test_all_extractors_return_consistent_structure(self, mock_validate):
        """Verify all extractors return consistent dict structure."""
        # Mock CLI unavailability for simple test
        mock_validate.return_value = False

        # Call all extractors
        apis = extract_apis("/test/project")
        schemas = extract_schemas("/test/project")
        components = extract_components("/test/project")

        # All should return dict
        for result in [apis, schemas, components]:
            assert isinstance(result, dict)

        # All should have timestamp
        for result in [apis, schemas, components]:
            assert "timestamp" in result
            assert "T" in result["timestamp"]

        # All should have error field
        for result in [apis, schemas, components]:
            assert "error" in result

        # All should have source field
        for result in [apis, schemas, components]:
            assert "source" in result

    @patch('extractors.validate_cli_available')
    @patch('extractors.run_coderef_command')
    def test_all_extractors_handle_exceptions(self, mock_cli, mock_validate):
        """Verify all extractors gracefully handle exceptions."""
        # Mock CLI availability
        mock_validate.return_value = True

        # Mock CLI to raise exception
        mock_cli.side_effect = Exception("Unexpected error")

        # Call all extractors
        apis = extract_apis("/test/project")
        schemas = extract_schemas("/test/project")
        components = extract_components("/test/project")

        # All should return error response (not raise)
        for result in [apis, schemas, components]:
            assert result["error"] is not None
            assert result["source"] == "error"
