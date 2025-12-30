#!/usr/bin/env python3
"""
Simple Phase 3 Test - Direct UDS testing

Tests Papertrail UDS generation without complex template system.
"""

import os
import sys

os.environ["PAPERTRAIL_ENABLED"] = "true"

from papertrail import UDSHeader, UDSFooter, DocumentStatus, TemplateEngine, create_template_engine
from papertrail.extensions import GitExtension, WorkflowExtension, CodeRefContextExtension

print("=" * 70)
print("PHASE 3 SIMPLE INTEGRATION TEST")
print("=" * 70)

# Test 1: UDS Header/Footer Generation
print("\n[TEST 1] UDS Header and Footer Generation")
print("-" * 70)

header = UDSHeader(
    workorder_id="WO-TEST-PHASE3-001",
    generated_by="coderef-docs v2.0.0",
    feature_id="phase3-test",
    timestamp="2025-12-29T20:00:00Z",
    title="Test Document",
    version="1.0.0",
    status=DocumentStatus.DRAFT
)

footer = UDSFooter(
    copyright_year=2025,
    organization="CodeRef",
    generated_by="coderef-docs v2.0.0",
    workorder_id="WO-TEST-PHASE3-001",
    feature_id="phase3-test",
    last_updated="2025-12-29"
)

print("Header YAML:")
print(header.to_yaml())

print("\nFooter YAML:")
print(footer.to_yaml())

# Test 2: Template Engine with UDS Injection
print("\n[TEST 2] Template Engine with UDS Injection")
print("-" * 70)

# Create simple Jinja2 template
template_content = """# {{ title }}

## Overview
{{ description }}

## Version
{{ version }}
"""

# Create template engine
engine = create_template_engine(extensions={
    "git": GitExtension(),
    "workflow": WorkflowExtension()
})

# Render template
context = {
    "title": "Test Project",
    "description": "This is a test project for Phase 3 validation",
    "version": "1.0.0"
}

rendered = engine.render(template_content, context)

print("Rendered content (before UDS):")
print(rendered)

# Inject UDS
final_doc = engine.inject_uds(rendered, header, footer)

print("\n" + "=" * 70)
print("FINAL DOCUMENT (with UDS):")
print("=" * 70)
print(final_doc)

# Verify UDS present
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

checks = {
    "workorder_id present": "workorder_id: WO-TEST-PHASE3-001" in final_doc,
    "generated_by present": "generated_by: coderef-docs" in final_doc,
    "feature_id present": "feature_id: phase3-test" in final_doc,
    "timestamp present": "timestamp:" in final_doc,
    "copyright present": "Copyright" in final_doc,
    "content rendered": "Test Project" in final_doc,
}

all_passed = True
for check, result in checks.items():
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} {check}")
    if not result:
        all_passed = False

print("=" * 70)
if all_passed:
    print("\n[SUCCESS] All Phase 3 UDS features working correctly!\n")
    sys.exit(0)
else:
    print("\n[FAIL] Some checks failed.\n")
    sys.exit(1)
