# Reference Sheet: output/schema-generator.ts

**File:** `modules/resource-sheet/output/schema-generator.ts`
**Purpose:** Generate JSON schemas for TypeScript types
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-003

---

## API

### `generateSchema(documentation: ComposedDocumentation, outputPath: string): Promise<string>`

Generate JSON schema file.

**Output File:** `{outputPath}/{elementName}.schema.json`

**Returns:** Absolute path to generated file

**Example:**
```typescript
const path = await generateSchema(
  documentation,
  '/path/to/project/coderef/schemas'
);
// Returns: "/path/to/project/coderef/schemas/FileTree.schema.json"
```

---

### `validateSchema(schema: string): { valid: boolean; errors: string[] }`

Validate JSON schema structure.

**Checks:**
- Valid JSON
- Conforms to JSON Schema Draft 7
- Required fields present
- Type definitions valid

---

## Output Format

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FileTree",
  "$id": "FileTree",
  "type": "object",
  "category": "UI Component",
  "metadata": {
    "workorder_id": "WO-DOCS-001",
    "generated": "2025-01-02T12:00:00Z",
    "file": "src/components/FileTree.tsx"
  },
  "properties": {
    "onSelect": {
      "type": "function",
      "description": "File selection callback",
      "signature": "(file: File) => void",
      "required": false
    },
    "expandAll": {
      "type": "boolean",
      "description": "Expand all folders on mount",
      "default": false
    }
  },
  "state": {
    "selectedFile": {
      "type": ["object", "null"],
      "description": "Currently selected file"
    }
  }
}
```

---

## Use Cases

1. **Type validation** - Validate component props at runtime
2. **Code generation** - Generate TypeScript types from schema
3. **Documentation** - Machine-readable component API
4. **Tooling** - IDE autocomplete, linting

---

## Version
**Created:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-003
