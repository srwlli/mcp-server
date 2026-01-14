---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.0.0
feature_id: foundation-docs-generation
doc_type: architecture
version: "1.0.0"
status: APPROVED
---

# Papertrail System Architecture

**Universal Documentation Standards (UDS) & Resource Sheet Metadata Standards (RSMS v2.0)**

---

## Purpose

This document provides complete system architecture for Papertrail, including component design, data flow, design patterns, and integration points with the CodeRef ecosystem.

## Overview

Papertrail is a **Python library and MCP server** providing document validation against Universal Documentation Standards (UDS) and Resource Sheet Metadata Standards (RSMS v2.0). It consists of **4 layers** (MCP Server, Validator, Schema, Factory) with **15 components** (1 base validator + 13 specialized validators + 1 factory).

**System Statistics** (from `.coderef/context.json`):
- **Total Elements**: 906 (662 methods, 135 functions, 109 classes)
- **Total Files**: 63
- **Languages**: Python (.py: 665 elements), TypeScript (.ts: 153 elements), JavaScript (.js: 88 elements)

**Architecture Style**: Layered architecture with dependency injection and factory pattern

---

## System Overview

### 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server Layer                     │
│  (papertrail/server.py - 7 tools, stdio/HTTP transport) │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Factory Layer                        │
│ (ValidatorFactory - 30+ patterns, auto-detection)      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Validator Layer                       │
│ (BaseUDSValidator + 13 validators, validation logic)   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Schema Layer                         │
│  (11 JSON Schema Draft-07 files, validation rules)     │
└─────────────────────────────────────────────────────────┘
```

### Data Flow: Validation Pipeline

```
MCP Client (Claude Code, coderef-docs)
    ↓
validate_document(file_path) [MCP Tool]
    ↓
ValidatorFactory.get_validator(file_path)
    ├─ Path pattern matching (30+ regex)
    ├─ Frontmatter inspection (detect doc_type)
    └─ Return validator instance
    ↓
validator.validate_file(file_path)
    ├─ Read file content
    ├─ Extract YAML frontmatter
    ├─ Load JSON schema
    ├─ Validate frontmatter (Draft7Validator)
    ├─ Category-specific validation (validate_specific)
    ├─ Calculate score (0-100)
    ├─ Calculate completeness (0-100%)
    └─ Return ValidationResult
    ↓
Format response (markdown text)
    ↓
