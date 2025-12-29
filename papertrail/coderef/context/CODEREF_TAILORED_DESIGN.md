# Papertrail → CodeRef Tailored Design

**Goal:** Adapt Papertrail to be CodeRef-native, not generic

---

## 1. CodeRef-Specific UDS Schemas

**Replace generic schemas with CodeRef docs:**

| Papertrail (Generic) | CodeRef (Specific) | Why? |
|---------------------|-------------------|------|
| readme, api, architecture | plan.json | Workorder planning is unique to CodeRef |
| user_guide | DELIVERABLES.md | Execution tracking unique to CodeRef |
| changelog | CHANGELOG.json | Version tracking with workorder links |
| deployment | analysis-report.md | coderef-context exports |
| testing | test-report.md | coderef-testing exports |
| - | ARCHITECTURE.md | Foundation docs (existing POWER) |
| - | README.md | Foundation docs (existing POWER) |
| - | API.md | Foundation docs (existing POWER) |

**New Schema: plan.json**
```json
{
  "uds_schema": {
    "document_type": "implementation_plan",
    "required_sections": [
      "META_DOCUMENTATION",
      "0_preparation",
      "1_executive_summary",
      "2_risk_assessment",
      "6_implementation_phases",
      "8_success_criteria"
    ],
    "required_metadata": {
      "workorder_id": "^WO-[A-Z0-9-]+-\\d{3}$",
      "feature_name": "^[a-z0-9_-]+$",
      "generated_by": "coderef-workflow v*"
    }
  }
}
```

**New Schema: DELIVERABLES.md**
```json
{
  "uds_schema": {
    "document_type": "execution_tracking",
    "required_sections": [
      "Overview",
      "Completion Status",
      "Implementation Metrics",
      "Testing & Validation"
    ],
    "required_metadata": {
      "workorder_id": "string",
      "feature_id": "string",
      "status": "enum[NOT_STARTED|IN_PROGRESS|COMPLETE]"
    }
  }
}
```

---

## 2. Template Engine Extensions (CodeRef Integration)

**Extend template engine to call MCP tools:**

### Extension Point: coderef-context Integration

```python
# papertrail/extensions/coderef_context.py

class CodeRefContextExtension:
    """Template extension calling coderef-context tools"""

    async def scan(self, project_path: str) -> dict:
        """{% coderef.scan project_path %}"""
        result = await mcp.call("coderef-context", "coderef_scan", {
            "project_path": project_path
        })
        return result

    async def query(self, element: str, query_type: str = "calls") -> dict:
        """{% coderef.query "AuthService" "calls" %}"""
        result = await mcp.call("coderef-context", "coderef_query", {
            "target": element,
            "query_type": query_type
        })
        return result

    async def impact(self, element: str) -> dict:
        """{% coderef.impact "deleteUser" %}"""
        result = await mcp.call("coderef-context", "coderef_impact", {
            "element": element
        })
        return result
```

**Template Usage:**
```markdown
# Architecture Documentation

## Component Dependencies

{% coderef.scan "/path/to/project" %}
<!-- Auto-injects dependency graph from coderef-context -->

## Impact Analysis

Changing `AuthService.login()` affects:
{% coderef.impact "AuthService#login" %}
<!-- Auto-injects impact analysis -->
```

---

### Extension Point: coderef-workflow Integration

```python
# papertrail/extensions/coderef_workflow.py

class CodeRefWorkflowExtension:
    """Inject workorder context into templates"""

    async def get_plan(self, feature_name: str) -> dict:
        """{% workflow.plan "auth-system" %}"""
        # Read plan.json from coderef/workorder/{feature_name}/
        pass

    async def get_tasks(self, feature_name: str) -> list:
        """{% workflow.tasks "auth-system" %}"""
        # Extract tasks from plan.json
        pass

    async def get_progress(self, feature_name: str) -> dict:
        """{% workflow.progress "auth-system" %}"""
        # Calculate completion percentage
        pass
```

**Template Usage:**
```markdown
# Implementation Plan Summary

{% workflow.plan "auth-system" %}
<!-- Auto-injects plan metadata -->

## Task Breakdown

{% workflow.tasks "auth-system" %}
<!-- Auto-generates task list -->

Progress: {% workflow.progress "auth-system" %}%
```

---

### Extension Point: Git Integration

