# Integration Module

**Type:** Universal (always included)
**Applies to:** All element types
**Auto-fill:** Import/export relationships, data flow
**Manual:** Integration contracts, failure modes

---

## Section: Integration Points

### Internal Integrations

{{AUTO_FILL: element.used_by}}

**Components that use this:**
{{#each element.consumers}}
- **{{this.name}}** (`{{this.file}}`) - {{this.usage_pattern}}
{{/each}}

**Components this uses:**
{{#each element.dependencies}}
- **{{this.name}}** (`{{this.file}}`) - {{this.purpose}}
{{/each}}

{{MANUAL: Explain integration relationships - How do these components interact? What data flows between them?}}

### External Integrations

{{AUTO_FILL: element.external_apis}}

**External Services:**
{{#each element.external_services}}
- **{{this.name}}** - {{this.endpoint}} - {{this.purpose}}
{{/each}}

**Browser APIs:**
{{#each element.browser_apis}}
- **{{this.api}}** - {{this.usage}}
{{/each}}

{{MANUAL: Explain external dependencies - Why these services? What happens if they fail?}}

### Data Flow

{{MANUAL: Describe the data flow through this element:

**Input:**
- Where does data come from? (props, API calls, localStorage, etc.)
- What format is expected?
- What validation is performed?

**Processing:**
- What transformations are applied?
- What business logic executes?

**Output:**
- Where does data go? (child components, API, storage, etc.)
- What format is produced?
- What side effects occur?

Use a diagram if helpful:}}

```
[Data Source] → [This Element] → [Data Destination]
```

### Integration Contracts

{{MANUAL: Define the contracts this element exposes:

**Public API:**
- What functions/methods are exported?
- What are the input parameters?
- What are the return values?
- What errors can be thrown?

**Events:**
- What events does this emit?
- What is the event payload?
- When are events fired?

**State:**
- What state is exposed (if any)?
- How can consumers observe state changes?

**Guarantees:**
- What does this element promise to consumers?
- What does it NOT promise?}}

### Failure Modes

{{MANUAL: Document how failures propagate:

**Upstream Failures:**
- What happens if a dependency fails?
- How are errors caught and handled?
- What recovery mechanisms exist?

**Downstream Impact:**
- What happens if this element fails?
- Which consumers are affected?
- How is failure communicated?

**Isolation:**
- Are failures contained?
- Can the system continue if this fails?
- What is the blast radius?}}

---

## Example Output

### Integration Points

#### Internal Integrations

**Components that use this:**
- **CodeRefExplorerWidget** (`widgets/coderef-explorer/CodeRefExplorerWidget.tsx`) - Embeds FileTree in sidebar
- **PromptingWorkflow** (`components/prompting/PromptingWorkflow.tsx`) - Receives file paths from "Add to Prompt" action

**Components this uses:**
- **FileTreeNode** (`components/coderef/FileTreeNode.tsx`) - Renders each tree node recursively
- **ContextMenu** (`components/coderef/ContextMenu.tsx`) - Provides right-click actions
- **useLocalStorage** (`hooks/useLocalStorage.ts`) - Persists favorites data

**Integration Relationships:** CodeRefExplorerWidget provides project data to FileTree via props. FileTree calls onFileSelect callback when user clicks a file, passing the file path back to parent. PromptingWorkflow receives file paths from context menu "Add to Prompt" action.

#### External Integrations

**Browser APIs:**
- **localStorage** - Stores favorites data across sessions
- **storage event** - Listens for cross-tab favorites changes

**External Services:** None

**External Dependencies:** localStorage is the only external dependency. If quota exceeded, gracefully fallback to session-only favorites (in-memory). No network calls, so no network failure modes.

#### Data Flow

**Input:**
- `tree: TreeNode[]` - File tree structure from parent (CodeRefExplorerWidget)
- `favorites: FavoritesData` - Restored from localStorage on mount
- `viewMode: ViewMode` - Projects or CodeRef mode from parent

**Processing:**
- Renders tree recursively using FileTreeNode
- Manages expansion state (which directories are open)
- Handles favorite add/remove actions
- Debounces localStorage writes (500ms) for performance

**Output:**
- `onFileSelect(path)` - Callback to parent when file clicked
- localStorage write - Persists favorites after debounce
- storage event - Triggers cross-tab sync when favorites change

```
[CodeRefExplorerWidget] → [FileTree] → [FileTreeNode (recursive)]
         ↓                       ↓
   [onFileSelect]          [localStorage]
         ↓                       ↓
   [FileViewer]           [Cross-tab sync]
```

#### Integration Contracts

**Public API:**

```typescript
interface FileTreeProps {
  tree: TreeNode[];
  onFileSelect: (path: string) => void;
  favorites?: FavoritesData;
  viewMode?: ViewMode;
}
```

**Guarantees:**
- ✅ Always calls onFileSelect with absolute file path
- ✅ Favorites persist across sessions (if localStorage available)
- ✅ Never throws - errors are logged and gracefully handled
- ❌ Does NOT guarantee file exists (parent must validate)
- ❌ Does NOT load file content (delegated to FileViewer)

**Events:**
- `storage` event - Emitted when favorites change (native browser event)
- Payload: `{ key: 'coderef_favorites', newValue: string }`

**State:**
- Expansion state (which directories are open) - Internal only, not exposed
- Favorites - Exposed via localStorage, observable via storage events

#### Failure Modes

**Upstream Failures:**
- **Empty tree prop:** Renders "No files found" message
- **Invalid favorites data:** Ignores corrupt data, starts with empty favorites
- **localStorage quota exceeded:** Logs warning, continues with session-only favorites

**Downstream Impact:**
- **FileTree fails to render:** CodeRefExplorerWidget shows error boundary
- **onFileSelect callback throws:** Error caught, logged, does not crash tree
- **localStorage write fails:** Favorites lost on page refresh, but in-memory state persists

**Isolation:**
- Failures are contained - FileTree errors don't crash parent widget
- Other widgets continue functioning if FileTree fails
- Blast radius: Limited to file browsing feature only

---

## Metadata

**Generated by:** Resource Sheet MCP Tool
**Module:** integration (universal)
**Version:** 1.0.0
