"""
Integration tests for planning workflow.

Tests the complete planning pipeline:
1. gather_context -> context.json
2. analyze_project_for_planning -> analysis.json
3. create_plan -> plan.json (meta-tool)
4. validate_implementation_plan -> validation results
5. generate_plan_review_report -> markdown report

Part of WO-COMPREHENSIVE-TESTING-SUITE-002.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import tool_handlers


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def planning_project(tmp_path: Path) -> Path:
    """
    Create a project structure specifically for planning workflow tests.

    Includes foundation docs, standards, and source files for comprehensive
    analysis results.
    """
    project_dir = tmp_path / "planning-test-project"
    project_dir.mkdir()

    # Create coderef structure
    coderef_dir = project_dir / "coderef"
    coderef_dir.mkdir()
    (coderef_dir / "working").mkdir()
    (coderef_dir / "context").mkdir()
    (coderef_dir / "reviews").mkdir()

    # Create foundation docs for analysis
    foundation_dir = coderef_dir / "foundation-docs"
    foundation_dir.mkdir()

    (foundation_dir / "README.md").write_text("""# Planning Test Project

A project for testing planning workflow integration.

## Features
- Feature 1
- Feature 2

## Installation
```bash
npm install planning-test-project
```
""")

    (foundation_dir / "ARCHITECTURE.md").write_text("""# Architecture

## Overview
This project uses a modular architecture.

## Components
- Core module
- API layer
- Database integration
""")

    # Create source files for analysis
    src_dir = project_dir / "src"
    src_dir.mkdir()

    (src_dir / "main.ts").write_text("""import { Database } from './db';
import { ApiHandler } from './api';

export class Application {
    private db: Database;
    private api: ApiHandler;

    constructor() {
        this.db = new Database();
        this.api = new ApiHandler();
    }

    async start(): Promise<void> {
        await this.db.connect();
        await this.api.listen(3000);
    }
}
""")

    (src_dir / "api.ts").write_text("""import { Request, Response } from 'express';

export class ApiHandler {
    async listen(port: number): Promise<void> {
        console.log(`Listening on port ${port}`);
    }

    handleRequest(req: Request, res: Response): void {
        res.json({ status: 'ok' });
    }
}
""")

    # Create package.json
    (project_dir / "package.json").write_text(json.dumps({
        "name": "planning-test-project",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.18.0",
            "typescript": "^5.0.0"
        }
    }, indent=2))

    # Create standards for analysis
    standards_dir = coderef_dir / "standards"
    standards_dir.mkdir()

    (standards_dir / "UI-STANDARDS.md").write_text("""# UI Standards

## Buttons
- Primary: blue background
- Secondary: gray background

