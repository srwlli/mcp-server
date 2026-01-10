# coderef-docs

**Version:** 3.4.0
**Status:** ✅ Production Ready
**Protocol:** Model Context Protocol (MCP)

---

## Purpose

**coderef-docs** is an MCP server providing 13 specialized tools for AI-driven documentation generation, changelog management, and standards enforcement. It enables AI agents to generate, maintain, and validate project documentation with optional real code intelligence from @coderef/core CLI.

**Core Innovation:** Sequential foundation doc generation with context injection + agentic changelog recording with git auto-detection + composable module-based resource sheets (WO-RESOURCE-SHEET-MCP-TOOL-001).

---

## Quick Start

### Installation

```bash
# Clone repository
cd C:\Users\willh\.mcp-servers\coderef-docs

# Install dependencies
uv sync

# Run server
python server.py
```

### MCP Configuration

Add to `~/.mcp.json` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "coderef-docs": {
      "command": "python",
      "args": ["-m", "coderef-docs.server"],
      "env": {}
    }
  }
}
```

### Usage (via Slash Commands)

```bash
/generate-docs              # Generate 5 foundation docs with context injection
/generate-user-docs         # Generate 4 user-facing docs (my-guide, USER-GUIDE, FEATURES, quickref)
/record-changes            # Smart changelog with git auto-detection
/establish-standards        # Extract coding standards from codebase
/audit-codebase            # Check standards compliance (0-100 score)
/check-consistency         # Pre-commit gate for staged changes
```

---

## Features

### 1. Foundation Documentation Generation

Generate 5 comprehensive docs with real code intelligence:

- **API.md** - Extracted API endpoints via @coderef/core CLI
- **SCHEMA.md** - Extracted data models and entities
- **COMPONENTS.md** - Extracted UI components
- **ARCHITECTURE.md** - System architecture and design patterns
- **README.md** - Project overview

**Key Benefits:**
- ✅ Sequential generation (no timeouts)
- ✅ Context injection from @coderef/core CLI
- ✅ POWER framework templates
- ✅ Graceful degradation to placeholders

### 2. Changelog Management

**Tools:**
- `get_changelog` - Query changelog by version/type
- `add_changelog_entry` - Manual entry with full metadata
- `record_changes` - Agentic tool with git auto-detection

**Features:**
- Auto-detects changed files via git
- Suggests change_type from commit messages
- Calculates severity from scope
- Workorder tracking (WO-XXX-###)

### 3. Standards & Compliance

**Tools:**
- `establish_standards` - Extract UI/UX/behavior patterns
- `audit_codebase` - Compliance checking (0-100 score)
- `check_consistency` - Pre-commit gate

**Output:**
- 4 markdown files in `coderef/standards/`
- Violations by severity (critical/major/minor)
- Fix suggestions

### 4. User-Facing Documentation Generation

**Command:** `/generate-user-docs`

**Generates 4 user docs:**
- my-guide.md - Concise tool reference (60-80 lines)
- USER-GUIDE.md - Comprehensive tutorial
- FEATURES.md - Feature overview
- quickref.md - Scannable quick reference (150-250 lines)

**Supports:** CLI, Web, API, Desktop, Library applications

**Output:** All files saved to `coderef/user/`

### 5. Resource Sheet Generator (NEW in v3.3.0)

**Tool:** `generate_resource_sheet`

**Purpose:** Generate composable module-based technical documentation for code elements using intelligent auto-detection and assembly.

**Core Innovation:** Replaces 20 rigid templates with ~30-40 composable modules that intelligently combine based on code characteristics.

**3-Step Workflow:**
1. **DETECT** - Analyze code to detect 20+ characteristics (state, network calls, JSX, auth, etc.)
2. **SELECT** - Choose appropriate modules based on detected traits
3. **ASSEMBLE** - Compose modules into comprehensive documentation

**Output Formats:**
- **Markdown** - Human-readable documentation with YAML frontmatter
- **JSON Schema** - Machine-readable type definitions
- **JSDoc** - Inline comment suggestions for IDE integration

**Generation Modes:**
- `reverse-engineer` - Analyze existing code and auto-fill documentation
- `template` - Generate empty template for new code
- `refresh` - Update existing docs with latest code changes

**Key Features:**
- ✅ Auto-detection from coderef_scan output
- ✅ 4 universal modules (architecture, integration, testing, performance)
- ✅ Smart module selection based on code traits
- ✅ 50%+ auto-fill rate from code analysis
- ✅ Graceful degradation when coderef_scan unavailable

**Example Usage:**
```python
# Generate resource sheet for AuthService
mcp__coderef-docs__generate_resource_sheet({
  "element_name": "AuthService",
  "project_path": "/path/to/project",
  "mode": "reverse-engineer",
  "auto_analyze": true
})
```

**Implementation:** WO-RESOURCE-SHEET-MCP-TOOL-001 (Phase 1 Complete)

### 6. Universal Document Standard (UDS)

**NEW in v3.2.0** - Structured metadata for workorder documents

**What is UDS?**
- YAML frontmatter for markdown files (DELIVERABLES.md, claude.md)
- JSON metadata for JSON files (plan.json, context.json, analysis.json)
- Tracks workorder_id, status, timestamps, review dates
- Enables lifecycle management and traceability

**UDS Fields:**
- `workorder_id` - Links to workorder (e.g., WO-FEATURE-001)
- `feature_id` - Feature name
- `status` - DRAFT/IN_REVIEW/APPROVED/ARCHIVED
- `generated_by` - Server version that created the doc
- `last_updated` - Last modification date
- `next_review` - Auto-calculated review date (+30 days)
- `ai_assistance` - Marks AI-generated docs

**Scope:** Only workorder documents (has workorder_id)
**Backward Compatible:** Existing docs without workorder IDs unchanged

---

## Architecture

### Component Hierarchy

```
server.py (MCP entry point)
├── tool_handlers.py (11 tool handlers)
├── generators/ (Document generation logic)
│   ├── base_generator.py
│   ├── foundation_generator.py
│   ├── changelog_generator.py
│   ├── standards_generator.py
│   ├── audit_generator.py
│   └── quickref_generator.py
├── extractors.py (Code intelligence extraction)
├── validation.py (Input validation)
├── error_responses.py (Error handling)
├── logger_config.py (Logging)
└── cli_utils.py (CLI integration)
```

### Design Principles

1. **Single Responsibility** - Each component has one clear purpose
2. **Separation of Concerns** - Handlers, generators, validation, errors separated
3. **Fail-Safe Degradation** - Context injection degrades gracefully to placeholders
4. **Validation at Boundaries** - All inputs validated before processing
5. **Consistent Error Handling** - Uniform error response format

See [ARCHITECTURE.md](coderef/foundation-docs/ARCHITECTURE.md) for details.

### Documentation Hierarchy

**NEW in v3.4.0** - 4-Tier documentation system (WO-RESOURCE-SHEET-MCP-TOOL-001 Phase 3C)

```
Project Documentation
│
├── Tier 1: Foundation Docs (Project-Wide)
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── SCHEMA.md
│   ├── API.md
│   └── COMPONENTS.md
│   └── Location: coderef/foundation-docs/
│   └── Authority: Canonical for project patterns
│
├── Tier 2: Reference Sheets (Element-Specific)
│   ├── {element}.md
│   ├── {element}.schema.json
│   └── {element}.jsdoc.txt
│   └── Location: coderef/reference-sheets/{category}/
│   └── Authority: Canonical for element behavior
│
├── Tier 3: Inline Documentation (Code-Level)
│   ├── JSDoc comments in source files
│   ├── TypeScript type definitions
│   └── Links to Tier 2 reference sheets
│   └── Location: Source files (*.ts, *.tsx, *.js)
│   └── Authority: Links to Tier 2
│
└── Tier 4: Generated API Docs (Optional)
    ├── HTML/Markdown from JSDoc
    ├── TypeDoc or similar output
    └── Location: docs/api/ (if generated)
    └── Authority: Derived from Tiers 2 & 3