Return to MCP client
```

---

## Key Components

### 1. MCP Server Layer

**File**: `papertrail/server.py`
**Lines**: 571
**Purpose**: Expose validation tools via Model Context Protocol (MCP) for integration with Claude Code and other AI agents

**Tools Exposed** (7):

| Tool | Purpose | Request | Response |
|------|---------|---------|----------|
| `validate_stub` | Validate stub.json files | file_path, auto_fill, save | Validation report with errors/warnings |
| `validate_resource_sheet` | RSMS v2.0 validation | file_path | Score (0-100) with compliance report |
| `check_all_resource_sheets` | Batch RSMS validation | directory | Summary with pass/fail counts |
| `validate_document` | UDS validation (auto-detect) | file_path | Score (0-100) with category detection |
| `check_all_docs` | Batch UDS validation | directory, pattern | Summary with average score |
| `validate_schema_completeness` | Schema sync validation | schema_name | Completeness report per doc_type |
| `validate_all_schemas` | Batch schema validation | (none) | Summary with issue counts |

**Transport**: stdio (standard input/output)

**Protocol**: MCP 1.0 (Model Context Protocol)

**Error Handling**: All tools return structured TextContent with markdown formatting, never raise exceptions to clients

---

### 2. Validator Layer

**Files**: `papertrail/validators/*.py`
**Purpose**: Implement validation logic for 13 document categories using Template Method pattern

#### Component Hierarchy

```
UDSValidator (papertrail/validator.py)
└── BaseUDSValidator (abstract base, 150+ lines, 8 methods)
    ├── FoundationDocValidator (README, API, ARCHITECTURE, SCHEMA, COMPONENTS)
    ├── WorkorderDocValidator (DELIVERABLES, context, analysis)
    ├── SystemDocValidator (CLAUDE.md, SYSTEM.md)
    ├── StandardsDocValidator (coding/doc standards)
    ├── UserFacingDocValidator (guides, tutorials, FAQs)
    ├── MigrationDocValidator (migration guides, breaking changes)
    ├── InfrastructureDocValidator (FILE-TREE, INVENTORY, INDEX)
    ├── SessionDocValidator (communication.json, instructions.json)
    ├── PlanValidator (plan.json structure validation)
    ├── ResourceSheetValidator (RSMS v2.0 compliance)
    ├── StubValidator (stub.json validation)
    ├── AnalysisValidator (analysis.json validation)
    ├── ExecutionLogValidator (execution-log.json validation)
    └── GeneralMarkdownValidator (fallback for unclassified docs)
```

#### BaseUDSValidator (Template Method Pattern)

**Core Methods**:

| Method | Visibility | Purpose |
|--------|-----------|---------|
| `validate_file(file_path)` | Public | Main entry point (template method) |
| `validate_content(content, file_path)` | Public | Validate content string |
| `validate_specific(frontmatter, content, file_path)` | Abstract | Hook method for category logic |
| `_load_schema()` | Private | Load JSON schema and resolve allOf |
| `_resolve_allof()` | Private | Manually merge allOf references |
| `_extract_frontmatter(content)` | Private | Parse YAML frontmatter |
| `_calculate_score(errors, warnings)` | Private | Calculate 0-100 score |
| `_calculate_completeness(frontmatter, content)` | Private | Calculate 0-100% section coverage |

**Template Method Implementation**:

```python
def validate_file(self, file_path: Path) -> ValidationResult:
    """Template method defining validation steps"""
    # Step 1: Read file
    content = self._read_file(file_path)

    # Step 2: Extract frontmatter
    frontmatter = self._extract_frontmatter(content)
    if not frontmatter:
        return ValidationResult(valid=False, errors=[...])

    # Step 3: Schema validation (base)
    schema_errors = self._validate_schema(frontmatter)

    # Step 4: Category-specific validation (subclass hook)
    category_errors, warnings = self.validate_specific(frontmatter, content, file_path)

    # Step 5: Aggregate errors
    all_errors = schema_errors + category_errors

    # Step 6: Calculate metrics
    score = self._calculate_score(all_errors, warnings)
    completeness = self._calculate_completeness(frontmatter, content)

    # Step 7: Return result
    return ValidationResult(
        valid=score >= 90,
        errors=all_errors,
        warnings=warnings,
        score=score,
        completeness=completeness
    )
```

**Benefits of Template Method**:
- **Consistent workflow**: All validators follow same steps
- **Easy extension**: New validators only implement `validate_specific()`
- **DRY principle**: Common logic in base class
- **Testability**: Can test base logic independently

---

### 3. Factory Layer (ValidatorFactory)

**File**: `papertrail/validators/factory.py`
**Lines**: 200+
**Purpose**: Auto-detect appropriate validator based on file path and frontmatter

#### Path Pattern Matching (30+ regex patterns)

| Priority | Pattern | Validator | Example |
|----------|---------|-----------|---------|
| 1 | `.*-RESOURCE-SHEET\.md$` | ResourceSheetValidator | `Auth-RESOURCE-SHEET.md` |
| 2 | `.*/README\.md$` | FoundationDocValidator | `coderef/foundation-docs/README.md` |
| 3 | `.*/ARCHITECTURE\.md$` | FoundationDocValidator | `coderef/foundation-docs/ARCHITECTURE.md` |
| 4 | `.*/API\.md$` | FoundationDocValidator | `coderef/foundation-docs/API.md` |
| 5 | `.*/SCHEMA\.md$` | FoundationDocValidator | `coderef/foundation-docs/SCHEMA.md` |
| 6 | `.*/COMPONENTS\.md$` | FoundationDocValidator | `coderef/foundation-docs/COMPONENTS.md` |
| 7 | `.*/DELIVERABLES\.md$` | WorkorderDocValidator | `coderef/workorder/feature/DELIVERABLES.md` |
| 8 | `.*/CLAUDE\.md$` | SystemDocValidator | `CLAUDE.md` |
| 9 | `.*-standards\.md$` | StandardsDocValidator | `coding-standards.md` |
| 10 | `.*-GUIDE\.md$` | UserGuideValidator | `USER-GUIDE.md` |
| 11 | `.*/MIGRATION-.*\.md$` | MigrationDocValidator | `MIGRATION-V2.md` |
| 12 | `.*/FILE-TREE\.md$` | InfrastructureDocValidator | `FILE-TREE.md` |
| 13 | `.*/communication\.json$` | SessionDocValidator | `communication.json` |
| 14 | `.*/plan\.json$` | PlanValidator | `plan.json` |
| 15 | `.*/stub\.json$` | StubValidator | `stub.json` |

**Detection Algorithm**:

```python
@classmethod
def get_validator(cls, file_path: Path) -> BaseUDSValidator:
    """Factory method"""
    # 1. Try path-based detection (30+ patterns, O(1) regex match)
    validator_type = cls._detect_from_path(str(file_path))

    # 2. Try frontmatter-based detection (requires file read)
    if not validator_type:
        validator_type = cls._detect_from_frontmatter(file_path)

    # 3. Return appropriate validator instance
    if validator_type == "foundation":
        return FoundationDocValidator()
    # ... 13 validators
    else:
        return GeneralMarkdownValidator()  # Fallback
