# CodeRef Complete Resources Inventory

**Generated:** 2026-01-03
**Source:** CodeRef Dashboard Resources Page
**Total Resources:** 68 Commands + 71+ Tools + 16 Scripts + 6 Output Formats

---

## 📋 TAB 1: COMMANDS (68 total)

### Documentation & Standards (10 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/list-templates` | List all available documentation templates (README, ARCHITECTURE, API, etc.) | Docs | `list_templates` |
| `/get-template` | Retrieve content of a specific documentation template | Docs | `get_template` |
| `/audit-codebase` | Audit codebase for standards violations with compliance report | Workflow | `audit_codebase` |
| `/check-consistency` | Check code changes against established standards (pre-commit validation) | Workflow | `check_consistency` |
| `/establish-standards` | Scan codebase to discover patterns and generate standards documentation | Workflow | `establish_standards` |
| `/update-docs` | Update all documentation files after completing a feature (agentic workflow) | Workflow | `update_all_documentation` |
| `/coderef-foundation-docs` | Generate foundation docs using coderef analysis (hybrid approach) | Workflow | `coderef_foundation_docs` |
| `/generate-docs` | Generate documentation from coderef data | Docs | `generate_individual_doc` |
| `/generate-user-docs` | Generate user-facing documentation and guides | Docs | `generate_quickref_interactive` |

### Planning & Workflow (14 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/gather-context` | Gather feature requirements and save to context.json | Workflow | `gather_context` |
| `/analyze-for-planning` | Analyze project to discover foundation docs, standards, patterns (Section 0 prep) | Workflow | `analyze_project_for_planning` |
| `/create-plan` | Generate 10-section implementation plan from context and analysis | Workflow | `create_plan` |
| `/validate-plan` | Validate implementation plan (0-100 score) against quality checklist | Workflow | `validate_implementation_plan` |
| `/get-planning-template` | Get feature implementation planning template for AI reference | Workflow | `get_planning_template` |
| `/generate-plan-review` | Generate human-readable plan review report with score and recommendations | Workflow | `generate_plan_review_report` |
| `/align-plan` | Generate TodoWrite task list from plan.json for execution tracking | Workflow | `execute_plan` |
| `/create-workorder` | Create workorder with context.json and communication.json setup | Orchestrator | Manual workflow |
| `/complete-workorder` | Complete workorder workflow (update deliverables + archive) | Workflow | `update_deliverables + archive_feature` |
| `/update-task-status` | Update task status in plan.json as agents complete work | Workflow | `update_task_status` |
| `/audit-plans` | Audit all plans in workorder/ directory with health score | Workflow | `audit_plans` |
| `/features-inventory` | Generate inventory of features in workorder/ and archived/ | Workflow | `generate_features_inventory` |
| `/git-release` | Git release workflow with versioning and changelog | Workflow | Git commands + changelog |
| `/record-changes` | Smart changelog recording with git auto-detection | Workflow | `record_changes` |

### Deliverables & Tracking (6 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/generate-deliverables` | Generate DELIVERABLES.md template from plan.json structure | Workflow | `generate_deliverables_template` |
| `/update-deliverables` | Update DELIVERABLES.md with git metrics (LOC, commits, time) | Workflow | `update_deliverables` |
| `/archive-feature` | Archive completed feature from workorder/ to archived/ | Workflow | `archive_feature` |
| `/log-workorder` | Log new workorder entry to global workorder log | Workflow | `log_workorder` |
| `/get-workorder-log` | Query global workorder log with filtering | Workflow | `get_workorder_log` |
| `/stub` | Capture idea as STUB-XXX in orchestrator | Orchestrator | Manual stub creation |

### Multi-Agent Coordination (6 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/generate-agent-communication` | Generate communication.json from plan.json for multi-agent coordination | Workflow | `generate_agent_communication` |
| `/assign-agent-task` | Assign specific task to agent with workorder scoping | Workflow | `assign_agent_task` |
| `/verify-agent-completion` | Verify agent completion with git diff checks and success criteria | Workflow | `verify_agent_completion` |
| `/aggregate-agent-deliverables` | Aggregate metrics from multiple agent DELIVERABLES.md files | Workflow | `aggregate_agent_deliverables` |
| `/track-agent-status` | Track agent status across features with real-time dashboard | Workflow | `track_agent_status` |
| `/generate-handoff-context` | Generate agent handoff context files (claude.md) from plan + git history | Workflow | `generate_handoff_context` |

