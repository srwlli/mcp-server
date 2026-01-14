---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-VALIDATION-ENHANCEMENT-001
generated_by: coderef-docs v1.0.0
feature_id: foundation-docs-generation
doc_type: components
version: "1.0.0"
status: APPROVED
---

# Papertrail Validator Components

**13 Validators + BaseUDSValidator + ValidatorFactory Architecture**

---

## Purpose

This document provides complete component reference for Papertrail's validator architecture, including BaseUDSValidator abstract class, 13 category-specific validators, ValidatorFactory auto-detection system, and core data structures (ValidationResult, ValidationSeverity).

## Overview

Papertrail uses **15 validator components** organized in an inheritance hierarchy:

| Component | Type | Responsibility | File |
|-----------|------|----------------|------|
| **BaseUDSValidator** | Abstract Base Class | Common validation logic, schema loading, score calculation | `papertrail/validators/base.py` |
| **FoundationDocValidator** | Category Validator | README, ARCHITECTURE, API, SCHEMA, COMPONENTS | `papertrail/validators/foundation.py` |
| **WorkorderDocValidator** | Category Validator | DELIVERABLES, context, analysis | `papertrail/validators/workorder.py` |
| **SystemDocValidator** | Category Validator | CLAUDE.md, SYSTEM.md | `papertrail/validators/system.py` |
| **StandardsDocValidator** | Category Validator | Coding/documentation standards | `papertrail/validators/standards.py` |
| **UserFacingDocValidator** | Category Validator | User guides, tutorials, FAQs | `papertrail/validators/user_facing.py` |
| **MigrationDocValidator** | Category Validator | Migration guides, breaking changes | `papertrail/validators/migration.py` |
| **InfrastructureDocValidator** | Category Validator | FILE-TREE, INVENTORY, INDEX | `papertrail/validators/infrastructure.py` |
| **SessionDocValidator** | Category Validator | communication.json, instructions.json | `papertrail/validators/session.py` |
| **PlanValidator** | Specialized Validator | plan.json structure validation | `papertrail/validators/plan.py` |
| **ResourceSheetValidator** | Specialized Validator | RSMS v2.0 compliance | `papertrail/validators/resource_sheet.py` |
| **StubValidator** | Specialized Validator | stub.json validation | `papertrail/validators/stub.py` |
| **AnalysisValidator** | Specialized Validator | analysis.json validation | `papertrail/validators/analysis.py` |
| **ExecutionLogValidator** | Specialized Validator | execution-log.json validation | `papertrail/validators/execution_log.py` |
| **GeneralMarkdownValidator** | Fallback Validator | Unclassified markdown docs | `papertrail/validators/general.py` |
| **ValidatorFactory** | Factory Class | Auto-detection via 30+ path patterns | `papertrail/validators/factory.py` |

**Total Components:** 15 (1 base + 13 validators + 1 factory)

---

## Component Catalog

The 15 validator components are organized into 5 categories:

1. **Base Class** (1): BaseUDSValidator - Abstract template method pattern
2. **Category Validators** (8): Foundation, Workorder, System, Standards, User-Facing, Migration, Infrastructure, Session
3. **Specialized Validators** (5): Plan, ResourceSheet, Stub, Analysis, ExecutionLog
4. **Fallback Validator** (1): GeneralMarkdown - handles unclassified docs
5. **Factory** (1): ValidatorFactory - auto-detection and instantiation

See table above for complete component list with responsibilities and file locations.

## Props/Parameters

### BaseUDSValidator Properties
- `schema_name: Optional[str]` - JSON schema filename (e.g., "foundation-doc-frontmatter-schema.json")
- `doc_category: str` - Document category (e.g., "foundation", "workorder", "system")
- `schema: dict` - Loaded and resolved JSON schema
- `schemas_dir: Path` - Path to schemas/documentation directory

### BaseUDSValidator Methods
- `validate_file(file_path: Path) -> ValidationResult` - Main validation entry point
- `validate_specific(frontmatter, content, file_path) -> tuple[errors, warnings]` - Abstract hook method
- `_load_schema() -> dict` - Load and resolve allOf references
- `_extract_frontmatter(content) -> dict` - Parse YAML front matter
- `_validate_required_sections(frontmatter, content) -> list[ValidationError]` - Check doc_type sections
- `_calculate_score(errors, warnings) -> int` - Calculate 0-100 score
- `_calculate_completeness(frontmatter, content) -> int` - Calculate 0-100% completeness