```

**Benefits of Factory Pattern**:
- **Single entry point**: `ValidatorFactory.get_validator()`
- **Auto-detection**: Reduces user error
- **Extensibility**: Easy to add new patterns
- **Testability**: Can test detection logic independently

---

### 4. Schema Layer

**Directory**: `schemas/documentation/`
**Purpose**: Define validation rules using JSON Schema Draft-07

#### Schema Inheritance (allOf Pattern)

**Base Schema** (`base-frontmatter-schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["agent", "date", "task"],
  "properties": {
    "agent": {"type": "string", "minLength": 1, "maxLength": 100},
    "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
    "task": {"type": "string", "enum": ["CREATE", "UPDATE", "REVIEW", "DOCUMENT", "CONSOLIDATE", "MIGRATE", "ARCHIVE"]}
  }
}
```

**Extended Schema** (e.g., `foundation-doc-frontmatter-schema.json`):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "allOf": [
    {"$ref": "./base-frontmatter-schema.json"},
    {
      "type": "object",
      "required": ["workorder_id", "generated_by", "feature_id", "doc_type"],
      "properties": {
        "workorder_id": {"type": "string", "pattern": "^WO-[A-Z0-9-]+-\\d{3}$"},
        "generated_by": {"type": "string", "pattern": "^coderef-docs"},
        "feature_id": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
        "doc_type": {"type": "string", "enum": ["readme", "architecture", "api", "schema", "components"]}
      }
    }
  ]
}
```

**Schema Resolution**:
- `BaseUDSValidator._resolve_allof()` manually merges schemas
- Avoids Draft7Validator network fetch errors
- Result: Single merged schema with all required fields

**11 Schemas**:
1. `base-frontmatter-schema.json` (foundation for all)
2. `foundation-doc-frontmatter-schema.json` (5 doc_types)
3. `resource-sheet-metadata-schema.json` (RSMS v2.0)
4. `workorder-doc-frontmatter-schema.json`
5. `system-doc-frontmatter-schema.json`
6. `standards-doc-frontmatter-schema.json`
7. `user-facing-doc-frontmatter-schema.json` (3 doc_types)
8. `migration-doc-frontmatter-schema.json`
9. `infrastructure-doc-frontmatter-schema.json`
10. `session-doc-frontmatter-schema.json`
11. `script-frontmatter-schema.json`

---

## Design Decisions

### Decision 1: Layered Architecture

**Decision**: 4-layer architecture (MCP Server → Factory → Validator → Schema)

**Alternatives Considered**:
- Monolithic server with inline validation
- Microservices architecture

**Rationale**:
- **Separation of concerns**: Each layer has single responsibility
- **Testability**: Can test each layer independently
- **Extensibility**: Can add validators without modifying server
- **Maintainability**: Clear boundaries reduce coupling

**Trade-offs**:
- ✅ Pro: Easy to add new validators (extend BaseUDSValidator)
- ✅ Pro: Schema changes don't require code changes
- ❌ Con: More indirection (4 layers vs 1)
- ❌ Con: Slightly slower (factory lookup + schema loading)

---

### Decision 2: Template Method Pattern for Validators