### Personas (11 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/ava` | Activate Ava - Frontend Specialist persona | Personas | `use_persona (ava)` |
| `/marcus` | Activate Marcus persona | Personas | `use_persona (marcus)` |
| `/quinn` | Activate Quinn persona | Personas | `use_persona (quinn)` |
| `/taylor` | Activate Taylor - General Purpose Agent persona | Personas | `use_persona (taylor)` |
| `/lloyd` | Activate Lloyd persona | Personas | `use_persona (lloyd)` |
| `/use-persona` | Activate any persona by name | Personas | `use_persona` |
| `/create-persona` | Create custom persona through guided workflow | Personas | `create_custom_persona` |
| `/coderef-assistant` | Activate CodeRef Assistant - Orchestrator persona | Personas | `use_persona (coderef-assistant)` |
| `/research-scout` | Activate Research Scout - Research assistant persona | Personas | `use_persona (research-scout)` |
| `/coderef-mcp-lead` | Activate MCP Lead persona - MCP system architect | Personas | `use_persona (coderef-mcp-lead)` |
| `/fix` | Activate fix/debug workflow persona | Personas | Specialized debug workflow |

### Testing (14 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/discover-tests` | Discover test files in project | Testing | `discover_tests` |
| `/list-frameworks` | List available testing frameworks | Testing | `list_frameworks` |
| `/run-tests` | Run all tests in project | Testing | `run_tests` |
| `/run-test-file` | Run specific test file | Testing | `run_test_file` |
| `/run-by-pattern` | Run tests matching pattern | Testing | `run_by_pattern` |
| `/run-parallel` | Run tests in parallel | Testing | `run_parallel` |
| `/test-results` | View test results | Testing | `test_results` |
| `/test-report` | Generate test report | Testing | `test_report` |
| `/compare-runs` | Compare test runs | Testing | `compare_runs` |
| `/test-coverage` | View test coverage | Testing | `test_coverage` |
| `/test-trends` | View test trends over time | Testing | `test_trends` |
| `/test-performance` | View test performance metrics | Testing | `test_performance` |
| `/detect-flaky` | Detect flaky tests | Testing | `detect_flaky` |
| `/test-health` | Check test health score | Testing | `test_health` |

### Agent-Specific (5 commands)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/coderef-context-agent` | Activate Context Agent - Code intelligence specialist | Context | `use_persona (coderef-context-agent)` |
| `/coderef-docs-agent` | Activate Docs Agent - Documentation specialist | Docs | `use_persona (coderef-docs-agent)` |
| `/coderef-testing-agent` | Activate Testing Agent - Test automation specialist | Testing | `use_persona (coderef-testing-agent)` |
| `/coderef-personas-agent` | Activate Personas Agent - Persona management specialist | Personas | `use_persona (coderef-personas-agent)` |
| `/testing-proof` | Generate testing completion proof | Testing | `proof_generator` |

### UI/Debug (1 command)

| Command | Description | Component | MCP Tool |
|---------|-------------|-----------|----------|
| `/debug-ui` | Debug UI issues using Chrome DevTools MCP with Ava's frontend expertise | Personas | Chrome DevTools MCP + Ava persona |

---

## 🛠️ TAB 2: TOOLS (71+ total)

### MCP Server: coderef-context (12 tools)

**Description:** Code Intelligence

**Tools:**
1. `coderef_scan` - Scan project and discover all code elements (functions, classes, components, hooks)
2. `coderef_query` - Query code relationships (calls, imports, dependencies)
3. `coderef_impact` - Analyze impact of modifying/deleting a code element
4. `coderef_complexity` - Get complexity metrics for a code element
5. `coderef_patterns` - Discover code patterns and test coverage gaps
6. `coderef_coverage` - Analyze test coverage in the codebase
7. `coderef_context` - Generate comprehensive codebase context (markdown + JSON)
8. `coderef_validate` - Validate CodeRef2 references in codebase
9. `coderef_drift` - Detect drift between CodeRef index and current code
10. `coderef_diagram` - Generate visual dependency diagrams (Mermaid or Graphviz)
11. `coderef_tag` - Add CodeRef2 tags to source files for tracking
12. `coderef_export` - Export coderef data in various formats (JSON, JSON-LD, Mermaid, DOT)

### MCP Server: coderef-workflow (23 tools)

**Description:** Planning & Workflow Management

**Tool Categories:**
- Planning & Context (9 tools)
- Multi-Agent Coordination (6 tools)
- Documentation & Standards (8 tools)

### MCP Server: coderef-personas (7 tools)

**Description:** Persona Management

