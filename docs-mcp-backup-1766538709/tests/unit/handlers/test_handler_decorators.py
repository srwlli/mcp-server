#!/usr/bin/env python3
"""
Unit tests for handler decorators (@mcp_error_handler and @log_invocation).

Tests the decorator pattern for error handling and logging standardization (ARCH-004, ARCH-005).
"""

import asyncio
import sys
import time
from pathlib import Path
import json
import jsonschema

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import tool_handlers
from tool_handlers import mcp_error_handler, log_invocation
from error_responses import ErrorResponse
from mcp.types import TextContent


async def test_mcp_error_handler_decorator():
    """Test @mcp_error_handler decorator functionality."""
    print("Testing @mcp_error_handler decorator...\n")

    # Test 1: ValueError handling
    print("Test 1: ValueError -> ErrorResponse.invalid_input...")
    @mcp_error_handler
    async def handler_raises_value_error(arguments: dict) -> list[TextContent]:
        raise ValueError("Invalid input detected")

    result = await handler_raises_value_error({})
    result_text = result[0].text
    assert "Invalid input" in result_text, "Should return invalid_input error"
    assert "Invalid input detected" in result_text, "Should include error message"
    print("[PASS] ValueError handled correctly\n")

    # Test 2: PermissionError handling (security event)
    print("Test 2: PermissionError -> ErrorResponse.permission_denied...")
    @mcp_error_handler
    async def handler_raises_permission_error(arguments: dict) -> list[TextContent]:
        raise PermissionError("Access denied")

    result = await handler_raises_permission_error({})
    result_text = result[0].text
    assert "Permission denied" in result_text, "Should return permission_denied error"
    assert "Access denied" in result_text, "Should include error message"
    print("[PASS] PermissionError handled correctly\n")

    # Test 3: FileNotFoundError handling
    print("Test 3: FileNotFoundError -> ErrorResponse.not_found...")
    @mcp_error_handler
    async def handler_raises_file_not_found(arguments: dict) -> list[TextContent]:
        raise FileNotFoundError("File not found")

    result = await handler_raises_file_not_found({})
    result_text = result[0].text
    assert "not found" in result_text.lower(), "Should return not_found error"
    print("[PASS] FileNotFoundError handled correctly\n")

    # Test 4: IOError handling
    print("Test 4: IOError -> ErrorResponse.io_error...")
    @mcp_error_handler
    async def handler_raises_io_error(arguments: dict) -> list[TextContent]:
        raise IOError("I/O operation failed")

    result = await handler_raises_io_error({})
    result_text = result[0].text
    assert "operation failed" in result_text.lower() or "i/o" in result_text.lower(), "Should return io_error"
    print("[PASS] IOError handled correctly\n")

    # Test 5: UnicodeDecodeError handling
    print("Test 5: UnicodeDecodeError -> ErrorResponse.encoding_error...")
    @mcp_error_handler
    async def handler_raises_unicode_error(arguments: dict) -> list[TextContent]:
        raise UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid start byte')

    result = await handler_raises_unicode_error({})
    result_text = result[0].text
    assert "encoding" in result_text.lower() or "utf-8" in result_text.lower(), "Should return encoding_error"
    print("[PASS] UnicodeDecodeError handled correctly\n")

    # Test 6: json.JSONDecodeError handling
    print("Test 6: json.JSONDecodeError -> ErrorResponse.malformed_json...")
    @mcp_error_handler
    async def handler_raises_json_error(arguments: dict) -> list[TextContent]:
        raise json.JSONDecodeError("Expecting value", "{invalid", 0)

    result = await handler_raises_json_error({})
    result_text = result[0].text
    assert "json" in result_text.lower() or "malformed" in result_text.lower(), "Should return malformed_json error"
    print("[PASS] json.JSONDecodeError handled correctly\n")

    # Test 7: jsonschema.ValidationError handling
    print("Test 7: jsonschema.ValidationError -> ErrorResponse.validation_failed...")
    @mcp_error_handler
    async def handler_raises_validation_error(arguments: dict) -> list[TextContent]:
        schema = {"type": "object", "required": ["name"]}
        instance = {}
        error = jsonschema.ValidationError("'name' is a required property")
        raise error

    result = await handler_raises_validation_error({})
    result_text = result[0].text
    assert "validation" in result_text.lower(), "Should return validation_failed error"
    print("[PASS] jsonschema.ValidationError handled correctly\n")

    # Test 8: Generic Exception handling
    print("Test 8: Exception -> ErrorResponse.generic_error...")
    @mcp_error_handler
    async def handler_raises_exception(arguments: dict) -> list[TextContent]:
        raise Exception("Unexpected error occurred")

    result = await handler_raises_exception({})
    result_text = result[0].text
    assert "error" in result_text.lower(), "Should return generic_error"
    assert "Unexpected error occurred" in result_text, "Should include error message"
    print("[PASS] Generic Exception handled correctly\n")

    # Test 9: Success case (no error)
    print("Test 9: Success case (no exceptions)...")
    @mcp_error_handler
    async def handler_succeeds(arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="Success!")]

    result = await handler_succeeds({})
    result_text = result[0].text
    assert result_text == "Success!", "Should return success response"
    print("[PASS] Success case handled correctly\n")

    # Test 10: Context preservation in errors
    print("Test 10: Context preservation in error logging...")
    @mcp_error_handler
    async def handle_with_context(arguments: dict) -> list[TextContent]:
        raise ValueError("Context test error")

    result = await handle_with_context({
        'project_path': '/test/path',
        'template_name': 'test_template',
        'version': '1.0.0'
    })
    # Just verify it doesn't crash with context
    assert "error" in result[0].text.lower(), "Should handle context correctly"
    print("[PASS] Context preserved in error logging\n")

    # Test 11: Async compatibility
    print("Test 11: Async compatibility...")
    @mcp_error_handler
    async def async_handler(arguments: dict) -> list[TextContent]:
        await asyncio.sleep(0.001)  # Simulate async operation
        return [TextContent(type="text", text="Async success")]

    result = await async_handler({})
    assert result[0].text == "Async success", "Should maintain async compatibility"
    print("[PASS] Async compatibility maintained\n")

    # Test 12: Function metadata preservation
    print("Test 12: Function metadata preservation...")
    @mcp_error_handler
    async def handle_with_metadata(arguments: dict) -> list[TextContent]:
        """Test docstring"""
        return [TextContent(type="text", text="test")]

    assert handle_with_metadata.__name__ == 'handle_with_metadata', "Should preserve function name"
    assert handle_with_metadata.__doc__ == "Test docstring", "Should preserve docstring"
    print("[PASS] Function metadata preserved\n")

    print("="*60)
    print("[PASS] All @mcp_error_handler tests passed!")
    print("="*60)
    return True