### ValidationResult Properties
- `valid: bool` - True if score >= 90
- `errors: list[ValidationError]` - Validation errors with severity
- `warnings: list[str]` - Non-blocking warnings
- `score: int` - 0-100 quality score
- `completeness: int` - 0-100% section coverage (optional)

### ValidationError Properties
- `severity: ValidationSeverity` - CRITICAL, MAJOR, MINOR, WARNING
- `message: str` - Human-readable error description
- `field: Optional[str]` - Field name that failed validation

## Usage Examples

### Example 1: Validate a Foundation Doc

```python
from papertrail.validators.factory import ValidatorFactory
from pathlib import Path

# Auto-detect validator from filename
validator = ValidatorFactory.get_validator(Path("README.md"))

# Validate the file
result = validator.validate_file(Path("README.md"))

# Check results
print(f"Valid: {result.valid}")
print(f"Score: {result.score}/100")
print(f"Completeness: {result.completeness}%")

# Print errors
for error in result.errors:
    print(f"[{error.severity.name}] {error.message}")
```

### Example 2: Validate All Docs in Directory

```python
from papertrail.validators.factory import ValidatorFactory
from pathlib import Path

docs_dir = Path("coderef/foundation-docs")
results = []

for doc_file in docs_dir.glob("*.md"):
    validator = ValidatorFactory.get_validator(doc_file)
    result = validator.validate_file(doc_file)
    results.append((doc_file.name, result))

# Report summary
passed = sum(1 for _, r in results if r.valid)
print(f"Passed: {passed}/{len(results)}")
avg_score = sum(r.score for _, r in results) / len(results)
print(f"Average Score: {avg_score:.1f}/100")
```

### Example 3: Custom Validator Subclass

```python
from papertrail.validators.base import BaseUDSValidator
from papertrail.validator import ValidationError, ValidationSeverity

class CustomDocValidator(BaseUDSValidator):
    schema_name = "custom-doc-schema.json"
    doc_category = "custom"

    def validate_specific(self, frontmatter: dict, content: str, file_path) -> tuple:
        errors = []
        warnings = []

        # Custom validation logic
        if "custom_field" not in frontmatter:
            errors.append(ValidationError(
                severity=ValidationSeverity.MAJOR,
                message="Missing custom_field",
                field="custom_field"
            ))

        return (errors, warnings)
```

---

---

## What: Component Catalog

### 1. BaseUDSValidator (Abstract Base Class)

**File**: `papertrail/validators/base.py`
**Lines**: 150+
**Purpose**: Abstract base class providing common validation functionality for all UDS validators

**Class Hierarchy**:
```
UDSValidator (papertrail/validator.py)
└── BaseUDSValidator (abstract)
    ├── FoundationDocValidator
    ├── WorkorderDocValidator
    ├── SystemDocValidator
    ├── StandardsDocValidator
    ├── UserFacingDocValidator
    ├── MigrationDocValidator
    ├── InfrastructureDocValidator
    └── SessionDocValidator
```

**Class Attributes**:
```python
class BaseUDSValidator(UDSValidator):
    schema_name: Optional[str] = None  # JSON schema filename
    doc_category: str = "unknown"       # Category name (foundation, workorder, etc.)
```

**Constructor**:
```python
def __init__(self, schemas_dir: Optional[Path] = None):
    """
    Initialize validator with schemas directory

    Args:
        schemas_dir: Path to schemas directory (default: package schemas/documentation/)
    """
```

**Core Methods**:

| Method | Signature | Returns | Purpose |
|--------|-----------|---------|---------|
| `validate_file()` | `(file_path: Union[str, Path])` | `ValidationResult` | Main entry point: validate file against schema |
| `validate_content()` | `(content: str, file_path: Optional[Path])` | `ValidationResult` | Validate document content (markdown with frontmatter) |
| `validate_specific()` | `(frontmatter: dict, content: str, file_path: Optional[Path])` | `tuple[list[ValidationError], list[str]]` | **Abstract method**: Category-specific validation logic |
| `_load_schema()` | `()` | `None` | Load JSON schema for validator |
| `_resolve_allof()` | `()` | `None` | Resolve allOf references by merging schemas |
| `_extract_frontmatter()` | `(content: str)` | `Optional[dict]` | Extract YAML frontmatter from markdown |
| `_calculate_score()` | `(errors: list[ValidationError], warnings: list[str])` | `int` | Calculate 0-100 score based on errors/warnings |
| `_calculate_completeness()` | `(frontmatter: dict, content: str)` | `Optional[int]` | Calculate 0-100% section coverage |
| `code_example_validation()` | `(frontmatter: dict, content: str, project_path: Optional[Path])` | `list[ValidationError]` | Validate code examples in API/COMPONENTS docs |

