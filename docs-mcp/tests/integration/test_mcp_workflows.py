"""
Integration tests for MCP tool workflows.

Tests end-to-end workflows across multiple MCP tools including:
- Documentation generation workflows
- Changelog management workflows
- Standards and audit workflows
- Inventory management workflows

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tool_handlers
from constants import Paths


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def setup_tool_handlers(tmp_path: Path):
    """Set up tool_handlers module with test templates directory."""
    # Store original values
    original_templates_dir = tool_handlers.TEMPLATES_DIR
    original_tool_templates_dir = tool_handlers.TOOL_TEMPLATES_DIR

    # Create test templates directory
    templates_dir = tmp_path / "templates" / "power"
    templates_dir.mkdir(parents=True)

    # Create sample templates
    (templates_dir / "readme.txt").write_text("""# {project_name}

## Overview
{project_description}

## Installation
```bash
pip install {project_name}
```
""")

    (templates_dir / "architecture.txt").write_text("""# Architecture

## System Design
{system_overview}

## Components
{components_list}
""")

    (templates_dir / "api.txt").write_text("""# API Documentation

## Endpoints
{endpoints}
""")

    (templates_dir / "components.txt").write_text("""# Components

## Component List
{components}
""")

    (templates_dir / "schema.txt").write_text("""# Schema

## Data Models
{models}
""")

    (templates_dir / "user-guide.txt").write_text("""# User Guide

