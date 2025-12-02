Create implementation plan by synthesizing context, analysis, and template into a complete plan.json file.

Ask the user for the feature name (alphanumeric, hyphens, underscores only), then call the `mcp__docs-mcp__create_plan` tool with:
- project_path: current working directory
- feature_name: the user-provided feature name

This is a **meta-tool** that guides AI through plan generation by:
1. Loading context.json from user's project (from prior `/gather-context` if available)
2. Loading project analysis (from prior `/analyze-for-planning` if available)
3. Loading AI-optimized template from **MCP server's directory** (not user's project)
4. Returning all inputs to AI with synthesis instructions
5. AI generates complete 10-section plan
6. AI saves to coderef/working/{feature_name}/plan.json

Generation process:
- **AI synthesizes**: Tool provides inputs, AI creates the actual plan content
- **Context-aware**: Uses user's requirements and project analysis
- **Template-guided**: Follows planning-template-for-ai.json structure
- **Complete plans**: No placeholder TODOs, real implementation details

Returns:
- Plan file path
- Feature name
- Sections completed (0-10)
- Status: 'complete' | 'partial'
- Has context/analysis indicators
- Next steps recommendations

**Workflow integration**:
1. `/gather-context` - Gather feature requirements (optional but recommended)
2. `/analyze-for-planning` - Analyze project context (optional but recommended)
3. `/create-plan` - **Generate plan** ← You are here
4. `/validate-plan` - Validate plan quality (score 0-100)
5. `/generate-plan-review` - Generate markdown review report

**Important**: Best results require both context.json and project analysis. Tool will warn if either is missing.

**Automatic DELIVERABLES.md Generation (NEW in v1.6.0)**:

After successfully creating plan.json, automatically call `mcp__docs-mcp__generate_deliverables_template` with:
- project_path: current working directory
- feature_name: the same feature name used for plan creation

This generates DELIVERABLES.md template with:
- Phase structure from plan.json
- Task checklists with [ ] checkboxes
- Metric placeholders (TBD) for LOC, commits, time
- Status: 🚧 Not Started

Returns both plan.json and DELIVERABLES.md paths to the user.

**Error handling**: If deliverables generation fails, warn the user but don't fail plan creation. The user can manually run `/generate-deliverables` later.