**Validation Flow**:
```
validate_file(Path)
    ↓
validate_content(content, file_path)
    ↓
_extract_frontmatter(content) → frontmatter dict
    ↓
Draft7Validator.validate(frontmatter, schema) → schema errors
    ↓
validate_specific(frontmatter, content, file_path) → category errors/warnings
    ↓
_calculate_score(errors, warnings) → score (0-100)
    ↓
_calculate_completeness(frontmatter, content) → completeness (0-100%)
    ↓
ValidationResult(valid, errors, warnings, score, completeness)
```

**Score Calculation Algorithm**:
```python
def _calculate_score(self, errors: list[ValidationError], warnings: list[str]) -> int:
    """
    Formula: score = 100 - 50*CRITICAL - 20*MAJOR - 10*MINOR - 5*WARNING - 2*warnings
    Floor: max(0, score)
    """
```

**Severity Deductions**:
- **CRITICAL**: -50 points (missing required fields, invalid schema structure)
- **MAJOR**: -20 points (invalid enum values, format violations)
- **MINOR**: -10 points (recommended field missing)
- **WARNING**: -5 points (style issues)
- **Warnings**: -2 points each (informational)

---

### 2. FoundationDocValidator

**File**: `papertrail/validators/foundation.py`
**Lines**: 100+
**Purpose**: Validates foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS) against POWER framework

**Class Attributes**:
```python
class FoundationDocValidator(BaseUDSValidator):
    schema_name = "foundation-doc-frontmatter-schema.json"
    doc_category = "foundation"

    POWER_SECTIONS = [
        "Purpose", "Overview", "What", "Why", "When", "Examples", "References"
    ]
```

**Methods**:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `validate_specific()` | `(frontmatter: dict, content: str, file_path: Optional[Path])` | Check POWER framework, validate code examples |
| `_check_power_framework()` | `(content: str)` | Check if POWER sections present |
| `_infer_doc_type_from_filename()` | `(file_path: Path)` | Infer doc_type from filename (README.md → readme) |

**POWER Framework Validation**:
- Checks for 7 recommended sections: Purpose, Overview, What, Why, When, Examples, References
- Warns if sections missing (non-blocking)
- Required sections per doc_type defined in schema (foundation-doc-frontmatter-schema.json lines 94-124)

**Code Example Validation** (API & COMPONENTS docs):
- Validates Python, JavaScript, TypeScript, JSON, YAML code blocks
- Checks syntax correctness
- Verifies code examples match documented API signatures

**doc_type Validation**:
- Infers expected doc_type from filename (README.md → `readme`)
- Errors if frontmatter doc_type doesn't match filename
- Supported types: `readme`, `architecture`, `api`, `schema`, `components`

---

### 3. ResourceSheetValidator (RSMS v2.0)

**File**: `papertrail/validators/resource_sheet.py`
**Lines**: 150+
**Purpose**: Validates resource sheets against RSMS v2.0 standards with snake_case frontmatter and naming convention enforcement

**Class Attributes**:
```python
class ResourceSheetValidator(BaseUDSValidator):
    schema_name = "resource-sheet-metadata-schema.json"
    doc_category = "resource_sheet"
```

**Unique Validations**:
1. **Naming Convention**: File must end with `-RESOURCE-SHEET.md` (enforced)
2. **snake_case Frontmatter**: All frontmatter keys must be snake_case (not camelCase)
3. **Required Fields**: `agent`, `date`, `task`, `subject`, `parent_project`, `category`
4. **Category Enum**: Must be one of 11 values (service, controller, model, utility, integration, component, middleware, validator, schema, config, other)
5. **related_files Validation**: Array of valid file paths (not markdown)
6. **related_docs Validation**: Array of markdown files ending with `.md`

**RSMS v2.0 Compliance Threshold**: Score >= 90/100

---

### 4. ValidatorFactory (Auto-Detection)

**File**: `papertrail/validators/factory.py`
**Lines**: 200+
**Purpose**: Auto-detect appropriate validator based on file path and frontmatter

**Path Patterns** (30+):

