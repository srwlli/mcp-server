#!/usr/bin/env python3
"""
Papertrail Live Demo - See it in action!

Demonstrates all core features of Papertrail.
"""

from papertrail import (
    UDSHeader,
    UDSFooter,
    DocumentStatus,
    TemplateEngine,
    create_template_engine,
    validate_uds,
    calculate_health
)
from papertrail.extensions import GitExtension, WorkflowExtension
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("PAPERTRAIL LIVE DEMO")
print("Universal Documentation Standards for CodeRef Ecosystem")
print("=" * 80)

# ============================================================================
# DEMO 1: Create a Document with UDS Headers
# ============================================================================
print("\n[DEMO 1] Generate Document with UDS Headers")
print("-" * 80)

# Create UDS Header
header = UDSHeader(
    workorder_id="WO-PAPERTRAIL-DEMO-001",
    generated_by="papertrail v1.0.0",
    feature_id="papertrail-demo",
    timestamp=datetime.utcnow().isoformat() + "Z",
    title="Papertrail Demo Document",
    version="1.0.0",
    status=DocumentStatus.DRAFT
)

# Create UDS Footer
footer = UDSFooter(
    copyright_year=2025,
    organization="CodeRef Ecosystem",
    generated_by="papertrail v1.0.0",
    workorder_id="WO-PAPERTRAIL-DEMO-001",
    feature_id="papertrail-demo",
    last_updated=datetime.utcnow().strftime("%Y-%m-%d")
)

# Create document content
content = """# Papertrail Demo Document

## What is Papertrail?

Papertrail is a Universal Documentation Standards (UDS) system for the CodeRef ecosystem. It provides:

- **Complete Traceability**: Every document links to its workorder
- **MCP Attribution**: Know which server generated each doc
- **Quality Scoring**: 0-100 health scores for documentation
- **Schema Validation**: Enforce required sections
- **Template Engine**: Jinja2 with CodeRef extensions

## Key Features

1. **UDS Headers**: YAML frontmatter with workorder_id, timestamps, attribution
2. **UDS Footers**: Copyright, workorder tracking, AI assistance flags
3. **Validation**: Schema-based validation for 5 doc types
4. **Health Scoring**: 4-factor scoring (traceability, completeness, freshness, validation)
5. **Template Engine**: Jinja2 with git/workflow/coderef extensions

## Example Usage

```python
from papertrail import UDSHeader, TemplateEngine

header = UDSHeader(
    workorder_id="WO-MY-FEATURE-001",
    generated_by="coderef-docs v2.0.0",
    feature_id="my-feature",
    timestamp="2025-12-29T20:00:00Z"
)

engine = TemplateEngine()
doc = engine.inject_uds(content, header)
```

## Status

**Phase 1**: Core UDS (31/31 tests passing)
**Phase 2**: Template Engine (44/44 tests passing)
**Phase 3**: coderef-docs integration (6/6 tests passing)
**Phase 4**: Gradual rollout (ready to start)

## Conclusion

Papertrail brings complete documentation traceability and quality scoring to the CodeRef ecosystem.
"""

# Inject UDS
engine = TemplateEngine()
final_doc = engine.inject_uds(content, header, footer)

# Save to file
output_file = Path(__file__).parent / "DEMO_OUTPUT.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_doc)

print(f"[SUCCESS] Generated document with UDS")
print(f"[OUTPUT] Saved to: {output_file}")
print("\nFirst 500 characters of output:")
print("-" * 80)
print(final_doc[:500])
print("-" * 80)

# ============================================================================
# DEMO 2: Validate Document Against UDS Schema
# ============================================================================
print("\n[DEMO 2] Validate Document Against UDS Schema")
print("-" * 80)

result = validate_uds(final_doc, "readme")

print(f"Validation Result: {'[VALID]' if result.valid else '[INVALID]'}")
print(f"Validation Score: {result.score}/100")
print(f"Errors: {len(result.errors)}")
print(f"Warnings: {len(result.warnings)}")

if result.errors:
    print("\nErrors:")
    for error in result.errors:
        print(f"  [{error.severity}] {error.message}")

if result.warnings:
    print("\nWarnings:")
    for warning in result.warnings:
        print(f"  [{warning.severity}] {warning.message}")

# ============================================================================
# DEMO 3: Calculate Health Score
# ============================================================================
print("\n[DEMO 3] Calculate Document Health Score")
print("-" * 80)

health = calculate_health(final_doc, "readme")

print(f"Overall Score: {health.score}/100")
print(f"\nBreakdown:")
print(f"  Traceability:  {health.traceability}/40  (workorder_id, feature_id, attribution)")
print(f"  Completeness:  {health.completeness}/30  (required sections present)")
print(f"  Freshness:     {health.freshness}/20  (document age)")
print(f"  Validation:    {health.validation}/10  (passes schema)")

print(f"\nDetails:")
print(f"  Has workorder_id:     {health.has_workorder_id}")
print(f"  Has feature_id:       {health.has_feature_id}")
print(f"  Has MCP attribution:  {health.has_mcp_attribution}")
print(f"  Document age:         {health.age_days} days")
print(f"  Passes validation:    {health.passes_validation}")

# ============================================================================
# DEMO 4: Template Engine with Extensions
# ============================================================================
print("\n[DEMO 4] Template Engine with CodeRef Extensions")
print("-" * 80)

# Create template with extensions
template_content = """# {{ project_name }}

## Git Statistics (Mock Data - Phase 2)
Commits: {{ git.stats().commits }}
Insertions: {{ git.stats().insertions }}
Deletions: {{ git.stats().deletions }}

## Contributors
{% for contributor in git.contributors() %}
- {{ contributor }}
{% endfor %}

## Workflow Progress (Mock Data - Phase 2)
Status: {{ workflow.plan('test-feature').status }}
Message: {{ workflow.plan('test-feature').message }}
"""

# Create engine with extensions
engine_with_ext = create_template_engine(extensions={
    "git": GitExtension(),
    "workflow": WorkflowExtension()
})

# Render
rendered = engine_with_ext.render(template_content, {
    "project_name": "Papertrail Demo"
})

print("Rendered template with extensions:")
print("-" * 80)
print(rendered)
print("-" * 80)
print("\n[NOTE] Extensions currently return mock data (Phase 2)")
print("       Phase 3+ will connect to real MCP servers")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("DEMO SUMMARY")
print("=" * 80)
print(f"[SUCCESS] Document generated with UDS: {output_file}")
print(f"[SUCCESS] Validation: {'PASSED' if result.valid else 'FAILED'} (Score: {result.score}/100)")
print(f"[SUCCESS] Health Score: {health.score}/100")
print(f"[SUCCESS] Template engine with extensions: Working")
print("=" * 80)
print(f"\nView the complete document: {output_file}")
print("=" * 80)
