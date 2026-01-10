# Reference Sheet: detection/analyzer.ts

**File:** `modules/resource-sheet/detection/analyzer.ts`
**Purpose:** Analyzes code elements from `.coderef/index.json` and extracts characteristics
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-001

---

## Overview

Detection engine that:
1. Reads `.coderef/index.json`
2. Finds element by name (with fuzzy matching)
3. Extracts characteristics (React, state, props, events, APIs)
4. Analyzes code patterns for classification hints
5. Calculates confidence scores

---

## Public API

### Main Functions

#### `analyzeElement(projectPath: string, elementName: string): Promise<ElementCharacteristics>`

**Purpose:** Read `.coderef/index.json` and extract element characteristics

**Parameters:**
- `projectPath` - Absolute path to project root
- `elementName` - Element name, file path, or ID to find

**Returns:** `ElementCharacteristics` object with metadata

**Throws:**
- `.coderef/index.json` not found
- Invalid index.json format
- Element not found

**Algorithm:**
1. Check if `.coderef/index.json` exists
2. Parse JSON file
3. Find element using `findElement()` (fuzzy matching)
4. Extract characteristics with `extractCharacteristics()`

**Example:**
```typescript
const element = await analyzeElement(
  '/path/to/project',
  'FileTree'
);

console.log(element.name);             // "FileTree"
console.log(element.type);             // "component"
console.log(element.metadata.hasJSX);  // true
console.log(element.metadata.props);   // [{ name: "onSelect", ... }]
```

**Error Handling:**
```typescript
try {
  const element = await analyzeElement('/path/to/project', 'NotFound');
} catch (error) {
  // Error: Element "NotFound" not found in .coderef/index.json.
  // Available elements: FileTree, useAuth, AuthService, ...
}
```

---

#### `analyzeCodeCharacteristics(element: ElementCharacteristics): CodeCharacteristics`

**Purpose:** Analyze element and detect code characteristics for classification

**Returns:**
```typescript
{
  isReactComponent: boolean;
  usesState: boolean;
  hasProps: boolean;
  hasLifecycle: boolean;
  hasEvents: boolean;
  isAPI: boolean;
  isCLI: boolean;
  isHook: boolean;
  isStore: boolean;
  isTest: boolean;
  isGenerator: boolean;
  isInfrastructure: boolean;
  hasAuth: boolean;
  hasValidation: boolean;
  hasPersistence: boolean;
  hasRouting: boolean;
  hasAccessibility: boolean;
}
```

**Detection Heuristics:**

**React Component:**
```typescript
isReactComponent = metadata.hasJSX === true
```

**State Management:**
```typescript
usesState =
  hooks includes 'useState' or 'useReducer'
  OR imports include 'redux', 'zustand', 'jotai'
```

**Props:**
```typescript
hasProps = metadata.props.length > 0
```

**Lifecycle:**
```typescript
hasLifecycle =
  hooks includes 'useEffect' or 'useLayoutEffect'
```

**Events:**
```typescript
hasEvents = metadata.eventHandlers.length > 0
```

**API:**
```typescript
isAPI =
  file includes 'api/' or 'routes/'
  OR imports include 'axios' or 'fetch'
  OR metadata.apiCalls.length > 0
```

**CLI:**
```typescript
isCLI =
  file includes 'cli/'
  OR name ends with 'Command'
  OR imports include 'commander' or 'yargs'
```

**Hook:**
```typescript
isHook = name starts with 'use' AND length > 3
```

**Store:**
```typescript
isStore =
  file includes 'store' or 'context'
  OR imports include 'redux' or 'zustand'
```

**Test:**
```typescript
isTest =
  file includes '.test.' or '.spec.' or '__tests__'
  OR imports include 'vitest' or 'jest'
```

**Generator:**
```typescript
isGenerator =
  file includes 'generator' or 'scaffold'
  OR name includes 'Generator'
```

