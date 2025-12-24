Extract coding standards from the current project by scanning for UI/UX/behavior patterns.

Call the `mcp__coderef-docs__establish_standards` tool with the current working directory as the project_path.

This will:
1. Scan the codebase for React/frontend components
2. Extract UI patterns (button sizes/variants, modals, colors, typography, spacing, icons)
3. Extract behavior patterns (error handling, loading states, toasts, validation rules)
4. Extract UX patterns (navigation, permissions, offline handling, accessibility)
5. Build a component inventory with metadata

The tool will create 4 standards documents in coderef/standards/:
- UI-STANDARDS.md
- BEHAVIOR-STANDARDS.md
- UX-PATTERNS.md
- COMPONENT-INDEX.md

**Run this ONCE per project** to establish baseline standards.