| Pattern | Validator | Example |
|---------|-----------|---------|
| `.*-RESOURCE-SHEET\.md$` | ResourceSheetValidator | `AuthService-RESOURCE-SHEET.md` |
| `.*/README\.md$` | FoundationDocValidator | `coderef/foundation-docs/README.md` |
| `.*/ARCHITECTURE\.md$` | FoundationDocValidator | `coderef/foundation-docs/ARCHITECTURE.md` |
| `.*/API\.md$` | FoundationDocValidator | `coderef/foundation-docs/API.md` |
| `.*/SCHEMA\.md$` | FoundationDocValidator | `coderef/foundation-docs/SCHEMA.md` |
| `.*/COMPONENTS\.md$` | FoundationDocValidator | `coderef/foundation-docs/COMPONENTS.md` |
| `.*/DELIVERABLES\.md$` | WorkorderDocValidator | `coderef/workorder/feature/DELIVERABLES.md` |
| `.*/CLAUDE\.md$` | SystemDocValidator | `CLAUDE.md` |
| `.*-standards\.md$` | StandardsDocValidator | `coding-standards.md` |
| `.*-GUIDE\.md$` | UserGuideValidator | `USER-GUIDE.md` |
| `.*/MIGRATION-.*\.md$` | MigrationDocValidator | `MIGRATION-V2.md` |
| `.*/FILE-TREE\.md$` | InfrastructureDocValidator | `FILE-TREE.md` |
| `.*/communication\.json$` | SessionDocValidator | `coderef/sessions/session-001/communication.json` |
| `.*/plan\.json$` | PlanValidator | `coderef/workorder/feature/plan.json` |
| `.*/stub\.json$` | StubValidator | `coderef/working/feature/stub.json` |

**Factory Methods**:

| Method | Signature | Purpose |
|--------|-----------|---------|
| `get_validator()` | `(file_path: Union[str, Path], schemas_dir: Optional[Path])` | Auto-detect and return validator instance |
| `_detect_from_path()` | `(path_str: str)` | Detect validator from file path patterns |
| `_detect_from_frontmatter()` | `(frontmatter: dict)` | Detect validator from frontmatter fields |

**Detection Logic**:
1. **Path-based detection** (30+ regex patterns)
2. **Frontmatter-based detection** (`workorder_id` → WorkorderDocValidator, `session_id` → SessionDocValidator)
3. **Fallback**: GeneralMarkdownValidator if no match

---

### 5. ValidationResult (Data Structure)

**File**: `papertrail/validator.py`
**Purpose**: Encapsulate validation results with score, errors, warnings, and completeness

**Structure**:
```python
@dataclass
class ValidationResult:
    valid: bool                          # True if score >= 90
    errors: list[ValidationError]        # List of validation errors
    warnings: list[str]                  # List of warnings
    score: int                           # 0-100 quality score
    completeness: Optional[int] = None   # 0-100% section coverage (foundation docs only)
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `valid` | bool | True if score >= 90/100 (validation passes) |
| `errors` | list[ValidationError] | Validation errors with severity levels |
| `warnings` | list[str] | Non-blocking warnings (informational) |
| `score` | int | 0-100 quality score (100 - severity deductions) |
| `completeness` | Optional[int] | 0-100% section coverage (foundation docs only) |

**Usage**:
```python
result = validator.validate_file(Path("README.md"))

if result.valid:
    print(f"✅ Valid (score: {result.score}/100)")
else:
    print(f"❌ Invalid (score: {result.score}/100)")
    for error in result.errors:
        print(f"  - [{error.severity.value}] {error.message}")
```

---

### 6. ValidationError (Data Structure)

**File**: `papertrail/validator.py`
**Purpose**: Represent individual validation error with severity and field context

**Structure**:
```python
@dataclass
class ValidationError:
    severity: ValidationSeverity  # CRITICAL, MAJOR, MINOR, WARNING
    message: str                  # Human-readable error message
    field: Optional[str] = None   # Frontmatter field that failed validation
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `severity` | ValidationSeverity | Error severity level (affects score deduction) |
| `message` | str | Human-readable error message |
| `field` | Optional[str] | Frontmatter field name (e.g., "workorder_id", "doc_type") |

**Example**:
```python
ValidationError(
    severity=ValidationSeverity.CRITICAL,
    message="Missing required field: workorder_id",
    field="workorder_id"
)
```

---

### 7. ValidationSeverity (Enum)