**Infrastructure:**
```typescript
isInfrastructure =
  file includes 'build', 'deploy', 'ci', or 'script'
```

**Auth:**
```typescript
hasAuth =
  name includes 'auth' (case-insensitive)
  OR imports include 'jwt' or 'auth'
```

**Validation:**
```typescript
hasValidation =
  imports include 'zod' or 'yup'
  OR name includes 'Validator' or 'Schema'
```

**Persistence:**
```typescript
hasPersistence =
  stateVariables have persisted: true
  OR imports include 'localStorage' or 'indexeddb'
```

**Routing:**
```typescript
hasRouting =
  file includes 'router' or 'routes'
  OR imports include 'react-router' or 'next/navigation'
```

**Accessibility:**
```typescript
hasAccessibility =
  file includes 'a11y'
  OR imports include 'aria'
  OR metadata has ariaAttributes or keyboardHandlers
```

**Example:**
```typescript
const element = await analyzeElement('/path/to/project', 'FileTree');
const characteristics = analyzeCodeCharacteristics(element);

if (characteristics.isReactComponent && characteristics.hasProps) {
  console.log('React component with props');
}

if (characteristics.hasAuth) {
  console.log('Includes authentication logic');
}
```

---

#### `calculateConfidence(characteristics: CodeCharacteristics): number`

**Purpose:** Calculate confidence score (0-100) for categorization

**Algorithm:**

1. Start at 50% baseline
2. Add confidence for strong signals:
   - React component: +20
   - CLI: +20
   - Hook: +20
   - Test: +25
   - API: +15
   - Store: +15
   - Generator: +15
   - Infrastructure: +15

