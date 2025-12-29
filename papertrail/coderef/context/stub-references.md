# Source Documentation References

This document links to the original stubs and source materials that informed the Papertrail workorder.

---

## Original Stubs (Consolidated)

### STUB-058: mcp-doc-standards-integration
**Path:** `C:\Users\willh\Desktop\assistant\coderef\working\mcp-doc-standards-integration\stub.json`

**Summary:** Integrate UDS Document Standards into MCP Servers with headers/footers for workorder tracking and MCP attribution.

**Key Contributions:**
- UDS header template with workorder_id, generated_by, feature_id, timestamp
- UDS footer template with workorder reference, next review date, MCP server attribution
- Example enhanced header/footer structures
- Phase-based implementation strategy

**Incorporated Into:** Phase 1 - Core UDS (headers/footers)

---

### STUB-064: uds-framework-coderef-docs
**Path:** `C:\Users\willh\Desktop\assistant\coderef\working\uds-framework-coderef-docs\stub.json`

**Summary:** Extract Papertrail's UDS framework for document type schemas, validation, and governance.

**Key Contributions:**
- Document type definitions (README, ARCHITECTURE, API, DELIVERABLES, COMPONENTS, SCHEMA)
- Required sections per document type
- Placeholder tokens ({{WORKORDER_ID}}, {{FEATURE_NAME}}, etc.)
- UDSValidator class concept
- /validate-docs MCP tool specification

**Incorporated Into:** Phase 1 - Core UDS (schemas, validation)

---

### STUB-059: papertrail-mcp-integration
**Path:** `C:\Users\willh\Desktop\assistant\coderef\working\papertrail-mcp-integration\stub.json`

**Summary:** Integrate Papertrail's AI-powered documentation generation for auto-generating UDS-compliant docs from plan.json.

**Key Contributions:**
- AI Generator concept (auto-generate DELIVERABLES.md, API.md, ARCHITECTURE.md)
- Papertrail Search Engine for document discovery
- Multi-format export ideas
- Time-to-docs goal (<30 seconds)

**Incorporated Into:** Future enhancement (Phase 2 - AI layer, deferred)

---

## Papertrail Source Code

### Location
`C:\Users\willh\Desktop\ARCHIVED\projects-idle\paper-trail-parsed-into-modules\`

### Key Modules Referenced

**1. UDS Framework**
- **File:** `uds-framework/uds.ts` (623 lines)
- **Purpose:** UDS schema definitions for 9 document types with required/optional sections
- **Adaptation:** Port to Python, simplify to 5 CodeRef-specific types

**2. Template Engine**
- **File:** `updated-template-engine/template-engine-app/template-engine-extended.ts`
- **Purpose:** Advanced templating with inheritance, conditionals, includes, extension points
- **Adaptation:** Port core features to Python, add CodeRef extensions

**3. Document System**
- **File:** `document-systems/document-system.ts` (543 lines)
- **Purpose:** Full document lifecycle with versioning, health metrics, search, validation
- **Adaptation:** Extract health metrics and validation concepts, skip version control (use git)

### What We're Skipping
- Version control (already have git)
- Search indexing (already have grep)
- Full document management system (too complex)
- Complex conditional logic (YAGNI)

---

## Design Documents (This Project)

### CODEREF_TAILORED_DESIGN.md
**Path:** `../context/CODEREF_TAILORED_DESIGN.md`

**Summary:** How we adapt Papertrail to be CodeRef-native, not generic.

**Key Sections:**
- CodeRef-specific UDS schemas (plan, deliverables, architecture, readme, api)
- Template engine extensions (coderef-context, git, workflow integrations)
- CodeRef-specific health scoring
- CodeRef-specific validation rules
- Integration with existing MCP tools

---

### SAFE_DEVELOPMENT_PLAN.md
**Path:** `../context/SAFE_DEVELOPMENT_PLAN.md`

**Summary:** 6-phase safe development strategy for Papertrail integration.

**Key Sections:**
- Option 1: Parallel Development Server approach (original)
- Phase 0: Setup parallel dev servers
- Phases 1-4: Development in isolation
- Phase 5: Production integration with feature flags
- Rollback plans and safety guarantees

**Note:** Superseded by Python package approach, but safety principles still apply.

---

### context-v2.md
**Path:** `../context/context-v2.md`

**Summary:** Draft architecture for Papertrail as Python package.

**Key Sections:**
- Core architecture (Python package → coderef-docs → ecosystem)
- Integration pattern (like coderef-context)
- What Papertrail provides (UDS, validation, health, templates)
- Implementation phases

---

## Workorder Documents

### context.json
**Path:** `../workorder/papertrail-python-package/context.json`

**Summary:** Complete requirements, motivation, and success criteria for WO-PAPERTRAIL-PYTHON-PACKAGE-001.

---

### plan.json
**Path:** `../workorder/papertrail-python-package/plan.json`

**Summary:** Full 4-phase implementation plan with 36 tasks, testing strategy, and success criteria.

---

### README.md
**Path:** `../workorder/papertrail-python-package/README.md`

**Summary:** Quick reference guide for the workorder.

---

## Universal Documentation Standards (UDS) Source

### Header Template
**Path:** `C:\Users\willh\Desktop\ARCHIVED\projects - back up\Universal-Documentation-Standards\templates\document-templates\standard-document-header-template.md`

**Format:**
```markdown
---
# [Project Name]
#### [Document Type] | V[X.Y.Z]
#### Created with AI assistance
---
```

**Enhanced Version (Papertrail):**
```yaml
---
title: Authentication System Architecture
version: 2.1.0
generated_by: coderef-docs v1.2.0
workorder_id: WO-AUTH-SYSTEM-001
feature_id: auth-system
status: APPROVED
timestamp: 2025-12-28T10:15:00Z
classification: INTERNAL
---
```

---

### Footer Template
**Path:** `C:\Users\willh\Desktop\ARCHIVED\projects - back up\Universal-Documentation-Standards\templates\document-templates\standard-document-footer-template.md`

**Format:**
```markdown
---
Copyright © {{YEAR}} | {{ORGANIZATION}}
Last updated: {{YYYY-MM-DD}} | Assisted by AI | Status: {{DRAFT|REVIEW|APPROVED|DEPRECATED}}
---
```

**Enhanced Version (Papertrail):**
```yaml
---
Copyright © 2025 | CodeRef Ecosystem
Generated by: coderef-docs v1.2.0
Workorder: WO-AUTH-SYSTEM-001
Feature: auth-system
Last Updated: 2025-12-28
AI Assistance: true
Status: APPROVED
Next Review: 2026-01-28
---
```

---

## Related MCP Servers

### coderef-docs
**Path:** `C:\Users\willh\.mcp-servers\coderef-docs\`
**Role:** Documentation authority - will integrate Papertrail package

### coderef-context
**Path:** `C:\Users\willh\.mcp-servers\coderef-context\`
**Role:** Code intelligence authority - provides dependency graphs, impact analysis for Papertrail extensions

### coderef-workflow
**Path:** `C:\Users\willh\.mcp-servers\coderef-workflow\`
**Role:** Planning authority - provides plan.json, workorder context for Papertrail extensions

---

## Changelog

**2025-12-29:** Created stub-references.md consolidating all source documentation
