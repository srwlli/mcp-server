# State Module

**Type:** Conditional
**Triggers:** useState, useReducer, Redux, Zustand, Jotai, Pinia, Vuex
**Applies to:** ui/components, ui/widgets, ui/pages, state/hooks, state/stores, state/context
**Auto-fill:** State variable names, initial values, update patterns
**Manual:** State ownership rationale, synchronization strategy

---

## Section: State Management

### State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
{{#each element.metadata.stateVariables}}
| {{this.name}} | {{../element.name}} | {{this.authority}} | {{#if this.persisted}}{{this.persistenceKey}}{{else}}None (ephemeral){{/if}} |
{{/each}}

{{MANUAL: Explain why each component owns specific state:
- Why this component and not a parent?
- Could this state be derived instead of stored?
- Is state properly scoped (not too high, not too low)?}}

### State Initialization

{{AUTO_FILL: element.metadata.stateVariables.map(s => s.initialValue)}}

```typescript
{{#each element.metadata.stateVariables}}
const [{{this.name}}, set{{capitalize this.name}}] = useState({{this.initialValue}});
{{/each}}
```

{{MANUAL: Explain initialization strategy:
- Where do initial values come from? (props, localStorage, API, hardcoded)
- What happens if initialization fails?
- Are there async initialization steps?}}

### State Updates

{{AUTO_FILL: element.metadata.stateVariables.map(s => s.updaters)}}

**Update Patterns:**
{{#each element.metadata.stateVariables}}
- **{{this.name}}:** {{this.updatePattern}}
{{/each}}

{{MANUAL: Explain update logic:
- What triggers state changes?
- Are updates batched or immediate?
- What validation occurs before updates?
- Are there side effects from updates?}}

### State Synchronization

{{MANUAL: If state is shared across components, explain sync mechanism:

**Synchronization Method:**
- Props drilling?
- Context API?
- External store (Redux/Zustand)?
- localStorage events?
- WebSocket/polling?

**Consistency Guarantees:**
- Is state eventually consistent?
- What happens during conflicts?
- How are race conditions handled?

**Example:**
```typescript
// Cross-tab sync via localStorage events
useEffect(() => {
  const handleStorage = (e: StorageEvent) => {
    if (e.key === 'favorites') {
      setFavorites(JSON.parse(e.newValue || '{}'));
    }
  };
  window.addEventListener('storage', handleStorage);
  return () => window.removeEventListener('storage', handleStorage);
}, []);
```}}

### State Persistence

{{AUTO_FILL: element.metadata.stateVariables.filter(s => s.persisted)}}

**Persisted State:**
{{#each element.metadata.stateVariables}}
{{#if this.persisted}}
- **{{this.name}}:** {{this.persistenceMethod}} (key: `{{this.persistenceKey}}`)
{{/if}}
{{/each}}

{{MANUAL: Explain persistence strategy:
- Why persist this state?
- What is the storage mechanism? (localStorage, IndexedDB, API)
- When is state restored?
- How is migration handled for schema changes?
- What happens if storage fails?}}

---

## Example Output

### State Management

#### State Ownership Table

| State | Owner | Authority | Persistence |
|-------|-------|-----------|-------------|
| viewMode | CodeRefExplorerWidget | React useState | localStorage (coderef_viewMode) |
| projectSelection | ProjectSelector | React useState | localStorage (coderef_selectedProject) |
| favorites | FileTree | React useState | localStorage (coderef_favorites) |
| fileSelection | FileTree | React useState | None (ephemeral) |
| treeExpansion | FileTree | React useState | None (ephemeral) |

**State Ownership Rationale:**
- **viewMode** owned by CodeRefExplorerWidget because it affects the entire widget (sidebar + content area)
- **projectSelection** isolated to ProjectSelector for reusability - can be used in other contexts
- **favorites** tied to FileTree as it renders and modifies them - no other component needs direct access
- **fileSelection** ephemeral - only matters during current session, cleared on unmount
- **treeExpansion** ephemeral - user can re-expand directories, not worth persisting

#### State Initialization

```typescript
const [viewMode, setViewMode] = useState<ViewMode>(() => {
  const saved = localStorage.getItem('coderef_viewMode');
  return saved ? (saved as ViewMode) : 'projects';
});

const [favorites, setFavorites] = useState<FavoritesData>(() => {
  try {
    const saved = localStorage.getItem('coderef_favorites');
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {}; // Fallback if corrupt
  }
});

const [fileSelection, setFileSelection] = useState<string | null>(null);
```

**Initialization Strategy:**
- viewMode and favorites restored from localStorage on mount (lazy initialization)
- If localStorage read fails, fallback to defaults (projects mode, empty favorites)
- fileSelection starts null (no file selected initially)
- No async initialization - all synchronous

#### State Updates

**Update Patterns:**
- **viewMode:** Updated on toggle button click, immediately persisted to localStorage
- **favorites:** Updated on add/remove actions, debounced 500ms before localStorage write
- **fileSelection:** Updated on file click, no persistence

**Update Logic:**
- viewMode toggle is instant (no validation needed)
- favorites validated (must be valid TreeNode path) before adding
- fileSelection cleared when project changes
- localStorage writes debounced to avoid excessive I/O (batches multiple favorite changes)

**Side Effects:**
- viewMode change triggers tree re-render (different data source)
- favorites change triggers localStorage write after debounce
- fileSelection change triggers FileViewer to load file content

#### State Synchronization

**Synchronization Method:** localStorage events for cross-tab sync

**How it Works:**
```typescript
useEffect(() => {
  const handleStorageEvent = (e: StorageEvent) => {
    if (e.key === 'coderef_favorites' && e.newValue) {
      try {
        setFavorites(JSON.parse(e.newValue));
      } catch {
        console.warn('Invalid favorites data from other tab');
      }
    }
  };
  window.addEventListener('storage', handleStorageEvent);
  return () => window.removeEventListener('storage', handleStorageEvent);
}, []);
```

**Consistency Guarantees:**
- Eventually consistent across tabs (updates propagate within 100ms)
- Last write wins in conflicts (no CRDT or OT)
- Race conditions possible (two tabs add same favorite simultaneously)
- Acceptable for favorites use case (low conflict probability)

#### State Persistence

**Persisted State:**
- **viewMode:** localStorage (key: `coderef_viewMode`)
- **favorites:** localStorage (key: `coderef_favorites`)

**Persistence Strategy:**
- Persist on every state change (viewMode) or debounced (favorites)
- Restore on component mount from localStorage
- No schema migration yet (v1 only) - future versions will need migration logic
- Graceful fallback if localStorage quota exceeded (log warning, continue with session-only state)

**Storage Failure Handling:**
```typescript
const persistFavorites = (data: FavoritesData) => {
  try {
    localStorage.setItem('coderef_favorites', JSON.stringify(data));
  } catch (e) {
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      console.warn('localStorage quota exceeded - favorites will not persist');
      // Continue with in-memory state
    }
  }
};
```

---

## Metadata

**Generated by:** Resource Sheet MCP Tool
**Module:** state (conditional)
**Triggers:** useState, useReducer, Redux, Zustand
**Version:** 1.0.0