```python
# papertrail/extensions/git_integration.py

class GitExtension:
    """Git statistics for DELIVERABLES"""

    def get_stats(self, feature_name: str) -> dict:
        """{% git.stats "auth-system" %}"""
        # Run git log, count commits, LOC changes
        return {
            "commits": 15,
            "files_changed": 23,
            "insertions": 450,
            "deletions": 120,
            "contributors": ["Agent1", "Agent2"]
        }

    def get_last_commit(self) -> dict:
        """{% git.last_commit %}"""
        # Get latest commit info
        pass
```

**Template Usage (DELIVERABLES.md):**
```markdown
## Implementation Metrics

{% git.stats "auth-system" %}
<!-- Auto-fills:
- Total Commits: 15
- Files Changed: 23
- Lines Added: 450
- Lines Removed: 120
- Contributors: Agent1, Agent2
-->
```

---

## 3. CodeRef-Specific Health Scoring

**Custom health metrics for CodeRef docs:**

```python
# papertrail/health.py

class CodeRefHealthScorer:
    def calculate_health(self, doc: str, doc_type: str) -> HealthScore:
        """
        CodeRef-specific health scoring (0-100)
        """
        score = 0

        # 1. Traceability (40 points)
        if has_workorder_id(doc):           score += 20
        if has_feature_id(doc):             score += 10
        if has_mcp_attribution(doc):        score += 10

        # 2. Completeness (30 points)
        if has_required_sections(doc, doc_type):  score += 20
        if has_examples(doc):                     score += 10

        # 3. Freshness (20 points)
        days_old = get_age_in_days(doc)
        if days_old < 7:    score += 20
        elif days_old < 30: score += 10
        elif days_old < 90: score += 5

        # 4. Validation (10 points)
        if validates_against_schema(doc, doc_type): score += 10

        return HealthScore(
            score=score,
            traceability=has_workorder_id(doc),
            completeness=has_required_sections(doc, doc_type),
            freshness=days_old,
            valid=validates_against_schema(doc, doc_type)
        )
```

---

## 4. CodeRef-Specific Validation Rules

**Enforce CodeRef standards:**

```python
# papertrail/validator.py

class CodeRefValidator:
    def validate(self, doc: str, doc_type: str) -> ValidationResult:
        errors = []
        warnings = []

        # CRITICAL: Every doc MUST have workorder_id
        if not has_workorder_id(doc):
            errors.append("CRITICAL: Missing workorder_id in header")

        # CRITICAL: Every doc MUST have MCP attribution
        if not has_generated_by(doc):
            errors.append("CRITICAL: Missing generated_by in header")

        # Doc-type specific validation
        if doc_type == "plan":
            if not has_10_sections(doc):
                errors.append("Plan must have 10 sections")

        elif doc_type == "deliverables":
            if not has_completion_status(doc):
                errors.append("DELIVERABLES must have completion status")

        elif doc_type == "changelog":
            if not has_version_number(doc):
                errors.append("CHANGELOG must have version number")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

---

## 5. Integration with Existing CodeRef Tools

**How Papertrail calls existing MCP tools:**

### coderef-context → Papertrail

```python
# When generating ARCHITECTURE.md with auto-injected dependency info

from papertrail import TemplateEngine
from papertrail.extensions import CodeRefContextExtension

engine = TemplateEngine()
engine.register_extension("coderef", CodeRefContextExtension())

template = """
# Architecture

## Component Graph

{% coderef.scan project_path %}

## Authentication Service

Dependencies:
{% coderef.query "AuthService" "depends-on" %}
"""

result = await engine.render(template, {
    "project_path": "/path/to/project"
})

# Result includes live data from coderef-context!
```

### coderef-workflow → Papertrail

```python
# When generating plan.json with UDS metadata

from papertrail import UDSHeader, UDSFooter

# coderef-workflow calls papertrail to add metadata
header = UDSHeader(
    workorder_id="WO-AUTH-SYSTEM-001",
    generated_by="coderef-workflow v1.0.0",
    feature_id="auth-system",
    timestamp=datetime.now().isoformat(),
    status="DRAFT"
)

plan_content = generate_plan(...)  # Existing logic
plan_with_uds = f"{header.to_yaml()}\n{plan_content}\n{footer.to_yaml()}"

# Save plan.json with UDS metadata
```

### coderef-testing → Papertrail

```python
# When generating test-report.md

from papertrail.extensions import GitExtension

template = """
# Test Report

## Metrics

{% git.stats feature_name %}

## Test Coverage

Coverage: {{ coverage }}%
Tests Passed: {{ tests_passed }}/{{ tests_total }}
"""

