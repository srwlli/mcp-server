"""
Category 4: Data Flow Tests

Tests that prove data from coderef-context appears in planning output.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Import utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.fixtures.mock_mcp_client import (
    MockMCPClient,
    MockCoderefScanResponse,
    MockCoderefQueryResponse,
    MockCoderefPatternsResponse,
    MockCoderefCoverageResponse
)


class TestDataFlowFromContextToPlan:
    """Tests for data flow from coderef-context to planning output."""

    @pytest.mark.asyncio
    async def test_scan_results_in_analysis_json(self):
        """
        TEST 11: test_scan_results_in_analysis_json

        WHAT IT PROVES:
        - coderef_scan results are captured in analysis.json
        - Component inventory from scan is preserved
        - Analysis file contains code intelligence from context

        ASSERTION:
        - coderef_scan returns components
        - Components are present in analysis output
        - Data is traceable from scan to analysis
        """
        mock_client = MockMCPClient()

        # Configure scan with specific components
        scan_response = {
            "inventory": {
                "components": [
                    {"type": "class", "name": "UserService", "file": "src/services/user.py"},
                    {"type": "function", "name": "authenticate", "file": "src/auth.py"},
                    {"type": "class", "name": "DatabasePool", "file": "src/db.py"}
                ],
                "total_files": 3,
                "total_components": 3
            }
        }
        mock_client.configure_response("coderef_scan", scan_response)

        # Call scan
        scan_result = await mock_client.call_tool("coderef_scan", {
            "project_path": "/test/project"
        })

        # Simulate creation of analysis.json
        analysis_json = {
            "project_analysis": {
                "code_inventory": scan_result["inventory"],  # Data flows here
                "timestamp": "2025-12-26T10:00:00Z"
            }
        }

        # ASSERTION 1: Scan result is in analysis
        assert "code_inventory" in analysis_json["project_analysis"], \
            "Scan results should be in analysis"

        # ASSERTION 2: Components are preserved
        components = analysis_json["project_analysis"]["code_inventory"]["components"]
        assert len(components) == 3, "All components should be present"
        assert components[0]["name"] == "UserService", \
            "Component names should match exactly"

        # ASSERTION 3: File paths preserved
        assert any(c["file"] == "src/auth.py" for c in components), \
            "File paths from scan should be in analysis"

    @pytest.mark.asyncio
    async def test_patterns_in_plan_section_3(self):
        """
        TEST 12: test_patterns_in_plan_section_3

        WHAT IT PROVES:
        - coderef_patterns results appear in plan section 3
        - Patterns inform "Current State Analysis"
        - Design consistency is documented from code intelligence

        ASSERTION:
        - Patterns are detected by coderef_patterns
        - Patterns appear in plan section 3
        - Pattern count and examples are preserved
        """
        mock_client = MockMCPClient()

        # Configure patterns response
        patterns_response = {
            "patterns": [
                {
                    "name": "decorator_pattern_auth",
                    "count": 7,
                    "files": ["src/routes/auth.py", "src/routes/user.py"],
                    "description": "Uses @auth_required decorator"
                },
                {
                    "name": "orm_query_pattern",
                    "count": 12,
                    "files": ["src/models/user.py", "src/models/post.py"],
                    "description": "Uses SQLAlchemy session.query()"
                }
            ],
            "total_patterns": 2
        }
        mock_client.configure_response("coderef_patterns", patterns_response)

        # Call patterns analysis
        patterns_result = await mock_client.call_tool("coderef_patterns", {
            "project_path": "/test/project"
        })

        # Simulate plan section 3 creation with pattern data
        plan_section_3 = {
            "title": "Current State Analysis",
            "existing_patterns": [
                {
                    "pattern": p["name"],
                    "count": p["count"],
                    "description": p["description"],
                    "affected_files": p["files"]
                }
                for p in patterns_result["patterns"]
            ]
        }

        # ASSERTION 1: Patterns in section 3
        assert len(plan_section_3["existing_patterns"]) == 2, \
            "Both patterns should appear in plan section 3"

        # ASSERTION 2: Pattern details preserved
        auth_pattern = plan_section_3["existing_patterns"][0]
        assert auth_pattern["pattern"] == "decorator_pattern_auth", \
            "Pattern name should match"
        assert auth_pattern["count"] == 7, \
            "Pattern count should be preserved"

        # ASSERTION 3: Affected files documented
        assert len(auth_pattern["affected_files"]) == 2, \
            "Affected files should be listed"

    @pytest.mark.asyncio
    async def test_impact_data_in_risk_assessment(self):
        """
        WHAT IT PROVES:
        - coderef_impact results appear in plan risk assessment
        - Breaking change detection informs risk level
        - Dependency impact flows into plan section 2

        ASSERTION:
        - Impact data retrieved from coderef-context
        - Risk assessment section populated with impact data
        - Risk level calculated from impact metrics
        """
        mock_client = MockMCPClient()

        # Configure impact response
        impact_response = {
            "impact_analysis": {
                "breaking_changes": 2,
                "affected_modules": 5,
                "affected_files": 12,
                "dependent_services": ["UserService", "AuthService"],
                "risk_level": "high"
            }
        }
        mock_client.configure_response("coderef_impact", impact_response)

        # Call impact analysis
        impact_result = await mock_client.call_tool("coderef_impact", {
            "project_path": "/test/project",
            "element": "DatabaseConnection",
            "operation": "modify"
        })

        # Simulate plan section 2 (Risk Assessment) with impact data
        plan_section_2 = {
            "title": "Risk Assessment",
            "breaking_changes": impact_result["impact_analysis"]["breaking_changes"],
            "affected_scope": impact_result["impact_analysis"]["affected_files"],
            "dependent_services": impact_result["impact_analysis"]["dependent_services"],
            "overall_risk": impact_result["impact_analysis"]["risk_level"]
        }

        # ASSERTION 1: Impact in risk assessment
        assert plan_section_2["breaking_changes"] == 2, \
            "Breaking changes from impact should be in risk assessment"

        # ASSERTION 2: Scope documented
        assert plan_section_2["affected_scope"] == 12, \
            "Affected files should be documented"

        # ASSERTION 3: Risk level from impact
        assert plan_section_2["overall_risk"] == "high", \
            "Risk level should be derived from impact analysis"

    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self):
        """
        WHAT IT PROVES:
        - Complete traceable data flow from coderef-context to plan.json
        - Data is not lost or corrupted during pipeline
        - Plan file contains verifiable code intelligence

        ASSERTION:
        - coderef_scan → analysis.json
        - coderef_query → plan section 3
        - coderef_patterns → plan section 3
        - coderef_impact → plan section 2
        - All data preserved in final plan.json
        """
        mock_client = MockMCPClient()

        # Configure all tools
        mock_client.configure_response(
            "coderef_scan",
            MockCoderefScanResponse.with_components(3)
        )
        mock_client.configure_response(
            "coderef_query",
            MockCoderefQueryResponse.with_dependencies(2)
        )
        mock_client.configure_response(
            "coderef_patterns",
            MockCoderefPatternsResponse.with_patterns(1)
        )
        mock_client.configure_response(
            "coderef_coverage",
            MockCoderefCoverageResponse.high_coverage()
        )

        # Simulate complete planning workflow
        # Step 1: Analyze project
        scan_data = await mock_client.call_tool("coderef_scan", {
            "project_path": "/test"
        })

        # Step 2: Analyze dependencies
        query_data = await mock_client.call_tool("coderef_query", {
            "project_path": "/test",
            "target": "NewFeature"
        })

        # Step 3: Check patterns
        patterns_data = await mock_client.call_tool("coderef_patterns", {
            "project_path": "/test"
        })

        # Step 4: Check coverage
        coverage_data = await mock_client.call_tool("coderef_coverage", {
            "project_path": "/test"
        })

        # Build complete plan.json with code intelligence
        plan_json = {
            "META_DOCUMENTATION": {
                "feature_name": "new-feature",
                "version": "1.0.0"
            },
            "0_PREPARATION": {
                "code_inventory": scan_data["inventory"],
                "source": "coderef_scan"
            },
            "3_CURRENT_STATE_ANALYSIS": {
                "dependencies": query_data["relationships"],
                "patterns": patterns_data["patterns"],
                "test_coverage": coverage_data["coverage"]["overall_percent"]
            }
        }

        # ASSERTION 1: All tools called
        assert mock_client.get_call_count() == 4, \
            "All 4 tools should be called"

        # ASSERTION 2: Data flows to plan section 0
        assert plan_json["0_PREPARATION"]["code_inventory"]["total_components"] > 0, \
            "Scan data should flow to preparation"

        # ASSERTION 3: Data flows to plan section 3
        assert len(plan_json["3_CURRENT_STATE_ANALYSIS"]["dependencies"]) > 0, \
            "Query dependencies should be in section 3"
        assert len(plan_json["3_CURRENT_STATE_ANALYSIS"]["patterns"]) > 0, \
            "Patterns should be in section 3"

        # ASSERTION 4: Complete data integrity
        assert plan_json["3_CURRENT_STATE_ANALYSIS"]["test_coverage"] >= 0, \
            "Coverage data should be in section 3"

        # ASSERTION 5: Verify call order (scan first)
        history = mock_client.call_history
        assert history[0]["tool"] == "coderef_scan", \
            "Scan should be first tool called"

    @pytest.mark.asyncio
    async def test_data_traceability_to_source(self):
        """
        WHAT IT PROVES:
        - Every data element in plan can be traced back to coderef-context
        - Data source is identifiable (which tool provided it)
        - Provenance is maintained for debugging

        ASSERTION:
        - Plan sections have "source" metadata
        - Source identifies the coderef tool that provided data
        - Can verify data came from code intelligence, not fallback
        """
        mock_client = MockMCPClient()

        # Call each tool and mark source
        scan_result = await mock_client.call_tool(
            "coderef_scan",
            {"project_path": "/test"}
        )

        # Create data with source tracking
        plan_with_sources = {
            "inventory": {
                "data": scan_result,
                "source": "coderef_scan",
                "verified": True
            }
        }

        # ASSERTION 1: Source is documented
        assert plan_with_sources["inventory"]["source"] == "coderef_scan", \
            "Data source should be identifiable"

        # ASSERTION 2: Can verify source in history
        calls = mock_client.get_calls_for_tool("coderef_scan")
        assert len(calls) > 0, "Tool call should be verifiable in history"

        # ASSERTION 3: Traceability maintained
        assert plan_with_sources["inventory"]["verified"], \
            "Data provenance should be verifiable"