**Tools:**
1. `use_persona` - Activate a persona by name
2. `create_custom_persona` - Create custom persona through guided workflow
3. `get_active_persona` - Get information about currently active persona
4. `clear_persona` - Deactivate current persona
5. `list_personas` - List all available personas
6. `generate_todo_list` - Convert plan task breakdown to TodoWrite format
7. `track_plan_execution` - Sync plan progress with todo status in real-time

### MCP Server: testing (18 tools)

**Description:** Test Automation & Validation

**Tools:**
1. `discover_tests` - Discover test files in project
2. `run_tests` - Run all tests
3. `test_results` - View test results
4. `test_coverage` - Analyze test coverage
5. `test_health` - Check test health score
6. `detect_flaky` - Detect flaky tests
7. `test_trends` - View test trends over time
8. `test_performance` - View test performance metrics
9. *(+ 10 more testing tools)*

### MCP Server: chrome-devtools (11 tools)

**Description:** Browser Debugging & UI Inspection

**Tools:**
1. `inspect_element` - Inspect DOM element
2. `console_log` - Access browser console logs
3. `network_monitor` - Monitor network requests
4. `performance_profile` - Profile performance
5. `screenshot` - Capture screenshots
6. `accessibility_audit` - Run accessibility audits
7. *(+ 5 more browser tools)*

---

## 📜 TAB 3: SCRIPTS (16+ total)

### Structure Creators (3 scripts)

