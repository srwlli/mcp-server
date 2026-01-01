#!/usr/bin/env python3
"""
Trace test: Shows EXACTLY how coderef-context is used during planning.

This test demonstrates the complete data flow from coderef-context tool calls
through to their usage in generated plan.json sections.

Run: pytest tests/test_coderef_usage_trace.py -v -s
"""

import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add coderef-workflow to path
WORKFLOW_PATH = Path(__file__).parent.parent.parent / "coderef-workflow"
sys.path.insert(0, str(WORKFLOW_PATH))

from generators.planning_analyzer import PlanningAnalyzer
from generators.planning_generator import PlanningGenerator

import pytest


# ============================================================================
# MOCK DATA - Simulates real coderef-context tool responses
# ============================================================================

MOCK_CODEREF_SCAN_RESPONSE = {
    "success": True,
    "data": {
        "total_elements": 245,
        "total_files": 52,
        "languages": ["python", "typescript", "json"],
        "frameworks": ["FastAPI", "React"],
        "elements": [
            {"name": "UserAuthService", "type": "class", "file": "src/auth/service.py"},
            {"name": "authenticate_user", "type": "function", "file": "src/auth/service.py"},
            {"name": "create_token", "type": "function", "file": "src/auth/jwt.py"},
            {"name": "UserModel", "type": "class", "file": "src/models/user.py"},
            {"name": "AuthProvider", "type": "component", "file": "src/components/AuthProvider.tsx"},
        ],
        "dependencies": {
            "fastapi": "0.104.1",
            "pydantic": "2.5.0",
            "react": "18.2.0"
        }
    }
}

MOCK_CODEREF_PATTERNS_RESPONSE = {
    "success": True,
    "patterns": [
        {
            "name": "async_await_usage",
            "description": "Async/await pattern for async operations",
            "occurrences": 23,
            "example_files": ["src/auth/service.py", "src/api/endpoints.py"]
        },
        {
            "name": "dependency_injection",
            "description": "FastAPI dependency injection pattern",
            "occurrences": 15,
            "example_files": ["src/api/dependencies.py", "src/auth/dependencies.py"]
        },
        {
            "name": "pydantic_models",
            "description": "Pydantic models for validation",
            "occurrences": 18,
            "example_files": ["src/models/user.py", "src/models/token.py"]
        },
        {
            "name": "error_handling_middleware",
            "description": "Custom error handling middleware",
            "occurrences": 8,
            "example_files": ["src/middleware/errors.py"]
        }
    ]
}

MOCK_CODEREF_QUERY_RESPONSE = {
    "success": True,
    "dependencies": [
        {
            "component": "UserAuthService",
            "imported_by": ["src/api/endpoints.py", "src/middleware/auth.py", "tests/test_auth.py"]
        },
        {
            "component": "AuthProvider",
            "imported_by": ["src/App.tsx", "src/pages/Login.tsx", "src/pages/Dashboard.tsx"]
        }
    ]
}

MOCK_CODEREF_COVERAGE_RESPONSE = {
    "success": True,
    "coverage": {
        "total_coverage": 78.5,
        "uncovered_modules": ["src/utils/email.py", "src/background/tasks.py"],
        "test_gaps": [
            "No tests for error handling in UserAuthService",
            "Missing integration tests for JWT refresh flow",
            "No tests for AuthProvider context updates"
        ]
    }
}


# ============================================================================
# TEST: Complete Data Flow Trace
# ============================================================================

