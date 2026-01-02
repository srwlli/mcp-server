# Resource Sheet System - Complete Reference Guide

**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001
**Created:** 2026-01-02
**Purpose:** Single source of truth for generating resource sheet documentation from code

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Innovation: Composable Modules](#core-innovation-composable-modules)
3. [The 8 User-Friendly Categories](#the-8-user-friendly-categories)
4. [Module Catalog](#module-catalog)
5. [Detection Logic](#detection-logic)
6. [3-Step Workflow](#3-step-workflow)
7. [Output Format Specifications](#output-format-specifications)
8. [Integration with .coderef/](#integration-with-coderef)
9. [Module Templates](#module-templates)
10. [Usage Examples](#usage-examples)
11. [Quality Standards](#quality-standards)

---

## System Overview

### What is a Resource Sheet?

A **resource sheet** is comprehensive technical documentation that covers:
- **WHAT** it is (architecture, purpose, role)
- **HOW** it works (state, behaviors, integration)
- **WHY** decisions were made (rationale, constraints)
- **WHEN** to use/modify it (patterns, pitfalls)

### Three Output Formats

**⚠️ CRITICAL: Every resource sheet MUST generate ALL 3 complementary formats:**

1. **Markdown (.md)** - Human-readable architectural reference (15-25 KB typical)
2. **JSON Schema (.json)** - Machine-readable type definitions and validation (8-15 KB typical)
3. **JSDoc (.txt)** - Inline code documentation suggestions (2-5 KB typical)

**Never stop after creating just the .md file.** All three outputs are required for a complete resource sheet.

### Authority Hierarchy

```
TypeScript Code = Runtime truth
JSDoc = Inline reference
JSON Schema = Validation truth
Markdown = Architectural truth
```

If conflicts arise, this hierarchy determines precedence.

---

## Core Innovation: Composable Modules

### The Problem with Templates

**Old Approach:** 20 rigid templates (top-level-widget, stateful-container, api-client, etc.)
- ❌ Massive duplication (copy "State" definition across 10+ templates)
- ❌ Hard to maintain (update "Performance" in 20 places)
- ❌ Technical jargon (developers don't think in these terms)

### The Solution: LEGO Blocks

**New Approach:** ~30-40 small modules that compose intelligently based on code characteristics

**Analogy:** Instead of 20 pre-built LEGO structures, provide 30-40 blocks that snap together based on what you're building.

### Module Types

**Universal Modules (Always Included):**
- `architecture` - Component hierarchy, dependencies, file structure
- `integration` - How it connects to other code
- `testing` - Test patterns, coverage, edge cases
- `performance` - Limits, bottlenecks, optimization opportunities

**Conditional Modules (Based on Code Analysis):**
- `endpoints` - API catalog (triggers: has fetch/axios calls)
- `auth` - Authentication strategy (triggers: manages JWT/tokens)
- `errors` - Error taxonomy (triggers: has try/catch, error classes)
- `state` - State management (triggers: useState, Redux, Zustand)
- `props` - React props documentation (triggers: React components)
- `events` - Event handlers (triggers: addEventListener, onClick)
- `lifecycle` - Component lifecycle (triggers: useEffect, componentDidMount)
- `validation` - Data validation (triggers: Zod, Yup, custom validators)
- `persistence` - Data persistence (triggers: localStorage, IndexedDB, API calls)
- `routing` - Navigation/routing (triggers: Next.js router, React Router)
- `accessibility` - A11y patterns (triggers: ARIA attributes, keyboard handlers)

---

## The 8 User-Friendly Categories

### Category Structure

```
modules/
├── tools/              # Helper utilities developers use
│   ├── cli-commands/
│   ├── scripts/
│   └── utilities/
├── ui/                 # Visual components users see
│   ├── widgets/
│   ├── pages/
│   └── components/
├── services/           # Backend logic and APIs
│   ├── api-endpoints/
│   ├── api-clients/
│   └── data-access/
├── state/              # Data storage and management
│   ├── hooks/
│   ├── stores/
│   └── context/
├── data/               # Data structures and validation
│   ├── models/
│   ├── schemas/
│   └── validators/
├── generators/         # Code/file creation tools
│   ├── scaffolding/
│   ├── templates/
│   └── migrations/
├── infrastructure/     # Build and deployment
│   ├── build-scripts/
│   ├── deployment/
│   └── ci-cd/
└── testing/            # Test utilities
    ├── test-helpers/
    ├── mocks/
    └── fixtures/
```

### Kitchen Analogy

| Category | Real Kitchen | Code Equivalent |
|----------|--------------|-----------------|
| **state/** | Pantry (stores ingredients) | useState, Redux, localStorage |
| **tools/** | Utensil drawer (things you use) | formatDate(), debounce(), CLI commands |
| **ui/** | Dining room (what you see) | Buttons, modals, pages |
| **services/** | Kitchen staff (does the work) | API calls, auth, database queries |
| **data/** | Recipe cards (instructions) | TypeScript types, Zod schemas |
| **generators/** | Meal prep machine (creates food) | Scaffolding tools, code generators |
| **infrastructure/** | Kitchen appliances (keeps things running) | Build scripts, Docker, CI/CD |
| **testing/** | Taste testers (check quality) | Jest helpers, mock data |

---

## Module Catalog

### Phase 1: Core Modules (15 Total)

#### Universal Modules (4)

**1. architecture**
- **Purpose:** Component hierarchy, dependencies, file structure
- **Always included:** Yes
- **Sections:** Component tree diagram, file organization, dependency graph
- **Example output:**
```markdown
## Architecture Overview

### Component Hierarchy
```
CodeRefExplorerWidget
├── ProjectSelector
├── ViewModeToggle
├── FileTree
│   ├── FileTreeNode (recursive)
│   └── ContextMenu
└── FileViewer
```

### File Structure
- packages/dashboard/src/widgets/coderef-explorer/CodeRefExplorerWidget.tsx
- packages/dashboard/src/components/coderef/FileTree.tsx
```

**2. integration**
- **Purpose:** How it connects to other code
- **Always included:** Yes
- **Sections:** Integration points, data flow, external dependencies
- **Example output:**
```markdown
## Integration Points

### Internal Dependencies
- ProjectSelector - Provides current project context
- FileViewer - Displays selected file content
- PromptingWorkflow - Receives file attachments

### External Dependencies
- localStorage - Persists favorites and state
- React Context - Shares state across components
```

**3. testing**
- **Purpose:** Test patterns, coverage, edge cases
- **Always included:** Yes
- **Sections:** Existing tests, coverage gaps, test recommendations
- **Example output:**
```markdown
## Testing Strategy

### Existing Coverage
- ✅ State management (favorites, tree expansion)
- ✅ localStorage persistence
- ✅ Cross-tab synchronization

### Coverage Gaps
- ❌ Keyboard navigation
- ❌ ARIA attribute validation
- ❌ Context menu positioning edge cases

### Recommended Tests
1. Test tree rendering with 500+ nodes (performance boundary)
2. Test localStorage quota exceeded scenario
3. Test corrupt favorites data recovery
```

**4. performance**
- **Purpose:** Limits, bottlenecks, optimization opportunities
- **Always included:** Yes
- **Sections:** Performance budgets, tested limits, optimization recommendations
- **Example output:**
```markdown
## Performance Considerations

### Tested Limits
- **Tree size:** Tested up to 500 nodes, renders in <100ms
- **localStorage:** Handles 5MB favorites data
- **Memory:** ~2MB per project with favorites

### Bottlenecks
- Recursive rendering of FileTreeNode (no virtualization)
- localStorage writes on every favorite change (no debouncing)

### Recommendations
- Implement virtual scrolling for trees >1000 nodes
- Debounce localStorage writes (500ms)
```

#### Conditional Modules (11)

**5. state**
- **Triggers:** useState, useReducer, Redux, Zustand, Jotai
- **Purpose:** Document state management patterns
- **Sections:** State ownership table, lifecycle, synchronization
- **Example output:**
```markdown
## State Management

### State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
| View mode | CodeRefExplorerWidget | React useState | localStorage |
| Project selection | ProjectSelector | React useState | localStorage |
| Favorites | FileTree | React useState | localStorage |
| File selection | FileTree | React useState | None (ephemeral) |
```

**6. props**
- **Triggers:** React components with props interfaces
- **Purpose:** Document component props
- **Sections:** Props reference table, validation, examples
- **Example output:**
```markdown
## Props Reference

### FileTreeProps

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tree | TreeNode[] | Yes | - | File tree structure |
| onFileSelect | (path: string) => void | Yes | - | Callback when file selected |
| favorites | FavoritesData | No | {} | Favorites configuration |
| viewMode | ViewMode | No | 'projects' | Display mode |
```

**7. events**
- **Triggers:** addEventListener, onClick, custom events
- **Purpose:** Document event handling patterns
- **Sections:** Event catalog, flow diagrams, handler contracts

**8. lifecycle**
- **Triggers:** useEffect, componentDidMount, cleanup functions
- **Purpose:** Document component lifecycle
- **Sections:** Initialization, cleanup, side effects

**9. endpoints**
- **Triggers:** fetch(), axios, API routes
- **Purpose:** API endpoint catalog
- **Sections:** Endpoint reference, request/response schemas, error codes

**10. auth**
- **Triggers:** JWT, sessions, auth tokens
- **Purpose:** Authentication strategy
- **Sections:** Auth flow, token management, permission model

**11. errors**
- **Triggers:** try/catch, error classes, error boundaries
- **Purpose:** Error taxonomy and handling
- **Sections:** Error types, recovery paths, user-facing messages

**12. validation**
- **Triggers:** Zod, Yup, custom validators
- **Purpose:** Data validation rules
- **Sections:** Validation schemas, error messages, sanitization

**13. persistence**
- **Triggers:** localStorage, IndexedDB, API calls
- **Purpose:** Data persistence strategy
- **Sections:** Storage mechanisms, sync patterns, migration paths

**14. routing**
- **Triggers:** Next.js router, React Router
- **Purpose:** Navigation patterns
- **Sections:** Route definitions, navigation flows, guards

**15. accessibility**
- **Triggers:** ARIA attributes, keyboard handlers
- **Purpose:** Accessibility patterns
- **Sections:** ARIA usage, keyboard navigation, screen reader support

---

## Detection Logic

### How Auto-Detection Works

**Step 1: Read .coderef/index.json**
```json
{
  "elements": [
    {
      "id": "FileTree.tsx#FileTree",
      "name": "FileTree",
      "type": "function",
      "file": "src/components/FileTree.tsx",
      "imports": ["react", "./FileTreeNode"],
      "exports": ["FileTree"],
      "metadata": {
        "props": ["tree", "onFileSelect", "favorites"],
        "hooks": ["useState", "useEffect"],
        "hasJSX": true
      }
    }
  ]
}
```

**Step 2: Analyze Characteristics**
```javascript
// Detection rules
const characteristics = {
  isReactComponent: metadata.hasJSX === true,
  usesState: hooks.includes('useState') || hooks.includes('useReducer'),
  hasProps: props.length > 0,
  hasLifecycle: hooks.includes('useEffect'),
  isAPI: file.includes('api/') || file.includes('routes/'),
  isCLI: file.includes('cli/') || name.endsWith('Command')
};
```

**Step 3: Map to Category**
```javascript
function detectCategory(element) {
  // UI: React components with JSX
  if (element.metadata.hasJSX) {
    if (element.file.includes('pages/')) return 'ui/pages';
    if (element.file.includes('widgets/')) return 'ui/widgets';
    return 'ui/components';
  }

  // State: Hooks and stores
  if (element.name.startsWith('use')) return 'state/hooks';
  if (element.file.includes('store') || element.file.includes('context')) return 'state/stores';

  // Services: API-related
  if (element.file.includes('api/') || element.file.includes('routes/')) return 'services/api-endpoints';
  if (element.name.includes('Client') || element.name.includes('Service')) return 'services/api-clients';

  // Tools: Utilities and helpers
  if (element.file.includes('utils/') || element.file.includes('helpers/')) return 'tools/utilities';
  if (element.file.includes('cli/')) return 'tools/cli-commands';

  // Data: Models and schemas
  if (element.file.includes('models/') || element.file.includes('schemas/')) return 'data/models';
  if (element.name.includes('Schema') || element.name.includes('Validator')) return 'data/schemas';

  // Generators: Code generation
  if (element.file.includes('generators/') || element.file.includes('templates/')) return 'generators/scaffolding';

  // Infrastructure: Build and deployment
  if (element.file.includes('scripts/') || element.name.includes('build')) return 'infrastructure/build-scripts';

  // Testing: Test utilities
  if (element.file.includes('test/') || element.file.includes('.test.') || element.file.includes('.spec.')) return 'testing/test-helpers';

  return 'tools/utilities'; // Default fallback
}
```

**Step 4: Select Modules**
```javascript
function selectModules(element, category) {
  const modules = [
    'architecture',  // Always
    'integration',   // Always
    'testing',       // Always
    'performance'    // Always
  ];

  // Conditional modules based on characteristics
  if (element.metadata.hooks?.includes('useState')) modules.push('state');
  if (element.metadata.props?.length > 0) modules.push('props');
  if (element.metadata.hooks?.includes('useEffect')) modules.push('lifecycle');
  if (element.imports.includes('axios') || element.imports.includes('fetch')) modules.push('endpoints');
  if (element.name.includes('Auth') || element.file.includes('auth/')) modules.push('auth');
  // ... more conditions

  return modules;
}
```

### Detection Accuracy Target

**Goal:** 90%+ correct category classification

**Edge Cases:**
1. **Hybrid elements** (e.g., component with embedded API logic) → Prompt user to choose primary category
2. **Missing .coderef/** → Graceful fallback: ask user for category
3. **Ambiguous naming** (e.g., utils/helpers.ts) → Use file path + imports as tiebreaker

---

## 3-Step Workflow (Manual Mode)

**IMPORTANT:** Resource sheets consist of **3 outputs**. You must generate ALL 3:
1. **Markdown documentation** (.md) - Main architectural reference
2. **JSON Schema** (.json) - Type definitions and validation
3. **JSDoc suggestions** (.txt) - Inline code documentation

### Step 1: WHAT IS THIS? (Detect)

**Input:** File path or element name
```
User: "Document FileTree.tsx"
```

**Process:**
1. Read `.coderef/index.json` → Find element "FileTree.tsx#FileTree"
2. Analyze characteristics → isReactComponent=true, usesState=true, hasProps=true
3. Classify → Category: `ui/components`

**Output:**
```
Detected: ui/components
Element: FileTree (React component)
Confidence: 95%
```

### Step 2: PICK VARIABLES (Select Modules)

**Input:** Element characteristics
```
Characteristics:
- React component ✓
- Uses useState ✓
- Has props (tree, onFileSelect, favorites) ✓
- Has useEffect ✓
- No API calls ✗
- No auth logic ✗
```

**Process:**
1. Universal modules → architecture, integration, testing, performance
2. Conditional modules → state (uses useState), props (has props), lifecycle (uses useEffect)

**Output:**
```
Selected Modules (7):
✓ architecture (universal)
✓ integration (universal)
✓ testing (universal)
✓ performance (universal)
✓ state (conditional - uses useState)
✓ props (conditional - has props)
✓ lifecycle (conditional - uses useEffect)
```

### Step 3: ASSEMBLE (Compose Documentation)

**Input:** Selected modules + code analysis

**Process:**
1. Read module templates from `modules/{category}/{module}.md`
2. Auto-fill from .coderef/ data (props, state, imports)
3. Prompt user for manual sections (rationale, pitfalls)
4. Generate **ALL 3 outputs** (Markdown + JSON Schema + JSDoc)

**CHECKLIST - You must create ALL 3 files:**

□ **Output 1: Markdown Documentation**
   - File: `coderef/foundation-docs/{ELEMENT-NAME}.md`
   - Size: 15-25 KB typical
   - Contains: All module sections composed together

□ **Output 2: JSON Schema**
   - File: `coderef/schemas/{element-name}-schema.json`
   - Size: 8-15 KB typical
   - Contains: Type definitions, validation rules, metadata

□ **Output 3: JSDoc Suggestions**
   - File: `coderef/foundation-docs/.jsdoc/{element-name}-jsdoc.txt`
   - Size: 2-5 KB typical
   - Contains: Copy-paste JSDoc comments + usage instructions

**Example Output:**
```
Generated:
✓ coderef/foundation-docs/FILE-TREE.md (22 KB)
✓ coderef/schemas/file-tree-schema.json (12 KB)
✓ coderef/foundation-docs/.jsdoc/file-tree-jsdoc.txt (3 KB)
```

**IMPORTANT:** Do not stop after creating just the .md file. Continue and create the .json schema and .txt JSDoc file.

---

## Output Format Specifications

### 1. Markdown Format

**File naming:** `{ELEMENT-NAME}.md` (e.g., `FILE-TREE.md`, `USE-AUTH.md`)

**File location:** `coderef/foundation-docs/{ELEMENT-NAME}.md`

**Structure:**
```markdown
# {Element Name} - Resource Sheet

**Category:** {category}
**Type:** {type}
**File:** {file_path}
**Created:** {date}

---

## Executive Summary

{1-2 paragraph overview}

---

## Audience & Intent

**Target Audience:** {who will read this}
**Use Cases:** {when to reference this}

---

{DYNAMIC SECTIONS - BASED ON SELECTED MODULES}

## Architecture Overview
{architecture module content}

## State Management
{state module content - if selected}

## Props Reference
{props module content - if selected}

## Integration Points
{integration module content}

## Performance Considerations
{performance module content}

## Testing Strategy
{testing module content}

---

## Mermaid Diagrams

{Auto-generated diagrams based on modules}

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** {workorder_id}
**Timestamp:** {timestamp}
```

**Section Order:**
1. Executive Summary
2. Audience & Intent
3. Architecture Overview (universal)
4. [Dynamic conditional sections in alphabetical order]
5. Integration Points (universal)
6. Performance Considerations (universal)
7. Testing Strategy (universal)
8. Mermaid Diagrams

### 2. JSON Schema Format

**File naming:** `{element-name}-schema.json` (lowercase with hyphens)

**File location:** `coderef/schemas/{element-name}-schema.json`

**Structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "{Element Name} Schema",
  "description": "{Brief description}",
  "definitions": {
    "{TypeName}": {
      "type": "object",
      "properties": {
        "{propertyName}": {
          "type": "string",
          "description": "{description}"
        }
      },
      "required": ["{requiredFields}"]
    }
  },
  "metadata": {
    "category": "{category}",
    "generated_by": "Resource Sheet MCP Tool",
    "workorder_id": "{workorder_id}",
    "timestamp": "{timestamp}"
  }
}
```

**Auto-extraction from TypeScript:**
```typescript
// Source code
interface FileTreeProps {
  tree: TreeNode[];
  onFileSelect: (path: string) => void;
  favorites?: FavoritesData;
}

// Auto-generated schema
{
  "definitions": {
    "FileTreeProps": {
      "type": "object",
      "properties": {
        "tree": {
          "type": "array",
          "items": { "$ref": "#/definitions/TreeNode" },
          "description": "File tree structure"
        },
        "onFileSelect": {
          "type": "function",
          "description": "Callback when file selected"
        },
        "favorites": {
          "$ref": "#/definitions/FavoritesData",
          "description": "Favorites configuration"
        }
      },
      "required": ["tree", "onFileSelect"]
    }
  }
}
```

### 3. JSDoc Format

**File location:** Inline in source files

**Enhancement strategy:**
- Read existing JSDoc → Enhance, don't replace
- Add missing @param, @returns, @example tags
- Add @component, @remarks, @see tags for components

**Template:**
```typescript
/**
 * {Component/Function name}
 *
 * {Brief description from architecture module}
 *
 * @component
 * @category {category}
 *
 * @example
 * ```tsx
 * <FileTree
 *   tree={fileTree}
 *   onFileSelect={(path) => console.log(path)}
 *   favorites={favoritesData}
 * />
 * ```
 *
 * @remarks
 * {Key insights from modules - e.g., state ownership, performance notes}
 *
 * @param {FileTreeProps} props - Component props
 * @param {TreeNode[]} props.tree - File tree structure
 * @param {function} props.onFileSelect - Callback when file selected
 * @param {FavoritesData} [props.favorites] - Optional favorites configuration
 *
 * @returns {JSX.Element} Rendered file tree component
 *
 * @see {@link FileTreeNode} for node rendering logic
 * @see {@link ContextMenu} for right-click actions
 */
export function FileTree({ tree, onFileSelect, favorites }: FileTreeProps) {
  // ... implementation
}
```

**Auto-fill from modules:**
- `@param` tags → From props module
- `@returns` → From architecture module
- `@example` → From props/events modules
- `@remarks` → From performance/state modules
- `@see` → From integration module

---

## Integration with .coderef/

### Required .coderef/ Files

**1. index.json** (Required)
- **Source:** `coderef scan` command
- **Purpose:** Element catalog with metadata
- **Used for:** Detection, classification, props extraction

**2. reports/patterns.json** (Optional)
- **Source:** `coderef patterns` command
- **Purpose:** Code pattern analysis
- **Used for:** Enhanced module selection (e.g., detect auth patterns, error handling)

**3. reports/complexity.json** (Optional)
- **Source:** `coderef complexity` command
- **Purpose:** Complexity metrics per element
- **Used for:** Performance module auto-fill

**4. diagrams/dependencies.mmd** (Optional)
- **Source:** `coderef diagram` command
- **Purpose:** Visual dependency graph
- **Used for:** Architecture module diagrams

### Workflow Integration

**Before generating resource sheet:**
```bash
# Run if .coderef/ doesn't exist
coderef scan --project-path /path/to/project
coderef patterns --project-path /path/to/project
coderef complexity --project-path /path/to/project
coderef diagram --project-path /path/to/project
```

**Then call MCP tool:**
```javascript
generate_resource_sheet({
  project_path: "/path/to/project",
  element_name: "FileTree",
  mode: "reverse-engineer"  // Auto-fill from .coderef/
})
```

### Graceful Degradation

**If .coderef/ missing:**
1. Prompt user: "No .coderef/ found. Run `coderef scan` first or choose manual mode?"
2. Options:
   - **Auto-scan:** Run `coderef scan` automatically (requires coderef CLI installed)
   - **Manual mode:** Prompt user for category and module selection
   - **Template mode:** Generate empty template for manual fill

---

## Module Templates

### Module Template Structure

Each module is a markdown file in `modules/{category}/{module}.md`:

```markdown
# {Module Name}

**Applies to:** {Categories this module applies to}
**Triggers:** {Conditions that activate this module}
**Auto-fill:** {What can be auto-filled from .coderef/}
**Manual:** {What requires human input}

---

## Section Title

{Template content with placeholders}

### Subsection

{AUTO_FILL: element.metadata.props}
{MANUAL: Explain rationale for prop design}

---

## Example Output

{Show example of what this module produces}
```

### Example: State Module

**File:** `modules/state/state.md`

```markdown
# State Module

**Applies to:** ui/components, ui/widgets, ui/pages, state/hooks, state/stores
**Triggers:** Uses useState, useReducer, Redux, Zustand, Jotai
**Auto-fill:** State variable names, initial values, update patterns
**Manual:** State ownership rationale, synchronization strategy

---

## State Management

### State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
{AUTO_FILL: element.metadata.stateVariables.map(state =>
  `| ${state.name} | ${element.name} | React useState | ${state.persisted ? 'localStorage' : 'None'} |`
)}

{MANUAL: Explain why each component owns specific state}

### State Lifecycle

{AUTO_FILL: element.metadata.hooks.filter(h => h.includes('useEffect')).map(hook =>
  `- **${hook.dependency}:** ${hook.description}`
)}

{MANUAL: Explain state initialization and cleanup strategy}

### Synchronization

{MANUAL: If state is shared across components, explain sync mechanism:
- Props drilling?
- Context API?
- External store (Redux/Zustand)?
- localStorage events?
}

---

## Example Output

```markdown
## State Management

### State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
| View mode | CodeRefExplorerWidget | React useState | localStorage |
| Project selection | ProjectSelector | React useState | localStorage |
| Favorites | FileTree | React useState | localStorage |

**Rationale:** Each component owns state it directly controls. View mode affects entire widget, so owned by top-level component. Project selection isolated to selector for reusability. Favorites tied to FileTree as it renders and modifies them.

### State Lifecycle

- **componentDidMount:** Restore from localStorage (view mode, favorites)
- **onProjectChange:** Clear file selection, reload tree
- **onFavoriteChange:** Debounce 500ms before localStorage write

**Strategy:** Optimistic updates (UI changes immediately), background persistence (localStorage write after debounce), cross-tab sync (listen to storage events).
```
```

### Example: Props Module

**File:** `modules/props/props.md`

```markdown
# Props Module

**Applies to:** ui/components, ui/widgets, ui/pages
**Triggers:** React components with props interface
**Auto-fill:** Prop names, types, required/optional status
**Manual:** Prop design rationale, validation rules, usage examples

---

## Props Reference

### {Element Name}Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
{AUTO_FILL: element.metadata.props.map(prop =>
  `| ${prop.name} | ${prop.type} | ${prop.required ? 'Yes' : 'No'} | ${prop.default || '-'} | ${prop.description || 'TODO'} |`
)}

{MANUAL: Explain prop design decisions - Why these props? Why required vs optional?}

### Validation

{AUTO_FILL: If PropTypes or Zod schema exists, show validation rules}

{MANUAL: Explain validation strategy and error handling}

### Examples

{MANUAL: Provide 2-3 usage examples showing common patterns}

---

## Example Output

```markdown
## Props Reference

### FileTreeProps

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tree | TreeNode[] | Yes | - | File tree structure to render |
| onFileSelect | (path: string) => void | Yes | - | Callback when file clicked |
| favorites | FavoritesData | No | {} | Favorites configuration |
| viewMode | ViewMode | No | 'projects' | Display mode (projects or coderef) |

**Design Rationale:**
- `tree` and `onFileSelect` required because component is useless without them
- `favorites` optional to support read-only mode
- `viewMode` optional with sensible default for common case

### Validation

```typescript
const FileTreePropsSchema = z.object({
  tree: z.array(TreeNodeSchema),
  onFileSelect: z.function().args(z.string()).returns(z.void()),
  favorites: FavoritesDataSchema.optional(),
  viewMode: z.enum(['projects', 'coderef']).optional()
});
```

### Examples

**Basic Usage:**
```tsx
<FileTree
  tree={projectFiles}
  onFileSelect={(path) => loadFile(path)}
/>
```

**With Favorites:**
```tsx
<FileTree
  tree={coderefFiles}
  onFileSelect={handleFileClick}
  favorites={userFavorites}
  viewMode="coderef"
/>
```
```
```

---

## Usage Examples

### Example 1: Document a React Component

**User request:**
```
"Document the FileTree component"
```

**Agent workflow:**

**Step 1: Detect**
```javascript
// Read .coderef/index.json
const element = findElement("FileTree");
// Result: {
//   name: "FileTree",
//   type: "function",
//   file: "src/components/coderef/FileTree.tsx",
//   metadata: {
//     hasJSX: true,
//     props: ["tree", "onFileSelect", "favorites", "viewMode"],
//     hooks: ["useState", "useEffect"],
//     imports: ["react", "./FileTreeNode", "./ContextMenu"]
//   }
// }

const category = detectCategory(element);
// Result: "ui/components"
```

**Step 2: Select Modules**
```javascript
const modules = selectModules(element, category);
// Result: [
//   'architecture',  // Universal
//   'integration',   // Universal
//   'testing',       // Universal
//   'performance',   // Universal
//   'state',         // Has useState
//   'props',         // Has props
//   'lifecycle',     // Has useEffect
//   'events'         // Has onClick handlers
// ]
```

**Step 3: Assemble**
```javascript
// For each module, read template and fill placeholders
const markdown = assembleMarkdown(modules, element);
const schema = assembleSchema(modules, element);
const jsdoc = assembleJSDoc(modules, element);

// Write outputs (ALL 3 REQUIRED)
writeFile('coderef/foundation-docs/FILE-TREE.md', markdown);
writeFile('coderef/schemas/file-tree-schema.json', schema);
writeFile('coderef/foundation-docs/.jsdoc/file-tree-jsdoc.txt', jsdoc);
```

**Output (ALL 3 FILES REQUIRED):**

✅ **File 1: Markdown Documentation**
- `coderef/foundation-docs/FILE-TREE.md` (22 KB)
- 8 sections (architecture, state, props, lifecycle, events, integration, performance, testing)

✅ **File 2: JSON Schema**
- `coderef/schemas/file-tree-schema.json` (12 KB)
- FileTreeProps, TreeNode, FavoritesData definitions

✅ **File 3: JSDoc Suggestions**
- `coderef/foundation-docs/.jsdoc/file-tree-jsdoc.txt` (5 KB)
- Copy-paste JSDoc with @component, @param, @example, @remarks tags

---

### Example 2: Document a Custom Hook

**User request:**
```
"Document the useAuth hook"
```

**Agent workflow:**

**Step 1: Detect**
```javascript
const element = findElement("useAuth");
// Result: {
//   name: "useAuth",
//   type: "function",
//   file: "src/hooks/useAuth.ts",
//   metadata: {
//     hasJSX: false,
//     hooks: ["useState", "useEffect"],
//     imports: ["react", "../services/AuthService"]
//   }
// }

const category = detectCategory(element);
// Result: "state/hooks" (starts with "use")
```

**Step 2: Select Modules**
```javascript
const modules = selectModules(element, category);
// Result: [
//   'architecture',  // Universal
//   'integration',   // Universal
//   'testing',       // Universal
//   'performance',   // Universal
//   'state',         // Hook manages state
//   'lifecycle',     // Has useEffect
//   'auth'           // Name includes "Auth"
// ]
```

**Step 3: Assemble**
```javascript
const markdown = assembleMarkdown(modules, element);
const schema = assembleSchema(modules, element);
const jsdoc = assembleJSDoc(modules, element);
```

**Output (ALL 3 FILES REQUIRED):**

✅ **File 1: Markdown Documentation**
- `coderef/foundation-docs/USE-AUTH.md` (18 KB)
- 7 sections (architecture, state, lifecycle, auth, integration, performance, testing)

✅ **File 2: JSON Schema**
- `coderef/schemas/use-auth-schema.json` (8 KB)
- AuthState, AuthActions, UseAuthReturn definitions

✅ **File 3: JSDoc Suggestions**
- `coderef/foundation-docs/.jsdoc/use-auth-jsdoc.txt` (3 KB)
- Copy-paste JSDoc with @hook, @returns, @example tags

---

### Example 3: Document an API Endpoint

**User request:**
```
"Document the /api/projects endpoint"
```

**Agent workflow:**

**Step 1: Detect**
```javascript
const element = findElement("api/projects");
// Result: {
//   name: "projects",
//   type: "function",
//   file: "src/app/api/projects/route.ts",
//   metadata: {
//     hasJSX: false,
//     exports: ["GET", "POST"],
//     imports: ["next/server", "../../../lib/db"]
//   }
// }

const category = detectCategory(element);
// Result: "services/api-endpoints" (file path includes "api/")
```

**Step 2: Select Modules**
```javascript
const modules = selectModules(element, category);
// Result: [
//   'architecture',  // Universal
//   'integration',   // Universal
//   'testing',       // Universal
//   'performance',   // Universal
//   'endpoints',     // Is an API endpoint
//   'validation',    // Validates request body
//   'errors'         // Returns error responses
// ]
```

**Step 3: Assemble**
```javascript
const markdown = assembleMarkdown(modules, element);
const schema = assembleSchema(modules, element);
const jsdoc = assembleJSDoc(modules, element);
```

**Output (ALL 3 FILES REQUIRED):**

✅ **File 1: Markdown Documentation**
- `coderef/foundation-docs/API-PROJECTS.md` (15 KB)
- 7 sections (architecture, endpoints, validation, errors, integration, performance, testing)

✅ **File 2: JSON Schema**
- `coderef/schemas/api-projects-schema.json` (9 KB)
- Request/Response types, error codes, query parameters

✅ **File 3: JSDoc Suggestions**
- `coderef/foundation-docs/.jsdoc/api-projects-jsdoc.txt` (4 KB)
- Copy-paste JSDoc with @route, @param, @returns, @throws tags

---

## Quality Standards

### Refactor Safety

Documentation must enable safe refactoring without breaking changes:

**✅ State Ownership Table**
- Explicitly defines "who owns what"
- Prevents accidental state conflicts during refactors

**✅ Integration Contracts**
- Documents how components connect
- Enables safe component swaps without breaking integrations

**✅ Failure Modes**
- Documents edge cases and recovery paths
- Prevents breaking changes from cascading

**Example:**
```markdown
## State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
| View mode | CodeRefExplorerWidget | React useState | localStorage |

**Authority:** CodeRefExplorerWidget is the ONLY component that should modify view mode. Children receive it as read-only prop.

## Failure Modes

### localStorage Quota Exceeded
- **Trigger:** favorites.json exceeds 5MB
- **Recovery:** Prompt user to delete old favorites, fallback to session storage
- **Prevention:** Limit favorites to 1000 items per project
```

### Onboarding Optimization

Documentation must enable new developers to understand the system quickly:

**✅ Progressive Disclosure**
- Executive Summary (30 seconds) → Architecture Overview (5 minutes) → Deep Dive (30 minutes)

**✅ Visual Aids**
- Mermaid diagrams reduce cognitive load
- Component hierarchy trees show relationships at a glance

**✅ Multiple Entry Points**
- Code JSDoc (immediate context while coding)
- Markdown guide (deep dive for onboarding)
- JSON schema (tooling integration)

**Example:**
```markdown
## Executive Summary

FileTree renders a hierarchical file browser with favorites, context menus, and cross-tab sync. Used in CodeRefExplorerWidget sidebar.

**Key Responsibilities:**
- Render file tree with expand/collapse
- Manage favorites (add/remove, groups)
- Provide context menu actions (copy path, add to prompt)

**Not Responsible For:**
- File content loading (handled by FileViewer)
- Project selection (handled by ProjectSelector)

[Read Architecture Overview for component hierarchy →]
```

### Maintenance Focus

Documentation must reduce maintenance burden:

**✅ Common Pitfalls**
- Documents known bugs and quirks to prevent regression

**✅ Performance Budgets**
- Sets clear expectations to prevent performance degradation

**✅ Accessibility Gaps**
- Tracks technical debt with priority levels

**✅ Non-Goals**
- Explicitly states what the component does NOT do

**Example:**
```markdown
## Common Pitfalls

### Text Overflow in Long Paths
- **Issue:** File names with 100+ characters overflow container
- **Fix:** Apply `min-w-0` CSS class to parent flex container
- **Why it happens:** Flex items don't shrink by default
- **Regression risk:** HIGH - easy to forget when refactoring layout

## Performance Budgets

- **Tree size:** Tested up to 500 nodes, renders in <100ms
- **Threshold:** 1000 nodes requires virtualization
- **Memory:** ~2MB per project with favorites

## Non-Goals

- ❌ Virtualized scrolling (not implemented yet)
- ❌ Drag-and-drop file organization (out of scope)
- ❌ File search (handled by separate search component)
```

### Validation Checklist

Before marking documentation as complete, verify:

**Content Quality:**
- [ ] All sections have content (no "TODO" placeholders)
- [ ] Examples are real (not pseudo-code)
- [ ] Diagrams render correctly
- [ ] Code snippets are syntactically valid

**Accuracy:**
- [ ] Props match TypeScript interfaces
- [ ] State ownership matches code implementation
- [ ] Integration points verified in actual code
- [ ] Performance numbers from real tests (not guesses)

**Completeness:**
- [ ] All required modules included (architecture, integration, testing, performance)
- [ ] All conditional modules justified (why props module? why not auth module?)
- [ ] Manual sections filled (rationale, pitfalls)
- [ ] Mermaid diagrams present

**Consistency:**
- [ ] Naming matches codebase (FileTree vs file-tree vs fileTree)
- [ ] Categories match folder structure (ui/components vs components/ui)
- [ ] Terminology consistent across markdown, schema, JSDoc

**Usability:**
- [ ] Markdown renders correctly in GitHub/VSCode
- [ ] Schema validates against JSON Schema Draft 07
- [ ] JSDoc shows in hover tooltips
- [ ] Links work (internal references, external docs)

---

## Future Enhancements (Phase 2+)

### Auto-Detection Improvements
- Support more frameworks (Vue, Angular, Svelte)
- Detect design patterns (Singleton, Factory, Observer)
- Identify cross-cutting concerns (logging, caching, retry logic)

### Additional Modules (15 more)
- `caching` - Cache strategies (in-memory, Redis, CDN)
- `retry` - Retry logic and backoff strategies
- `logging` - Logging patterns and levels
- `monitoring` - Metrics and observability
- `security` - Security considerations (XSS, CSRF, SQL injection)
- `migrations` - Data migration patterns
- `webhooks` - Webhook handling
- `batching` - Batch processing patterns
- `pagination` - Pagination strategies
- `search` - Search implementation
- `filtering` - Filtering patterns
- `sorting` - Sorting strategies
- `theming` - Theme system
- `i18n` - Internationalization
- `analytics` - Analytics integration

### Output Formats
- **HTML:** Generate static HTML documentation site
- **PDF:** Export to PDF for offline reference
- **OpenAPI:** Generate OpenAPI specs from API endpoints
- **GraphQL Schema:** Generate GraphQL schemas from resolvers

### MCP Tool Modes

**Mode 1: Reverse-Engineer (Current)**
- Input: Existing code file
- Output: Generated resource sheet (60-70% auto-filled)

**Mode 2: Template (Future)**
- Input: Element type (e.g., "React component")
- Output: Empty template for manual fill (planning phase)

**Mode 3: Refresh (Future)**
- Input: Existing resource sheet + updated code
- Output: Updated resource sheet (preserve manual sections, refresh auto-filled)

---

## Appendix: File Locations

### Module Templates
```
C:\Users\willh\.mcp-servers\coderef-docs\modules\
├── tools\
│   ├── cli-commands\
│   │   └── architecture.md
│   ├── scripts\
│   └── utilities\
├── ui\
│   ├── widgets\
│   ├── pages\
│   └── components\
│       ├── architecture.md
│       ├── props.md
│       ├── state.md
│       └── lifecycle.md
├── services\
│   ├── api-endpoints\
│   │   ├── architecture.md
│   │   ├── endpoints.md
│   │   └── validation.md
│   ├── api-clients\
│   └── data-access\
├── state\
│   ├── hooks\
│   │   ├── architecture.md
│   │   ├── state.md
│   │   └── lifecycle.md
│   ├── stores\
│   └── context\
├── data\
│   ├── models\
│   ├── schemas\
│   └── validators\
├── generators\
│   ├── scaffolding\
│   ├── templates\
│   └── migrations\
├── infrastructure\
│   ├── build-scripts\
│   ├── deployment\
│   └── ci-cd\
└── testing\
    ├── test-helpers\
    ├── mocks\
    └── fixtures\
```

### Universal Modules (All Categories)
```
C:\Users\willh\.mcp-servers\coderef-docs\modules\_universal\
├── architecture.md
├── integration.md
├── testing.md
└── performance.md
```

### Generated Output (ALL 3 REQUIRED)
```
{project}\coderef\
├── foundation-docs\
│   ├── FILE-TREE.md              ✅ Markdown documentation
│   ├── USE-AUTH.md               ✅ Markdown documentation
│   ├── API-PROJECTS.md           ✅ Markdown documentation
│   └── .jsdoc\
│       ├── file-tree-jsdoc.txt   ✅ JSDoc suggestions
│       ├── use-auth-jsdoc.txt    ✅ JSDoc suggestions
│       └── api-projects-jsdoc.txt✅ JSDoc suggestions
└── schemas\
    ├── file-tree-schema.json     ✅ JSON Schema
    ├── use-auth-schema.json      ✅ JSON Schema
    └── api-projects-schema.json  ✅ JSON Schema
```

---

**End of Reference Guide**

**To use this guide:**
1. Paste a file path or code snippet
2. Reference: "Use RESOURCE-SHEET-SYSTEM.md to generate documentation"
3. Agent follows 3-step workflow (Detect → Select → Assemble)
4. **CRITICAL:** Outputs ALL 3 formats (Markdown + JSON Schema + JSDoc) - Never stop after just the .md file

**Quality target:** 60-70% auto-filled, 30-40% human input, 90%+ detection accuracy

**⚠️ REMINDER:** Complete resource sheet = 3 files created (.md + .json + .txt)