**Decision**: BaseUDSValidator defines validation workflow, subclasses implement `validate_specific()`

**Alternatives Considered**:
- Strategy pattern (composition over inheritance)
- No abstraction (duplicate validation logic)

**Rationale**:
- **Consistent workflow**: All validators follow same steps (extract frontmatter → validate schema → validate category → calculate score)
- **DRY principle**: Schema validation, score calculation, frontmatter extraction in base class
- **Easy extension**: New validators only implement category-specific logic

**Trade-offs**:
- ✅ Pro: Only ~50-100 lines per validator (vs ~200+ without base)
- ✅ Pro: Guaranteed consistency (all validators have same workflow)
- ❌ Con: Tight coupling between base and subclasses
- ❌ Con: Cannot swap validation algorithm at runtime (vs Strategy pattern)

---

### Decision 3: Score-Based Validation (0-100 scale)

**Decision**: Calculate weighted scores from errors/warnings instead of binary pass/fail

**Formula**:
```
score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
score = max(0, score)
```

**Severity Deductions**:
- CRITICAL: -50 points (missing required fields, invalid schema)
- MAJOR: -20 points (invalid enum values, format violations)
- MINOR: -10 points (recommended field missing)
- WARNING: -5 points (style issues)
- Warnings: -2 points each

**Alternatives Considered**:
- Binary pass/fail (valid=true if no errors)
- Percentage-based (errors / total checks)

**Rationale**:
- **Actionable metrics**: Score shows quality level (not just pass/fail)
- **Gradual improvement**: Can track quality over time
- **Prioritization**: Critical errors weighted heavily
- **Flexibility**: Threshold can vary (90 for foundation docs, 70 for drafts)

**Trade-offs**:
- ✅ Pro: Quality progress tracking
- ✅ Pro: Prioritize critical issues
- ❌ Con: More complex than binary
- ❌ Con: Threshold selection subjective

---

### Decision 4: ValidatorFactory Auto-Detection

**Decision**: Auto-detect validator type from file path patterns + frontmatter

**Alternatives Considered**:
- Manual validator selection (user specifies type)
- File extension-based detection (.md, .json)

**Rationale**:
- **Better UX**: No need to specify validator type
- **Reduced errors**: Automated detection prevents mismatches
- **Batch operations**: Can validate entire directories without manual configuration
- **Extensibility**: Easy to add new patterns

**Trade-offs**:
- ✅ Pro: Zero configuration for users
- ✅ Pro: Works for batch validation
- ❌ Con: Pattern matching overhead (~30 regex checks)
- ❌ Con: Cannot override auto-detection (by design)

---

### Decision 5: Completeness Metric (Section Coverage)

**Decision**: Calculate 0-100% completeness for foundation docs based on required sections

**Formula**:
```
completeness = (sections_found / sections_required) * 100
```

**Example**:
```
# README.md (doc_type: readme)
Required sections: ["Purpose", "Overview", "What/Why/When", "Examples", "References"]
Found: ["Purpose", "Overview", "Examples"] = 3/5 = 60%
```

**Alternatives Considered**:
- Boolean section checks (has_purpose=true)
- No completeness metric (only validate required fields)

**Rationale**:
- **Progress tracking**: Shows how complete documentation is
- **Prioritization**: Identify missing sections to add
- **Quality gate**: Can require completeness >= 90% for APPROVED status

**Trade-offs**:
- ✅ Pro: Actionable metric (shows what to add)
- ✅ Pro: Gradual improvement tracking
- ❌ Con: Only applies to foundation docs (not all validators)
- ❌ Con: Doesn't measure section quality (only presence)

---

### Decision 6: JSON Schema Draft-07 (Not Custom DSL)

**Decision**: Use JSON Schema Draft-07 for validation rules

**Alternatives Considered**:
- Custom validation DSL (Python functions)
- Pydantic models

**Rationale**:
- **Industry standard**: JSON Schema widely used and understood
- **Tooling**: Excellent IDE support, validators, documentation generators
- **Declarative**: Schema is data, not code
- **Portability**: Can be consumed by non-Python tools

