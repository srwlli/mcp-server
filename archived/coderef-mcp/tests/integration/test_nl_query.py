"""Integration tests for Natural Language Query (Phase 3).

Tests the NL query parsing and handling:
- parse_query_intent() function with 7+ query types
- handle_nl_query() handler with routing and NL summaries
- Context-aware parsing and disambiguation
- >90% parsing accuracy target
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tool_handlers import parse_query_intent, handle_nl_query


def test_parse_callers_intent():
    """Test parsing queries for finding callers."""
    print("\n=== Testing: Callers Intent ===" )

    test_cases = [
        "what calls login?",
        "who calls authenticate",
        "find callers of processPayment",
        "show callers of validateUser",
        "what uses sendEmail?",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "callers", f"Failed to parse '{query}' as callers"
        assert parsed["confidence"] >= 0.9, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> callers (confidence: {parsed['confidence']})")

    return True


def test_parse_callees_intent():
    """Test parsing queries for finding callees."""
    print("\n=== Testing: Callees Intent ===")

    test_cases = [
        "what does login call?",
        "what functions does authenticate use?",
        "find callees of processPayment",
        "what is called by validateUser",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "callees", f"Failed to parse '{query}' as callees"
        assert parsed["confidence"] >= 0.9, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> callees (confidence: {parsed['confidence']})")

    return True


def test_parse_coverage_intent():
    """Test parsing queries for finding test coverage."""
    print("\n=== Testing: Coverage Intent ===")

    test_cases = [
        "find tests for login",
        "test coverage for authenticate",
        "is processPayment tested?",
        "does validateUser have tests",
        "show tests for sendEmail",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "coverage", f"Failed to parse '{query}' as coverage"
        assert parsed["confidence"] >= 0.85, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> coverage (confidence: {parsed['confidence']})")

    return True


def test_parse_impact_intent():
    """Test parsing queries for impact analysis."""
    print("\n=== Testing: Impact Intent ===")

    test_cases = [
        "impact of login",
        "what breaks if authenticate changes?",
        "analyze impact of processPayment",
        "what depends on validateUser?",
        "show impact for sendEmail",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "impact", f"Failed to parse '{query}' as impact"
        assert parsed["confidence"] >= 0.85, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> impact (confidence: {parsed['confidence']})")

    return True


def test_parse_dependencies_intent():
    """Test parsing queries for dependencies."""
    print("\n=== Testing: Dependencies Intent ===")

    test_cases = [
        "dependencies of login",
        "what does authenticate depend on?",
        "show dependencies for processPayment",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "dependencies", f"Failed to parse '{query}' as dependencies"
        assert parsed["confidence"] >= 0.85, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> dependencies (confidence: {parsed['confidence']})")

    return True


def test_parse_search_intent():
    """Test parsing queries for search."""
    print("\n=== Testing: Search Intent ===")

    test_cases = [
        ("find all login", "login", None),
        ("search for authenticate in auth module", "authenticate", "auth module"),
        ("list all tests in payment", "tests", "payment"),
        ("show all functions", "functions", None),
    ]

    for query, expected_elem, expected_scope in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "search", f"Failed to parse '{query}' as search"
        assert parsed["confidence"] >= 0.75, f"Low confidence for '{query}'"
        assert expected_elem in parsed["element"], f"Element mismatch for '{query}'"
        if expected_scope:
            assert parsed["parameters"].get("scope") == expected_scope, f"Scope mismatch for '{query}'"
        print(f"[PASS] Parsed '{query}' -> search (element: {parsed['element']})")

    return True


def test_parse_analysis_intent():
    """Test parsing queries for analysis."""
    print("\n=== Testing: Analysis Intent ===")

    test_cases = [
        "analyze login",
        "show authenticate",
        "tell me about processPayment",
        "describe validateUser",
        "explain sendEmail",
    ]

    for query in test_cases:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "analysis", f"Failed to parse '{query}' as analysis"
        assert parsed["confidence"] >= 0.7, f"Low confidence for '{query}'"
        print(f"[PASS] Parsed '{query}' -> analysis (confidence: {parsed['confidence']})")

    return True


def test_parse_with_context():
    """Test context-aware parsing."""
    print("\n=== Testing: Context-Aware Parsing ===")

    context = {
        "current_file": "src/auth/login.ts",
        "current_element": "@Fn/auth/login#authenticate:42",
        "language": "ts"
    }

    # Test 1: Basic parsing with context
    parsed1 = parse_query_intent("what calls validateUser", context)
    assert parsed1["intent"] == "callers"
    assert "context" in parsed1["parameters"]
    print(f"[PASS] Context passed through for 'what calls validateUser'")

    # Test 2: Context storage
    parsed2 = parse_query_intent("find tests for login", context)
    assert parsed2["parameters"]["context"] == context
    print(f"[PASS] Context stored in parameters")

    return True


def test_element_extraction():
    """Test element name extraction accuracy."""
    print("\n=== Testing: Element Extraction ===")

    test_cases = [
        ("what calls the login function?", "login"),
        ("who uses authenticate?", "authenticate"),
        ("find tests for processPayment", "processpayment"),  # lowercase due to query_lower
        ("impact of validateUser", "validateuser"),  # lowercase due to query_lower
    ]

    for query, expected_contains in test_cases:
        parsed = parse_query_intent(query)
        # Element should contain the expected text (case-insensitive after cleanup)
        element_lower = parsed["element"].lower()
        expected_lower = expected_contains.lower().rstrip("?.,!")
        assert expected_lower in element_lower or element_lower in expected_lower, \
               f"Element extraction failed for '{query}': got '{parsed['element']}', expected to contain '{expected_contains}'"
        print(f"[PASS] Extracted element from '{query}' -> '{parsed['element']}'")

    return True


def test_unknown_intent():
    """Test handling of unparseable queries."""
    print("\n=== Testing: Unknown Intent Handling ===")

    unparseable_queries = [
        "asdfghjkl",
        "random words without structure",
        "123 456 789",
    ]

    for query in unparseable_queries:
        parsed = parse_query_intent(query)
        assert parsed["intent"] == "unknown", f"Should return unknown for '{query}'"
        assert parsed["confidence"] < 0.5, f"Confidence should be low for unknown: '{query}'"
        print(f"[PASS] Correctly identified '{query}' as unknown (confidence: {parsed['confidence']})")

    return True


async def test_nl_query_handler_basic():
    """Test basic NL query handler functionality."""
    print("\n=== Testing: NL Query Handler (Basic) ===")

    # Test with a valid query
    result = await handle_nl_query({
        "query": "what calls login",
        "format": "structured"
    })

    assert result["status"] in ["success", "low_confidence"], "Should return valid status"
    assert "query" in result, "Should include original query"
    print(f"[PASS] Handler returned status: {result['status']}")

    return True


async def test_nl_query_handler_low_confidence():
    """Test NL query handler with low confidence query."""
    print("\n=== Testing: NL Query Handler (Low Confidence) ===")

    # Test with unparseable query
    result = await handle_nl_query({
        "query": "asdfghjkl random words",
        "format": "structured"
    })

    assert result["status"] == "low_confidence", "Should return low_confidence for unparseable query"
    assert "suggestion" in result, "Should include suggestion for rephrasing"
    print(f"[PASS] Handler correctly identified low confidence query")

    return True


async def test_nl_query_formats():
    """Test different response formats."""
    print("\n=== Testing: NL Query Response Formats ===")

    query = "analyze login"

    # Test natural format
    result_natural = await handle_nl_query({"query": query, "format": "natural"})
    if result_natural["status"] == "success":
        assert "summary" in result_natural, "Natural format should include summary"
        print(f"[PASS] Natural format includes summary")

    # Test structured format
    result_structured = await handle_nl_query({"query": query, "format": "structured"})
    if result_structured["status"] == "success":
        assert "intent" in result_structured, "Structured format should include intent"
        assert "element" in result_structured, "Structured format should include element"
        print(f"[PASS] Structured format includes intent and element")

    # Test JSON format
    result_json = await handle_nl_query({"query": query, "format": "json"})
    if result_json["status"] == "success":
        assert "parsed_intent" in result_json, "JSON format should include parsed_intent"
        assert "result" in result_json, "JSON format should include raw result"
        print(f"[PASS] JSON format includes parsed_intent and result")

    return True


def test_parsing_accuracy():
    """Calculate overall parsing accuracy."""
    print("\n=== Testing: Overall Parsing Accuracy ===")

    # Comprehensive test set across all intents
    test_queries = [
        ("what calls login", "callers"),
        ("who uses authenticate", "callers"),
        ("what does login call", "callees"),
        ("find tests for login", "coverage"),
        ("is authenticate tested", "coverage"),
        ("impact of login", "impact"),
        ("what breaks if login changes", "impact"),
        ("dependencies of authenticate", "dependencies"),
        ("find all login", "search"),
        ("analyze login", "analysis"),
        ("show authenticate", "analysis"),
        ("what calls processPayment", "callers"),
        ("test coverage for validateUser", "coverage"),
        ("what depends on sendEmail", "impact"),
        ("search for helper in utils", "search"),
    ]

    correct = 0
    total = len(test_queries)

    for query, expected_intent in test_queries:
        parsed = parse_query_intent(query)
        if parsed["intent"] == expected_intent and parsed["confidence"] >= 0.5:
            correct += 1
        else:
            print(f"[MISS] '{query}' -> got {parsed['intent']} (expected {expected_intent})")

    accuracy = (correct / total) * 100
    print(f"\n[ACCURACY] {correct}/{total} correct = {accuracy:.1f}%")

    assert accuracy >= 90.0, f"Parsing accuracy {accuracy:.1f}% is below 90% target"
    print(f"[PASS] Parsing accuracy {accuracy:.1f}% meets >90% target")

    return True


async def run_all_tests():
    """Run all NL query tests."""
    print("=" * 60)
    print("NL QUERY INTEGRATION TESTS (PHASE 3)")
    print("=" * 60)

    try:
        # Synchronous parsing tests
        test_parse_callers_intent()
        test_parse_callees_intent()
        test_parse_coverage_intent()
        test_parse_impact_intent()
        test_parse_dependencies_intent()
        test_parse_search_intent()
        test_parse_analysis_intent()
        test_parse_with_context()
        test_element_extraction()
        test_unknown_intent()

        # Async handler tests
        await test_nl_query_handler_basic()
        await test_nl_query_handler_low_confidence()
        await test_nl_query_formats()

        # Accuracy test
        test_parsing_accuracy()

        print("\n" + "=" * 60)
        print("[PASS] ALL TESTS PASSED - Phase 3 Complete")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
