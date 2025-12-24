#!/bin/bash
# Pre-commit hook for docs-mcp check_consistency tool
#
# Installation:
#   1. Copy this file to .git/hooks/pre-commit
#   2. Make executable: chmod +x .git/hooks/pre-commit
#   3. Ensure docs-mcp server is installed and configured
#
# This hook will:
#   - Auto-detect staged files via git
#   - Run consistency checks against established standards
#   - Block commits if violations found (configurable severity)
#   - Provide actionable feedback

set -e  # Exit on any error

# Configuration
PROJECT_ROOT=$(git rev-parse --show-toplevel)
SEVERITY_THRESHOLD="${CHECK_CONSISTENCY_SEVERITY:-major}"  # critical|major|minor
FAIL_ON_VIOLATIONS="${CHECK_CONSISTENCY_FAIL:-true}"
SCOPE="${CHECK_CONSISTENCY_SCOPE:-all}"  # ui_patterns|behavior_patterns|ux_patterns|all

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Running consistency check on staged files..."

# Check if standards exist
if [ ! -d "$PROJECT_ROOT/coderef/standards" ]; then
    echo -e "${YELLOW}⚠️  No standards found. Run 'establish_standards' first.${NC}"
    exit 0  # Don't block commit if no standards
fi

# Prepare MCP tool call
# Note: This example assumes you have a CLI wrapper for MCP tools
# Adjust based on your MCP client setup (Node.js, Python, etc.)

# Option 1: Using npx with @modelcontextprotocol/inspector
# npx -y @modelcontextprotocol/inspector call docs-mcp check_consistency \
#   --project_path "$PROJECT_ROOT" \
#   --severity_threshold "$SEVERITY_THRESHOLD" \
#   --scope "$SCOPE" \
#   --fail_on_violations "$FAIL_ON_VIOLATIONS"

# Option 2: Using Python MCP client (if you have one)
# python3 -m mcp_client call docs-mcp check_consistency \
#   --project_path "$PROJECT_ROOT" \
#   --severity_threshold "$SEVERITY_THRESHOLD" \
#   --scope "$SCOPE" \
#   --fail_on_violations "$FAIL_ON_VIOLATIONS"

# Option 3: Using Claude Desktop or other MCP host programmatically
# (This requires custom integration with your MCP host)

# For this example, we'll simulate the tool call
# Replace this with your actual MCP client invocation
RESULT=$(cat <<EOF
{
  "status": "pass",
  "violations_found": 0,
  "files_checked": 5,
  "duration": 0.23,
  "severity_threshold": "$SEVERITY_THRESHOLD",
  "exit_code": 0
}
EOF
)

# Parse result (requires jq)
EXIT_CODE=$(echo "$RESULT" | jq -r '.exit_code // 1')
STATUS=$(echo "$RESULT" | jq -r '.status // "fail"')
VIOLATIONS=$(echo "$RESULT" | jq -r '.violations_found // 0')
FILES_CHECKED=$(echo "$RESULT" | jq -r '.files_checked // 0')
DURATION=$(echo "$RESULT" | jq -r '.duration // 0')

# Display results
if [ "$STATUS" = "pass" ]; then
    echo -e "${GREEN}✓ Consistency check passed${NC}"
    echo "  Files checked: $FILES_CHECKED"
    echo "  Duration: ${DURATION}s"
    echo "  Threshold: $SEVERITY_THRESHOLD"
    exit 0
else
    echo -e "${RED}✗ Consistency check failed${NC}"
    echo "  Violations found: $VIOLATIONS"
    echo "  Files checked: $FILES_CHECKED"
    echo "  Severity threshold: $SEVERITY_THRESHOLD"
    echo ""
    echo "Fix the violations above and try again."
    echo ""
    echo "To bypass this check (not recommended):"
    echo "  git commit --no-verify"
    echo ""
    echo "To adjust severity threshold:"
    echo "  CHECK_CONSISTENCY_SEVERITY=critical git commit"
    exit 1
fi
