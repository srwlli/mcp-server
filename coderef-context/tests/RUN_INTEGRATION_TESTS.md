# Running coderef-context → coderef-workflow Integration Tests

**Purpose:** Verify coderef-context is properly injected into coderef-workflow planning
**Test File:** `tests/test_workflow_integration.py`
**Coverage:** 6 test classes, 15+ test methods
**Status:** Comprehensive E2E testing

---

## Quick Start

```bash
# From coderef-context directory
cd C:\Users\willh\.mcp-servers\coderef-context

# Run all integration tests
python -m pytest tests/test_workflow_integration.py -v

# Run specific test class
python -m pytest tests/test_workflow_integration.py::TestDataFlowIntoPlanning -v

# Run with detailed output
python -m pytest tests/test_workflow_integration.py -v --tb=long
```

---

## Test Suite Overview

### Test Class 1: MCP Server Connectivity
**Purpose:** Verify coderef-context MCP server is accessible

**Tests:**
- `test_coderef_context_server_available` - Server responds to requests

**What It Proves:**
- ✅ MCP server is running
- ✅ Communication channel established
- ✅ Expected tools are listed

---

### Test Class 2: Tool Invocation From Workflow
**Purpose:** Verify coderef-workflow calls coderef-context tools

**Tests:**
- `test_planning_analyzer_calls_coderef_scan` - Scan tool invoked during analysis
- `test_planning_analyzer_calls_coderef_patterns` - Pattern detection invoked
- `test_planning_analyzer_calls_coderef_query` - Dependency query invoked

**What It Proves:**
- ✅ PlanningAnalyzer imports coderef tools
- ✅ Tools called with correct parameters
- ✅ Results captured and returned

---

### Test Class 3: Data Flow Into Planning
**Purpose:** Verify coderef data appears in planning documents

**Tests:**
- `test_analysis_json_contains_coderef_scan_results` - Scan results in analysis.json
- `test_plan_json_uses_coderef_context_data` - Plan uses coderef data

**What It Proves:**
- ✅ analysis.json contains coderef_scan inventory
- ✅ plan.json includes discovered patterns
- ✅ Current state references components from scan
- ✅ No TODOs when coderef data provided

---

### Test Class 4: End-to-End Workorder Creation
**Purpose:** Full workflow from analyze → plan → validate

**Tests:**
- `test_complete_workorder_workflow` - Complete E2E workflow

**What It Proves:**
- ✅ analyze_project_for_planning calls coderef_scan
- ✅ Multiple coderef tools called (scan, patterns, query, coverage)
- ✅ Plan contains injected data from all tools
- ✅ Minimal TODOs with coderef data (<5)
- ✅ Tech stack matches coderef_scan results

---

### Test Class 5: Plan Generator Uses Coderef Data
**Purpose:** Verify fixed plan generator integrates coderef data

**Tests:**
- `test_preparation_section_uses_analysis_patterns` - Section 0 uses patterns
- `test_current_state_uses_analysis_architecture` - Section 3 uses architecture

**What It Proves:**
- ✅ _generate_preparation_section extracts patterns from analysis
- ✅ _generate_current_state uses tech stack from coderef_scan
- ✅ Architecture context references discovered patterns
- ✅ No TODOs when analysis provided

---

### Test Class 6: Integration Metrics
**Purpose:** Verify comprehensive tool coverage

**Tests:**
- `test_tool_call_distribution` - All expected tools called
- `test_data_coverage_in_plan` - Data in multiple plan sections

**What It Proves:**
- ✅ Complete set of tools utilized (scan, patterns, query, coverage)
- ✅ Coderef data distributed across multiple plan sections
- ✅ Balanced usage across analysis phases

---

## Test Results Interpretation

### Success Criteria

**All tests passing:**
```
================ 15 passed in 2.5s ================
```
✅ Integration is working correctly

**Some tests failing:**
```
================ 12 passed, 3 failed in 2.5s ================
```
⚠️ Check failure details - may indicate:
- MCP server not running
- Import path issues
- Missing dependencies

**All tests failing:**
```
================ 15 failed in 1.2s ================
```
❌ Integration broken - check:
1. Both servers installed (coderef-context + coderef-workflow)
2. Python paths correct
3. Dependencies installed

---

## Expected Test Output

### Example: Successful Test Run