## Getting Started
{getting_started}
""")

    # Create tool templates directory
    tool_templates_dir = tmp_path / "templates" / "tools"
    tool_templates_dir.mkdir(parents=True)

    # Create planning template
    planning_template = {
        "META_DOCUMENTATION": {
            "schema_version": "1.0.0",
            "description": "Implementation planning template"
        },
        "sections": {
            "1_executive_summary": {},
            "2_risk_assessment": {},
            "3_current_state_analysis": {}
        }
    }
    (tool_templates_dir / "feature-implementation-planning-standard.json").write_text(
        json.dumps(planning_template, indent=2)
    )

    # Set module globals
    tool_handlers.TEMPLATES_DIR = templates_dir
    tool_handlers.TOOL_TEMPLATES_DIR = tool_templates_dir

    yield

    # Restore original values
    tool_handlers.TEMPLATES_DIR = original_templates_dir
    tool_handlers.TOOL_TEMPLATES_DIR = original_tool_templates_dir


# Note: mock_project fixture is provided by conftest.py
# Removed duplicate fixture - using shared mock_project from conftest.py


# ============================================================================
# TEST: Template Workflow
# ============================================================================

class TestTemplateWorkflow:
    """Integration tests for template listing and retrieval workflow."""

    @pytest.mark.asyncio
    async def test_list_then_get_template(self):
        """Test listing templates then getting a specific one."""
        # List templates
        list_result = await tool_handlers.handle_list_templates({})
        assert len(list_result) == 1
        result_text = list_result[0].text

        # Verify templates are listed
        assert "readme" in result_text.lower()

        # Get a specific template
        get_result = await tool_handlers.handle_get_template({"template_name": "readme"})
        assert len(get_result) == 1
        template_content = get_result[0].text

        # Verify template content
        assert "README" in template_content
        assert "{project_name}" in template_content

    @pytest.mark.asyncio
    async def test_get_all_listed_templates(self):
        """Test that all listed templates can be retrieved."""
        # List templates
        list_result = await tool_handlers.handle_list_templates({})
        result_text = list_result[0].text

        # Extract template names
        template_names = ["readme", "architecture", "api", "components", "schema", "user-guide"]

        for name in template_names:
            # Each template should be retrievable
            get_result = await tool_handlers.handle_get_template({"template_name": name})
            assert len(get_result) == 1
            assert name.upper() in get_result[0].text.upper()


# ============================================================================
# TEST: Documentation Generation Workflow
# ============================================================================

class TestDocGenerationWorkflow:
    """Integration tests for documentation generation workflow."""

    @pytest.mark.asyncio
    async def test_generate_foundation_docs_workflow(self, mock_project: Path):
        """Test complete foundation docs generation workflow."""
        # Generate foundation docs
        result = await tool_handlers.handle_generate_foundation_docs({
            "project_path": str(mock_project)
        })

        assert len(result) == 1
        result_text = result[0].text

        # Verify all templates are included
        assert "README" in result_text
        assert "ARCHITECTURE" in result_text
        assert "INSTRUCTIONS" in result_text

        # Verify save locations are specified
        assert "README.md" in result_text

    @pytest.mark.asyncio
    async def test_generate_individual_doc_workflow(self, mock_project: Path):
        """Test generating individual documentation."""
        # Generate individual doc
        result = await tool_handlers.handle_generate_individual_doc({
            "project_path": str(mock_project),
            "template_name": "readme"
        })

        assert len(result) == 1
        result_text = result[0].text

        # Verify template content
        assert "README" in result_text
        assert "TEMPLATE" in result_text
        assert "Output:" in result_text


# ============================================================================
# TEST: Changelog Workflow
# ============================================================================

class TestChangelogWorkflow:
    """Integration tests for changelog management workflow."""

    @pytest.mark.asyncio
    async def test_full_changelog_workflow(self, mock_project: Path):
        """Test complete changelog workflow: add entry then retrieve."""
        project_path = str(mock_project)

        # Add a changelog entry
        add_result = await tool_handlers.handle_add_changelog_entry({
            "project_path": project_path,
            "version": "1.0.1",
            "change_type": "feature",
            "severity": "minor",
            "title": "Add new feature",
            "description": "Added a comprehensive new feature",
            "files": ["src/main.py", "src/utils.py"],
            "reason": "User requested this feature",
            "impact": "Users can now do more things"
        })

        assert len(add_result) == 1
        add_text = add_result[0].text
        assert "success" in add_text.lower() or "added" in add_text.lower() or "CHG-" in add_text

        # Retrieve the changelog
        get_result = await tool_handlers.handle_get_changelog({
            "project_path": project_path
        })

        assert len(get_result) == 1
        get_text = get_result[0].text

        # Verify the entry exists
        assert "1.0.1" in get_text or "Add new feature" in get_text

    @pytest.mark.asyncio
    async def test_changelog_version_filter(self, mock_project: Path):
        """Test changelog retrieval with version filter."""
        project_path = str(mock_project)

        # Add entries for multiple versions
        await tool_handlers.handle_add_changelog_entry({
            "project_path": project_path,
            "version": "1.0.1",
            "change_type": "feature",
            "severity": "minor",
            "title": "Feature v1.0.1",
            "description": "Feature for version 1.0.1",
            "files": ["src/main.py"],
            "reason": "New feature",
            "impact": "New capability"
        })

        await tool_handlers.handle_add_changelog_entry({
            "project_path": project_path,
            "version": "1.0.2",
            "change_type": "bugfix",
            "severity": "patch",
            "title": "Bugfix v1.0.2",
            "description": "Bugfix for version 1.0.2",
            "files": ["src/utils.py"],
            "reason": "Bug found",
            "impact": "Bug fixed"
        })

        # Filter by specific version
        filter_result = await tool_handlers.handle_get_changelog({
            "project_path": project_path,
            "version": "1.0.1"
        })

        assert len(filter_result) == 1
        filter_text = filter_result[0].text

        # Should contain v1.0.1 entry
        assert "1.0.1" in filter_text

    @pytest.mark.asyncio
    async def test_update_changelog_workflow(self, mock_project: Path):
        """Test update_changelog meta-tool workflow."""
        project_path = str(mock_project)

        # Call update_changelog (meta-tool that returns instructions)
        result = await tool_handlers.handle_update_changelog({
            "project_path": project_path,
            "version": "1.0.3"
        })

        assert len(result) == 1
        result_text = result[0].text

        # Verify it returns instructions
        assert "STEP" in result_text or "step" in result_text.lower()
        assert "add_changelog_entry" in result_text.lower() or "changelog" in result_text.lower()


# ============================================================================
# TEST: Inventory Workflow
# ============================================================================

class TestInventoryWorkflow:
    """Integration tests for inventory management workflow."""

    @pytest.mark.asyncio
    async def test_inventory_manifest_workflow(self, mock_project: Path):
        """Test complete inventory manifest generation workflow."""
        project_path = str(mock_project)

        # Generate inventory manifest
        result = await tool_handlers.handle_inventory_manifest({
            "project_path": project_path,
            "analysis_depth": "standard"
        })

        assert len(result) == 1
        result_json = json.loads(result[0].text)

        # Verify manifest was created
        assert "success" in result_json or "manifest_path" in result_json
        assert "total_files" in result_json.get("metrics", result_json)

    @pytest.mark.asyncio
    async def test_inventory_with_different_depths(self, mock_project: Path):
        """Test inventory generation with different analysis depths."""
        project_path = str(mock_project)

        for depth in ["quick", "standard"]:
            result = await tool_handlers.handle_inventory_manifest({
                "project_path": project_path,
                "analysis_depth": depth
            })

            assert len(result) == 1
            result_json = json.loads(result[0].text)

            # All depths should produce valid results
            assert "success" in result_json or "manifest_path" in result_json


# ============================================================================
# TEST: Planning Workflow
# ============================================================================

class TestPlanningWorkflow:
    """Integration tests for planning workflow."""

    @pytest.mark.asyncio
    async def test_get_planning_template_workflow(self):
        """Test retrieving planning template."""
        result = await tool_handlers.handle_get_planning_template({})

        assert len(result) == 1
        result_text = result[0].text

        # Should contain template structure
        assert "template" in result_text.lower() or "planning" in result_text.lower()

    @pytest.mark.asyncio
    async def test_analyze_project_workflow(self, mock_project: Path):
        """Test project analysis for planning."""
        project_path = str(mock_project)

        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": project_path
        })

        assert len(result) == 1
        result_json = json.loads(result[0].text)

        # Should include analysis results
        assert "technology_stack" in result_json or "project_structure" in result_json

    @pytest.mark.asyncio
    async def test_gather_context_workflow(self, mock_project: Path):
        """Test gather context for planning."""
        project_path = str(mock_project)

        result = await tool_handlers.handle_gather_context({
            "project_path": project_path,
            "feature_name": "test-feature",
            "description": "A test feature for testing",
            "goal": "Test the gather context workflow",
            "requirements": ["Requirement 1", "Requirement 2"]
        })

        assert len(result) == 1
        result_text = result[0].text

        # Handler returns formatted text with embedded JSON, not pure JSON
        # Check for success indicators in text
        assert "context" in result_text.lower()
        # Should indicate workorder ID was generated
        assert "WO-TEST-FEATURE" in result_text or "workorder" in result_text.lower()


# ============================================================================
# TEST: Context Expert Workflow
# ============================================================================

class TestContextExpertWorkflow:
    """Integration tests for context expert workflow."""

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text that may have header lines."""
        # Find the first { and parse from there
        json_start = text.find('{')
        if json_start >= 0:
            return json.loads(text[json_start:])
        return json.loads(text)

    @pytest.mark.asyncio
    async def test_create_and_list_expert_workflow(self, mock_project: Path):
        """Test creating and listing context experts."""
        project_path = str(mock_project)

        # Create a context expert
        create_result = await tool_handlers.handle_create_context_expert({
            "project_path": project_path,
            "resource_path": "src/main.py",
            "resource_type": "file",
            "domain": "core"
        })

        assert len(create_result) == 1
        create_text = create_result[0].text

        # Handler returns formatted text with header then JSON
        assert "expert" in create_text.lower()
        create_json = self._extract_json(create_text)

        # Should have expert_id
        assert "expert_id" in create_json
        expert_id = create_json["expert_id"]

        # List experts
        list_result = await tool_handlers.handle_list_context_experts({
            "project_path": project_path
        })

        assert len(list_result) == 1
        list_json = self._extract_json(list_result[0].text)

        # Should include the created expert
        assert "experts" in list_json
        expert_ids = [e.get("expert_id") for e in list_json["experts"]]
        assert expert_id in expert_ids

    @pytest.mark.asyncio
    async def test_suggest_experts_workflow(self, mock_project: Path):
        """Test suggesting context experts."""
        project_path = str(mock_project)

        result = await tool_handlers.handle_suggest_context_experts({
            "project_path": project_path,
            "limit": 5
        })

        assert len(result) == 1
        result_json = self._extract_json(result[0].text)

        # Should have suggestions
        assert "suggestions" in result_json
        assert isinstance(result_json["suggestions"], list)