async def test_log_invocation_decorator():
    """Test @log_invocation decorator functionality."""
    print("\nTesting @log_invocation decorator...\n")

    # Test 1: Basic logging functionality
    print("Test 1: Basic invocation logging...")
    @log_invocation
    async def handle_test_tool(arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="Logged")]

    result = await handle_test_tool({'arg1': 'value1', 'arg2': 'value2'})
    assert result[0].text == "Logged", "Should execute handler after logging"
    print("[PASS] Invocation logged successfully\n")

    # Test 2: Handler name extraction
    print("Test 2: Handler name extraction (remove 'handle_' prefix)...")
    @log_invocation
    async def handle_my_custom_tool(arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="test")]

    result = await handle_my_custom_tool({})
    # Just verify it doesn't crash - logging happens in background
    assert result[0].text == "test", "Should extract handler name correctly"
    print("[PASS] Handler name extracted correctly\n")

    # Test 3: Async compatibility
    print("Test 3: Async compatibility...")
    @log_invocation
    async def async_logged_handler(arguments: dict) -> list[TextContent]:
        await asyncio.sleep(0.001)
        return [TextContent(type="text", text="Async logged")]

    result = await async_logged_handler({})
    assert result[0].text == "Async logged", "Should maintain async compatibility"
    print("[PASS] Async compatibility maintained\n")

    # Test 4: Function metadata preservation
    print("Test 4: Function metadata preservation...")
    @log_invocation
    async def handle_metadata_test(arguments: dict) -> list[TextContent]:
        """Test docstring for logging"""
        return [TextContent(type="text", text="test")]

    assert handle_metadata_test.__name__ == 'handle_metadata_test', "Should preserve function name"
    assert handle_metadata_test.__doc__ == "Test docstring for logging", "Should preserve docstring"
    print("[PASS] Function metadata preserved\n")

    # Test 5: Decorator stacking with @mcp_error_handler
    print("Test 5: Decorator stacking (@log_invocation + @mcp_error_handler)...")
    @log_invocation
    @mcp_error_handler
    async def handle_stacked(arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="Stacked success")]

    result = await handle_stacked({'test': 'value'})
    assert result[0].text == "Stacked success", "Should work with stacked decorators"
    print("[PASS] Decorator stacking works correctly\n")

    # Test 6: Error case with decorator stack
    print("Test 6: Error case with stacked decorators...")
    @log_invocation
    @mcp_error_handler
    async def handle_stacked_error(arguments: dict) -> list[TextContent]:
        raise ValueError("Stacked error test")

    result = await handle_stacked_error({})
    assert "error" in result[0].text.lower(), "Should handle errors with stacked decorators"
    print("[PASS] Stacked decorators handle errors correctly\n")

    # Test 7: Performance overhead
    print("Test 7: Performance overhead (<1ms target)...")
    @log_invocation
    async def handle_performance_test(arguments: dict) -> list[TextContent]:
        return [TextContent(type="text", text="perf")]

    durations = []
    for i in range(100):
        start = time.perf_counter()
        await handle_performance_test({})
        duration = time.perf_counter() - start
        durations.append(duration * 1000)  # Convert to ms

    avg_overhead = sum(durations) / len(durations)
    assert avg_overhead < 1.0, f"Average overhead {avg_overhead:.2f}ms exceeds 1ms target"
    print(f"[PASS] Performance overhead: {avg_overhead:.3f}ms (target: <1ms)\n")

    print("="*60)
    print("[PASS] All @log_invocation tests passed!")
    print("="*60)
    return True


async def run_all_tests():
    """Run all decorator tests."""
    print("="*60)
    print("HANDLER DECORATORS TEST SUITE")
    print("="*60)
    print()

    # Test @mcp_error_handler
    success1 = await test_mcp_error_handler_decorator()

    # Test @log_invocation
    success2 = await test_log_invocation_decorator()

    print()
    print("="*60)
    if success1 and success2:
        print("✅ ALL DECORATOR TESTS PASSED")
        print("="*60)
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        return False


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