```

**Authority Precedence (when docs conflict):**
1. **Code** (runtime truth)
2. **Reference Sheets** (Tier 2 - behavioral contracts)
3. **Foundation Docs** (Tier 1 - architectural patterns)
4. **Inline JSDoc** (Tier 3 - quick reference)
5. **Generated Docs** (Tier 4 - derived documentation)

**Navigation:**
- **Find element docs:** See [coderef/reference-sheets/INDEX.md](coderef/reference-sheets/INDEX.md)
- **Understand hierarchy:** INDEX.md has complete navigation guide
- **Update workflow:** Code change → Re-run `generate_resource_sheet()` → Commit all files

---

## Tools Catalog

| Tool | Purpose | Type |
|------|---------|------|
| `list_templates` | Show available POWER templates | Utility |
| `get_template` | Get specific template | Utility |
| `generate_foundation_docs` | Create 5 docs with context injection | Generator |
| `generate_individual_doc` | Create single doc | Generator |
| `generate_quickref_interactive` | Interactive quickref ⭐ | Generator |
| `add_changelog_entry` | Manual changelog entry | Writer |
| `record_changes` | Smart recording with git ⭐ | Agentic |
| `establish_standards` | Extract coding standards | Analyzer |
| `audit_codebase` | Compliance check (0-100 score) | Auditor |
| `check_consistency` | Pre-commit gate ⭐ | Auditor |

**Total:** 10 tools across 3 domains (Documentation, Changelog, Standards)

See [API.md](coderef/foundation-docs/API.md) for API reference.

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Tools** | 11 MCP tools |
| **Generators** | 6 specialized generators |
| **Templates** | 7 POWER framework templates |
| **Test Coverage** | 27/30 tests passing (90%) |
| **Lines of Code** | ~4,000 (Python) |
| **Dependencies** | mcp, jsonschema, uvicorn |

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run with coverage
pytest --cov=. --cov-report=html
```

**Test Status:** 27/30 passing (90% coverage)

---

## Development

### Project Structure