**File**: `papertrail/validator.py`
**Purpose**: Define severity levels with associated score deductions

**Enum Values**:

| Severity | Score Deduction | Use Case |
|----------|----------------|----------|
| **CRITICAL** | -50 points | Missing required fields, invalid schema structure |
| **MAJOR** | -20 points | Invalid enum values, format violations |
| **MINOR** | -10 points | Recommended field missing, minor format issues |
| **WARNING** | -5 points | Style issues, non-blocking suggestions |

**Implementation**:
```python
from enum import Enum

class ValidationSeverity(Enum):
    CRITICAL = "CRITICAL"  # -50
    MAJOR = "MAJOR"        # -20
    MINOR = "MINOR"        # -10
    WARNING = "WARNING"    # -5
```

**Usage in Scoring**:
```python
score = 100
for error in errors:
    if error.severity == ValidationSeverity.CRITICAL:
        score -= 50
    elif error.severity == ValidationSeverity.MAJOR:
        score -= 20
    elif error.severity == ValidationSeverity.MINOR:
        score -= 10
    elif error.severity == ValidationSeverity.WARNING:
        score -= 5
score = max(0, score)  # Floor at 0
```

---

### 8. WorkorderDocValidator

**File**: `papertrail/validators/workorder.py`
**Purpose**: Validates workorder documentation (DELIVERABLES.md, context.json, analysis.json)

**Class Attributes**:
```python
class WorkorderDocValidator(BaseUDSValidator):
    schema_name = "workorder-doc-frontmatter-schema.json"
    doc_category = "workorder"
```

**Unique Validations**:
- Workorder ID format: `WO-{FEATURE}-{CATEGORY}-###`
- Feature ID format: kebab-case
- Status enum: PLANNING, IN_PROGRESS, TESTING, COMPLETE, ARCHIVED

---

### 9. SystemDocValidator

**File**: `papertrail/validators/system.py`
**Purpose**: Validates system documentation (CLAUDE.md, SYSTEM.md, SESSION-INDEX.md)

**Class Attributes**:
```python
class SystemDocValidator(BaseUDSValidator):
    schema_name = "system-doc-frontmatter-schema.json"
    doc_category = "system"
```

**Unique Validations**:
- Project name validation
- Version format: semantic versioning (X.Y.Z)
- Status enum: DEVELOPMENT, PRODUCTION, DEPRECATED

---

### 10. StandardsDocValidator

**File**: `papertrail/validators/standards.py`
**Purpose**: Validates coding and documentation standards

**Class Attributes**:
```python
class StandardsDocValidator(BaseUDSValidator):
    schema_name = "standards-doc-frontmatter-schema.json"
    doc_category = "standards"
```

**Unique Validations**:
- Scope enum: project, organization, team
- Enforcement enum: mandatory, recommended, optional
- Version format: semantic versioning

---

### 11. UserFacingDocValidator

**File**: `papertrail/validators/user_facing.py`
**Purpose**: Validates user guides, tutorials, FAQs, and quickstarts

**Class Attributes**:
```python
class UserFacingDocValidator(BaseUDSValidator):
    schema_name = "user-facing-doc-frontmatter-schema.json"
    doc_category = "user_facing"
```

**Unique Validations**:
- Audience field validation
- doc_type enum: guide, tutorial, faq, quickstart, reference, troubleshooting
- Difficulty enum: beginner, intermediate, advanced
- Prerequisites array validation

---

### 12. MigrationDocValidator

**File**: `papertrail/validators/migration.py`
**Purpose**: Validates migration guides, breaking change docs, and audit reports

**Class Attributes**:
```python
class MigrationDocValidator(BaseUDSValidator):
    schema_name = "migration-doc-frontmatter-schema.json"
    doc_category = "migration"
```

**Unique Validations**:
- migration_type enum: version_upgrade, api_change, schema_migration, breaking_change
- Version format: from_version and to_version (semantic versioning)
- breaking_changes array validation

---

### 13. InfrastructureDocValidator

**File**: `papertrail/validators/infrastructure.py`
**Purpose**: Validates infrastructure documentation (FILE-TREE.md, INVENTORY.md, INDEX.md)

**Class Attributes**:
```python
class InfrastructureDocValidator(BaseUDSValidator):
    schema_name = "infrastructure-doc-frontmatter-schema.json"
    doc_category = "infrastructure"
```

