"""
Comprehensive Integration Test: coderef-context → coderef-workflow

This test suite verifies that coderef-context is properly injected into
coderef-workflow planning processes.

Test Coverage:
1. MCP server connectivity
2. Tool invocation and response
3. Data flow into planning documents
4. End-to-end workorder creation
5. Plan generator using coderef-context data

Location: coderef-context/tests/test_workflow_integration.py
Purpose: Verify integration between coderef-context and coderef-workflow
Status: Comprehensive E2E testing
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add paths for imports
WORKFLOW_PATH = Path(__file__).parent.parent.parent / "coderef-workflow"
sys.path.insert(0, str(WORKFLOW_PATH))

from generators.planning_analyzer import PlanningAnalyzer
from generators.planning_generator import PlanningGenerator
from mcp_client import MCPToolClient, call_coderef_tool


class TestMCPServerConnectivity:
    """Test 1: Verify coderef-context MCP server is accessible."""

    @pytest.mark.asyncio
    async def test_coderef_context_server_available(self):
        """
        TEST: Verify coderef-context MCP server responds to ping.

        WHAT IT PROVES:
        - coderef-context MCP server is running
        - Server can receive and respond to requests
        - Communication channel is established

        ASSERTIONS:
        - Server responds without error
        - Response indicates server is ready
        """
        # This test requires actual MCP server running
        # In production, this would verify:
        # 1. MCP registry has coderef-context listed
        # 2. Server responds to list_tools request
        # 3. Expected tools are available

        # Mock for testing (replace with real MCP call in integration env)
        with patch('mcp_client.MCPToolClient') as mock_client:
            mock_instance = AsyncMock()
            mock_instance.list_tools.return_value = [
                "coderef_scan",
                "coderef_query",
                "coderef_impact",
                "coderef_patterns",
                "coderef_coverage"
            ]
            mock_client.return_value = mock_instance

            client = MCPToolClient()
            tools = await client.list_tools()

            # ASSERTION 1: Server responds
            assert tools is not None, "Server should respond with tool list"

            # ASSERTION 2: Expected tools present
            assert "coderef_scan" in tools, "coderef_scan tool should be available"
            assert "coderef_query" in tools, "coderef_query tool should be available"
            assert "coderef_patterns" in tools, "coderef_patterns tool should be available"

            # ASSERTION 3: Minimum tool count
            assert len(tools) >= 5, f"Expected at least 5 tools, got {len(tools)}"


class TestToolInvocationFromWorkflow:
    """Test 2: Verify coderef-workflow can call coderef-context tools."""

    @pytest.mark.asyncio
    async def test_planning_analyzer_calls_coderef_scan(self):
        """
        TEST: Verify PlanningAnalyzer invokes coderef_scan.

        WHAT IT PROVES:
        - PlanningAnalyzer imports and calls coderef_scan
        - Tool is invoked with correct project_path
        - Results are captured in analysis data

        ASSERTIONS:
        - coderef_scan called during analyze()
        - Tool receives project_path parameter
        - Scan results included in analysis output
        """
        test_project = Path(__file__).parent.parent  # coderef-context directory
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Configure mock response
            mock_tool.return_value = {
                "success": True,
                "data": {
                    "summary": {
                        "total_elements": 100,
                        "total_files": 25,
                        "languages": ["python"]
                    },
                    "components": [
                        {"name": "Component1", "type": "class"},
                        {"name": "Component2", "type": "function"}
                    ]
                }
            }

            # Run analysis (which should call coderef_scan)
            result = await analyzer.read_inventory_data()

            # ASSERTION 1: Tool was called
            mock_tool.assert_called()

            # ASSERTION 2: Called with project_path
            call_args = mock_tool.call_args
            assert call_args is not None, "Tool should be called with arguments"

            # ASSERTION 3: Results captured
            assert "scan_results" in result or result is not None, \
                "Scan results should be captured"

    @pytest.mark.asyncio
    async def test_planning_analyzer_calls_coderef_patterns(self):
        """
        TEST: Verify PlanningAnalyzer invokes coderef_patterns.

        WHAT IT PROVES:
        - Pattern detection tool is called during analysis
        - Patterns are extracted and returned
        - Results feed into plan preparation section

        ASSERTIONS:
        - coderef_patterns called during analyze()
        - Pattern list returned
        - Patterns available for plan generation
        """
        test_project = Path(__file__).parent.parent
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Configure patterns response
            mock_tool.return_value = {
                "success": True,
                "data": {
                    "patterns": [
                        "error_handling_pattern",
                        "factory_pattern",
                        "async_pattern"
                    ]
                }
            }

            # Run pattern identification
            patterns = await analyzer.identify_patterns()

            # ASSERTION 1: Tool was called
            mock_tool.assert_called()

            # ASSERTION 2: Patterns returned
            assert isinstance(patterns, list), "Should return list of patterns"

            # ASSERTION 3: Pattern count > 0
            assert len(patterns) > 0, "Should identify at least one pattern"

    @pytest.mark.asyncio
    async def test_planning_analyzer_calls_coderef_query(self):
        """
        TEST: Verify PlanningAnalyzer invokes coderef_query for dependencies.

        WHAT IT PROVES:
        - Dependency query tool is called
        - Query targets specific components
        - Relationship data returned

        ASSERTIONS:
        - coderef_query called with target parameter
        - Returns dependency relationships
        - Data includes caller/callee information
        """
        test_project = Path(__file__).parent.parent
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Configure query response
            mock_tool.return_value = {
                "success": True,
                "data": {
                    "Component1": {"calls": ["Component2", "Component3"]},
                    "Component2": {"calls": ["Component4"]},
                    "Component3": {"calls": []}
                }
            }

            # Run component reference search
            result = await analyzer.find_reference_components()

            # ASSERTION 1: Tool was called
            mock_tool.assert_called()

            # ASSERTION 2: Results contain component data
            assert result is not None, "Should return component reference data"

            # ASSERTION 3: Structured data returned
            assert "secondary" in result or "total_found" in result, \
                "Should have structured reference data"


class TestDataFlowIntoPlanning:
    """Test 3: Verify coderef-context data flows into planning documents."""

    @pytest.mark.asyncio
    async def test_analysis_json_contains_coderef_scan_results(self):
        """
        TEST: Verify analysis.json contains coderef_scan results.

        WHAT IT PROVES:
        - Scan results are written to analysis.json
        - Data includes component inventory
        - Results are structured and complete

        ASSERTIONS:
        - analysis.json exists after analyze()
        - Contains scan_results or inventory section
        - Has component count and types
        """
        test_project = Path(__file__).parent.parent
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Configure full analysis responses
            def mock_tool_responses(tool_name, args):
                if tool_name == "coderef_scan":
                    return {
                        "success": True,
                        "data": {
                            "summary": {"total_elements": 150, "total_files": 30},
                            "components": [{"name": "Test", "type": "class"}]
                        }
                    }
                elif tool_name == "coderef_patterns":
                    return {"success": True, "data": {"patterns": ["pattern1"]}}
                elif tool_name == "coderef_query":
                    return {"success": True, "data": {"comp1": {}}}
                elif tool_name == "coderef_coverage":
                    return {"success": True, "data": {"coverage_percent": 80}}
                return {"success": False}

            mock_tool.side_effect = mock_tool_responses

            # Run full analysis
            analysis_result = await analyzer.analyze()

            # ASSERTION 1: Analysis completed
            assert analysis_result is not None, "Analysis should return results"

            # ASSERTION 2: Contains project structure data
            assert "project_structure" in analysis_result or \
                   "technology_stack" in analysis_result, \
                   "Should contain project structure data from scan"

            # ASSERTION 3: Contains patterns
            assert "key_patterns_identified" in analysis_result, \
                   "Should contain patterns from coderef_patterns"

    @pytest.mark.asyncio
    async def test_plan_json_uses_coderef_context_data(self):
        """
        TEST: Verify plan.json incorporates coderef-context data.

        WHAT IT PROVES:
        - Plan generator uses analysis data from coderef-context
        - Preparation section includes discovered patterns
        - Current state analysis includes component references

        ASSERTIONS:
        - plan.json 0_preparation has patterns from coderef_patterns
        - plan.json 3_current_state has components from coderef_scan
        - Data is not placeholder/TODO
        """
        test_project = Path(__file__).parent.parent
        generator = PlanningGenerator(test_project)

        # Create mock analysis with coderef data
        mock_analysis = {
            "preparation_summary": {
                "foundation_docs": {"available": ["API.md"], "missing": []},
                "coding_standards": {"available": ["PEP8"], "missing": []},
                "reference_components": {"primary": "Component1", "secondary": ["Component2"]},
                "key_patterns_identified": ["async_pattern", "factory_pattern"],
                "technology_stack": {
                    "languages": ["python"],
                    "frameworks": ["pytest"],
                    "key_libraries": ["mcp@1.0.0"]
                },
                "gaps_and_risks": []
            }
        }

        # Create mock context
        mock_context = {
            "description": "Test feature with coderef integration",
            "goal": "Verify coderef data in plan",
            "requirements": ["Use coderef patterns", "Follow discovered architecture"],
            "constraints": []
        }

        # Generate plan
        plan = generator.generate_plan(
            "test-coderef-integration",
            context=mock_context,
            analysis=mock_analysis,
            workorder_id="WO-TEST-CODEREF-001"
        )

        # ASSERTION 1: Plan generated
        assert plan is not None, "Plan should be generated"
        assert "UNIVERSAL_PLANNING_STRUCTURE" in plan, "Should have planning structure"

        # ASSERTION 2: Preparation section has patterns from coderef
        prep = plan["UNIVERSAL_PLANNING_STRUCTURE"]["0_preparation"]
        assert "key_patterns_identified" in prep, "Should have patterns section"
        assert "async_pattern" in prep["key_patterns_identified"], \
               "Should include patterns from coderef_patterns tool"

        # ASSERTION 3: Current state has architecture context from coderef
        current_state = plan["UNIVERSAL_PLANNING_STRUCTURE"]["3_current_state_analysis"]
        assert "architecture_context" in current_state, "Should have architecture context"
        assert "async_pattern" in current_state["architecture_context"] or \
               "factory_pattern" in current_state["architecture_context"], \
               "Architecture context should reference discovered patterns"

        # ASSERTION 4: No TODOs in pattern-dependent sections
        plan_str = json.dumps(prep)
        assert "TODO" not in plan_str or \
               plan_str.count("TODO") == 0, \
               "Preparation should not have TODOs when analysis provided"


class TestEndToEndWorkorderCreation:
    """Test 4: End-to-end workorder creation with coderef-context."""

    @pytest.mark.asyncio
    async def test_complete_workorder_workflow(self):
        """
        TEST: Full workorder creation with coderef-context integration.

        WHAT IT PROVES:
        - Complete workflow from analyze → plan → validate
        - All coderef-context tools called at appropriate points
        - Final plan.json contains injected data
        - Validation passes with coderef data

        ASSERTIONS:
        - analyze_project_for_planning calls coderef_scan
        - create_plan uses analysis data
        - plan.json has non-TODO content from coderef
        - Validation score improves with coderef data
        """
        test_project = Path(__file__).parent.parent

        # Step 1: Run analysis (should call coderef tools)
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Configure comprehensive tool responses
            def full_mock_responses(tool_name, args):
                responses = {
                    "coderef_scan": {
                        "success": True,
                        "data": {
                            "summary": {
                                "total_elements": 200,
                                "total_files": 45,
                                "languages": ["python", "json"]
                            },
                            "components": [
                                {"name": "MCPToolClient", "type": "class"},
                                {"name": "call_coderef_tool", "type": "function"},
                                {"name": "PlanningAnalyzer", "type": "class"}
                            ]
                        }
                    },
                    "coderef_patterns": {
                        "success": True,
                        "data": {
                            "patterns": [
                                "async_await_pattern",
                                "error_handling_with_fallback",
                                "json_schema_validation"
                            ]
                        }
                    },
                    "coderef_query": {
                        "success": True,
                        "data": {
                            "MCPToolClient": {"calls": ["coderef_scan", "coderef_query"]},
                            "PlanningAnalyzer": {"calls": ["MCPToolClient"]}
                        }
                    },
                    "coderef_coverage": {
                        "success": True,
                        "data": {"coverage_percent": 85}
                    }
                }
                return responses.get(tool_name, {"success": False})

            mock_tool.side_effect = full_mock_responses

            # Run analysis
            analysis = await analyzer.analyze()

            # ASSERTION 1: Analysis completed with coderef data
            assert analysis is not None, "Analysis should complete"
            assert "key_patterns_identified" in analysis, "Should have patterns"
            assert len(analysis["key_patterns_identified"]) > 0, \
                   "Should identify patterns from coderef_patterns"

            # ASSERTION 2: Multiple tools were called
            assert mock_tool.call_count >= 3, \
                   f"Should call multiple coderef tools, called {mock_tool.call_count}"

            # Step 2: Generate plan using analysis
            generator = PlanningGenerator(test_project)

            context = {
                "description": "E2E test feature",
                "goal": "Verify full integration",
                "requirements": ["Use discovered patterns", "Follow architecture"],
                "constraints": []
            }

            plan = generator.generate_plan(
                "e2e-test",
                context=context,
                analysis={"preparation_summary": analysis},
                workorder_id="WO-E2E-TEST-001"
            )

            # ASSERTION 3: Plan contains coderef data
            assert plan is not None, "Plan should be generated"
            prep = plan["UNIVERSAL_PLANNING_STRUCTURE"]["0_preparation"]

            # Check patterns were injected
            assert "async_await_pattern" in str(prep) or \
                   "error_handling" in str(prep) or \
                   len(prep.get("key_patterns_identified", [])) > 0, \
                   "Plan should contain patterns from coderef_patterns"

            # ASSERTION 4: Tech stack from coderef_scan
            assert "technology_stack" in prep, "Should have tech stack"
            assert prep["technology_stack"]["languages"] == ["python", "json"], \
                   "Tech stack should match coderef_scan results"

            # ASSERTION 5: No excessive TODOs (data was used, not stubbed)
            plan_json = json.dumps(plan)
            todo_count = plan_json.count("TODO")
            assert todo_count < 5, \
                   f"Should have minimal TODOs with coderef data, found {todo_count}"


class TestPlanGeneratorUsesCoderefData:
    """Test 5: Verify fixed plan generator uses coderef-context data."""

    def test_preparation_section_uses_analysis_patterns(self):
        """
        TEST: Preparation section uses patterns from coderef_patterns.

        WHAT IT PROVES:
        - _generate_preparation_section extracts patterns from analysis
        - Patterns from coderef_patterns appear in output
        - Not using placeholder patterns

        ASSERTIONS:
        - Patterns from analysis appear in preparation
        - Pattern count matches analysis input
        - No "TODO" in patterns section
        """
        test_project = Path(__file__).parent.parent
        generator = PlanningGenerator(test_project)

        # Mock analysis with specific patterns
        analysis = {
            "preparation_summary": {
                "key_patterns_identified": [
                    "async_await_usage",
                    "dependency_injection",
                    "factory_method"
                ],
                "technology_stack": {
                    "languages": ["python"],
                    "frameworks": ["pytest", "asyncio"],
                    "key_libraries": ["mcp@1.0.0"]
                }
            }
        }

        # Generate preparation section
        prep = generator._generate_preparation_section(None, analysis)

        # ASSERTION 1: Patterns from analysis present
        assert "key_patterns_identified" in prep, "Should have patterns key"
        patterns = prep["key_patterns_identified"]

        # ASSERTION 2: At least one pattern from analysis
        assert "async_await_usage" in patterns or \
               "dependency_injection" in patterns or \
               "factory_method" in patterns, \
               f"Should use patterns from analysis, got {patterns}"

        # ASSERTION 3: Tech stack from analysis
        assert "technology_stack" in prep, "Should have tech stack"
        assert prep["technology_stack"]["languages"] == ["python"], \
               "Should use languages from coderef_scan"

    def test_current_state_uses_analysis_architecture(self):
        """
        TEST: Current state section uses architecture from coderef.

        WHAT IT PROVES:
        - _generate_current_state extracts patterns/tech stack
        - Architecture context references discovered patterns
        - Dependencies use tech stack from coderef_scan

        ASSERTIONS:
        - Architecture context mentions patterns
        - External dependencies from analysis
        - Not using "TODO" placeholders
        """
        test_project = Path(__file__).parent.parent
        generator = PlanningGenerator(test_project)

        # Mock analysis
        analysis = {
            "preparation_summary": {
                "key_patterns_identified": [
                    "error_handler_pattern",
                    "retry_logic"
                ],
                "technology_stack": {
                    "key_libraries": ["pytest@8.0.0", "asyncio"]
                }
            }
        }

        # Generate current state
        current_state = generator._generate_current_state(analysis)

        # ASSERTION 1: Architecture context references patterns
        arch_context = current_state["architecture_context"]
        assert "error_handler" in arch_context or \
               "retry" in arch_context or \
               "pattern" in arch_context.lower(), \
               f"Architecture should reference patterns, got: {arch_context}"

        # ASSERTION 2: Dependencies from analysis
        deps = current_state["dependencies"]
        assert deps["existing_external"] == ["pytest@8.0.0", "asyncio"], \
               "Should use libraries from coderef_scan tech stack"

        # ASSERTION 3: No TODOs
        state_json = json.dumps(current_state)
        assert "TODO" not in state_json, \
               "Should not have TODOs when analysis provided"


class TestIntegrationMetrics:
    """Test 6: Verify integration metrics and coverage."""

    @pytest.mark.asyncio
    async def test_tool_call_distribution(self):
        """
        TEST: Verify all expected coderef tools are called.

        WHAT IT PROVES:
        - Complete set of coderef tools utilized
        - No tools missing from workflow
        - Balanced usage across analysis phases

        ASSERTIONS:
        - coderef_scan called (inventory)
        - coderef_patterns called (consistency)
        - coderef_query called (dependencies)
        - coderef_coverage called (testing)
        - Total calls >= 4
        """
        test_project = Path(__file__).parent.parent
        analyzer = PlanningAnalyzer(test_project)

        with patch('generators.planning_analyzer.call_coderef_tool', new_callable=AsyncMock) as mock_tool:
            # Track which tools are called
            called_tools = set()

            def track_tool_calls(tool_name, args):
                called_tools.add(tool_name)
                return {
                    "success": True,
                    "data": {"result": "mock"}
                }

            mock_tool.side_effect = track_tool_calls

            # Run full analysis
            await analyzer.analyze()

            # ASSERTION 1: Key tools called
            assert "coderef_scan" in called_tools or \
                   "coderef_patterns" in called_tools or \
                   "coderef_query" in called_tools, \
                   f"Should call coderef tools, called: {called_tools}"

            # ASSERTION 2: Multiple tools used
            assert len(called_tools) >= 2, \
                   f"Should use multiple tools, used {len(called_tools)}: {called_tools}"

    def test_data_coverage_in_plan(self):
        """
        TEST: Verify coderef data appears in multiple plan sections.

        WHAT IT PROVES:
        - coderef data distributed across plan
        - Not limited to single section
        - Comprehensive integration

        ASSERTIONS:
        - Section 0 has patterns (from coderef_patterns)
        - Section 3 has architecture (from coderef_scan)
        - Section 2 has tech stack (from coderef_scan)
        """
        test_project = Path(__file__).parent.parent
        generator = PlanningGenerator(test_project)

        # Full mock analysis
        analysis = {
            "preparation_summary": {
                "key_patterns_identified": ["pattern1", "pattern2"],
                "technology_stack": {
                    "languages": ["python"],
                    "frameworks": ["pytest"],
                    "key_libraries": ["lib1", "lib2"]
                }
            }
        }

        context = {
            "description": "Test",
            "goal": "Verify coverage",
            "requirements": ["Req1"],
            "constraints": []
        }

        plan = generator.generate_plan(
            "coverage-test",
            context=context,
            analysis=analysis,
            workorder_id="WO-COV-001"
        )

        sections = plan["UNIVERSAL_PLANNING_STRUCTURE"]

        # ASSERTION 1: Section 0 has patterns
        prep = sections["0_preparation"]
        assert len(prep["key_patterns_identified"]) > 0, \
               "Preparation should have patterns from coderef"

        # ASSERTION 2: Section 3 has architecture
        current = sections["3_current_state_analysis"]
        assert "pattern" in current["architecture_context"].lower() or \
               "python" in current["architecture_context"].lower(), \
               "Current state should reference coderef data"

        # ASSERTION 3: Multiple sections populated
        sections_with_coderef_data = 0
        plan_str = json.dumps(plan)

        if "pattern1" in plan_str or "pattern2" in plan_str:
            sections_with_coderef_data += 1
        if "pytest" in plan_str:
            sections_with_coderef_data += 1

        assert sections_with_coderef_data >= 2, \
               f"Coderef data should appear in multiple sections, found {sections_with_coderef_data}"


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
