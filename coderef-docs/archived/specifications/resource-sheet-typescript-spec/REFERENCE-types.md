# Reference Sheet: types.ts

**File:** `modules/resource-sheet/types.ts`
**Purpose:** Core type definitions for Resource Sheet Module System
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/SETUP-003

---

## Overview

Defines TypeScript types and interfaces for:
- Element categories (19 types)
- Documentation modules (11 module types)
- Code characteristics detection
- Generation workflows
- Input/output structures

---

## Type Categories

### 1. Element Categories

#### `ElementCategory` (Union Type)

19 user-friendly classifications for code elements:

**Tools:**
- `'tools/cli-commands'` - CLI commands
- `'tools/scripts'` - Automation scripts
- `'tools/utilities'` - Helper utilities

**UI:**
- `'ui/widgets'` - Small UI components
- `'ui/pages'` - Full page components
- `'ui/components'` - Reusable components

**Services:**
- `'services/api-endpoints'` - REST/GraphQL endpoints
- `'services/api-clients'` - API client wrappers
- `'services/data-access'` - Database/data layer

**State:**
- `'state/hooks'` - React hooks
- `'state/stores'` - State management stores
- `'state/context'` - Context providers

**Data:**
- `'data/models'` - Data models
- `'data/schemas'` - JSON schemas
- `'data/validators'` - Validation logic

**Generators:**
- `'generators/scaffolding'` - Code generators
- `'generators/templates'` - Template systems
- `'generators/migrations'` - Database migrations

**Infrastructure:**
- `'infrastructure/build-scripts'` - Build tools
- `'infrastructure/deployment'` - Deployment scripts
- `'infrastructure/ci-cd'` - CI/CD pipelines

**Testing:**
- `'testing/test-helpers'` - Test utilities
- `'testing/mocks'` - Mock data/services
- `'testing/fixtures'` - Test fixtures

---

### 2. Module Names

#### `ModuleName` (Union Type)

**Universal Modules (always included):**
- `'architecture'` - Architecture patterns
- `'integration'` - Integration points
- `'testing'` - Testing strategies
- `'performance'` - Performance considerations

**Conditional Modules (based on characteristics):**
- `'state'` - State management
- `'props'` - Component props
- `'lifecycle'` - Component lifecycle
- `'events'` - Event handlers
- `'endpoints'` - API endpoints
- `'auth'` - Authentication
- `'errors'` - Error handling
- `'validation'` - Input validation
- `'persistence'` - Data persistence
- `'routing'` - URL routing
- `'accessibility'` - A11y features

---

## Core Interfaces

### Element Analysis

#### `ElementCharacteristics`

Represents code element detected from `.coderef/index.json`:

```typescript
interface ElementCharacteristics {
  name: string;          // "FileTree", "useAuth", "AuthService"
  type: string;          // "function", "class", "interface"
  file: string;          // File path
  imports: string[];     // Imported modules
  exports: string[];     // Exported items
  metadata: {
    hasJSX?: boolean;                  // React component
    hooks?: string[];                  // React hooks used
    props?: PropMetadata[];            // Component props
    stateVariables?: StateMetadata[];  // State vars
    eventHandlers?: EventMetadata[];   // Event handlers
    apiCalls?: ApiCallMetadata[];      // API calls
    [key: string]: any;                // Additional metadata
  };
}
```

**Usage:**
```typescript
const element: ElementCharacteristics = await analyzeElement(
  '/path/to/project',
  'FileTree'
);

console.log(element.name);              // "FileTree"
console.log(element.metadata.hasJSX);   // true
console.log(element.metadata.hooks);    // ["useState", "useEffect"]
```

---

#### `PropMetadata`

TypeScript component prop definition:

```typescript
interface PropMetadata {
  name: string;
  type: string;
  required: boolean;
  default?: string;
  description?: string;
}
```

**Example:**
```typescript
{
  name: "onSelect",
  type: "(file: File) => void",
  required: false,
  default: "undefined",
  description: "Callback when file is selected"
}
```

---

#### `StateMetadata`

State variable metadata:

```typescript
interface StateMetadata {
  name: string;
  type: string;
  initialValue?: string;
  persisted: boolean;
  persistenceKey?: string;
}
```

**Example:**
```typescript
{
  name: "selectedFile",
  type: "File | null",
  initialValue: "null",
  persisted: true,
  persistenceKey: "filetree:selectedFile"
}
```

