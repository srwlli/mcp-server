# MCP Tools & Commands Quick Reference

## personas-mcp - Expert Agent Personas

Persona Management:
- use_persona - Activate expert persona (e.g., 'mcp-expert')
- get_active_persona - Get currently active persona info
- clear_persona - Deactivate current persona
- list_personas - List all available personas

Available Personas:
- mcp-expert (v1.0.0) - Expert in MCP architecture, server implementation, tool design, and best practices

## docs-mcp - Documentation & Planning Tools

Documentation Generation:
- list_templates - List available documentation templates
- get_template - Get specific template content
- generate_foundation_docs - Generate README, ARCHITECTURE, API, COMPONENTS, SCHEMA docs
- generate_individual_doc - Generate single documentation file
- generate_quickref_interactive - Create quickref guides for any application

Changelog Management:
- get_changelog - Retrieve project changelog
- add_changelog_entry - Add new changelog entry
- update_changelog - Analyze recent changes and update changelog automatically
- update_all_documentation - Update all docs (README, CLAUDE, CHANGELOG) with version auto-increment and workorder tracking

Standards & Consistency:
- establish_standards - Scan codebase to discover UI/UX/behavior patterns
- audit_codebase - Audit for standards violations
- check_consistency - Lightweight pre-commit quality gate

Planning & Validation:
- get_planning_template - Get implementation planning template
- analyze_project_for_planning - Discover docs, standards, patterns (optional: save to feature folder)
- gather_context - Gather feature requirements (assigns workorder ID)
- create_plan - Generate implementation plan (auto-generates DELIVERABLES.md)
- validate_implementation_plan - Validate plan quality (scores 0-100)
- generate_plan_review_report - Create human-readable plan review

Deliverables Tracking:
- generate_deliverables_template - Generate DELIVERABLES.md from plan.json (automatic with /create-plan)
- update_deliverables - Update DELIVERABLES.md with git metrics (LOC, commits, time)

Project Inventory:
- inventory_manifest - Generate comprehensive file inventory with metadata, categories, and risk levels
- dependency_inventory - Analyze dependencies across ecosystems with security scanning via OSV API
- api_inventory - Discover API endpoints across frameworks (FastAPI, Flask, Express, GraphQL) with documentation coverage
- database_inventory - Discover database schemas across systems (PostgreSQL, MySQL, MongoDB, SQLite) from ORM models and migrations
- config_inventory - Analyze configuration files with security masking for API keys, passwords, tokens
- test_inventory - Discover test frameworks, analyze coverage, identify untested code
- documentation_inventory - Analyze documentation quality across formats (Markdown, RST, AsciiDoc, HTML, Org-mode)

## coderef-mcp - Semantic Code Reference Analysis

Code Analysis & Query:
- mcp__coderef__query - Query CodeRef elements by reference or pattern
- mcp__coderef__analyze - Deep analysis (impact, coverage, complexity)
- mcp__coderef__validate - Validate CodeRef reference format and structure
- mcp__coderef__batch_validate - Batch validate multiple references (parallel or sequential)
- mcp__coderef__generate_docs - Generate documentation for CodeRef elements
- mcp__coderef__audit - Audit for validation, coverage, and performance

## ide - IDE Integration Tools

VS Code Integration:
- getDiagnostics - Get language diagnostics from VS Code
- executeCode - Execute Python code in Jupyter kernel

## MCP Server Management

You can manage MCP servers using:
- claude mcp list - List installed servers
- claude mcp get <name> - Get details about specific server
- claude mcp add - Add new MCP server
- claude mcp remove - Remove MCP server

## Available Slash Commands

Persona Management:
- /use-persona - Activate expert persona
- /list-personas - List available personas

Documentation Generation:
- /generate-docs - Generate foundation documentation for current project
- /generate-user-guide - Generate user guide documentation
- /generate-my-guide - Generate concise tool reference (60-80 lines)
- /generate-quickref - Generate quick reference guide
- /list-templates - List available documentation templates
- /get-template - Get specific template content

Changelog Management:
- /get-changelog - Retrieve project changelog
- /add-changelog - Add new changelog entry
- /update-changelog - Analyze and update changelog automatically
- /update-docs - Update all documentation after feature completion (README, CLAUDE, CHANGELOG)

Standards & Consistency:
- /establish-standards - Extract UI/UX/behavior standards from current project
- /audit-codebase - Audit current project for standards compliance
- /check-consistency - Quick consistency check on modified files (pre-commit gate)

Planning & Validation:
- /gather-context - Gather feature requirements and context (assigns workorder ID)
- /analyze-for-planning - Analyze project for implementation planning
- /get-planning-template - Get implementation planning template
- /create-plan - Create implementation plan (auto-generates DELIVERABLES.md)
- /validate-plan - Validate implementation plan quality (scores 0-100)
- /generate-plan-review - Generate human-readable plan review report

Deliverables Tracking:
- /generate-deliverables - Generate DELIVERABLES.md template from plan.json
- /update-deliverables - Update DELIVERABLES.md with git metrics (LOC, commits, time)

Project Inventory:
- /inventory-manifest - Generate comprehensive project file inventory
- /dependency-inventory - Analyze project dependencies with security scanning
- /api-inventory - Discover API endpoints across multiple frameworks with documentation coverage
- /database-inventory - Discover database schemas across multiple systems with ORM/migration parsing
- /config-inventory - Analyze configuration files with security detection
- /test-inventory - Discover test frameworks and analyze coverage metrics
- /documentation-inventory - Analyze documentation quality and metrics

---


Multi-Agent Coordination:
- generate_agent_communication - Generate communication.json from plan.json for parallel agents
- assign_agent_task - Assign task to specific agent with workorder scoping
- verify_agent_completion - Verify agent work with automated checks
- aggregate_agent_deliverables - Combine metrics from multiple agent DELIVERABLES.md files
- track_agent_status - Track agent status across features with real-time dashboard

Feature Management:
- archive_feature - Archive completed features from working to archived directory
- update_all_documentation - Update all docs (README, CLAUDE, CHANGELOG) with auto version bump
- execute_plan - Generate TodoWrite task list from plan.json with TASK-ID first format

Workorder Tracking:
- log_workorder - Log workorder entry to global activity log
- get_workorder_log - Query global workorder log with filters

Multi-Agent Coordination Slash Commands:
- /generate-agent-communication - Generate communication.json for parallel agents
- /assign-agent-task - Assign task to specific agent with workorder scoping
- /verify-agent-completion - Verify agent completion with automated checks
- /aggregate-agent-deliverables - Combine metrics from multiple agents
- /track-agent-status - Track agent status across features

Feature Management Slash Commands:
- /archive-feature - Archive completed features to archived directory
- /execute-plan - Generate TodoWrite task list from plan.json

Workorder Tracking Slash Commands:
- /log-workorder - Log workorder to global activity log
- /get-workorder-log - Query global workorder log with filters

---

**Total Tools:** 4 personas + 36 docs + 6 coderef + 2 ide = 48 tools
**Total Slash Commands:** 37+ commands across all categories
**Active MCP Servers:** personas-mcp, docs-mcp, coderef-mcp, hello-world-mcp, ide
