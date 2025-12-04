  docs-mcp - Documentation & Planning Tools

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
  - Use /start-feature command for full workflow (recommended)
  - execute_plan - Generate TodoWrite task list from plan.json
  - validate_implementation_plan - Validate plan quality (scores 0-100)
  - generate_plan_review_report - Create human-readable plan review

  Advanced Planning (standalone tools):
  - gather_context - Gather feature requirements (assigns workorder ID)
  - analyze_project_for_planning - Discover docs, standards, patterns
  - create_plan - Generate implementation plan (auto-generates DELIVERABLES.md)
  - get_planning_template - Get implementation planning template

  Schema Validation Helpers (NEW in v1.1.0):
  - get_phases(plan) - Extract phases from array or legacy dict format
  - get_tasks(plan) - Extract tasks from array or task_breakdown format
  - get_files_to_create(plan) - Normalize strings to {path, purpose} objects
  - get_workorder_id(plan) - Safe extraction with fallback

  Deliverables Tracking:
  - generate_deliverables_template - Generate DELIVERABLES.md from plan.json (automatic with /create-plan)
  - update_deliverables - Update DELIVERABLES.md with git metrics (LOC, commits, time)

  Agent Handoff:
  - generate_handoff_context - Auto-generate agent handoff context from plan.json, analysis.json, and git history (reduces handoff time from 20-30 min to <5 min)

  Risk Assessment:
  - assess_risk - AI-powered risk evaluation across 5 dimensions (breaking changes, security, performance, maintainability, reversibility) with multi-option comparison and go/no-go recommendations

  Project Inventory:
  - inventory_manifest - Generate comprehensive file inventory with metadata, categories, and risk levels
  - dependency_inventory - Analyze dependencies across ecosystems with security scanning via OSV API
  - api_inventory - Discover API endpoints across frameworks (FastAPI, Flask, Express, GraphQL) with documentation coverage
  - database_inventory - Discover database schemas across systems (PostgreSQL, MySQL, MongoDB, SQLite) from ORM models and migrations
  - config_inventory - Analyze configuration files with security masking for API keys, passwords, tokens
  - test_inventory - Discover test frameworks, analyze coverage, identify untested code
  - documentation_inventory - Analyze documentation quality across formats (Markdown, RST, AsciiDoc, HTML, Org-mode)

  ide - IDE Integration Tools

  - getDiagnostics - Get language diagnostics from VS Code
  - executeCode - Execute Python code in Jupyter kernel

  You can also manage MCP servers using:
  - claude mcp list - List installed servers
  - claude mcp add - Add new MCP server
  - claude mcp remove - Remove MCP server

  Available Slash Commands

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
  - /start-feature - RECOMMENDED: Full planning workflow (gather → analyze → plan → validate → commit)
  - /execute-plan - Generate TodoWrite task list from plan.json
  - /validate-plan - Validate implementation plan quality (scores 0-100)
  - /generate-plan-review - Generate human-readable plan review report

  Advanced (standalone):
  - /gather-context - Gather feature requirements (use /start-feature instead)
  - /analyze-for-planning - Analyze project for planning (use /start-feature instead)
  - /create-plan - Create implementation plan (use /start-feature instead)
  - /get-planning-template - Get implementation planning template

  Deliverables Tracking:
  - /generate-deliverables - Generate DELIVERABLES.md template from plan.json
  - /update-deliverables - Update DELIVERABLES.md with git metrics (LOC, commits, time)

  Project Inventory:
  - /quick-inventory - Run ALL 7 inventory tools for complete project snapshot (recommended)
  - /inventory-manifest - Generate comprehensive project file inventory
  - /dependency-inventory - Analyze project dependencies with security scanning
  - /api-inventory - Discover API endpoints across multiple frameworks
  - /database-inventory - Discover database schemas with ORM/migration parsing
  - /config-inventory - Analyze configuration files with security detection
  - /test-inventory - Discover test frameworks and analyze coverage
  - /documentation-inventory - Analyze documentation quality

  
  Multi-Agent Coordination:
  - generate_agent_communication - Generate communication.json from plan.json for parallel agents
  - assign_agent_task - Assign task to specific agent with workorder scoping (Agent 2, 3, etc.)
  - verify_agent_completion - Verify agent work with automated checks
  - aggregate_agent_deliverables - Combine metrics from multiple agent DELIVERABLES.md files
  - track_agent_status - Track agent status across features with real-time dashboard

  Feature Management:
  - archive_feature - Archive completed features from working to archived directory (auto-logs workorder to workorder-log.txt)
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
  - /archive-feature - Archive completed features to archived directory (auto-logs workorder)
  - /update-docs - Update all documentation after feature completion
  - /execute-plan - Generate TodoWrite task list from plan.json

  Agent Handoff Slash Commands:
  - /generate-handoff-context - Auto-generate agent handoff context (reduces handoff time from 20-30 min to <5 min)

  Workorder Tracking Slash Commands:
  - /log-workorder - Log workorder to global activity log
  - /get-workorder-log - Query global workorder log with filters

  Reference:
  - /list-tools - Show all 54 MCP tools across 3 servers (docs-mcp, personas-mcp, coderef-mcp)
  - /list-commands - Show all slash commands by category

  Total: 38 MCP tools and 40 slash commands from docs-mcp server!