---

#### `EventMetadata`

Event handler metadata:

```typescript
interface EventMetadata {
  name: string;
  type: string;
  description?: string;
}
```

**Example:**
```typescript
{
  name: "handleFileClick",
  type: "MouseEventHandler",
  description: "Handles file selection on click"
}
```

---

#### `ApiCallMetadata`

API call detection:

```typescript
interface ApiCallMetadata {
  method: string;      // "GET", "POST", etc.
  endpoint?: string;   // "/api/files"
  library: string;     // "fetch", "axios"
}
```

---

### Module System

#### `CharacteristicCheck`

Function type for checking element characteristics:

```typescript
type CharacteristicCheck = (element: ElementCharacteristics) => boolean;
```

**Example:**
```typescript
const hasState: CharacteristicCheck = (element) =>
  element.metadata.stateVariables && element.metadata.stateVariables.length > 0;
```

---

#### `ModuleTriggers`

Defines when a module should be included:

```typescript
interface ModuleTriggers {
  module: ModuleName;
  conditions: CharacteristicCheck[];
  description: string;
}
```

**Example:**
```typescript
{
  module: 'state',
  conditions: [
    (el) => el.metadata.hooks?.includes('useState'),
    (el) => (el.metadata.stateVariables?.length || 0) > 0
  ],
  description: 'Element manages state'
}
```

---

#### `DocumentationModule`

Complete module definition:

```typescript
interface DocumentationModule {
  name: ModuleName;
  type: 'universal' | 'conditional';
  appliesTo: ElementCategory[];
  triggers?: ModuleTriggers;
  markdownTemplate: string;
  schemaTemplate: string;
  jsdocTemplate: string;
  autoFill: {
    fields: string[];
    extract: (element: ElementCharacteristics) => Record<string, any>;
  };
  manualSections: {
    name: string;
    prompt: string;
    example?: string;
  }[];
}
```

**Example:**
```typescript
{
  name: 'state',
  type: 'conditional',
  appliesTo: ['ui/components', 'state/hooks'],
  triggers: { /* ... */ },
  markdownTemplate: '## State Management\n...',
  schemaTemplate: '{ "properties": { "state": ... } }',
  jsdocTemplate: '/** @state ... */',
  autoFill: {
    fields: ['stateVariables', 'initialValues'],
    extract: (el) => ({
      stateVariables: el.metadata.stateVariables || [],
      initialValues: /* ... */
    })
  },
  manualSections: [
    {
      name: 'State Diagram',
      prompt: 'Add state transition diagram',
      example: '```mermaid\nstateDiagram...\n```'
    }
  ]
}
```

---

### Results

#### `DetectionResult`

Output from classification step:

```typescript
interface DetectionResult {
  element: ElementCharacteristics;
  category: ElementCategory;
  confidence: number;          // 0-100
  alternates?: {
    category: ElementCategory;
    confidence: number;
  }[];
}
```

**Example:**
```typescript
{
  element: { /* ... */ },
  category: 'state/hooks',
  confidence: 95,
  alternates: [
    { category: 'ui/components', confidence: 40 }
  ]
}
```

---

#### `SelectionResult`

Output from module selection step:

```typescript
interface SelectionResult {
  modules: ModuleName[];
  rationale: Record<ModuleName, string>;
  estimatedAutoFill: number;   // 0-100
}
```

**Example:**
```typescript
{
  modules: ['architecture', 'integration', 'testing', 'state', 'props'],
  rationale: {
    'architecture': 'Universal module',
    'state': 'Detected useState hook',
    'props': 'Component has props interface'
  },
  estimatedAutoFill: 82
}
```

---

#### `SelectedModules`

Combined detection + selection result:

```typescript
interface SelectedModules {
  element: ElementCharacteristics;
  category: ElementCategory;
  modules: ModuleName[];
  confidence: number;
  reason: string;
}
```

---

#### `ComposedDocumentation`

Final documentation output:

```typescript
interface ComposedDocumentation {
  elementName: string;
  category: ElementCategory;
  modulesUsed: ModuleName[];
  markdown: string;
  schema: string;
  jsdoc: string;
  autoFillRate: number;        // 0-100
  reviewFlags: {
    section: string;
    reason: string;
  }[];
  uds: {
    workorder_id?: string;
    feature_id?: string;
    generated_by: string;
    timestamp: string;
  };
}
```

