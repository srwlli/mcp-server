Validate CodeRef2 reference format and check if elements exist.

Call the `mcp__coderef__validate` tool to validate reference syntax and existence.

**Usage Examples:**
- `/coderef-validate @Fn/utils/format#formatDate:12` - Validate single reference
- `/coderef-validate @Fn/utils/format#formatDate:12 --check-exists` - Also check if element exists

**Parameters:**
- reference: Single CodeRef2 reference to validate
- references: Multiple references to validate (array)
- validate_existence: Check if element actually exists (default: false)

Returns: Validation results with syntax check, existence check, and error details if invalid.
