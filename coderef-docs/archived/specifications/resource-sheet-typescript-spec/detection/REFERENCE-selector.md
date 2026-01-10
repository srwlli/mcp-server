# Reference Sheet: detection/selector.ts

**File:** `modules/resource-sheet/detection/selector.ts`
**Purpose:** Select documentation modules based on element characteristics
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/SELECT-001

---

## API

### `selectModules(element: ElementCharacteristics, category: ElementCategory): SelectionResult`

Select which documentation modules to include.

**Returns:**
```typescript
{
  modules: ModuleName[];
  rationale: Record<ModuleName, string>;
  estimatedAutoFill: number;  // 0-100
}
```

**Selection Logic:**

**Universal Modules (always included):**
- `architecture`
- `integration`
- `testing`
- `performance`

**Conditional Modules (based on characteristics):**
- `usesState` → `state`
- `hasProps` → `props`
- `hasLifecycle` → `lifecycle`
- `hasEvents` → `events`
- `isAPI` → `endpoints`
- `hasAuth` → `auth`
- `category === 'services/*' OR 'state/*'` → `errors`
- `hasValidation` → `validation`
- `hasPersistence` → `persistence`
- `hasRouting` → `routing`
- `hasAccessibility` → `accessibility`

**Example:**
```typescript
const result = selectModules(element, 'ui/components');
// result.modules: ['architecture', 'integration', 'testing', 'performance', 'state', 'props', 'events']
// result.estimatedAutoFill: 85
// result.rationale: {
//   architecture: 'Universal module',
//   state: 'Element uses useState hook',
//   props: 'Component has 3 props'
// }
```

---

### `sortModules(modules: ModuleName[]): ModuleName[]`

Sort modules in display order (universal first, then conditional alphabetically).

---

## Auto-Fill Estimation

**Estimate based on:**
- Universal modules: 70% auto-fill
- Conditional modules: 80-90% auto-fill
- Manual sections: Architecture decisions, performance notes

**Calculation:**
```typescript
estimatedAutoFill = (
  (universalCount * 70) +
  (conditionalCount * 85)
) / totalModules
```

---

## Version
**Created:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/SELECT-001
