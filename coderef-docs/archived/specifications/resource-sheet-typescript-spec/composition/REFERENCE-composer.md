# Reference Sheet: composition/composer.ts

**File:** `modules/resource-sheet/composition/composer.ts`
**Purpose:** Assemble selected modules into cohesive documentation
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/COMPOSE-001

---

## API

### `composeDocumentation(element, selectedModules, options): Promise<ComposedDocumentation>`

Compose documentation from selected modules.

**Parameters:**
```typescript
{
  element: ElementCharacteristics;
  selectedModules: ModuleName[];
  options: {
    workorderId?: string;
    featureId?: string;
    category: string;
  };
}
```

**Workflow:**
1. Read module template files from `_universal/` and `conditional/`
2. Extract auto-fill data from element (props, state, events, etc.)
3. Compose markdown (substitute variables, merge modules)
4. Compose JSON schema
5. Compose JSDoc comments
6. Calculate actual auto-fill rate (count filled vs unfilled)
7. Identify review flags (sections with `TODO:` or `MANUAL:`)

**Example:**
```typescript
const documentation = await composeDocumentation(
  element,
  ['architecture', 'integration', 'testing', 'state', 'props'],
  {
    category: 'React Hook',
    workorderId: 'WO-DOCS-001'
  }
);

// documentation.markdown: "# useAuth\n\n## Architecture..."
// documentation.autoFillRate: 85
// documentation.reviewFlags: [{ section: 'Performance', reason: 'Manual input required' }]
```

---

## Composition Process

### 1. Read Module Templates

Reads `.md` files from:
- `_universal/architecture.md`
- `_universal/integration.md`
- `_universal/testing.md`
- `_universal/performance.md`
- `conditional/state.md`
- `conditional/props.md`
- etc.

### 2. Extract Auto-Fill Data

```typescript
{
  name: element.name,
  type: element.type,
  file: element.file,
  props: element.metadata.props || [],
  stateVariables: element.metadata.stateVariables || [],
  eventHandlers: element.metadata.eventHandlers || [],
  imports: element.imports,
  exports: element.exports
}
```

### 3. Compose Markdown

- Merge module templates in order
- Replace variables: `{{name}}`, `{{type}}`, `{{props[0].name}}`
- Insert auto-filled content
- Mark manual sections with `<!-- MANUAL: ... -->`

### 4. Calculate Auto-Fill Rate

```typescript
autoFillRate = (filledSections / totalSections) * 100
```

### 5. Identify Review Flags

Scan for:
- `<!-- MANUAL: ... -->` markers
- `TODO:` comments
- Empty sections

**Example:**
```typescript
reviewFlags = [
  { section: 'Performance', reason: 'Manual input required' },
  { section: 'Architecture', reason: 'Verify design decisions' }
]
```

---

## Output Structure

### Markdown
```markdown
# ElementName

**Category:** React Hook
**Type:** function
**File:** src/hooks/useAuth.ts

## Architecture
<!-- Auto-filled from architecture.md -->

## Integration
<!-- Auto-filled from integration.md -->

## State Management
<!-- Conditional module - auto-filled -->

## Props
<!-- Conditional module - auto-filled -->

## Testing
<!-- Universal module - manual input required -->

<!-- UDS Footer -->
```

### JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ElementName",
  "type": "object",
  "properties": { ... }
}
```

### JSDoc
```javascript
/**
 * @name ElementName
 * @category React Hook
 * @param {Props} props
 * @returns {ReturnType}
 */
```

---

## Version
**Created:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/COMPOSE-001
