Run all 7 inventory tools in sequence to generate a complete project snapshot.

## Instructions

Execute all inventory tools for the current project directory, then provide a combined summary.

### Step 1: Run All Inventory Tools

Call these 7 MCP tools in sequence (do NOT run in parallel - they share file system resources):

```python
# 1. File inventory
mcp__docs_mcp__inventory_manifest({
    "project_path": <current_working_directory>,
    "analysis_depth": "standard"
})

# 2. Dependency inventory (with security scan)
mcp__docs_mcp__dependency_inventory({
    "project_path": <current_working_directory>,
    "scan_security": true,
    "ecosystems": ["all"]
})

# 3. API inventory
mcp__docs_mcp__api_inventory({
    "project_path": <current_working_directory>,
    "frameworks": ["all"],
    "scan_documentation": true
})

# 4. Database inventory
mcp__docs_mcp__database_inventory({
    "project_path": <current_working_directory>,
    "database_systems": ["all"],
    "include_migrations": true
})

# 5. Config inventory (with secret masking)
mcp__docs_mcp__config_inventory({
    "project_path": <current_working_directory>,
    "formats": ["all"],
    "mask_sensitive": true
})

# 6. Test inventory
mcp__docs_mcp__test_inventory({
    "project_path": <current_working_directory>,
    "frameworks": ["all"],
    "include_coverage": true
})

# 7. Documentation inventory
mcp__docs_mcp__documentation_inventory({
    "project_path": <current_working_directory>
})
```

### Step 2: Generate Combined Summary

After all tools complete, present a unified summary:

```
Project Inventory Complete
==========================

Files:
- Total files: {from inventory_manifest}
- By category: {breakdown}

Dependencies:
- Total: {count}
- Outdated: {count} (run fix commands in dependencies.json)
- Vulnerable: {count} ({critical} critical, {high} high)

APIs:
- Endpoints: {count}
- Documentation coverage: {percent}%

Database:
- Tables/Collections: {count}
- Schemas detected: {list}

Configuration:
- Config files: {count}
- Sensitive values: {count} (masked)

Tests:
- Test files: {count}
- Frameworks: {list}
- Coverage: {percent}% (if available)

Documentation:
- Doc files: {count}
- Formats: {list}

All manifests saved to: coderef/inventory/
- manifest.json
- dependencies.json
- api.json
- database.json
- config.json
- tests.json
- documentation.json
```

## Output Files

All inventory data is saved to `coderef/inventory/` for later reference:
- `manifest.json` - File inventory
- `dependencies.json` - Dependencies with fix_command for outdated packages
- `api.json` - API endpoints
- `database.json` - Database schemas
- `config.json` - Configuration (secrets masked)
- `tests.json` - Test infrastructure
- `documentation.json` - Documentation files

## Use Cases

- **New project onboarding** - Understand entire codebase in 30 seconds
- **Security audit** - Check dependencies for vulnerabilities
- **Tech debt assessment** - Find untested code, outdated packages
- **Documentation review** - Identify missing docs