**Unique Validations**:
- infra_type enum: file_tree, inventory, index, catalog
- environment enum: development, staging, production, all
- platform enum: windows, linux, macos, cross_platform

---

### 14. SessionDocValidator

**File**: `papertrail/validators/session.py`
**Purpose**: Validates multi-agent session communication files (communication.json, instructions.json)

**Class Attributes**:
```python
class SessionDocValidator(BaseUDSValidator):
    schema_name = "session-doc-frontmatter-schema.json"
    doc_category = "session"
```

**Unique Validations**:
- session_type enum: multi_agent, single_agent, orchestrated
- session_id format: kebab-case
- Orchestrator agent name validation
- Participants array (agent names)

---

### 15. PlanValidator

**File**: `papertrail/validators/plan.py`
**Purpose**: Validates plan.json structure (10-section workorder plans)

**Lines**: 26 elements (from context.json)

**Unique Validations**:
- 10-section plan structure (META_DOCUMENTATION, 0_PREPARATION, 1_EXECUTIVE_SUMMARY, etc.)
- Workorder ID format
- Task ID system validation
- Phase dependencies validation

---

## Why: Architecture Patterns

### Pattern 1: Template Method Pattern

**BaseUDSValidator** uses Template Method pattern:

```python
class BaseUDSValidator:
    def validate_file(self, file_path: Path) -> ValidationResult:
        """Template method defining validation steps"""
        content = self._read_file(file_path)
        frontmatter = self._extract_frontmatter(content)

        # Step 1: Schema validation (base)
        schema_errors = self._validate_schema(frontmatter)

        # Step 2: Category-specific validation (subclass override)
        errors, warnings = self.validate_specific(frontmatter, content, file_path)

        # Step 3: Calculate score and completeness (base)
        score = self._calculate_score(schema_errors + errors, warnings)
        completeness = self._calculate_completeness(frontmatter, content)

        return ValidationResult(valid, errors, warnings, score, completeness)

    def validate_specific(self, frontmatter, content, file_path):
        """Hook method - subclasses must implement"""
        raise NotImplementedError
```

**Benefits**:
- Consistent validation workflow across all validators
- Subclasses only implement category-specific logic
- Easy to add new validators (extend BaseUDSValidator, implement validate_specific())

---

### Pattern 2: Factory Pattern

**ValidatorFactory** uses Factory pattern for auto-detection:

```python
class ValidatorFactory:
    PATH_PATTERNS = {
        r".*-RESOURCE-SHEET\.md$": "resource_sheet",
        r".*/README\.md$": "foundation",
        # ... 30+ patterns
    }

    @classmethod
    def get_validator(cls, file_path: Path) -> BaseUDSValidator:
        """Factory method"""
        # Try path-based detection
        validator_type = cls._detect_from_path(str(file_path))

        # Try frontmatter-based detection
        if not validator_type:
            validator_type = cls._detect_from_frontmatter(file_path)

        # Return appropriate validator instance
        if validator_type == "foundation":
            return FoundationDocValidator()
        elif validator_type == "resource_sheet":
            return ResourceSheetValidator()
        # ... 13 validators
        else:
            return GeneralMarkdownValidator()
```

**Benefits**:
- Single entry point for validation (`ValidatorFactory.get_validator()`)
- Auto-detection reduces user error
- Easy to add new detection patterns

---

### Pattern 3: Composition over Inheritance

**Code Example Validation** uses composition:

```python
class BaseUDSValidator:
    def code_example_validation(self, frontmatter: dict, content: str, project_path: Optional[Path]) -> list[ValidationError]:
        """Composable code example validation"""
        # Import validation modules on-demand
        from ..tools.code_validator import CodeValidator

        validator = CodeValidator()
        return validator.validate_examples(content, project_path)
```

**FoundationDocValidator** composes code validation:

```python
class FoundationDocValidator(BaseUDSValidator):
    def validate_specific(self, frontmatter, content, file_path):
        errors = []

        # Compose code example validation
        if frontmatter.get('doc_type') in ['api', 'components']:
            errors.extend(self.code_example_validation(frontmatter, content, file_path.parent))

        return errors, warnings
```

**Benefits**:
- Reusable validation logic
- Optional composition (only for API/COMPONENTS docs)
- Easy to swap implementations

---

## When: Integration Points

### With MCP Server (papertrail/server.py)