3. Subtract confidence for ambiguity:
   - React component + API: -15 (hybrid component)
   - Hook + Store: -15 (hook that's also a store)
   - CLI + API: -15 (CLI that calls APIs)

4. Clamp to 0-100

**Examples:**

```typescript
// High confidence: Clear React component
{
  isReactComponent: true,
  hasProps: true,
  hasEvents: true,
  // ... all others false
}
// Confidence: 50 + 20 = 70

// Very high confidence: Clear test file
{
  isTest: true,
  // ... all others false
}
// Confidence: 50 + 25 = 75

// Low confidence: Ambiguous (React component + API endpoint)
{
  isReactComponent: true,
  isAPI: true,
  // ... all others false
}
// Confidence: 50 + 20 + 15 - 15 = 70

// Medium confidence: Hook with state
{
  isHook: true,
  usesState: true,
  // ... all others false
}
// Confidence: 50 + 20 = 70
```

**Usage:**
```typescript
const element = await analyzeElement('/path/to/project', 'useAuth');
const characteristics = analyzeCodeCharacteristics(element);
const confidence = calculateConfidence(characteristics);

if (confidence < 60) {
  console.log('Low confidence, may need manual review');
} else if (confidence > 90) {
  console.log('High confidence, proceed with auto-generation');
}
```

---

## Internal Functions

### `findElement(elements: any[], elementName: string): any | null`

**Purpose:** Find element in index using multiple matching strategies

**Matching Priority:**
1. **Exact name match:** `element.name === elementName`
2. **Case-insensitive match:** `element.name.toLowerCase() === elementName.toLowerCase()`
3. **File path match:** `element.file === elementName`
4. **File path partial match:** `element.file.endsWith(elementName)`
5. **ID match:** `element.id === elementName`

**Examples:**
```typescript
// Input: "FileTree"
findElement(elements, "FileTree")           // Matches name
findElement(elements, "filetree")           // Matches case-insensitive
findElement(elements, "src/components/FileTree.tsx")  // Matches file path
findElement(elements, "FileTree.tsx")       // Matches partial path
findElement(elements, "FileTree.tsx#FileTree")  // Matches ID
```

---

### `extractCharacteristics(element: any): ElementCharacteristics`

**Purpose:** Convert raw `.coderef/index.json` element to `ElementCharacteristics`

**Extraction Logic:**

```typescript
{
  name: element.name || '',
  type: element.type || 'unknown',
  file: element.file || '',
  imports: element.imports || [],
  exports: element.exports || [],
  metadata: {
    // React-specific
    hasJSX: element.metadata?.hasJSX || false,
    hooks: element.metadata?.hooks || [],
    props: element.metadata?.props?.map(transformProp) || [],

    // State management
    stateVariables: element.metadata?.stateVariables?.map(transformState) || [],

    // Event handlers
    eventHandlers: element.metadata?.eventHandlers?.map(transformEvent) || [],

    // API calls
    apiCalls: element.metadata?.apiCalls?.map(transformApiCall) || [],

    // Additional metadata (spread)
    ...element.metadata
  }
}
```

**Transformations:**
- Props: Extract name, type, required, default, description
- State: Extract name, type, initialValue, persisted, persistenceKey
- Events: Extract name, type, description
- API calls: Extract method, endpoint, library

---

## Usage Patterns

### Pattern 1: Basic Analysis
```typescript
import { analyzeElement } from './detection/analyzer';

const element = await analyzeElement('/path/to/project', 'FileTree');
console.log(`Found: ${element.name} (${element.type})`);
```

### Pattern 2: Full Detection Pipeline
```typescript
import { analyzeElement, analyzeCodeCharacteristics, calculateConfidence } from './detection/analyzer';

const element = await analyzeElement('/path/to/project', 'useAuth');
const characteristics = analyzeCodeCharacteristics(element);
const confidence = calculateConfidence(characteristics);

console.log(`Element: ${element.name}`);
console.log(`Is Hook: ${characteristics.isHook}`);
console.log(`Has Auth: ${characteristics.hasAuth}`);
console.log(`Confidence: ${confidence}%`);
```

### Pattern 3: Conditional Logic Based on Characteristics
```typescript
const element = await analyzeElement('/path/to/project', 'UserProfile');
const characteristics = analyzeCodeCharacteristics(element);

if (characteristics.isReactComponent) {
  if (characteristics.hasProps) {
    console.log('Include Props module');
  }
  if (characteristics.usesState) {
    console.log('Include State module');
  }
  if (characteristics.hasEvents) {
    console.log('Include Events module');
  }
}

if (characteristics.hasAuth) {
  console.log('Include Auth module');
}

if (characteristics.hasAccessibility) {
  console.log('Include Accessibility module');
}
```

---

## Error Handling

### Missing .coderef/index.json
```typescript
try {
  await analyzeElement('/invalid/path', 'Element');
} catch (error) {
  // Error: No .coderef/index.json found at /invalid/path/.coderef/index.json.
  // Run 'coderef scan --project-path /invalid/path' first.
}
```

### Invalid JSON Format
```typescript
// If .coderef/index.json is:
{ "invalid": "format" }

// Throws:
// Error: Invalid .coderef/index.json format - missing elements array
```

### Element Not Found
```typescript
try {
  await analyzeElement('/path/to/project', 'NonExistent');
} catch (error) {
  // Error: Element "NonExistent" not found in .coderef/index.json.
  // Available elements: FileTree, useAuth, AuthService, Button, Modal, ...
}
```

---

## Dependencies

**Node.js Built-ins:**
- `fs` - File system operations
- `path` - Path manipulation

**Internal:**
- `../types` - TypeScript type definitions

**External:**
- None

---

## Performance

- **File read:** ~5-20ms (reads `.coderef/index.json`)
- **Element search:** ~1-5ms (linear search with early exit)
- **Characteristic extraction:** ~1-2ms (object transformation)
- **Characteristic analysis:** ~1-2ms (boolean checks)
- **Confidence calculation:** <1ms (arithmetic)

**Total:** ~10-30ms per element

---

## Version

**Created:** 2025-01-02
**Last Updated:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/DETECT-001