result = engine.render(template, {
    "feature_name": "auth-system",
    "coverage": 85,
    "tests_passed": 120,
    "tests_total": 125
})
```

---

## 6. Papertrail Package Structure (CodeRef-Tailored)

```
papertrail/
├── setup.py
├── papertrail/
│   ├── __init__.py
│   ├── uds.py                      # UDS headers/footers
│   ├── engine.py                   # Template engine with {% %} support
│   ├── validator.py                # CodeRef-specific validation
│   ├── health.py                   # CodeRef health scoring
│   ├── extensions/
│   │   ├── __init__.py
│   │   ├── coderef_context.py     # coderef-context integration
│   │   ├── coderef_workflow.py    # coderef-workflow integration
│   │   ├── git_integration.py     # Git stats extraction
│   │   └── mcp_client.py          # MCP tool caller
│   └── schemas/
│       ├── plan.json              # plan.json schema
│       ├── deliverables.json      # DELIVERABLES.md schema
│       ├── changelog.json         # CHANGELOG.json schema
│       ├── architecture.json      # ARCHITECTURE.md schema (POWER)
│       └── readme.json            # README.md schema (POWER)
└── tests/
```

---

## 7. Usage Examples (CodeRef-Native)

### Example 1: Generate ARCHITECTURE.md with Live Code Analysis

```python
# coderef-docs uses papertrail with coderef-context extension

from papertrail import TemplateEngine, UDSHeader, UDSFooter
from papertrail.extensions import CodeRefContextExtension

engine = TemplateEngine()
engine.register_extension("coderef", CodeRefContextExtension())

# Template with dynamic code analysis
template = """
# {{project_name}} Architecture

## System Overview

{{overview}}

## Component Dependencies

{% coderef.scan project_path %}
<!-- Calls coderef-context → injects dependency graph -->

## Authentication Flow

{% coderef.query "AuthService" "calls" %}
<!-- Shows what AuthService calls -->
"""

# Render with UDS
header = UDSHeader(
    workorder_id="WO-ARCH-DOC-001",
    generated_by="coderef-docs v1.2.0",
    feature_id="architecture-update"
)

content = await engine.render(template, {
    "project_name": "CodeRef System",
    "project_path": "/path/to/coderef-system",
    "overview": "5-server MCP ecosystem..."
})

final = engine.inject_uds(content, header, footer)
```

**Result:** ARCHITECTURE.md with live dependency graph from coderef-context!

---

### Example 2: Generate DELIVERABLES.md with Git Stats

```python
# coderef-workflow generates DELIVERABLES with auto-filled metrics

from papertrail import TemplateEngine
from papertrail.extensions import GitExtension

engine = TemplateEngine()
engine.register_extension("git", GitExtension())

template = """
# Deliverables: {{feature_name}}

## Completion Status

Status: {{status}}

## Implementation Metrics

{% git.stats feature_name %}
<!-- Auto-fills from git log -->

## Files Modified

{% git.files feature_name %}
"""

content = await engine.render(template, {
    "feature_name": "auth-system",
    "status": "COMPLETE"
})
```

**Result:** DELIVERABLES.md with real git metrics, no manual input!

---

## 8. Benefits of CodeRef-Tailored Approach

| Generic Papertrail | CodeRef-Tailored Papertrail |
|-------------------|---------------------------|
| Generic doc types | CodeRef-specific (plan.json, DELIVERABLES) |
| Manual data entry | Auto-inject from coderef-context, git |
| No traceability | Every doc links to workorder |
| Standalone tool | Integrated with all 5 MCP servers |
| 9 generic schemas | 5 CodeRef schemas + POWER templates |
| No MCP awareness | First-class MCP tool integration |

---

## Next Steps

**Phase 1: Core UDS + CodeRef Schemas**
1. Define 5 CodeRef schemas (plan, deliverables, changelog, architecture, readme)
2. Build UDSHeader/UDSFooter generators
3. Test with real workorder

**Phase 2: Template Engine + Extensions**
1. Build basic template engine ({% if %}, {% include %})
2. Add coderef-context extension (scan, query, impact)
3. Add git extension (stats, files, contributors)

**Phase 3: Validation + Health**
1. CodeRef-specific validation rules
2. Health scoring with traceability checks
3. Integration testing with all 5 servers

**Should we start building Phase 1?**