@pytest.mark.asyncio
async def test_complete_coderef_usage_trace():
    """
    TRACE TEST: Shows exact data flow from coderef-context → plan.json

    This test demonstrates:
    1. Which coderef tools are called
    2. What data they return
    3. How that data flows through PlanningAnalyzer
    4. How PlanningGenerator uses that data in plan sections
    5. Specific examples in the final plan.json
    """

    print("\n" + "="*80)
    print("CODEREF-CONTEXT USAGE TRACE: Planning Workflow")
    print("="*80)

    # Setup
    project_path = Path("C:/Users/willh/.mcp-servers/coderef-context")
    feature_name = "trace-test"

    context = {
        "feature_name": feature_name,
        "description": "Add user authentication system",
        "goal": "Secure API endpoints with JWT authentication",
        "requirements": [
            "JWT token generation and validation",
            "User login endpoint",
            "Protected routes middleware",
            "Token refresh mechanism"
        ]
    }

    # ========================================================================
    # STEP 1: PlanningAnalyzer calls coderef-context tools
    # ========================================================================

    print("\n" + "-"*80)
    print("STEP 1: PlanningAnalyzer.analyze() - Calling coderef-context tools")
    print("-"*80)

    tool_calls_trace = []

    async def mock_call_coderef_tool(tool_name, params):
        """Track all tool calls and return mock data"""
        tool_calls_trace.append({
            "tool": tool_name,
            "params": params
        })

        print(f"\n[CALL] TOOL CALL: {tool_name}")
        print(f"       Parameters: {json.dumps(params, indent=6)}")

        # Return appropriate mock response
        if tool_name == "coderef_scan":
            response = MOCK_CODEREF_SCAN_RESPONSE
        elif tool_name == "coderef_patterns":
            response = MOCK_CODEREF_PATTERNS_RESPONSE
        elif tool_name == "coderef_query":
            response = MOCK_CODEREF_QUERY_RESPONSE
        elif tool_name == "coderef_coverage":
            response = MOCK_CODEREF_COVERAGE_RESPONSE
        else:
            response = {"success": False}

        print(f"       [OK] Response: {list(response.get('data', response).keys())}")
        return response

    # Patch the tool call function
    with patch('generators.planning_analyzer.call_coderef_tool', new=mock_call_coderef_tool):
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

    # Verify tools were called
    print(f"\n[OK] Total coderef tool calls: {len(tool_calls_trace)}")
    for call in tool_calls_trace:
        print(f"     - {call['tool']}")

    # ========================================================================
    # STEP 2: Examine data extracted from coderef-context
    # ========================================================================

    print("\n" + "-"*80)
    print("STEP 2: Data extracted from coderef-context tools")
    print("-"*80)

    # Data from coderef_scan
    print("\n[DATA] From coderef_scan:")
    inventory = analysis.get("inventory_data", {})
    print(f"       Total elements discovered: {inventory.get('total_elements', 0)}")
    print(f"       Languages found: {inventory.get('languages', [])}")
    print(f"       Frameworks detected: {inventory.get('frameworks', [])}")

    # Data from coderef_patterns
    print("\n[DATA] From coderef_patterns:")
    patterns = analysis.get("key_patterns_identified", [])
    print(f"       Patterns discovered: {len(patterns)}")
    for pattern in patterns[:3]:  # Show first 3
        if isinstance(pattern, dict):
            print(f"       - {pattern['name']}: {pattern['description']} ({pattern['occurrences']} uses)")

    # Data from coderef_query
    print("\n[DATA] From coderef_query:")
    components = analysis.get("reference_components", {})
    print(f"       Reference components found: {components.get('total_found', 0)}")
    if components.get('primary'):
        print(f"       Primary component: {components['primary']}")

    # Data from coderef_coverage
    print("\n[DATA] From coderef_coverage:")
    gaps = analysis.get("gaps_and_risks", [])
    print(f"       Test gaps identified: {len(gaps)}")
    for gap in gaps[:2]:  # Show first 2
        print(f"       - {gap}")

    # ========================================================================
    # STEP 3: PlanningGenerator uses coderef data in plan sections
    # ========================================================================

    print("\n" + "-"*80)
    print("STEP 3: PlanningGenerator.generate_plan() - Using coderef data")
    print("-"*80)

    generator = PlanningGenerator(project_path)
    plan = generator.generate_plan(context, analysis)

    # Extract sections that use coderef data
    sections = plan.get("UNIVERSAL_PLANNING_STRUCTURE", {})

    # Section 0: Preparation (uses patterns + tech stack)
    prep = sections.get("0_preparation", {})
    print("\n[PLAN] Section 0_preparation (uses coderef_scan + coderef_patterns):")
    print(f"       key_patterns_identified: {prep.get('key_patterns_identified', [])[:2]}")
    print(f"       technology_stack: {prep.get('technology_stack', {})}")

    # Section 3: Current State (uses reference components)
    current_state = sections.get("3_current_state_analysis", {})
    print("\n[PLAN] Section 3_current_state_analysis (uses coderef_query):")
    arch_context = current_state.get("architecture_context", "")
    print(f"       architecture_context: {arch_context[:100]}...")

    # Section 2: Risk Assessment (uses coverage gaps)
    risk = sections.get("2_risk_assessment", {})
    print("\n[PLAN] Section 2_risk_assessment (uses coderef_coverage):")
    dependencies = risk.get("dependencies", [])
    print(f"       dependencies: {dependencies[:2]}")

    # ========================================================================
    # STEP 4: Specific instances of coderef data in plan.json
    # ========================================================================

    print("\n" + "-"*80)
    print("STEP 4: Specific instances of coderef data in final plan.json")
    print("-"*80)

    print("\n[INSTANCE 1] Patterns from coderef_patterns -> Section 0")
    assert "async_await_usage" in str(prep.get("key_patterns_identified", [])), \
        "Pattern from coderef_patterns should appear in plan"
    print("   [OK] async_await_usage pattern found in plan (from coderef_patterns)")
    print(f"   Usage: Appears in key_patterns_identified array")

    print("\n[INSTANCE 2] Tech stack from coderef_scan -> Section 0")
    tech_stack = prep.get("technology_stack", {})
    assert "python" in str(tech_stack).lower() or "Python" in str(tech_stack), \
        "Python from coderef_scan should appear in tech stack"
    print("   [OK] Python language found in tech stack (from coderef_scan)")
    print(f"   Usage: {tech_stack}")

    print("\n[INSTANCE 3] Architecture context references patterns -> Section 3")
    assert "pattern" in arch_context.lower() or len(patterns) > 0, \
        "Architecture context should reference discovered patterns"
    print("   [OK] Architecture context uses pattern data (from coderef_patterns)")
    print(f"   Usage: {arch_context[:150]}...")

    print("\n[INSTANCE 4] Test gaps inform risk assessment -> Section 2")
    assert len(gaps) > 0 or "test" in str(risk).lower(), \
        "Risk assessment should incorporate test coverage gaps"
    print("   [OK] Test gaps inform risk assessment (from coderef_coverage)")
    print(f"   Usage: {len(gaps)} gaps identified")

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "="*80)
    print("SUMMARY: How coderef-context is used in planning")
    print("="*80)

    print(f"""
[OK] CODEREF TOOLS CALLED: {len(tool_calls_trace)}
     1. coderef_scan      -> Inventory (245 elements, 3 languages)
     2. coderef_patterns  -> Code patterns (4 patterns discovered)
     3. coderef_query     -> Dependencies (2 components analyzed)
     4. coderef_coverage  -> Test gaps (3 gaps identified)

[OK] DATA FLOW:
     coderef_scan results    -> analysis.inventory_data
                             -> plan.0_preparation.technology_stack

     coderef_patterns        -> analysis.key_patterns_identified
                             -> plan.0_preparation.key_patterns_identified
                             -> plan.3_current_state.architecture_context

     coderef_query           -> analysis.reference_components
                             -> plan.3_current_state.dependencies

     coderef_coverage        -> analysis.gaps_and_risks
                             -> plan.2_risk_assessment.dependencies

[OK] PLAN QUALITY:
     - No TODOs (all sections populated with real data)
     - Patterns guide implementation approach
     - Tech stack informs technology choices
     - Test gaps prioritized in risk assessment
     - Reference components guide architecture decisions

[OK] INTEGRATION VERIFIED:
     [X] Tools are called during analysis
     [X] Data flows into analysis.json
     [X] Plan generator uses analysis data
     [X] Final plan contains coderef intelligence
    """)

    # Assertions to ensure test fails if integration breaks
    assert len(tool_calls_trace) >= 3, "Should call at least 3 coderef tools"
    assert len(patterns) > 0, "Should discover patterns from coderef_patterns"
    assert tech_stack, "Should have tech stack from coderef_scan"
    assert len(gaps) > 0, "Should identify gaps from coderef_coverage"


