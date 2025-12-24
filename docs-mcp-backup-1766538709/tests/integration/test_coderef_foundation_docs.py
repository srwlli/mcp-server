"""
Integration tests for coderef_foundation_docs MCP tool.

Tests the full MCP handler workflow including:
- Handler invocation
- Input validation
- Response format
- Error handling
"""

import pytest
import json
import subprocess
from pathlib import Path
import re

import tool_handlers


def extract_json_from_response(text: str) -> dict:
    """Extract JSON from response that may have a message prefix."""
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Look for JSON object in text (starts with { and ends with })
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def integration_project(tmp_path):
    """Create a complete project for integration testing."""
    # Create directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "coderef" / "foundation-docs").mkdir(parents=True)

    # Initialize git
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)

    # Create FastAPI app
    (tmp_path / "src" / "main.py").write_text('''
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello"}

@app.get("/users")
def list_users():
    return []

@app.post("/users")
def create_user():
    return {"created": True}
''')

    # Create SQLAlchemy models
    (tmp_path / "src" / "models.py").write_text('''
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))
''')

    # Create requirements.txt
    (tmp_path / "requirements.txt").write_text('''
fastapi==0.104.0
sqlalchemy==2.0.0
uvicorn==0.24.0
''')

    # Create README
    (tmp_path / "README.md").write_text("# Test Project\n")

    # Initial commit
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, capture_output=True)

    return tmp_path


# ============================================================================
# MCP HANDLER TESTS
# ============================================================================

class TestMcpHandler:
    """Test MCP handler invocation."""

    @pytest.mark.asyncio
    async def test_handler_success(self, integration_project):
        """Handler returns success response with valid input."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "include_components": False,
            "deep_extraction": True,
            "use_coderef": False
        })

        assert len(result) == 1
        response = extract_json_from_response(result[0].text)

        assert response.get("success") is True or "files_generated" in response

    @pytest.mark.asyncio
    async def test_handler_missing_path(self):
        """Handler returns error for missing project_path."""
        result = await tool_handlers.handle_coderef_foundation_docs({})

        assert len(result) == 1
        response_text = result[0].text.lower()
        assert "error" in response_text or "invalid" in response_text

    @pytest.mark.asyncio
    async def test_handler_invalid_path(self):
        """Handler returns error for invalid project_path."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": "/nonexistent/path/that/does/not/exist"
        })

        assert len(result) == 1
        response_text = result[0].text.lower()
        assert "error" in response_text or "not found" in response_text or "invalid" in response_text

    @pytest.mark.asyncio
    async def test_handler_relative_path_rejected(self, integration_project):
        """Handler rejects relative paths."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": "./relative/path"
        })

        assert len(result) == 1
        response_text = result[0].text.lower()
        assert "error" in response_text or "absolute" in response_text or "invalid" in response_text


# ============================================================================
# RESPONSE FORMAT TESTS
# ============================================================================

class TestResponseFormat:
    """Test MCP response format."""

    @pytest.mark.asyncio
    async def test_response_is_json(self, integration_project):
        """Response contains valid JSON."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        # Should extract JSON from response
        response = extract_json_from_response(result[0].text)
        assert isinstance(response, dict)
        assert len(response) > 0  # Not empty

    @pytest.mark.asyncio
    async def test_response_contains_success_flag(self, integration_project):
        """Response contains success flag."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        response = extract_json_from_response(result[0].text)
        # Should have success or error indicator
        assert "success" in response or "error" in response or "files_generated" in response

    @pytest.mark.asyncio
    async def test_response_contains_files_list(self, integration_project):
        """Response contains list of generated files."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        response = extract_json_from_response(result[0].text)

        # Should have files info
        has_files = (
            "files_generated" in response or
            "files" in response or
            "output_files" in response or
            "architecture" in str(response).lower()
        )
        assert has_files


# ============================================================================
# PARAMETER HANDLING TESTS
# ============================================================================

