# Reference Sheet: output/jsdoc-generator.ts

**File:** `modules/resource-sheet/output/jsdoc-generator.ts`
**Purpose:** Generate JSDoc comment blocks
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-002

---

## API

### `generateJSDoc(documentation: ComposedDocumentation, outputPath: string): Promise<string>`

Generate JSDoc comments file.

**Output File:** `{outputPath}/{elementName}.jsdoc`

**Returns:** Absolute path to generated file

**Example:**
```typescript
const path = await generateJSDoc(
  documentation,
  '/path/to/project/coderef/foundation-docs/.jsdoc'
);
// Returns: "/path/to/project/coderef/foundation-docs/.jsdoc/FileTree.jsdoc"
```

---

### `previewJSDoc(documentation: ComposedDocumentation): string`

Preview JSDoc without writing file.

**Returns:** JSDoc string

---

## Output Format

```javascript
/**
 * FileTree Component
 *
 * @name FileTree
 * @category UI Component
 * @type component
 * @file src/components/FileTree.tsx
 *
 * @description
 * Interactive file tree component for browsing project structure
 *
 * @prop {(file: File) => void} onSelect - File selection callback
 * @prop {boolean} expandAll - Expand all folders on mount
 *
 * @state {File | null} selectedFile - Currently selected file
 * @state {boolean} isExpanded - Tree expansion state
 *
 * @example
 * <FileTree onSelect={handleSelect} expandAll={false} />
 *
 * @workorder WO-DOCS-001
 * @generated 2025-01-02T12:00:00Z
 */
```

---

## Version
**Created:** 2025-01-02
**Workorder:** WO-RESOURCE-SHEET-MCP-TOOL-001/OUTPUT-002
