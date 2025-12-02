Analyze the current project to discover foundation docs, coding standards, reference components, and patterns for implementation planning.

Call the `mcp__docs-mcp__analyze_project_for_planning` tool with the current working directory as the project_path.

This tool automates section 0 (Preparation) of the feature implementation planning template by:
1. Scanning for foundation documentation (API.md, ARCHITECTURE.md, README.md, etc.)
2. Scanning for coding standards (BEHAVIOR-STANDARDS.md, UI-STANDARDS.md, etc.)
3. Finding reference components to use as examples
4. Identifying reusable patterns
5. Detecting technology stack
6. Identifying gaps and risks

Returns a comprehensive preparation summary that includes:
- Available and missing foundation docs
- Available and missing coding standards
- Primary and secondary reference components
- Key patterns identified
- Technology stack details
- Gaps and risks to address

**After running the analysis:**
1. Determine the feature name from context (look for `coderef/working/<feature-name>/context.json`) or ask the user
2. Save the JSON results to: `<project_root>/coderef/working/<feature-name>/analysis.json`
3. Create the directory if it doesn't exist
4. Pretty-print the JSON with 2-space indentation
5. Report to the user: "✅ Analysis saved to coderef/working/<feature-name>/analysis.json"

**This allows `/create-plan` to generate complete plans without placeholder TODOs.**

**Run this BEFORE creating implementation plans** to gather all necessary context (~80ms, very fast!).