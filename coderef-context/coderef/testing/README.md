# coderef-context Testing

**Unit & Integration Tests for Code Intelligence Server**

---

## Quick Links

- **Central Hub:** `../../../../coderef/testing/INDEX.md`
- **This Server's Results:** `results/2025-12-26/`
- **Test Coverage:** All 10 tools (scan, query, impact, complexity, patterns, coverage, context, validate, drift, diagram)

---

## Test Structure

```
coderef-context/coderef/testing/
├── README.md (this file)
├── results/
│   ├── 2025-12-26/
│   │   ├── test-scan-tool.md
│   │   ├── test-query-tool.md
│   │   ├── test-impact-tool.md
│   │   ├── test-complexity-tool.md
│   │   ├── test-patterns-tool.md
│   │   └── ...
│   └── LATEST/ → symlink
└── unit/
    ├── test-scan.py (or .md)
    ├── test-query.py (or .md)
    └── ...
```

---

## Tools to Test

| Tool | Purpose | Status | Result File |
|------|---------|--------|-------------|
| coderef_scan | Discover code elements | ⏳ Pending | `results/2025-12-26/test-scan-tool.md` |
| coderef_query | Query relationships | ⏳ Pending | `results/2025-12-26/test-query-tool.md` |
| coderef_impact | Impact analysis | ⏳ Pending | `results/2025-12-26/test-impact-tool.md` |
| coderef_complexity | Complexity metrics | ⏳ Pending | `results/2025-12-26/test-complexity-tool.md` |
| coderef_patterns | Pattern discovery | ⏳ Pending | `results/2025-12-26/test-patterns-tool.md` |
| coderef_coverage | Test coverage | ⏳ Pending | `results/2025-12-26/test-coverage-tool.md` |
| coderef_context | Codebase context | ⏳ Pending | `results/2025-12-26/test-context-tool.md` |
| coderef_validate | Reference validation | ⏳ Pending | `results/2025-12-26/test-validate-tool.md` |
| coderef_drift | Drift detection | ⏳ Pending | `results/2025-12-26/test-drift-tool.md` |
| coderef_diagram | Diagram generation | ⏳ Pending | `results/2025-12-26/test-diagram-tool.md` |

---

## Test Status

**Completed:** 0/10 tools tested
**In Progress:** 0/10 tools
**Pending:** 10/10 tools

**Overall:** ⏳ Setup phase complete, tests pending

---

**Last Updated:** 2025-12-26
**Maintained by:** willh, Claude Code AI

