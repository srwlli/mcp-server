"""Integration tests for AI-powered planning workflow."""

import pytest
import json
from pathlib import Path
from generators.planning_generator import PlanningGenerator


class TestAIPlanningIntegration:
    """End-to-end integration tests for AI planning."""

    @pytest.fixture
    def project_with_coderef(self, tmp_path):
        """Create temporary project with .coderef/ structure."""
        # Create .coderef/ directory
        coderef_dir = tmp_path / ".coderef"
        coderef_dir.mkdir()

        # Create index.json
        index_data = [
            {"name": "authenticate_user", "type": "function", "file": "src/auth.py", "line": 45},
            {"name": "generate_token", "type": "function", "file": "src/auth.py", "line": 67},
            {"name": "AuthService", "type": "class", "file": "src/services/auth_service.py", "line": 12}
        ]
        (coderef_dir / "index.json").write_text(json.dumps(index_data))

        # Create graph.json
        graph_data = {
            "nodes": [
                {"id": "authenticate_user", "type": "function"},
                {"id": "generate_token", "type": "function"}
            ],
            "edges": [
                {"source": "authenticate_user", "target": "generate_token"}
            ]
        }
        (coderef_dir / "graph.json").write_text(json.dumps(graph_data))

        # Create reports directory
        reports_dir = coderef_dir / "reports"
        reports_dir.mkdir()

        # Create patterns.json
        patterns_data = {
            "patterns": [
                {"name": "error_handling", "pattern": "try/except with logging", "count": 15},
                {"name": "naming_convention", "pattern": "snake_case", "count": 100}
            ]
        }
        (reports_dir / "patterns.json").write_text(json.dumps(patterns_data))

        # Create coverage.json
        coverage_data = {"overall_coverage": 75.5, "uncovered_files": ["src/new_module.py"]}
        (reports_dir / "coverage.json").write_text(json.dumps(coverage_data))

        # Create complexity.json
        complexity_data = {
            "files": [
                {"path": "src/auth.py", "complexity": 15},
                {"path": "src/services/auth_service.py", "complexity": 25}
            ]
        }
        (reports_dir / "complexity.json").write_text(json.dumps(complexity_data))

        return tmp_path

    @pytest.mark.asyncio
    async def test_full_plan_generation_workflow(self, project_with_coderef):
        """Test complete plan generation workflow with coderef data."""
        # Setup
        generator = PlanningGenerator(project_with_coderef)

        context = {
            "description": "Add JWT authentication with refresh tokens",
            "goal": "Secure API endpoints with token-based auth",
            "requirements": [
                "JWT token generation",
                "Refresh token support",
                "Token validation middleware"
            ],
            "constraints": [
                "Use existing AuthService",
                "No breaking changes to API"
            ]
        }

        analysis = {
            "foundation_doc_content": {
                "ARCHITECTURE.md": {"preview": "Test architecture"},
                "API.md": {"preview": "Test API"}
            }
        }

        # Execute
        plan = await generator.generate_plan(
            feature_name="jwt-authentication",
            context=context,
            analysis=analysis,
            workorder_id="WO-JWT-AUTH-001"
        )

        # Verify plan structure
        assert plan is not None
        assert "META_DOCUMENTATION" in plan
        assert "UNIVERSAL_PLANNING_STRUCTURE" in plan

        # Verify metadata
        meta = plan["META_DOCUMENTATION"]
        assert meta["feature_name"] == "jwt-authentication"
        assert meta["workorder_id"] == "WO-JWT-AUTH-001"
        assert meta["has_context"] is True
        assert meta["has_analysis"] is True

        # Verify plan sections
        structure = plan["UNIVERSAL_PLANNING_STRUCTURE"]
        assert "0_preparation" in structure
        assert "1_executive_summary" in structure
        assert "2_risk_assessment" in structure
        assert "5_task_id_system" in structure
        assert "6_implementation_phases" in structure

        # Verify tasks exist
        tasks = structure["5_task_id_system"]["tasks"]
        assert len(tasks) > 0
        assert any("SETUP" in task for task in tasks)
        assert any("IMPL" in task or "LOGIC" in task for task in tasks)

        # Verify phases exist
        phases = structure["6_implementation_phases"]["phases"]
        assert len(phases) > 0
        assert all("name" in phase for phase in phases)

    @pytest.mark.asyncio
    async def test_plan_generation_with_missing_coderef(self, tmp_path):
        """Test plan generation fails gracefully without .coderef/."""
        generator = PlanningGenerator(tmp_path)

        context = {"description": "Test", "goal": "Test", "requirements": ["Test"]}
        analysis = {}

        # Execute - should raise ValueError about missing .coderef/
        with pytest.raises(ValueError) as exc_info:
            await generator.generate_plan(
                feature_name="test-feature",
                context=context,
                analysis=analysis
            )

        assert ".coderef/ directory not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_plan_generation_falls_back_on_agent_error(self, project_with_coderef):
        """Test plan generation falls back to template when agent unavailable."""
        generator = PlanningGenerator(project_with_coderef)

        context = {
            "description": "Test feature",
            "goal": "Test goal",
            "requirements": ["Requirement 1", "Requirement 2"]
        }
        analysis = {"foundation_doc_content": {}}

        # Execute - should fall back gracefully
        plan = await generator.generate_plan(
            feature_name="test-fallback",
            context=context,
            analysis=analysis
        )

        # Verify fallback plan was generated
        assert plan is not None
        assert "META_DOCUMENTATION" in plan

        # Verify it's using fallback (not "AI Agent")
        generated_by = plan["META_DOCUMENTATION"]["generated_by"]
        assert "fallback" in generated_by.lower() or "PlanningGenerator" in generated_by

    def test_coderef_data_loading_integration(self, project_with_coderef):
        """Test all coderef data files are loaded correctly."""
        generator = PlanningGenerator(project_with_coderef)

        # Load all data
        index = generator._load_coderef_index()
        patterns = generator._load_coderef_patterns()
        graph = generator._load_coderef_graph()
        coverage = generator._load_coderef_coverage()
        complexity = generator._load_coderef_complexity()

        # Verify all loaded successfully
        assert index is not None
        assert len(index) == 3
        assert patterns is not None
        assert len(patterns["patterns"]) == 2
        assert graph is not None
        assert len(graph["nodes"]) == 2
        assert coverage is not None
        assert coverage["overall_coverage"] == 75.5
        assert complexity is not None
        assert len(complexity["files"]) == 2

    def test_prompt_builder_uses_all_context(self, project_with_coderef):
        """Test prompt builder includes all available context."""
        generator = PlanningGenerator(project_with_coderef)

        context = {
            "description": "JWT auth feature",
            "goal": "Secure endpoints",
            "requirements": ["Token gen", "Token validation"],
            "constraints": ["No breaking changes"]
        }

        analysis = {
            "foundation_doc_content": {
                "ARCHITECTURE.md": {"preview": "Architecture overview"},
                "API.md": {"preview": "API documentation"}
            }
        }

        # Load coderef data
        coderef_data = {
            "index": generator._load_coderef_index(),
            "patterns": generator._load_coderef_patterns(),
            "graph": generator._load_coderef_graph(),
            "coverage": generator._load_coderef_coverage(),
            "complexity": generator._load_coderef_complexity()
        }

        template = {}

        # Build prompt
        prompt = generator._build_agent_prompt(
            "jwt-auth", context, analysis, coderef_data, template
        )

        # Verify all context is included
        assert "JWT auth feature" in prompt
        assert "Secure endpoints" in prompt
        assert "Token gen" in prompt
        assert "Token validation" in prompt
        assert "No breaking changes" in prompt
        assert "CODE INVENTORY" in prompt
        assert "CODING PATTERNS" in prompt
        assert "DEPENDENCY GRAPH" in prompt
        assert "TEST COVERAGE" in prompt
        assert "75.5%" in prompt  # Coverage percentage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
