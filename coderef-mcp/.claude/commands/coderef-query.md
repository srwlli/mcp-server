Query CodeRef2 elements by reference or pattern using the coderef2-mcp server.

Call the `mcp__coderef__query` tool with the provided query string.

**Usage Examples:**
- `/coderef-query @Fn/utils/format#formatDate` - Find specific function
- `/coderef-query @C/components/Button` - Find React component
- `/coderef-query pattern:auth` - Search by pattern

**Parameters:**
- query: CodeRef2 reference or search pattern (required)
- filter: Optional filters (type_designators, path_pattern, metadata_filters)
- limit: Max results (default: 100)
- include_relationships: Include dependency info (default: true)
- include_metadata: Include element metadata (default: true)
- include_source: Include source code snippets (default: false)

Returns: JSON with matching elements, relationships, and metadata.