# ============================================================================
# TEST: Error Handling Across Workflows
# ============================================================================

class TestWorkflowErrorHandling:
    """Test error handling across different workflows."""

    @pytest.mark.asyncio
    async def test_invalid_project_path_handling(self):
        """Test that invalid project paths are handled gracefully."""
        # Use non-existent path
        result = await tool_handlers.handle_generate_foundation_docs({
            "project_path": "/nonexistent/path/to/project"
        })

        assert len(result) == 1
        result_text = result[0].text.lower()

        # Should return error message
        assert "error" in result_text or "not found" in result_text or "invalid" in result_text

    @pytest.mark.asyncio
    async def test_invalid_template_name_handling(self):
        """Test that invalid template names are handled gracefully."""
        result = await tool_handlers.handle_get_template({
            "template_name": "nonexistent_template"
        })

        assert len(result) == 1
        result_text = result[0].text.lower()

        # Should return error message - may use "invalid" or "not found"
        assert "invalid" in result_text or "not found" in result_text or "error" in result_text

    @pytest.mark.asyncio
    async def test_missing_required_arguments(self, mock_project: Path):
        """Test handling of missing required arguments."""
        # Missing version in changelog
        result = await tool_handlers.handle_add_changelog_entry({
            "project_path": str(mock_project),
            # Missing required fields
            "title": "Test"
        })

        assert len(result) == 1
        result_text = result[0].text.lower()

        # Should indicate missing/invalid input - response format uses "invalid input"
        assert "invalid" in result_text or "required" in result_text or "missing" in result_text or "error" in result_text