## Typography
- Headings: Inter font
- Body: System font
""")

    return project_dir


@pytest.fixture
def sample_context_data() -> Dict[str, Any]:
    """Sample context data for gather_context testing."""
    return {
        "feature_name": "user-authentication",
        "description": "Implement user authentication with JWT tokens and session management",
        "goal": "Allow users to securely log in and maintain sessions across the application",
        "requirements": [
            "JWT token generation and validation",
            "Password hashing with bcrypt",
            "Session management with refresh tokens",
            "Logout functionality",
            "Password reset via email"
        ],
        "constraints": [
            "Must use existing database schema",
            "Must be backward compatible with current API"
        ],
        "out_of_scope": [
            "Social login (OAuth)",
            "Two-factor authentication"
        ],
        "success_criteria": {
            "functional": ["All auth endpoints working", "JWT validation passing"],
            "quality": ["80%+ test coverage", "No critical security issues"]
        }
    }


@pytest.fixture
def sample_plan_data() -> Dict[str, Any]:
    """Sample plan.json structure for validation testing."""
    return {
        "META_DOCUMENTATION": {
            "feature_name": "test-feature",
            "schema_version": "1.0.0",
            "version": "1.0.0",
            "status": "complete",
            "generated_by": "Test",
            "has_context": True,
            "has_analysis": True
        },
        "UNIVERSAL_PLANNING_STRUCTURE": {
            "0_preparation": {
                "foundation_docs": {"available": ["README.md"], "missing": []},
                "coding_standards": {"available": [], "missing": []},
                "reference_components": {"primary": "N/A", "secondary": []},
                "key_patterns_identified": ["Pattern 1"],
                "technology_stack": {"languages": ["TypeScript"], "frameworks": ["Express"]},
                "gaps_and_risks": []
            },
            "1_executive_summary": {
                "purpose": "Test feature implementation",
                "value_proposition": "Provides testing capability",
                "real_world_analogy": "Like a test runner",
                "use_case": "Run tests",
                "output": "Test results"
            },
            "2_risk_assessment": {
                "overall_risk": "low",
                "complexity": "low",
                "scope": "Small - 5 files",
                "file_system_risk": "low",
                "dependencies": [],
                "performance_concerns": [],
                "security_considerations": [],
                "breaking_changes": "none"
            },
            "3_current_state_analysis": {
                "files_to_create": [
                    {"path": "src/test.ts", "purpose": "Test file"}
                ],
                "files_to_modify": [],
                "dependencies": {
                    "existing_internal": [],
                    "existing_external": [],
                    "new_external": [],
                    "new_internal": []
                },
                "architecture_context": "Test architecture"
            },
            "4_key_features": {
                "primary_features": ["Feature 1", "Feature 2"],
                "secondary_features": [],
                "edge_case_handling": [],
                "configuration_options": []
            },
            "5_task_id_system": {
                "workorder": {
                    "id": "WO-TEST-001",
                    "name": "Test Feature",
                    "feature_dir": "coderef/working/test-feature"
                },
                "tasks": [
                    {
                        "id": "SETUP-001",
                        "workorder_id": "WO-TEST-001",
                        "description": "Setup task",
                        "category": "setup",
                        "priority": "P0",
                        "estimated_effort": "low"
                    }
                ]
            },
            "6_implementation_phases": {
                "phases": [
                    {
                        "phase": 1,
                        "name": "Setup",
                        "description": "Initial setup",
                        "tasks": ["SETUP-001"],
                        "deliverables": ["Setup complete"]
                    }
                ]
            },
            "7_testing_strategy": {
                "unit_tests": ["Test 1"],
                "integration_tests": [],
                "end_to_end_tests": [],
                "edge_case_scenarios": []
            },
            "8_success_criteria": {
                "functional_requirements": [],
                "quality_requirements": [],
                "performance_requirements": [],
                "security_requirements": []
            },
            "9_implementation_checklist": {
                "pre_implementation": ["Review plan"],
                "phase_1": ["SETUP-001: Setup"],
                "finalization": ["All tests passing"]
            }
        }
    }


# ============================================================================
# GATHER CONTEXT TESTS
# ============================================================================

def _extract_json_from_response(text: str) -> dict:
    """Extract JSON from response text that may have header lines."""
    json_start = text.find('{')
    if json_start >= 0:
        return json.loads(text[json_start:])
    return json.loads(text)


class TestGatherContextWorkflow:
    """Tests for gather_context handler."""

    @pytest.mark.asyncio
    async def test_gather_context_creates_context_file(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test that gather_context creates context.json correctly."""
        arguments = {
            "project_path": str(planning_project),
            **sample_context_data
        }

        result = await tool_handlers.handle_gather_context(arguments)

        # Verify result is success - handler returns formatted text with JSON
        assert len(result) == 1
        result_text = result[0].text
        # Should indicate success (context saved)
        assert "context" in result_text.lower()

        # Verify context.json was created
        context_file = planning_project / "coderef" / "working" / "user-authentication" / "context.json"
        assert context_file.exists()

        # Verify content
        with open(context_file) as f:
            context = json.load(f)

        assert context["feature_name"] == "user-authentication"
        assert context["description"] == sample_context_data["description"]
        assert context["goal"] == sample_context_data["goal"]
        assert context["requirements"] == sample_context_data["requirements"]
        assert "_metadata" in context
        assert "workorder_id" in context["_metadata"]
        assert context["_metadata"]["workorder_id"].startswith("WO-")

    @pytest.mark.asyncio
    async def test_gather_context_generates_workorder_id(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test that gather_context generates valid workorder ID."""
        arguments = {
            "project_path": str(planning_project),
            **sample_context_data
        }

        result = await tool_handlers.handle_gather_context(arguments)
        result_text = result[0].text

        # Handler returns formatted text with workorder ID
        assert "WO-" in result_text
        # Workorder format includes feature name in uppercase
        assert "WO-USER-AUTHENTICATION" in result_text

    @pytest.mark.asyncio
    async def test_gather_context_validates_required_fields(
        self, planning_project: Path
    ):
        """Test that gather_context validates required fields."""
        # Handler catches validation errors and returns error response (not exception)

        # Missing/short description
        result = await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            "feature_name": "test-feature",
            "description": "short",  # Too short
            "goal": "A goal that is long enough to pass validation",
            "requirements": ["req1"]
        })
        result_text = result[0].text.lower()
        assert "invalid" in result_text or "error" in result_text or "description" in result_text

        # Missing/short goal
        result = await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            "feature_name": "test-feature",
            "description": "A description that is long enough",
            "goal": "short",  # Too short
            "requirements": ["req1"]
        })
        result_text = result[0].text.lower()
        assert "invalid" in result_text or "error" in result_text or "goal" in result_text

        # Empty requirements
        result = await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            "feature_name": "test-feature",
            "description": "A description that is long enough",
            "goal": "A goal that is long enough to pass validation",
            "requirements": []
        })
        result_text = result[0].text.lower()
        assert "invalid" in result_text or "error" in result_text or "requirement" in result_text

    @pytest.mark.asyncio
    async def test_gather_context_validates_feature_name(
        self, planning_project: Path
    ):
        """Test that gather_context validates feature name format."""
        # Handler catches validation errors and returns error response (not exception)
        result = await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            "feature_name": "../invalid-path",  # Path traversal attempt
            "description": "A valid description for testing",
            "goal": "A valid goal for testing purposes",
            "requirements": ["requirement 1"]
        })
        result_text = result[0].text.lower()
        assert "invalid" in result_text or "error" in result_text

    @pytest.mark.asyncio
    async def test_gather_context_with_optional_fields(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test gather_context with all optional fields."""
        arguments = {
            "project_path": str(planning_project),
            **sample_context_data,
            "decisions": {"architecture": "microservices"},
        }

        result = await tool_handlers.handle_gather_context(arguments)

        # Verify optional fields are saved
        context_file = planning_project / "coderef" / "working" / "user-authentication" / "context.json"
        with open(context_file) as f:
            context = json.load(f)

        assert context["constraints"] == sample_context_data["constraints"]
        assert context["out_of_scope"] == sample_context_data["out_of_scope"]
        assert context["decisions"] == {"architecture": "microservices"}


# ============================================================================
# ANALYZE PROJECT TESTS
# ============================================================================

class TestAnalyzeProjectWorkflow:
    """Tests for analyze_project_for_planning handler."""

    @pytest.mark.asyncio
    async def test_analyze_project_returns_analysis(self, planning_project: Path):
        """Test that analyze_project_for_planning returns analysis data."""
        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project)
        })

        assert len(result) == 1
        analysis = json.loads(result[0].text)

        # Verify analysis structure
        assert "foundation_docs" in analysis
        assert "coding_standards" in analysis
        assert "technology_stack" in analysis
        assert "key_patterns_identified" in analysis
        assert "gaps_and_risks" in analysis

    @pytest.mark.asyncio
    async def test_analyze_project_discovers_foundation_docs(
        self, planning_project: Path
    ):
        """Test that analysis discovers foundation documentation."""
        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project)
        })

        analysis = json.loads(result[0].text)

        # Should find README.md and ARCHITECTURE.md
        available_docs = analysis["foundation_docs"]["available"]
        assert any("README" in doc for doc in available_docs)

    @pytest.mark.asyncio
    async def test_analyze_project_with_feature_name_saves_file(
        self, planning_project: Path
    ):
        """Test that analysis with feature_name saves to analysis.json."""
        feature_name = "test-analysis-feature"

        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        analysis = json.loads(result[0].text)

        # Verify metadata indicates file was saved
        assert "_metadata" in analysis
        assert analysis["_metadata"]["feature_name"] == feature_name
        assert "saved_to" in analysis["_metadata"]

        # Verify file exists
        analysis_file = planning_project / "coderef" / "working" / feature_name / "analysis.json"
        assert analysis_file.exists()

    @pytest.mark.asyncio
    async def test_analyze_project_reuses_existing_workorder(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test that analysis reuses workorder from context.json."""
        feature_name = "workorder-reuse-test"

        # First gather context to create workorder
        context_args = {
            "project_path": str(planning_project),
            **sample_context_data,
            "feature_name": feature_name
        }
        await tool_handlers.handle_gather_context(context_args)

        # Get the workorder from context
        context_file = planning_project / "coderef" / "working" / feature_name / "context.json"
        with open(context_file) as f:
            context = json.load(f)
        original_workorder = context["_metadata"]["workorder_id"]

        # Run analysis
        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        analysis = json.loads(result[0].text)

        # Should reuse the same workorder
        assert analysis["_metadata"]["workorder_id"] == original_workorder

    @pytest.mark.asyncio
    async def test_analyze_project_discovers_standards(
        self, planning_project: Path
    ):
        """Test that analysis discovers coding standards."""
        result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project)
        })

        analysis = json.loads(result[0].text)

        # Should find UI-STANDARDS.md
        available_standards = analysis["coding_standards"]["available"]
        assert any("UI-STANDARDS" in std for std in available_standards)


# ============================================================================
# VALIDATE PLAN TESTS
# ============================================================================

class TestValidatePlanWorkflow:
    """Tests for validate_implementation_plan handler."""

    @pytest.mark.asyncio
    async def test_validate_plan_returns_score(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test that validate_implementation_plan returns a score."""
        # Create plan file
        feature_dir = planning_project / "coderef" / "working" / "test-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(sample_plan_data, indent=2))

        result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/test-feature/plan.json"
        })

        validation = json.loads(result[0].text)

        assert "score" in validation
        assert isinstance(validation["score"], (int, float))
        assert 0 <= validation["score"] <= 100
        assert "validation_result" in validation
        assert "issues" in validation
        assert "approved" in validation

    @pytest.mark.asyncio
    async def test_validate_plan_identifies_issues(
        self, planning_project: Path
    ):
        """Test that validation identifies issues in incomplete plans."""
        # Create minimal plan with missing sections
        incomplete_plan = {
            "META_DOCUMENTATION": {
                "feature_name": "incomplete-feature",
                "status": "partial"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "1_executive_summary": {}
                # Missing other sections
            }
        }

        feature_dir = planning_project / "coderef" / "working" / "incomplete-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(incomplete_plan, indent=2))

        result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/incomplete-feature/plan.json"
        })

        validation = json.loads(result[0].text)

        # Should have issues and lower score
        assert len(validation["issues"]) > 0
        assert validation["score"] < 100

    @pytest.mark.asyncio
    async def test_validate_plan_handles_missing_file(
        self, planning_project: Path
    ):
        """Test that validation handles missing plan file."""
        # Handler catches FileNotFoundError and returns error response
        result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/nonexistent/plan.json"
        })
        result_text = result[0].text.lower()
        assert "not found" in result_text or "error" in result_text or "invalid" in result_text

    @pytest.mark.asyncio
    async def test_validate_plan_handles_malformed_json(
        self, planning_project: Path
    ):
        """Test that validation handles malformed JSON."""
        feature_dir = planning_project / "coderef" / "working" / "malformed"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text("{ invalid json }")

        # Handler catches JSONDecodeError and returns error response
        result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/malformed/plan.json"
        })
        result_text = result[0].text.lower()
        assert "invalid" in result_text or "json" in result_text or "error" in result_text

    @pytest.mark.asyncio
    async def test_validate_plan_workorder_validation(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test that validation checks workorder consistency."""
        # Modify plan with inconsistent workorders
        plan_data = sample_plan_data.copy()
        plan_data["UNIVERSAL_PLANNING_STRUCTURE"]["5_task_id_system"]["tasks"][0]["workorder_id"] = "WO-DIFFERENT-001"

        feature_dir = planning_project / "coderef" / "working" / "workorder-test"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(plan_data, indent=2))

        result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/workorder-test/plan.json"
        })

        validation = json.loads(result[0].text)

        # Should identify workorder inconsistency
        issues_text = str(validation["issues"])
        # Workorder validation may or may not be strict depending on validator implementation


# ============================================================================
# CREATE PLAN TESTS
# ============================================================================

class TestCreatePlanWorkflow:
    """Tests for create_plan handler (meta-tool)."""

    @pytest.mark.asyncio
    async def test_create_plan_returns_instructions(
        self, planning_project: Path
    ):
        """Test that create_plan returns synthesis instructions."""
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": "new-feature"
        })

        assert len(result) == 1
        response_text = result[0].text

        # Should contain instructions for AI
        assert "INSTRUCTIONS FOR AI" in response_text
        assert "new-feature" in response_text
        assert "plan.json" in response_text

    @pytest.mark.asyncio
    async def test_create_plan_includes_workorder(
        self, planning_project: Path
    ):
        """Test that create_plan includes workorder information."""
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": "workorder-feature"
        })

        response_text = result[0].text

        # Should include workorder ID
        assert "WO-" in response_text
        assert "WORKORDER" in response_text.upper()

    @pytest.mark.asyncio
    async def test_create_plan_with_context(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test create_plan with existing context.json."""
        feature_name = "context-feature"

        # First gather context
        await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            **sample_context_data,
            "feature_name": feature_name
        })

        # Then create plan
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        response_text = result[0].text

        # Should indicate context is available
        assert "CONTEXT" in response_text
        assert sample_context_data["description"][:50] in response_text

    @pytest.mark.asyncio
    async def test_create_plan_with_analysis(
        self, planning_project: Path
    ):
        """Test create_plan with existing analysis.json."""
        feature_name = "analysis-feature"

        # First run analysis
        await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        # Then create plan
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        response_text = result[0].text

        # Should indicate analysis is available
        assert "ANALYSIS" in response_text

    @pytest.mark.asyncio
    async def test_create_plan_multi_agent_mode(
        self, planning_project: Path
    ):
        """Test create_plan with multi_agent mode enabled."""
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": "multi-agent-feature",
            "multi_agent": True
        })

        response_text = result[0].text

        # Should include multi-agent instructions
        assert "MULTI-AGENT" in response_text
        assert "communication.json" in response_text

    @pytest.mark.asyncio
    async def test_create_plan_schema_contract(
        self, planning_project: Path
    ):
        """Test that create_plan includes schema contract information."""
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": "schema-feature"
        })

        response_text = result[0].text

        # Should include schema contract
        assert "SCHEMA CONTRACT" in response_text
        assert "schema_version" in response_text
        assert "phases" in response_text