**Trade-offs**:
- ✅ Pro: Industry standard with excellent tooling
- ✅ Pro: Schema can be used for code generation
- ✅ Pro: Clear separation between validation rules (schema) and logic (code)
- ❌ Con: allOf resolution required (manual merging)
- ❌ Con: Limited expressiveness (can't define complex relationships)

---

## Integration Points

### With coderef-docs (Documentation Generation)

**Integration**: Real-time validation after document generation

```python
# coderef-docs generates README.md
await call_tool("coderef-docs", "generate_individual_doc", {
    "template_name": "readme",
    "project_path": "/path/to/project",
    "auto_validate": True  # ← Calls papertrail validate_document
})

# Papertrail validates
result = await call_tool("papertrail", "validate_document", {
    "file_path": "/path/to/project/coderef/foundation-docs/README.md"
})

# coderef-docs checks score
if result.score < 90:
    print(f"❌ Validation failed (score: {result.score}/100) - fix before commit")
```

**Quality Gate**: coderef-docs requires score >= 90 for foundation docs

---

### With coderef-workflow (Workorder Management)

**Integration**: Validate plan.json, DELIVERABLES.md, stub.json

```python
# Before archiving feature, validate all docs
result = await call_tool("papertrail", "check_all_docs", {
    "directory": "/path/to/coderef/workorder/feature-001",
    "pattern": "**/*.{md,json}"
})

# Only archive if all docs valid
if result.average_score >= 85:
    await call_tool("coderef-workflow", "archive_feature", {"feature_id": "feature-001"})
```

---

### With Git Workflows (Pre-Commit Hooks)

**Integration**: Validate staged files before commit

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --staged --name-only | grep '.md$'); do
    python -c "
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path('$file'))
result = validator.validate_file(Path('$file'))

if not result.valid:
    print(f'❌ Validation failed: $file (score: {result.score}/100)')
    exit(1)
"
done
```

---

### With CI/CD Pipelines

**Integration**: Automated validation on PR creation

```yaml
# .github/workflows/validate-docs.yml
name: Validate Documentation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Foundation Docs
        run: |
          python -c "
          from papertrail.server import check_all_docs
          import asyncio

          result = asyncio.run(check_all_docs({'directory': 'coderef/foundation-docs'}))
          print(result.text)
          "
```

---

## Performance Considerations

### 1. Schema Loading (Lazy Loading)

**Implementation**: Schemas loaded on-demand, not at validator construction

```python
class BaseUDSValidator:
    def __init__(self, schemas_dir: Optional[Path] = None):
        self.schema = None  # Not loaded yet

        if self.schema_name:
            self._load_schema()  # Only loads if schema_name set
```

**Benefit**: Faster validator creation, especially for ValidatorFactory

---

### 2. Factory Pattern Overhead (Regex Caching)

**Implementation**: PATH_PATTERNS compiled once at class definition

```python
class ValidatorFactory:
    PATH_PATTERNS = {
        r".*-RESOURCE-SHEET\.md$": "resource_sheet",  # Pre-compiled regex
        # ... 30+ patterns
    }
```

**Benefit**: O(1) pattern matching (pre-compiled regex)

---

### 3. Batch Validation (Parallel Processing)

**Implementation**: Can validate multiple files in parallel using ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor

files = list(Path("docs").glob("**/*.md"))

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(lambda f: ValidatorFactory.get_validator(f).validate_file(f), files))
```

**Benefit**: ~4x speedup for large documentation sets

---

## References

### Internal
- **BaseUDSValidator**: `papertrail/validators/base.py` (150+ lines, Template Method pattern)
- **ValidatorFactory**: `papertrail/validators/factory.py` (200+ lines, Factory pattern, 30+ patterns)
- **MCP Server**: `papertrail/server.py` (571 lines, 7 tools, stdio transport)
- **11 JSON Schemas**: `schemas/documentation/*.json` (Draft-07, allOf inheritance)

### External
- [Model Context Protocol (MCP) Specification](https://spec.modelcontextprotocol.io/)
- [JSON Schema Draft-07](https://json-schema.org/draft-07/schema)
- [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)

### Related Documents
- [API.md](API.md) - Complete API reference for 7 MCP tools
- [SCHEMA.md](SCHEMA.md) - All 11 JSON schemas with field validations
- [COMPONENTS.md](COMPONENTS.md) - 15 validator components with architecture
- [README.md](README.md) - Project overview and quick start

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem - Papertrail MCP Server