# ============================================================================
# TEST: Multi-Step Workflows
# ============================================================================

class TestMultiStepWorkflows:
    """Test workflows that span multiple tool calls."""

    @pytest.mark.asyncio
    async def test_documentation_review_cycle(self, mock_project: Path):
        """Test documentation generation and review cycle."""
        project_path = str(mock_project)

        # Step 1: Generate foundation docs
        gen_result = await tool_handlers.handle_generate_foundation_docs({
            "project_path": project_path
        })
        assert "TEMPLATE" in gen_result[0].text

        # Step 2: Generate inventory
        inv_result = await tool_handlers.handle_inventory_manifest({
            "project_path": project_path,
            "analysis_depth": "quick"
        })
        inv_json = json.loads(inv_result[0].text)
        assert "success" in inv_json or "manifest_path" in inv_json

        # Step 3: Log changes to changelog
        log_result = await tool_handlers.handle_add_changelog_entry({
            "project_path": project_path,
            "version": "1.1.0",
            "change_type": "feature",
            "severity": "minor",
            "title": "Generated documentation",
            "description": "Generated project documentation and inventory",
            "files": ["coderef/foundation-docs/", "coderef/inventory/manifest.json"],
            "reason": "Project setup",
            "impact": "Project now has documentation"
        })
        assert len(log_result) == 1

    @pytest.mark.asyncio
    async def test_planning_to_execution_workflow(self, mock_project: Path):
        """Test planning workflow from analysis to context gathering."""
        project_path = str(mock_project)

        # Step 1: Analyze project
        analyze_result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": project_path
        })
        analyze_json = json.loads(analyze_result[0].text)
        assert "technology_stack" in analyze_json or "project_structure" in analyze_json

        # Step 2: Gather context for a feature
        context_result = await tool_handlers.handle_gather_context({
            "project_path": project_path,
            "feature_name": "new-feature",
            "description": "A new feature based on analysis",
            "goal": "Implement based on project analysis",
            "requirements": ["Use existing patterns", "Follow project standards"]
        })
        # Handler returns formatted text with header, not pure JSON
        context_text = context_result[0].text
        assert "context" in context_text.lower()
        assert "WO-NEW-FEATURE" in context_text or "workorder" in context_text.lower()


# ============================================================================
# TEST: Performance of Workflows
# ============================================================================

class TestWorkflowPerformance:
    """Performance tests for MCP workflows."""

    @pytest.mark.asyncio
    async def test_template_listing_performance(self):
        """Test that template listing completes quickly."""
        import time

        start = time.time()
        await tool_handlers.handle_list_templates({})
        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0

    @pytest.mark.asyncio
    async def test_inventory_performance(self, mock_project: Path):
        """Test inventory generation performance."""
        import time

        start = time.time()
        await tool_handlers.handle_inventory_manifest({
            "project_path": str(mock_project),
            "analysis_depth": "quick"
        })
        elapsed = time.time() - start

        # Should complete in under 5 seconds for small project
        assert elapsed < 5.0

    @pytest.mark.asyncio
    async def test_multiple_sequential_operations(self, mock_project: Path):
        """Test performance of multiple sequential operations."""
        import time

        operations = [
            ("list_templates", {}),
            ("generate_foundation_docs", {"project_path": str(mock_project)}),
            ("analyze_project_for_planning", {"project_path": str(mock_project)}),
        ]

        start = time.time()
        for op_name, args in operations:
            handler = tool_handlers.TOOL_HANDLERS.get(op_name)
            if handler:
                await handler(args)
        elapsed = time.time() - start

        # All operations should complete in under 10 seconds
        assert elapsed < 10.0