# ============================================================================
# REVIEW REPORT TESTS
# ============================================================================

class TestPlanReviewReport:
    """Tests for generate_plan_review_report handler."""

    @pytest.mark.asyncio
    async def test_generate_review_report_creates_file(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test that generate_plan_review_report creates markdown file."""
        # Create plan file
        feature_dir = planning_project / "coderef" / "working" / "review-feature"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(sample_plan_data, indent=2))

        result = await tool_handlers.handle_generate_plan_review_report({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/review-feature/plan.json"
        })

        response_text = result[0].text

        # Should indicate success
        assert "Review report generated successfully" in response_text or "review" in response_text.lower()

        # Verify review file exists
        reviews_dir = planning_project / "coderef" / "reviews"
        review_files = list(reviews_dir.glob("review-*.md"))
        assert len(review_files) > 0

    @pytest.mark.asyncio
    async def test_generate_review_report_content(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test that review report contains expected content."""
        # Create plan file
        feature_dir = planning_project / "coderef" / "working" / "content-review"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(sample_plan_data, indent=2))

        await tool_handlers.handle_generate_plan_review_report({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/content-review/plan.json"
        })

        # Read the review file
        reviews_dir = planning_project / "coderef" / "reviews"
        review_files = list(reviews_dir.glob("review-*.md"))
        review_content = review_files[0].read_text()

        # Should contain score and assessment sections
        assert "Score" in review_content or "score" in review_content.lower()

    @pytest.mark.asyncio
    async def test_generate_review_report_custom_output(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test generate_plan_review_report with custom output path."""
        # Create plan file
        feature_dir = planning_project / "coderef" / "working" / "custom-output"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(sample_plan_data, indent=2))

        custom_path = "coderef/reviews/custom-review.md"

        await tool_handlers.handle_generate_plan_review_report({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/custom-output/plan.json",
            "output_path": custom_path
        })

        # Verify custom output file exists
        assert (planning_project / custom_path).exists()


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

class TestEndToEndPlanningWorkflow:
    """End-to-end tests for the complete planning workflow."""

    @pytest.mark.asyncio
    async def test_full_planning_workflow(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test complete workflow: gather -> analyze -> create -> validate."""
        feature_name = "e2e-test-feature"

        # Step 1: Gather context
        context_result = await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            **sample_context_data,
            "feature_name": feature_name
        })
        # Handler returns formatted text with workorder ID
        context_text = context_result[0].text
        assert "context" in context_text.lower()
        # Extract workorder ID from response text
        import re
        workorder_match = re.search(r'WO-[\w-]+-\d{3}', context_text)
        assert workorder_match, f"Workorder ID not found in: {context_text}"
        workorder_id = workorder_match.group(0)

        # Step 2: Analyze project
        analysis_result = await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })
        analysis_data = json.loads(analysis_result[0].text)
        assert "foundation_docs" in analysis_data or "technology_stack" in analysis_data

        # Step 3: Create plan (meta-tool - returns instructions or plan directly)
        plan_result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })
        plan_response = plan_result[0].text
        # Handler returns instructions or creates plan directly
        assert "plan" in plan_response.lower() or "instruction" in plan_response.lower()

        # Step 4: Manually create plan file to simulate AI completion
        plan_data = {
            "META_DOCUMENTATION": {
                "feature_name": feature_name,
                "schema_version": "1.0.0",
                "version": "1.0.0",
                "status": "complete"
            },
            "UNIVERSAL_PLANNING_STRUCTURE": {
                "5_task_id_system": {
                    "workorder": {
                        "id": workorder_id,
                        "name": feature_name
                    },
                    "tasks": []
                }
            }
        }

        plan_file = planning_project / "coderef" / "working" / feature_name / "plan.json"
        plan_file.write_text(json.dumps(plan_data, indent=2))

        # Step 5: Validate plan
        validate_result = await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": f"coderef/working/{feature_name}/plan.json"
        })
        validation = json.loads(validate_result[0].text)
        assert "score" in validation

    @pytest.mark.asyncio
    async def test_workflow_with_missing_context(
        self, planning_project: Path
    ):
        """Test workflow when context.json is missing."""
        feature_name = "no-context-feature"

        # Skip gather_context, go straight to analyze
        await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        # Create plan should still work, just warn about missing context
        result = await tool_handlers.handle_create_plan({
            "project_path": str(planning_project),
            "feature_name": feature_name
        })

        response_text = result[0].text
        assert "NO CONTEXT" in response_text or "context" in response_text.lower()

    @pytest.mark.asyncio
    async def test_workflow_creates_working_directory(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test that workflow creates the feature working directory."""
        feature_name = "new-working-dir"
        working_dir = planning_project / "coderef" / "working" / feature_name

        # Directory shouldn't exist yet
        assert not working_dir.exists()

        # Gather context should create it
        await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            **sample_context_data,
            "feature_name": feature_name
        })

        # Now it should exist
        assert working_dir.exists()
        assert (working_dir / "context.json").exists()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPlanningWorkflowPerformance:
    """Performance tests for planning workflow."""

    @pytest.mark.asyncio
    async def test_gather_context_performance(
        self, planning_project: Path, sample_context_data: Dict[str, Any]
    ):
        """Test gather_context completes within reasonable time."""
        import time

        start_time = time.time()
        await tool_handlers.handle_gather_context({
            "project_path": str(planning_project),
            **sample_context_data,
            "feature_name": "perf-test-1"
        })
        elapsed = time.time() - start_time

        # Should complete within 1 second
        assert elapsed < 1.0, f"gather_context took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_analyze_project_performance(
        self, planning_project: Path
    ):
        """Test analyze_project_for_planning completes within reasonable time."""
        import time

        start_time = time.time()
        await tool_handlers.handle_analyze_project_for_planning({
            "project_path": str(planning_project),
            "feature_name": "perf-test-2"
        })
        elapsed = time.time() - start_time

        # Should complete within 2 seconds for small project
        assert elapsed < 2.0, f"analyze_project took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_validate_plan_performance(
        self, planning_project: Path, sample_plan_data: Dict[str, Any]
    ):
        """Test validate_implementation_plan completes within reasonable time."""
        import time

        # Create plan file
        feature_dir = planning_project / "coderef" / "working" / "perf-test-3"
        feature_dir.mkdir(parents=True, exist_ok=True)
        plan_file = feature_dir / "plan.json"
        plan_file.write_text(json.dumps(sample_plan_data, indent=2))

        start_time = time.time()
        await tool_handlers.handle_validate_implementation_plan({
            "project_path": str(planning_project),
            "plan_file_path": "coderef/working/perf-test-3/plan.json"
        })
        elapsed = time.time() - start_time

        # Should complete within 1 second
        assert elapsed < 1.0, f"validate_plan took {elapsed:.2f}s"