**Example:**
```typescript
{
  elementName: 'FileTree',
  category: 'ui/components',
  modulesUsed: ['architecture', 'integration', 'testing', 'props', 'events'],
  markdown: '# FileTree Component\n...',
  schema: '{ "$schema": "...", ... }',
  jsdoc: '/** @component FileTree ... */',
  autoFillRate: 85,
  reviewFlags: [
    { section: 'Performance', reason: 'Manual input required' }
  ],
  uds: {
    workorder_id: 'WO-DOCS-001',
    generated_by: 'resource-sheet-module v1.0.0',
    timestamp: '2025-01-02T12:00:00Z'
  }
}
```

---

### Tool I/O

#### `GenerationMode`

Documentation generation modes:

```typescript
type GenerationMode =
  | 'reverse-engineer'   // Auto-fill from existing code
  | 'template'           // Empty template for planning
  | 'refresh';           // Update existing docs
```

**Usage:**
- `'reverse-engineer'` - Default, analyze existing code and auto-fill
- `'template'` - Generate empty template for planning new feature
- `'refresh'` - Update docs to match current code

---

#### `GenerateResourceSheetInput`

Tool input parameters:

```typescript
interface GenerateResourceSheetInput {
  project_path: string;
  element_name: string;
  mode: GenerationMode;
  workorder_id?: string;
  feature_id?: string;
  output_path?: string;
  auto_analyze?: boolean;
  validate_against_code?: boolean;
}
```

**Example:**
```typescript
{
  project_path: '/path/to/project',
  element_name: 'FileTree',
  mode: 'reverse-engineer',
  workorder_id: 'WO-DOCS-001',
  output_path: '/custom/path'
}
```

---

#### `GenerateResourceSheetOutput`

Tool output:

```typescript
interface GenerateResourceSheetOutput {
  success: boolean;
  documentation?: ComposedDocumentation;
  files?: {
    markdown: string;
    schema: string;
    jsdoc: string;
  };
  error?: string;
  warnings?: string[];
}
```

**Success Example:**
```typescript
{
  success: true,
  documentation: { /* ComposedDocumentation */ },
  files: {
    markdown: '/path/to/FileTree.md',
    schema: '/path/to/FileTree.schema.json',
    jsdoc: '/path/to/.jsdoc/FileTree.jsdoc'
  },
  warnings: ['Performance section requires manual input']
}
```

**Error Example:**
```typescript
{
  success: false,
  error: 'Element "InvalidName" not found in .coderef/index.json'
}
```

---

## Type Guards & Utilities

### Characteristic Checks

```typescript
// Check if element has JSX
const hasJSX: CharacteristicCheck = (el) => el.metadata.hasJSX === true;

// Check if element uses React hooks
const usesHooks: CharacteristicCheck = (el) =>
  (el.metadata.hooks?.length || 0) > 0;

// Check if element has props
const hasProps: CharacteristicCheck = (el) =>
  (el.metadata.props?.length || 0) > 0;

// Check if element has state
const hasState: CharacteristicCheck = (el) =>
  (el.metadata.stateVariables?.length || 0) > 0;

// Check if element makes API calls
const makesApiCalls: CharacteristicCheck = (el) =>
  (el.metadata.apiCalls?.length || 0) > 0;
```

---

## Common Patterns

### Pattern 1: Type-Safe Module Definition

```typescript
const stateModule: DocumentationModule = {
  name: 'state',
  type: 'conditional',
  appliesTo: ['ui/components', 'state/hooks'],
  // TypeScript enforces all required fields
  markdownTemplate: '...',
  schemaTemplate: '...',
  jsdocTemplate: '...',
  autoFill: { /* ... */ },
  manualSections: []
};
```

### Pattern 2: Detection Result Handling

```typescript
const result: DetectionResult = await classifyElement(element);

if (result.confidence > 90) {
  // High confidence, proceed
} else if (result.alternates && result.alternates.length > 0) {
  // Show alternatives to user
  console.log('Possible categories:', result.alternates);
}
```

### Pattern 3: Output Validation

```typescript
const output: GenerateResourceSheetOutput = await generateResourceSheet(input);

if (!output.success) {
  throw new Error(output.error);
}

// TypeScript knows documentation exists here
console.log('Auto-fill rate:', output.documentation.autoFillRate);
```

---

## Version

**Created:** 2025-01-02
**Last Updated:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/SETUP-003