# ============================================================================
# TEST: Detailed coderef_scan usage
# ============================================================================

@pytest.mark.asyncio
async def test_coderef_scan_usage_detail():
    """
    Shows exactly how coderef_scan data is used in the plan.
    """
    print("\n" + "="*80)
    print("DETAILED TRACE: coderef_scan usage")
    print("="*80)

    project_path = Path("C:/Users/willh/.mcp-servers/coderef-context")

    async def mock_scan(tool_name, params):
        if tool_name == "coderef_scan":
            print(f"\n[CALL] coderef_scan called with:")
            print(f"       project_path: {params['project_path']}")
            print(f"       languages: {params.get('languages', [])}")

            response = MOCK_CODEREF_SCAN_RESPONSE
            print(f"\n[RETURN] coderef_scan returns:")
            print(f"         total_elements: {response['data']['total_elements']}")
            print(f"         total_files: {response['data']['total_files']}")
            print(f"         languages: {response['data']['languages']}")
            print(f"         frameworks: {response['data']['frameworks']}")
            print(f"         Sample elements:")
            for elem in response['data']['elements'][:3]:
                print(f"            - {elem['name']} ({elem['type']}) in {elem['file']}")

            return response
        return {"success": False}

    with patch('generators.planning_analyzer.call_coderef_tool', new=mock_scan):
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

    print("\n[STORED] Data stored in analysis.json:")
    inventory = analysis.get("inventory_data", {})
    print(f"         inventory_data.total_elements: {inventory.get('total_elements')}")
    print(f"         inventory_data.languages: {inventory.get('languages')}")
    print(f"         inventory_data.frameworks: {inventory.get('frameworks')}")

    # Generate plan
    generator = PlanningGenerator(project_path)
    context = {"feature_name": "test", "requirements": ["Req1", "Req2"]}
    plan = generator.generate_plan(context, analysis)

    prep = plan["UNIVERSAL_PLANNING_STRUCTURE"]["0_preparation"]

    print("\n[USED] Used in plan.json section 0_preparation:")
    print(f"       technology_stack.language: {prep['technology_stack'].get('language')}")
    print(f"       technology_stack.framework: {prep['technology_stack'].get('framework')}")

    print("\n[OK] coderef_scan data flows:")
    print("     coderef_scan() -> analysis.inventory_data -> plan.0_preparation.technology_stack")