| Script | Description | Component | Used In | Location |
|--------|-------------|-----------|---------|----------|
| `create-coderef-structure.py` | Create coderef/ directory structure (workorder/, archived/, foundation/, user/, standards/) | Orchestrator | Project initialization, workorder setup | `C:\Users\willh\Desktop\assistant\scripts\` |
| `scan-all.py` | Generate minimal .coderef/ structure (2-3 files: index.json, context.md) | System | Quick context generation, MCP server scans, v2 refactor | `C:\Users\willh\Desktop\projects\coderef-system\scripts\` |
| `populate-coderef.py` | Generate complete .coderef/ structure (all 16 files: reports/, diagrams/, exports/) | System | Full documentation pipeline, foundation docs, standards generation | `C:\Users\willh\Desktop\projects\coderef-system\scripts\` |

### Documentation Generators (7 scripts)

| Script | Description | Component | Used In | Location |
|--------|-------------|-----------|---------|----------|
| `generate_docs.py` | Generate foundation docs from .coderef/ data (README, ARCHITECTURE, API, SCHEMA, COMPONENTS) | System | Documentation pipeline (stage 3), per-project doc generation | `C:\Users\willh\Desktop\projects\coderef-system\.coderef\` |
| `foundation_generator.py` | Generate foundation docs (traditional approach - reads source files directly) | Workflow | coderef_foundation_docs MCP tool, legacy doc generation | `C:\Users\willh\.mcp-servers\coderef-workflow\generators\` |
| `coderef_foundation_generator.py` | Generate foundation docs (hybrid approach - uses .coderef/ data + source analysis) | Workflow | coderef_foundation_docs MCP tool (preferred), v2 refactor | `C:\Users\willh\.mcp-servers\coderef-workflow\generators\` |
| `enhance-standards.py` | Generate UI/behavior/UX standards using .coderef/ data | System | Documentation pipeline (stage 2), /establish-standards workflow | `C:\Users\willh\Desktop\projects\coderef-system\scripts\` |
| `standards_generator.py` | Generate standards (MCP tool integration with .coderef/ fast path) | Workflow | establish_standards MCP tool, consistency checking | `C:\Users\willh\.mcp-servers\coderef-workflow\generators\` |
| `diagram-generator.py` | Generate visual diagrams from codebase structure (Mermaid/DOT) | System | Documentation pipeline (stage 4), coderef_diagram MCP tool | `C:\Users\willh\Desktop\projects\coderef-system\scripts\` |
| `mermaid_formatter.py` | Format Mermaid diagrams | Workflow | Diagram formatting, visual dependency graphs | `C:\Users\willh\.mcp-servers\coderef-workflow\generators\` |

### Data Processing (2 scripts)

| Script | Description | Component | Used In | Location |
|--------|-------------|-----------|---------|----------|
| `parse_coderef_data.py` | Preprocess large index files (summarizes .coderef/index.json for large codebases) | System | Documentation pipeline (stage 2), large codebase optimization | `C:\Users\willh\Desktop\projects\coderef-system\packages\` (149 LOC) |
| `extract-context.py` | Extract context from source files | System | Context extraction, metadata generation | `C:\Users\willh\Desktop\projects\coderef-system\scripts\` |

---

## 🔄 TAB 4: WORKFLOWS (4 core workflows)

### 1. Complete Feature Implementation (End-to-End)
**Time:** 1-8+ hours
**Complexity:** High

**Phase 1: Plan (5-10 min)**
- `/create-workorder` → Gather context (interactive Q&A)
- Analyze project (coderef-context intelligence)
- Create 10-section plan.json
- Validate (score >= 90 recommended)

**Phase 2: Execute (1-8 hours)**
- `/execute-plan` → Generate TodoWrite tasks
- Activate expert persona (/ava, /marcus, etc)
- Implement with code context
- Update task status as work completes

**Phase 3: Complete (2-5 min)**
- `/complete-workorder` → Update deliverables
- Archive feature
- Git commit and push

### 2. Documentation Update Workflow
**Time:** 5-15 min
**Complexity:** Medium

**Foundation Docs:**
- `/coderef-foundation-docs` → Generate ARCHITECTURE, README, API docs
- `/establish-standards` → Create UI/UX/behavior standards
- Review and commit

### 3. Multi-Agent Coordination Workflow
**Time:** 30 min - 2 hours
**Complexity:** Very High

**Setup:**
- Create plan with multi_agent: true
- `/generate-agent-communication` → Auto-generate coordination file
- Review agent assignments

**Execution:**
- `/assign-agent-task` → Assign phase to Agent 1, 2, 3...
- Each agent executes independently
- `/track-agent-status` → Monitor progress

**Completion:**
- `/verify-agent-completion` → Validate each agent
- `/aggregate-agent-deliverables` → Combine metrics

### 4. Git Release Workflow
**Time:** 5-10 min
**Complexity:** Low

**Release Steps:**
- `/record-changes` → Log changes to CHANGELOG.json
- Update version in package.json
- `git add . && git commit`
- `git tag -a v1.0.0 -m "Release v1.0.0"`
- `git push && git push --tags`

---

## ⚙️ TAB 5: SETUP (4 phases)

### Phase 1: Install MCP Servers
**Badge:** Required

1. `npm install -g @anthropic/claude-mcp`
2. Clone coderef-mcp servers to ~/.mcp-servers/
3. Verify installation: `claude-mcp --version`

### Phase 2: Configure Claude Desktop
**Badge:** Required

1. Edit ~/.claude/claude_desktop_config.json
2. Add coderef-workflow, coderef-context, coderef-personas servers
3. Restart Claude Desktop to load MCP servers

### Phase 3: Initialize Project Structure
**Badge:** Required

1. Run: `python create-coderef-structure.py`
2. Creates coderef/ directory with workorder/, archived/, foundation/, user/, standards/
3. Run: `python scan-all.py` to generate .coderef/ structure

### Phase 4: Generate Foundation Docs
**Badge:** Optional

1. `/coderef-foundation-docs` to generate ARCHITECTURE, README, API docs
2. `/establish-standards` to create UI/UX/behavior standards
3. Review and commit documentation

---

## 📥 TAB 6: OUTPUT FORMATS (6 formats)

### 1. JSON (.json)
**Description:** Structured data format for machine-readable output and API responses

**Common Use Cases:**
- `index.json` - Complete codebase structure
- `plan.json` - Implementation plans
- `communication.json` - Multi-agent coordination
- `context.json` - Feature requirements

### 2. Markdown (.md)
**Description:** Human-readable documentation format with rich formatting support

**Common Use Cases:**
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design
- `DELIVERABLES.md` - Completion checklists
- `context.md` - Codebase summary

### 3. Mermaid Diagrams (.mmd)
**Description:** Visual diagrams for architecture and dependencies

**Common Use Cases:**
- `architecture.mmd` - Package-level architecture
- `dependencies.mmd` - Dependency graphs
- `workflows.mmd` - Process flowcharts

### 4. GraphViz DOT (.dot)
**Description:** Graph description language for complex visualizations

**Common Use Cases:**
- Full dependency trees
- Call graphs
- Module relationships

### 5. CSV (.csv)
**Description:** Tabular data format for spreadsheet analysis

**Common Use Cases:**
- Metrics export
- Test results
- Code statistics

### 6. HTML (.html)
**Description:** Interactive documentation with navigation and styling

**Common Use Cases:**
- Documentation websites
- Interactive reports
- User guides with TOC

---

## 📊 SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| **Total Commands** | 68 |
| **Total MCP Tools** | 71+ |
| **Total Scripts** | 16+ |
| **Total Workflows** | 4 |
| **Total Output Formats** | 6 |
| **MCP Servers** | 5 |
| **Command Categories** | 8 |

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-03
**Maintained By:** CodeRef Team