```
coderef-docs/
├── server.py                      # MCP server entry
├── tool_handlers.py               # 11 tool handlers
├── extractors.py                  # Context injection
├── generators/                    # Doc generation
│   ├── base_generator.py
│   ├── foundation_generator.py
│   ├── changelog_generator.py
│   ├── standards_generator.py
│   ├── audit_generator.py
│   └── quickref_generator.py
├── templates/power/               # POWER templates
├── tests/                         # Test suites
├── coderef/                       # Output artifacts
│   ├── foundation-docs/           # Technical docs (API, ARCHITECTURE, etc.)
│   ├── user/                      # User-facing docs (my-guide, USER-GUIDE, etc.)
│   ├── changelog/                 # CHANGELOG.json
│   └── standards/                 # Standards docs
├── CLAUDE.md                      # AI context (v3.2.0)
└── README.md                      # This file
```

### Adding a New Tool

1. Add handler in `tool_handlers.py`:
```python
@log_invocation
@mcp_error_handler
async def handle_new_tool(arguments: dict) -> list[TextContent]:
    project_path = validate_project_path_input(arguments.get("project_path"))
    result = generator.generate(project_path)
    return [TextContent(type="text", text=result)]
```

2. Register in `server.py`:
```python
Tool(
    name="new_tool",
    description="Tool description",
    inputSchema={...}
)
```

3. Add tests in `tests/unit/test_tool_handlers.py`

---

## Integration

### With @coderef/core CLI

**CLI Path Resolution Order:**
1. `CODEREF_CLI_PATH` environment variable (explicit override)
2. Global `coderef` command in PATH (npm install -g @coderef/cli)
3. Hardcoded path (deprecated, shows warning)

**Configuration:**

```bash
# Option 1: Environment Variable (Recommended)
# Windows
set CODEREF_CLI_PATH=C:\path\to\coderef\packages\cli\dist\cli.js

# Linux/Mac
export CODEREF_CLI_PATH=/path/to/coderef/packages/cli/dist/cli.js

# Option 2: Global Install (Easiest)
npm install -g @coderef/cli

# Option 3: Local Development
# Uses hardcoded path (shows deprecation warning)
```

**Usage:**
- Extracts API endpoints
- Extracts data models
- Extracts UI components

**Cache:** Results cached with `@lru_cache(maxsize=32)`

### With coderef-workflow

**Integration Points:**
- Workflow calls `generate_foundation_docs` after feature completion
- Workflow calls `record_changes` to update changelog
- Workflow uses `/generate-user-docs` for user-facing documentation

---

## Documentation

- **[API Reference](coderef/foundation-docs/API.md)** - Complete tool API documentation
- **[Architecture](coderef/foundation-docs/ARCHITECTURE.md)** - System architecture and design patterns
- **[Components](coderef/foundation-docs/COMPONENTS.md)** - Component structure and dependencies
- **[Schema](coderef/foundation-docs/SCHEMA.md)** - Data schemas and validation rules
- **[CLAUDE.md](CLAUDE.md)** - AI context documentation (v3.2.0)

---

## Recent Changes

### v3.2.0 - Sequential Generation with Context Injection (2025-12-27)

- ✅ UPGRADED: `generate_foundation_docs` uses sequential generation (5 calls to `generate_individual_doc`)
- ✅ UPGRADED: `generate_individual_doc` injects real code intelligence for API/Schema/Components
- ✅ Context injection via @coderef/core CLI eliminates timeout errors
- ✅ Progress markers [1/5] through [5/5] for visibility
- ✅ Graceful degradation to placeholders if CLI unavailable

### v3.1.0 - Smart Changelog & Standards (2025-12-23)

- ✅ Added `record_changes` agentic tool with git auto-detection
- ✅ Added standards establishment and compliance auditing
- ✅ Added quickref generation for any application type
- 🗑️ Deprecated `update_changelog` (replaced by `record_changes`)

---

## Troubleshooting

### Context Injection Not Working

**Symptom:** Tools return `[FALLBACK] Using template placeholders`

**Solution:**
1. Check CLI availability:
   ```bash
   coderef --version
   ```

2. If not installed:
   ```bash
   npm install -g @coderef/core
   ```

3. Restart MCP server (restart Claude Code)

### Tests Failing

**Current Status:** 27/30 tests passing

**Known Issues:**
- 3 tests fail due to schema validation edge cases
- No impact on production functionality

---

## Contributing

1. Create feature branch
2. Add tests for new functionality
3. Update CLAUDE.md with architectural notes
4. Run test suite: `pytest tests/ -v`
5. Submit PR with clear description

---

## License

**Internal Tool** - Part of CodeRef Ecosystem

---

## References

- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **POWER Framework:** `templates/power/`
- **CodeRef Ecosystem:** `C:\Users\willh\.mcp-servers\`
- **Related Servers:** coderef-workflow, coderef-context, coderef-personas

---

**Maintained by:** willh, Claude Code AI

**For AI Agents:** This server provides 10 specialized documentation tools with optional real code intelligence injection via @coderef/core CLI.

*Generated: 2025-12-27*
