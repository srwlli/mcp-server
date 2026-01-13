---
agent: Claude Sonnet 4.5
date: "2026-01-13"
task: CREATE
workorder_id: WO-FOUNDATION-DOCS-001
generated_by: Claude Code
feature_id: foundation-documentation
doc_type: components
---

# Papertrail Validator Components

## Component Catalog

### Base Validator
**Class:** BaseUDSValidator
**File:** papertrail/validators/base.py
**Purpose:** Abstract base class providing common validation functionality

### Category Validators (10)
1. **FoundationDocValidator** - Foundation docs (README, ARCHITECTURE, API, SCHEMA, COMPONENTS)
2. **WorkorderDocValidator** - Workorder docs (plan, deliverables, analysis)
3. **SystemDocValidator** - System docs (CLAUDE.md, SYSTEM.md)
4. **StandardsDocValidator** - Standards docs (coding/doc standards)
5. **UserFacingDocValidator** - User docs (tutorial, faq, troubleshooting)
6. **UserGuideValidator** - User guides (extends UserFacingDocValidator)
7. **QuickrefValidator** - Quickstart/reference docs (extends UserFacingDocValidator)
8. **MigrationDocValidator** - Migration docs
9. **InfrastructureDocValidator** - Infrastructure docs
10. **SessionDocValidator** - Multi-agent session docs

### Specialized Validators (3)
11. **PlanValidator** - plan.json validation
12. **ResourceSheetValidator** - RSMS v2.0 compliance
13. **GeneralMarkdownValidator** - Fallback for unclassified docs

## Props/Parameters

### BaseUDSValidator
**Constructor:**
- schema_name: str (JSON schema filename)

**Methods:**
- validate_file(file_path: Path) -> ValidationResult
- validate_content(content: str, file_path: Optional[Path]) -> ValidationResult
- code_example_validation(frontmatter: dict, content: str) -> list[ValidationError]
- _calculate_completeness(frontmatter: dict, content: str) -> Optional[int]

### ValidationResult
**Properties:**
- valid: bool (True if score >= 90)
- errors: list[ValidationError]
- warnings: list[str]
- score: int (0-100)
- completeness: Optional[int] (0-100%)

### ValidationError
**Properties:**
- severity: ValidationSeverity (CRITICAL, MAJOR, MINOR, WARNING)
- message: str
- field: Optional[str]

## Usage Examples

### Example 1: Validate Foundation Doc
```python
from papertrail.validators.foundation import FoundationDocValidator

validator = FoundationDocValidator()
result = validator.validate_file(Path("README.md"))

if not result.valid:
    print(f"Validation failed: {result.score}/100")
    for error in result.errors:
        print(f"- {error.message}")
```

### Example 2: Validate Resource Sheet  
```python
from papertrail.validators.resource_sheet import ResourceSheetValidator

validator = ResourceSheetValidator()
result = validator.validate_file(Path("coderef/resources-sheets/Auth-Service-RESOURCE-SHEET.md"))

print(f"Score: {result.score}/100")
print(f"Completeness: {result.completeness}%")
```

### Example 3: Auto-Detect Validator
```python
from papertrail.validators.factory import ValidatorFactory

validator = ValidatorFactory.get_validator(Path("CLAUDE.md"))
# Returns SystemDocValidator

result = validator.validate_file(Path("CLAUDE.md"))
```

## Dependencies

### Required
- Python 3.10+
- jsonschema 4.17+
- pydantic 2.0+
- PyYAML 6.0+

### Optional
- coderef-context (for code example validation)

---

**Last Updated:** 2026-01-13
**Maintained by:** Papertrail Team