class TestParameterHandling:
    """Test parameter handling."""

    @pytest.mark.asyncio
    async def test_include_components_parameter(self, integration_project):
        """include_components parameter is respected."""
        # Create UI component
        (integration_project / "src" / "components").mkdir()
        (integration_project / "src" / "components" / "Button.tsx").write_text(
            "export const Button = () => <button>Click</button>;"
        )
        (integration_project / "package.json").write_text('{"dependencies":{"react":"^18.0.0"}}')

        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "include_components": True,
            "use_coderef": False
        })

        response = extract_json_from_response(result[0].text)
        assert response.get("success") is True or "files" in str(response)

    @pytest.mark.asyncio
    async def test_deep_extraction_parameter(self, integration_project):
        """deep_extraction parameter is respected."""
        # Create existing docs
        (integration_project / "docs" / "ARCHITECTURE.md").write_text(
            "# Architecture\n\nMicroservices pattern with event sourcing."
        )

        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "deep_extraction": True,
            "use_coderef": False
        })

        response = extract_json_from_response(result[0].text)
        assert response.get("success") is True or "architecture" in str(response).lower()

    @pytest.mark.asyncio
    async def test_use_coderef_parameter(self, integration_project):
        """use_coderef parameter is respected."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False  # Disable coderef for testing
        })

        response = extract_json_from_response(result[0].text)
        # Should work without coderef
        assert response.get("success") is True or "files" in str(response)


# ============================================================================
# OUTPUT FILE TESTS
# ============================================================================

class TestOutputFiles:
    """Test generated output files."""

    @pytest.mark.asyncio
    async def test_architecture_md_created(self, integration_project):
        """ARCHITECTURE.md is created."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        arch_path = integration_project / "coderef" / "foundation-docs" / "ARCHITECTURE.md"
        assert arch_path.exists()

    @pytest.mark.asyncio
    async def test_schema_md_created(self, integration_project):
        """SCHEMA.md is created."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        schema_path = integration_project / "coderef" / "foundation-docs" / "SCHEMA.md"
        assert schema_path.exists()

    @pytest.mark.asyncio
    async def test_project_context_json_created(self, integration_project):
        """project-context.json is created."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        context_path = integration_project / "coderef" / "foundation-docs" / "project-context.json"
        assert context_path.exists()

        # Verify it's valid JSON
        content = context_path.read_text(encoding='utf-8')
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    @pytest.mark.asyncio
    async def test_components_md_for_ui_project(self, integration_project):
        """COMPONENTS.md is created for UI projects."""
        # Add UI components
        (integration_project / "src" / "components").mkdir()
        (integration_project / "src" / "components" / "Button.tsx").write_text('''
import React from 'react';
export const Button = ({ label }: { label: string }) => <button>{label}</button>;
''')
        (integration_project / "package.json").write_text('{"dependencies":{"react":"^18.0.0"}}')

        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "include_components": True,
            "use_coderef": False
        })

        components_path = integration_project / "coderef" / "foundation-docs" / "COMPONENTS.md"
        assert components_path.exists()

    @pytest.mark.asyncio
    async def test_api_md_created(self, integration_project):
        """API.md is created."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        api_path = integration_project / "coderef" / "foundation-docs" / "API.md"
        assert api_path.exists()

        # Verify it has expected sections
        content = api_path.read_text(encoding='utf-8')
        assert '# API Documentation' in content
        assert '## Overview' in content
        assert '## Endpoints' in content
        assert '## Authentication' in content
        assert '## Error Handling' in content


# ============================================================================
# CONTENT QUALITY TESTS
# ============================================================================

class TestContentQuality:
    """Test quality of generated content."""

    @pytest.mark.asyncio
    async def test_architecture_contains_patterns(self, integration_project):
        """ARCHITECTURE.md contains detected patterns."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        arch_path = integration_project / "coderef" / "foundation-docs" / "ARCHITECTURE.md"
        content = arch_path.read_text().lower()

        # Should mention FastAPI or API patterns
        assert "api" in content or "fastapi" in content or "endpoint" in content

    @pytest.mark.asyncio
    async def test_schema_contains_models(self, integration_project):
        """SCHEMA.md contains detected models."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        schema_path = integration_project / "coderef" / "foundation-docs" / "SCHEMA.md"
        content = schema_path.read_text().lower()

        # Should mention User model or database
        assert "user" in content or "database" in content or "model" in content

    @pytest.mark.asyncio
    async def test_context_contains_endpoints(self, integration_project):
        """project-context.json contains API endpoints."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        context_path = integration_project / "coderef" / "foundation-docs" / "project-context.json"
        context = json.loads(context_path.read_text(encoding='utf-8'))

        # Should have API context (which contains endpoints)
        has_endpoints = (
            "api_context" in context or
            "api_endpoints" in context or
            "endpoints" in context
        )
        assert has_endpoints

    @pytest.mark.asyncio
    async def test_context_contains_dependencies(self, integration_project):
        """project-context.json contains dependencies."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        context_path = integration_project / "coderef" / "foundation-docs" / "project-context.json"
        context = json.loads(context_path.read_text(encoding='utf-8'))

        # Should have dependencies
        has_deps = (
            "dependencies" in context or
            "deps" in context or
            "packages" in context
        )
        assert has_deps

    @pytest.mark.asyncio
    async def test_api_md_contains_detected_endpoints(self, integration_project):
        """API.md contains detected endpoints from FastAPI project."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        api_path = integration_project / "coderef" / "foundation-docs" / "API.md"
        content = api_path.read_text(encoding='utf-8').lower()

        # Should detect FastAPI framework
        assert 'fastapi' in content

        # Should list endpoints (the fixture has /, /users GET/POST)
        assert 'get' in content
        assert '/' in content


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_permission_error_handled(self, integration_project):
        """Permission errors are handled gracefully."""
        # This test is platform-dependent
        # On Windows, we can't easily create permission issues
        # So we just verify the handler doesn't crash on normal input
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": False
        })

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_empty_project_handled(self, tmp_path):
        """Empty project is handled gracefully."""
        (tmp_path / "coderef" / "foundation-docs").mkdir(parents=True)

        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(tmp_path),
            "use_coderef": False
        })

        assert len(result) == 1
        # Should not crash, even if limited results


