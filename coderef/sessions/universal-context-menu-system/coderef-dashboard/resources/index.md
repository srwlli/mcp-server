# Resources Index - coderef-dashboard

## Session Documents
- [Analysis Document](../../ANALYSIS.md) - Full problem analysis and proposed solution
- [Context JSON](../../../coderef-dashboard/coderef/working/universal-context-menu-system/context.json) - Original session context

## Existing Implementations (Study These)
- [AddFileToBoardMenu](../../../coderef-dashboard/packages/dashboard/src/components/coderef/AddFileToBoardMenu.tsx) - Best implementation (486 lines, lazy loading, 4 actions)
- [BoardContextMenu](../../../coderef-dashboard/packages/dashboard/src/components/BoardContextMenu/index.tsx) - Needs improvement (192 lines, eager loading)
- [ContextMenu](../../../coderef-dashboard/packages/dashboard/src/components/coderef/ContextMenu.tsx) - Base component (372 lines, REUSE THIS)

## Existing Hooks (Study These)
- [useBoards](../../../coderef-dashboard/packages/dashboard/src/hooks/useBoards.ts) - 30s cache, global cache - USE THIS
- [useBoardHierarchy](../../../coderef-dashboard/packages/dashboard/src/hooks/useBoardHierarchy.ts) - Lazy loading - USE THIS
- [useBoardsCache](../../../coderef-dashboard/packages/dashboard/src/hooks/useBoardsCache.ts) - Monolithic, eager - DEPRECATE THIS

## Existing Helpers (Extract Logic From)
- [file-to-board-helpers.ts](../../../coderef-dashboard/packages/dashboard/src/lib/boards/file-to-board-helpers.ts) - 270 lines of file conversion logic

## Type Definitions
- [boards.ts](../../../coderef-dashboard/packages/dashboard/src/types/boards.ts) - Board, BoardList, BoardCard interfaces
- [board-integration.ts](../../../coderef-dashboard/packages/dashboard/src/types/board-integration.ts) - Integration types

## Technical Context
- Agent Home: `C:\Users\willh\Desktop\coderef-dashboard`
- Session: `C:\Users\willh\.mcp-servers\coderef\sessions\universal-context-menu-system`
- Phase: phase_1 (Implementation)
- Workorder: WO-UNIVERSAL-CTX-MENU-001-DASHBOARD
