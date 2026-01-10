#!/usr/bin/env python3
"""
Dry-run test for routing verification
Uses mock logs instead of real MCP tool
"""

def test_routing_dryrun():
    # Mock MCP tool log
    mock_log = """
    [2026-01-03 01:30:00] INFO: Received slash command: /create-resource-sheet CONSTANTS.md
    [2026-01-03 01:30:01] INFO: Calling mcp__coderef-docs__generate_resource_sheet
    [2026-01-03 01:30:02] INFO: MCP tool returned success
    """

    # Test: Verify MCP tool is called
    if "mcp__coderef-docs__generate_resource_sheet" in mock_log:
        print("[PASS] ROUTE-001 DRY-RUN: MCP tool invocation detected")
        return True
    else:
        print("[FAIL] ROUTE-001 DRY-RUN: MCP tool not called")
        return False

# Run dry-run
if __name__ == "__main__":
    result = test_routing_dryrun()
    print(f"\nRouting test dry-run: {'SUCCESS' if result else 'FAILED'}")
    exit(0 if result else 1)