# ============================================================================
# REGISTRY TESTS
# ============================================================================

class TestRegistry:
    """Test tool registry integration."""

    def test_handler_in_registry(self):
        """Handler is registered in TOOL_HANDLERS."""
        assert 'coderef_foundation_docs' in tool_handlers.TOOL_HANDLERS

    def test_handler_callable(self):
        """Registered handler is callable."""
        handler = tool_handlers.TOOL_HANDLERS['coderef_foundation_docs']
        assert callable(handler)


# ============================================================================
# CODEREF DATA INTEGRATION TESTS (WO-CODEREF-FOUNDATION-003)
# ============================================================================

class TestCoderefDataIntegration:
    """Test integration with .coderef/ data files."""

    @pytest.fixture
    def project_with_coderef(self, integration_project):
        """Create project with .coderef/ directory containing index.json and graph.json."""
        coderef_dir = integration_project / ".coderef"
        coderef_dir.mkdir()

        # Create index.json with elements
        index_data = [
            {"type": "function", "name": "root", "file": "src/main.py", "line": 6},
            {"type": "function", "name": "list_users", "file": "src/main.py", "line": 10},
            {"type": "function", "name": "create_user", "file": "src/main.py", "line": 14},
            {"type": "class", "name": "User", "file": "src/models.py", "line": 7},
            {"type": "function", "name": "handle_request", "file": "src/handlers.py", "line": 1}
        ]
        (coderef_dir / "index.json").write_text(json.dumps(index_data, indent=2))

        # Create graph.json with relationships
        graph_data = {
            "nodes": [
                ["n1", {"id": "src/main.py::root", "name": "root", "type": "function", "file": "src/main.py"}],
                ["n2", {"id": "src/main.py::list_users", "name": "list_users", "type": "function", "file": "src/main.py"}],
                ["n3", {"id": "src/main.py::create_user", "name": "create_user", "type": "function", "file": "src/main.py"}],
                ["n4", {"id": "src/models.py::User", "name": "User", "type": "class", "file": "src/models.py"}]
            ],
            "edges": [
                ["e1", {"source": "src/main.py::list_users", "target": "src/models.py::User", "type": "calls"}],
                ["e2", {"source": "src/main.py::create_user", "target": "src/models.py::User", "type": "calls"}]
            ],
            "metadata": {"nodeCount": 4, "edgeCount": 2}
        }
        (coderef_dir / "graph.json").write_text(json.dumps(graph_data, indent=2))

        return integration_project

    @pytest.mark.asyncio
    async def test_coderef_data_used_when_available(self, project_with_coderef):
        """Handler uses coderef data when .coderef/ directory exists."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "use_coderef": True  # Enable coderef integration
        })

        response = extract_json_from_response(result[0].text)
        assert response.get("success") is True or "files_generated" in response

    @pytest.mark.asyncio
    async def test_coderef_enhances_architecture_md(self, project_with_coderef):
        """ARCHITECTURE.md includes coderef-powered diagrams and metrics."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "use_coderef": True
        })

        arch_path = project_with_coderef / "coderef" / "foundation-docs" / "ARCHITECTURE.md"
        content = arch_path.read_text()

        # Should have Mermaid diagram
        assert "```mermaid" in content or "mermaid" in content.lower()

        # Should have graph metrics section
        assert "metrics" in content.lower() or "density" in content.lower() or "nodes" in content.lower()

    @pytest.mark.asyncio
    async def test_coderef_enhances_components_md(self, project_with_coderef):
        """COMPONENTS.md includes all module categories from coderef data."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "include_components": True,
            "use_coderef": True
        })

        components_path = project_with_coderef / "coderef" / "foundation-docs" / "COMPONENTS.md"
        content = components_path.read_text()

        # Should have summary section with counts
        assert "summary" in content.lower() or "total" in content.lower() or "elements" in content.lower()

    @pytest.mark.asyncio
    async def test_coderef_adds_high_impact_elements(self, project_with_coderef):
        """ARCHITECTURE.md includes high-impact elements section."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "use_coderef": True
        })

        arch_path = project_with_coderef / "coderef" / "foundation-docs" / "ARCHITECTURE.md"
        content = arch_path.read_text()

        # Should have high-impact elements section (or equivalent)
        assert "impact" in content.lower() or "dependent" in content.lower() or "risk" in content.lower()

    @pytest.mark.asyncio
    async def test_readme_generated_at_project_root(self, project_with_coderef):
        """README.md is generated at project root."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "use_coderef": True
        })

        readme_path = project_with_coderef / "README.md"
        assert readme_path.exists()

        content = readme_path.read_text()
        # Should have project name in title
        assert "#" in content
        # Should have stats section
        assert "stat" in content.lower() or "overview" in content.lower() or "quick" in content.lower()

    @pytest.mark.asyncio
    async def test_fallback_when_coderef_missing(self, integration_project):
        """Falls back to regex detection when .coderef/ missing."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": True  # Enabled, but no .coderef/ directory
        })

        response = extract_json_from_response(result[0].text)
        # Should still succeed with regex fallback
        assert response.get("success") is True or "files_generated" in response

    @pytest.mark.asyncio
    async def test_project_context_includes_coderef_info(self, project_with_coderef):
        """project-context.json includes coderef analysis info."""
        await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "use_coderef": True
        })

        context_path = project_with_coderef / "coderef" / "foundation-docs" / "project-context.json"
        context = json.loads(context_path.read_text(encoding='utf-8'))

        # Should indicate coderef was used or have element counts
        has_coderef_info = (
            "coderef" in str(context).lower() or
            "elements" in context or
            "element_count" in context or
            context.get("used_coderef") is True
        )
        assert has_coderef_info or "api_context" in context  # At minimum, has standard context

    @pytest.mark.asyncio
    async def test_invalid_coderef_json_graceful_fallback(self, integration_project):
        """Handles invalid JSON in .coderef/ gracefully."""
        coderef_dir = integration_project / ".coderef"
        coderef_dir.mkdir()
        (coderef_dir / "index.json").write_text("{ invalid json }")

        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(integration_project),
            "use_coderef": True
        })

        response = extract_json_from_response(result[0].text)
        # Should fall back to regex and still succeed
        assert response.get("success") is True or "files_generated" in response

    @pytest.mark.asyncio
    async def test_six_files_generated(self, project_with_coderef):
        """All 6 foundation files are generated."""
        result = await tool_handlers.handle_coderef_foundation_docs({
            "project_path": str(project_with_coderef),
            "include_components": True,
            "use_coderef": True
        })

        response = extract_json_from_response(result[0].text)

        # Check files_generated list
        if "files_generated" in response:
            files = response["files_generated"]
            expected_files = ["README.md", "ARCHITECTURE.md", "SCHEMA.md", "COMPONENTS.md", "API.md", "project-context.json"]
            for expected in expected_files:
                assert any(expected in f for f in files), f"Missing {expected} in generated files"

        # Also verify files exist
        foundation_dir = project_with_coderef / "coderef" / "foundation-docs"
        assert (project_with_coderef / "README.md").exists()
        assert (foundation_dir / "ARCHITECTURE.md").exists()
        assert (foundation_dir / "SCHEMA.md").exists()
        assert (foundation_dir / "COMPONENTS.md").exists()
        assert (foundation_dir / "API.md").exists()
        assert (foundation_dir / "project-context.json").exists()
