# Reference Sheet: detection/classifier.ts

**File:** `modules/resource-sheet/detection/classifier.ts`
**Purpose:** Classify elements into 19 user-friendly categories
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-002

---

## API

### `classifyElement(element: ElementCharacteristics): DetectionResult`

Classify element into primary category with alternates.

**Returns:**
```typescript
{
  element: ElementCharacteristics;
  category: ElementCategory;
  confidence: number;
  alternates?: { category: ElementCategory; confidence: number }[];
}
```

**Example:**
```typescript
const result = classifyElement(element);
// result.category: 'state/hooks'
// result.confidence: 95
// result.alternates: [{ category: 'ui/components', confidence: 40 }]
```

---

## Classification Priority

1. **Testing** (highest) - `testing/*`
2. **Infrastructure** - `infrastructure/*`
3. **Generators** - `generators/*`
4. **UI Components** - `ui/*`
5. **State Management** - `state/*`
6. **Services/API** - `services/*`
7. **Data** - `data/*`
8. **Tools** (lowest) - `tools/*`

---

## Category Decision Tree

### Testing
- `isTest` + `file.includes('mock')` → `testing/mocks`
- `isTest` + `file.includes('fixture')` → `testing/fixtures`
- `isTest` → `testing/test-helpers`

### Infrastructure
- `isInfrastructure` + `file.includes('build')` → `infrastructure/build-scripts`
- `isInfrastructure` + `file.includes('deploy')` → `infrastructure/deployment`
- `isInfrastructure` + `file.includes('ci')` → `infrastructure/ci-cd`

### Generators
- `isGenerator` + `file.includes('scaffold')` → `generators/scaffolding`
- `isGenerator` + `file.includes('template')` → `generators/templates`
- `isGenerator` + `file.includes('migration')` → `generators/migrations`

### UI
- `isReactComponent` + `file.includes('pages/')` → `ui/pages`
- `isReactComponent` + `file.includes('widgets/')` → `ui/widgets`
- `isReactComponent` → `ui/components`

### State
- `isHook` → `state/hooks`
- `isStore` + `file.includes('context')` → `state/context`
- `isStore` → `state/stores`

### Services
- `isAPI` + `file.includes('api/')` → `services/api-endpoints`
- `isAPI` + `name.includes('Client')` → `services/api-clients`
- `isAPI` → `services/data-access`

### Data
- `hasValidation` + `name.includes('Schema')` → `data/schemas`
- `hasValidation` + `name.includes('Validator')` → `data/validators`
- `file.includes('models/')` → `data/models`
- `file.includes('schemas/')` → `data/schemas`

### Tools
- `isCLI` → `tools/cli-commands`
- `file.includes('scripts/')` → `tools/scripts`
- `file.includes('utils/')` → `tools/utilities`
- **Default fallback** → `tools/utilities`

---

## Utilities

### `getCategoryDisplayName(category: ElementCategory): string`

Convert category ID to human-readable name.

**Examples:**
- `'state/hooks'` → `'React Hook'`
- `'ui/components'` → `'UI Component'`
- `'services/api-endpoints'` → `'API Endpoint'`

### `getCategoryDescription(category: ElementCategory): string`

Get category description.

**Example:**
```typescript
getCategoryDescription('state/hooks');
// "React hooks for state management and side effects"
```

---

## Version
**Created:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-002