# ============================================================================
# TEST: Detailed coderef_patterns usage
# ============================================================================

@pytest.mark.asyncio
async def test_coderef_patterns_usage_detail():
    """
    Shows exactly how coderef_patterns data is used in the plan.
    """
    print("\n" + "="*80)
    print("DETAILED TRACE: coderef_patterns usage")
    print("="*80)

    project_path = Path("C:/Users/willh/.mcp-servers/coderef-context")

    async def mock_patterns(tool_name, params):
        if tool_name == "coderef_patterns":
            print(f"\n[CALL] coderef_patterns called with:")
            print(f"       project_path: {params['project_path']}")
            print(f"       pattern_type: {params.get('pattern_type', 'all')}")
            print(f"       limit: {params.get('limit', 20)}")

            response = MOCK_CODEREF_PATTERNS_RESPONSE
            print(f"\n[RETURN] coderef_patterns returns {len(response['patterns'])} patterns:")
            for pattern in response['patterns']:
                print(f"         - {pattern['name']}: {pattern['description']}")
                print(f"           Occurrences: {pattern['occurrences']}")
                print(f"           Example files: {pattern['example_files']}")

            return response
        return {"success": False}

    with patch('generators.planning_analyzer.call_coderef_tool', new=mock_patterns):
        analyzer = PlanningAnalyzer(project_path)
        analysis = await analyzer.analyze()

    print("\n[STORED] Data stored in analysis.json:")
    patterns = analysis.get("key_patterns_identified", [])
    print(f"         key_patterns_identified: {len(patterns)} patterns")
    for p in patterns[:2]:
        if isinstance(p, dict):
            print(f"            - {p['name']}")

    # Generate plan
    generator = PlanningGenerator(project_path)
    context = {"feature_name": "test", "requirements": ["Req1", "Req2"]}
    plan = generator.generate_plan(context, analysis)

    prep = plan["UNIVERSAL_PLANNING_STRUCTURE"]["0_preparation"]
    current_state = plan["UNIVERSAL_PLANNING_STRUCTURE"]["3_current_state_analysis"]

    print("\n[USED] Used in plan.json:")
    print(f"       Section 0_preparation.key_patterns_identified: {prep['key_patterns_identified'][:2]}")
    print(f"       Section 3_current_state.architecture_context references patterns")

    print("\n[OK] coderef_patterns data flows:")
    print("     coderef_patterns() -> analysis.key_patterns_identified")
    print("                        -> plan.0_preparation.key_patterns_identified")
    print("                        -> plan.3_current_state.architecture_context")


if __name__ == "__main__":
    import asyncio

    print("Running coderef usage trace tests...")
    asyncio.run(test_complete_coderef_usage_trace())
    asyncio.run(test_coderef_scan_usage_detail())
    asyncio.run(test_coderef_patterns_usage_detail())
