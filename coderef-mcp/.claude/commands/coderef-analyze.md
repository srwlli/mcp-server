Perform deep analysis on CodeRef2 elements (impact, coverage, complexity).

Call the `mcp__coderef__analyze` tool to analyze a code element's impact and relationships.

**Usage Examples:**
- `/coderef-analyze @Fn/services/auth#authenticate` - Analyze function impact
- `/coderef-analyze @Cl/models/User` - Analyze class complexity

**Parameters:**
- reference: CodeRef2 reference to analyze (required)
- analysis_type: Type of analysis - "impact", "deep", "coverage", "complexity" (default: "impact")
- depth: Analysis depth 1-10 (default: 3)
- include_test_impact: Include test-related impacts (default: true)

Returns: Analysis results with impact metrics, dependencies, and recommendations.
