Generate comprehensive foundation documentation powered by coderef analysis.

Call the `mcp__docs-mcp__coderef_foundation_docs` tool with the current working directory as the project_path.

## What Gets Generated

This unified command generates **6 files**:

| File | Location | Description |
|------|----------|-------------|
| **README.md** | Project root | Overview, stats, architecture diagram |
| **ARCHITECTURE.md** | coderef/foundation-docs/ | Module graph, metrics, high-impact elements |
| **SCHEMA.md** | coderef/foundation-docs/ | Database tables, relationships, migrations |
| **COMPONENTS.md** | coderef/foundation-docs/ | ALL modules (Handlers, Generators, Services, Utilities) |
| **API.md** | coderef/foundation-docs/ | Endpoints, authentication, error handling |
| **project-context.json** | coderef/foundation-docs/ | Machine-readable context for planning |

## Coderef Integration (99% Accuracy)

**For best results, run `coderef index` first:**

```bash
cd /path/to/project
npx @coderef/cli index --analyzer ast
```

This creates `.coderef/index.json` and `.coderef/graph.json` with:
- 99% accurate element detection (AST-based)
- Full call graphs and relationships
- Dependency analysis for diagrams

**If `.coderef/` exists:**
- Uses 99% accurate AST data from index.json
- Generates Mermaid dependency diagrams
- Shows callers/callees for each element
- Displays graph metrics (density, circularity)
- Shows high-impact elements with risk levels

**If `.coderef/` is missing:**
- Falls back to regex-based detection (85% accuracy)
- Skips diagram and relationship data
- Still generates all 6 files with basic content

## The Tool Performs

1. **Phase 0:** Load coderef data (.coderef/index.json, graph.json)
2. **Phase 1:** Deep extraction from existing foundation docs
3. **Phase 2:** Auto-detection (API endpoints, database schemas, dependencies)
4. **Phase 3:** Git activity analysis (commits, active files, contributors)
5. **Phase 4:** Code pattern detection (handlers, decorators, error types)
6. **Phase 5:** Similar feature discovery from coderef/archived/

## AGENT Markers

Generated docs include `<!-- AGENT: prompt -->` markers for gaps that should be filled:

- `<!-- AGENT: Describe what this does and why -->`
- `<!-- AGENT: Add usage example -->`
- `<!-- AGENT: Installation and usage instructions -->`

After generation, read each file and fill these markers with context-aware content.

## Replaces These Commands

- /api-inventory
- /database-inventory
- /dependency-inventory
- /config-inventory
- /test-inventory
- /inventory-manifest
- /documentation-inventory
- /generate-docs

## Usage

Use this command at the start of the /create-workorder workflow to gather comprehensive project context for planning.