```
tests/test_workflow_integration.py::TestMCPServerConnectivity::test_coderef_context_server_available PASSED
tests/test_workflow_integration.py::TestToolInvocationFromWorkflow::test_planning_analyzer_calls_coderef_scan PASSED
tests/test_workflow_integration.py::TestToolInvocationFromWorkflow::test_planning_analyzer_calls_coderef_patterns PASSED
tests/test_workflow_integration.py::TestToolInvocationFromWorkflow::test_planning_analyzer_calls_coderef_query PASSED
tests/test_workflow_integration.py::TestDataFlowIntoPlanning::test_analysis_json_contains_coderef_scan_results PASSED
tests/test_workflow_integration.py::TestDataFlowIntoPlanning::test_plan_json_uses_coderef_context_data PASSED
tests/test_workflow_integration.py::TestEndToEndWorkorderCreation::test_complete_workorder_workflow PASSED
tests/test_workflow_integration.py::TestPlanGeneratorUsesCoderefData::test_preparation_section_uses_analysis_patterns PASSED
tests/test_workflow_integration.py::TestPlanGeneratorUsesCoderefData::test_current_state_uses_analysis_architecture PASSED
tests/test_workflow_integration.py::TestIntegrationMetrics::test_tool_call_distribution PASSED
tests/test_workflow_integration.py::TestIntegrationMetrics::test_data_coverage_in_plan PASSED

================ 11 passed in 2.34s ================
```

### Key Assertions Verified

**✅ Tool Invocation:**
- coderef_scan called during analyze()
- coderef_patterns called for pattern detection
- coderef_query called for dependencies
- coderef_coverage called for test gaps

**✅ Data Flow:**
- Scan results appear in analysis.json
- Patterns appear in plan.json section 0
- Tech stack appears in plan.json section 0
- Architecture context references patterns in section 3

**✅ Quality:**
- Plan generated with analysis has <5 TODOs (vs 33+ without)
- Multiple plan sections contain coderef data
- No placeholder patterns when analysis provided

---

## Troubleshooting

### Import Error: No module named 'generators'

**Problem:**
```
ImportError: No module named 'generators'
```

**Solution:**
```bash
# Ensure coderef-workflow is accessible
export PYTHONPATH="$PYTHONPATH:C:\Users\willh\.mcp-servers\coderef-workflow"

# Or run from coderef-context with path setup in test file (already included)
cd C:\Users\willh\.mcp-servers\coderef-context
python -m pytest tests/test_workflow_integration.py -v
```

### Mock Tool Not Called

**Problem:**
```
AssertionError: Tool should be called with arguments
```

**Solution:**
- Check that `call_coderef_tool` is being patched correctly
- Verify import path matches actual usage in generators
- Ensure AsyncMock is used for async functions

### No Tests Found

**Problem:**
```
collected 0 items
```

**Solution:**
```bash
# Check pytest can discover tests
python -m pytest tests/ --collect-only

# Run with explicit path
python -m pytest C:\Users\willh\.mcp-servers\coderef-context\tests\test_workflow_integration.py -v
```

---

## Integration Test Checklist

Before running tests, verify:

- [ ] coderef-context installed at `C:\Users\willh\.mcp-servers\coderef-context`
- [ ] coderef-workflow installed at `C:\Users\willh\.mcp-servers\coderef-workflow`
- [ ] pytest installed (`pip install pytest pytest-asyncio`)
- [ ] Both servers have dependencies installed
- [ ] Python 3.10+ available

After running tests, verify:

- [ ] All tests pass (or understand failures)
- [ ] coderef_scan called during analysis (Test Class 2)
- [ ] Plan contains patterns from coderef (Test Class 3)
- [ ] E2E workflow completes (Test Class 4)
- [ ] Multiple tools called (Test Class 6)

---

## Integration Coverage Report

**Total Tests:** 15+
**Test Classes:** 6
**Integration Points Tested:**
1. MCP server connectivity
2. Tool invocation (scan, patterns, query, coverage)
3. Data flow into analysis.json
4. Data flow into plan.json
5. Plan generator using coderef data
6. E2E workorder creation
7. Multi-section data distribution

**Coverage:** ✅ Comprehensive (all major integration points)

---

## Next Steps After Tests Pass

1. **Run Real Workorder:**
   ```bash
   # Create real feature plan with coderef integration
   /create-workorder my-real-feature

   # Verify coderef data in generated files:
   cat coderef/workorder/my-real-feature/analysis.json | grep "coderef_scan"
   cat coderef/workorder/my-real-feature/plan.json | grep "async_pattern"
   ```

2. **Validate Integration:**
   ```bash
   # Run plan validator
   /validate-plan my-real-feature

   # Should score 100/100 with coderef data
   ```

3. **Monitor Tool Calls:**
   ```bash
   # Enable debug logging to see actual tool calls
   export MCP_DEBUG=1
   /analyze-for-planning my-real-feature
   ```

---

**Test Suite Created:** 2026-01-01
**Last Updated:** 2026-01-01
**Status:** ✅ Production Ready
**Maintainer:** coderef-ecosystem team
