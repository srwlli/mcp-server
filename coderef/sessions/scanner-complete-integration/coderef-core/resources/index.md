# Resources Index

## Primary Specifications
- [Scanner Effectiveness Improvements Resource Sheet](../../../../coderef-dashboard/packages/coderef-core/coderef/resources-sheets/Scanner-Effectiveness-Improvements-RESOURCE-SHEET.md)
- [Consolidated Scanner Resource Sheet](../../../../coderef-dashboard/packages/coderef-core/src/scanner/CONSOLIDATED-SCANNER-RESOURCE-SHEET.md)

## Existing Implementation
- [AST Element Scanner](../../../../coderef-dashboard/packages/coderef-core/src/analyzer/ast-element-scanner.ts) - Already exists, needs integration
- [Main Scanner](../../../../coderef-dashboard/packages/coderef-core/src/scanner/scanner.ts) - Needs AST integration
- [Types](../../../../coderef-dashboard/packages/coderef-core/src/types/types.ts) - ElementData interface

## Reference Sessions
- [Context Enhancement V2](../../context-enhancement-v2/) - Phase 1 complete, scanner Phase 1 improvements implemented
- [Scanner Context Enhancement V1](../../archived/scanner-context-enhancement-v1/) - Original session (archived)

## Technical Context
- **Agent Home:** `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core`
- **Session:** `C:\Users\willh\.mcp-servers\coderef\sessions\scanner-complete-integration\coderef-core`
- **Phase:** phase_1
- **Tasks:** 7 scanner improvements (P1.1, P1.2, P2.4, P2.5, P3.7, P3.8, P4.11)
- **Goal:** 95% accuracy, 3-5x performance, enhanced coverage

## Success Metrics
- **Accuracy:** 85% → 95%+ (detect interfaces, decorators, type aliases, properties)
- **Performance:** 1185ms → 300-400ms (3-5x faster via parallelization)
- **Memory:** Unbounded → 50MB cap (LRU caching)
- **Coverage:** 7 types → 12+ types (expanded detection)
