Generate documentation for a specific CodeRef2 element.

Call the `mcp__coderef__generate_docs` tool to create element-level documentation.

**Usage Examples:**
- `/coderef-docs @Fn/utils/format#formatDate` - Generate function docs
- `/coderef-docs @C/components/Button --detailed` - Detailed component docs

**Parameters:**
- reference: CodeRef2 reference to document (required)
- doc_type: Documentation type - "summary", "detailed", "api" (default: "summary")
- include_examples: Include code examples (default: true)
- include_metadata: Include element metadata (default: true)

Returns: Generated documentation with description, parameters, examples, and metadata.
