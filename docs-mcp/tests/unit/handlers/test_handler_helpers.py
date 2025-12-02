#!/usr/bin/env python3
"""
Unit tests for handler helper functions (format_success_response).

Tests the helper pattern for consistent response formatting (QUA-004).
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tool_handlers import format_success_response
from mcp.types import TextContent


def test_format_success_response():
    """Test format_success_response helper function."""
    print("Testing format_success_response helper...\n")

    # Test 1: Basic data formatting (no message)
    print("Test 1: Basic data formatting without message...")
    data = {'status': 'success', 'count': 42}
    result = format_success_response(data)

    assert isinstance(result, list), "Should return a list"
    assert len(result) == 1, "Should return single TextContent"
    assert isinstance(result[0], TextContent), "Should contain TextContent"
    assert result[0].type == "text", "Should be text type"

    # Parse the JSON to verify structure
    result_json = json.loads(result[0].text)
    assert result_json['status'] == 'success', "Should preserve data"
    assert result_json['count'] == 42, "Should preserve data values"
    print("[PASS] Basic data formatting works\n")

    # Test 2: Data formatting with message
    print("Test 2: Data formatting with success message...")
    data = {'files': ['file1.txt', 'file2.txt'], 'total': 2}
    message = "✅ Files retrieved successfully"
    result = format_success_response(data, message)

    result_text = result[0].text
    assert message in result_text, "Should include success message"
    assert '"files"' in result_text, "Should include data as JSON"
    assert '"total"' in result_text, "Should include all data fields"

    # Verify message comes before JSON
    message_index = result_text.index(message)
    files_index = result_text.index('"files"')
    assert message_index < files_index, "Message should come before JSON data"
    print("[PASS] Message + data formatting works\n")

    # Test 3: Empty data dictionary
    print("Test 3: Empty data dictionary...")
    data = {}
    result = format_success_response(data)

    result_json = json.loads(result[0].text)
    assert result_json == {}, "Should handle empty dict"
    print("[PASS] Empty data handled correctly\n")

    # Test 4: Nested data structures
    print("Test 4: Nested data structures...")
    data = {
        'metrics': {
            'total_files': 100,
            'by_type': {
                'python': 50,
                'javascript': 30,
                'other': 20
            }
        },
        'success': True
    }
    result = format_success_response(data)

    result_json = json.loads(result[0].text)
    assert result_json['metrics']['total_files'] == 100, "Should preserve nested data"
    assert result_json['metrics']['by_type']['python'] == 50, "Should preserve deeply nested data"
    print("[PASS] Nested structures handled correctly\n")

    # Test 5: Arrays in data
    print("Test 5: Arrays in data...")
    data = {
        'files': ['a.txt', 'b.txt', 'c.txt'],
        'errors': []
    }
    result = format_success_response(data)

    result_json = json.loads(result[0].text)
    assert len(result_json['files']) == 3, "Should preserve array length"
    assert result_json['files'][0] == 'a.txt', "Should preserve array elements"
    assert result_json['errors'] == [], "Should handle empty arrays"
    print("[PASS] Arrays handled correctly\n")

    # Test 6: JSON formatting (indentation)
    print("Test 6: JSON formatting with indentation...")
    data = {'key1': 'value1', 'key2': 'value2'}
    result = format_success_response(data)

    result_text = result[0].text
    # Should have indentation (2 spaces)
    assert '  "key1"' in result_text or '  "key2"' in result_text, "Should have indented JSON"
    print("[PASS] JSON indentation preserved\n")

    # Test 7: Special characters in data
    print("Test 7: Special characters in data...")
    data = {
        'path': 'C:\\Users\\test\\file.txt',
        'message': 'Line 1\nLine 2',
        'quote': 'He said "hello"'
    }
    result = format_success_response(data)

    result_json = json.loads(result[0].text)
    assert result_json['path'] == 'C:\\Users\\test\\file.txt', "Should escape backslashes"
    assert result_json['message'] == 'Line 1\nLine 2', "Should preserve newlines"
    assert result_json['quote'] == 'He said "hello"', "Should escape quotes"
    print("[PASS] Special characters handled correctly\n")

    # Test 8: Multiple message formats
    print("Test 8: Different message formats...")
    messages = [
        "✅ Success",
        "⚠️ Warning: partial results",
        "📊 Analysis complete",
        "Simple message"
    ]

    for msg in messages:
        result = format_success_response({'test': 'data'}, msg)
        assert msg in result[0].text, f"Should include message: {msg}"

    print("[PASS] Various message formats work\n")

    # Test 9: Return type validation
    print("Test 9: Return type validation...")
    result = format_success_response({'test': 'data'})

    # Validate return type matches MCP handler signature
    assert isinstance(result, list), "Must return list"
    assert all(isinstance(item, TextContent) for item in result), "Must contain TextContent"
    assert all(item.type == "text" for item in result), "Must be text type"
    print("[PASS] Return type validated\n")

    # Test 10: Large data structures
    print("Test 10: Large data structures...")
    data = {
        'items': [{'id': i, 'name': f'item_{i}'} for i in range(100)]
    }
    result = format_success_response(data)

    result_json = json.loads(result[0].text)
    assert len(result_json['items']) == 100, "Should handle large datasets"
    assert result_json['items'][0]['id'] == 0, "Should preserve data integrity"
    assert result_json['items'][99]['id'] == 99, "Should preserve all elements"
    print("[PASS] Large data structures handled\n")

    print("="*60)
    print("[PASS] All format_success_response tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = test_format_success_response()
    sys.exit(0 if success else 1)