**validate_document tool**:
```python
async def validate_document(arguments: dict) -> list[TextContent]:
    """MCP tool: validate any document"""
    file_path = Path(arguments["file_path"])

    # Use ValidatorFactory for auto-detection
    validator = ValidatorFactory.get_validator(file_path)

    # Validate using appropriate validator
    result = validator.validate_file(file_path)

    # Format response
    return [TextContent(text=format_result(result))]
```

---

### With coderef-docs

**Foundation doc generation**:
```python
# After generating README.md, validate it
from papertrail.validators.foundation import FoundationDocValidator

validator = FoundationDocValidator()
result = validator.validate_file(Path("README.md"))

if not result.valid:
    print(f"❌ Validation failed (score: {result.score}/100)")
    # Fix issues and regenerate
```

---

### Pre-Commit Hook

**Validate all staged markdown files**:
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

## Examples: Usage Patterns

### Example 1: Basic Validation
```python
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

# Auto-detect and validate
validator = ValidatorFactory.get_validator(Path("README.md"))
result = validator.validate_file(Path("README.md"))

print(f"Valid: {result.valid}")
print(f"Score: {result.score}/100")
print(f"Completeness: {result.completeness}%")

for error in result.errors:
    print(f"[{error.severity.value}] {error.message}")
```

### Example 2: Manual Validator Selection
```python
from papertrail.validators.foundation import FoundationDocValidator

# Manually select validator
validator = FoundationDocValidator()
result = validator.validate_file(Path("API.md"))

if result.valid and result.score >= 95:
    print("✅ Excellent documentation quality!")
```

### Example 3: Batch Validation
```python
from pathlib import Path
from papertrail.validators.factory import ValidatorFactory

docs_dir = Path("coderef/foundation-docs")
results = []

for file in docs_dir.glob("*.md"):
    validator = ValidatorFactory.get_validator(file)
    result = validator.validate_file(file)
    results.append((file.name, result.score))

avg_score = sum(r[1] for r in results) / len(results)
print(f"Average score: {avg_score:.1f}/100")
```

### Example 4: Resource Sheet Validation
```python
from papertrail.validators.resource_sheet import ResourceSheetValidator

validator = ResourceSheetValidator()
result = validator.validate_file(Path("AuthService-RESOURCE-SHEET.md"))

if result.score >= 90:
    print(f"✅ RSMS v2.0 compliant (score: {result.score}/100)")
else:
    print(f"❌ RSMS v2.0 violations (score: {result.score}/100)")
    for error in result.errors:
        print(f"  - {error.message}")
```

---

## Dependencies

### Internal Dependencies

| Validator | Depends On |
|-----------|-----------|
| All Category Validators | BaseUDSValidator |
| BaseUDSValidator | UDSValidator (papertrail/validator.py) |
| BaseUDSValidator | JSON Schema Draft-07 (schemas/documentation/) |
| FoundationDocValidator | Code Validator (papertrail/tools/code_validator.py) |
| ValidatorFactory | All 13 validators |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `jsonschema` | 4.x | JSON Schema Draft-07 validation |
| `pyyaml` | 6.x | YAML frontmatter parsing |
| `pathlib` | stdlib | File path handling |

---

## References

### Internal
- **BaseUDSValidator**: `papertrail/validators/base.py` (150+ lines, 8 methods)
- **ValidatorFactory**: `papertrail/validators/factory.py` (200+ lines, 30+ patterns)
- **ValidationResult**: `papertrail/validator.py` (dataclass)
- **SchemaSyncTool**: `papertrail/tools/sync_schemas.py` (380 lines, schema completeness validation)
- **13 Category Validators**: `papertrail/validators/{foundation,workorder,system,standards,user_facing,migration,infrastructure,session,plan,resource_sheet,stub,analysis,execution_log,general}.py`

### External
- [JSON Schema Draft-07 Specification](https://json-schema.org/draft-07/schema)
- [Universal Documentation Standards (UDS)](../standards/documentation/uds-specification.md)
- [Resource Sheet Metadata Standards (RSMS) v2.0](../standards/documentation/resource-sheet-standards.md)
- [Template Method Pattern](https://refactoring.guru/design-patterns/template-method)
- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)

### Related Documents
- [API.md](API.md) - MCP tools for validation
- [SCHEMA.md](SCHEMA.md) - JSON schema definitions
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [README.md](README.md) - Project overview

---

**Last Updated:** 2026-01-13
**Version:** 1.0.0
**Maintained by:** CodeRef Ecosystem - Papertrail MCP Server
