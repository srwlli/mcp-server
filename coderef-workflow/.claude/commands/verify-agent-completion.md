Verify agent completion with automated checks

Call the `mcp__coderef-docs__verify_agent_completion` tool with the current working directory as the project_path.

Ask the user for:
1. Feature name
2. Agent number to verify (1-10)

This tool:
- Validates agent status is COMPLETE (not ASSIGNED or IN_PROGRESS)
- Runs git diff on forbidden files to ensure they're unchanged
- Validates success criteria from communication.json
- Updates agent status to VERIFIED (if all checks pass) or VERIFICATION_FAILED
- Logs forbidden file violations and success criteria status
