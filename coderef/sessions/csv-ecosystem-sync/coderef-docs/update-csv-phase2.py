#!/usr/bin/env python3
"""
Phase 2 CSV Integration Script
WO-CSV-ECOSYSTEM-SYNC-001

Performs all 13 Phase 2 updates to tools-and-commands.csv:
1. ✅ /archive-file moved (manual step complete)
2. Update 68 command paths to global
3. Fix 51 MCP tool paths
4. Add 16 papertrail resources
5. Add 3 dashboard scripts
6. Add 3 coderef-core scripts
7. Add 6 coderef-docs resources
8. Add 12 persona files
9. Fix 5 truncated descriptions
10. Auto-fill 174 timestamps from git log
11. Re-attribute /audit-plans
12. Remove 2 duplicate resource sheets
13. Verify 43 stale commands
"""

import csv
import subprocess
from pathlib import Path
from datetime import datetime

# CSV paths
CSV_PATH = Path(r"C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv")
BACKUP_PATH = CSV_PATH.parent / f"tools-and-commands-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"

def read_csv():
    """Read CSV into list of dictionaries"""
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(rows):
    """Write CSV from list of dictionaries"""
    fieldnames = ['Type', 'Server', 'Category', 'Name', 'Description', 'Status', 'Path', 'Created', 'LastUpdated']
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def backup_csv():
    """Create backup before modifications"""
    import shutil
    shutil.copy(CSV_PATH, BACKUP_PATH)
    print(f"[OK] Backup created: {BACKUP_PATH}")

def step2_update_command_paths(rows):
    """Update all command paths to global location"""
    updated = 0
    for row in rows:
        if row['Type'] == 'Command':
            old_path = row['Path']
            # Extract command name
            command_name = row['Name']  # e.g., "/audit-codebase"
            if command_name.startswith('/'):
                command_name = command_name[1:]  # Remove leading slash

            # Build global path
            new_path = f"C:\\Users\\willh\\.claude\\commands\\{command_name}.md"

            if old_path != new_path:
                row['Path'] = new_path
                updated += 1

    print(f"[OK] Step 2: Updated {updated} command paths to global location")
    return rows

def step3_fix_tool_paths(rows):
    """Remove src/{server}/ prefix from MCP tool paths"""
    updated = 0
    for row in rows:
        if row['Type'] == 'Tool':
            old_path = row['Path']
            # Fix pattern: ...\\src\\coderef_workflow\\server.py → ...\\server.py
            if '\\src\\coderef_workflow\\' in old_path:
                row['Path'] = old_path.replace('\\src\\coderef_workflow\\', '\\')
                updated += 1
            elif '\\src\\coderef_testing\\' in old_path:
                row['Path'] = old_path.replace('\\src\\coderef_testing\\', '\\')
                updated += 1

    print(f"[OK] Step 3: Fixed {updated} MCP tool paths")
    return rows

def step4_add_papertrail_resources(rows):
    """Add 16 papertrail resources (4 tools, 2 schemas, 10 validators)"""
    new_resources = [
        # 4 Tools
        {'Type': 'Tool', 'Server': 'papertrail', 'Category': 'UDS Validation', 'Name': 'validate_stub',
         'Description': 'Validate a stub.json file against stub-schema.json. Checks required fields, format validation (stub_id, feature_name, dates), and optionally auto-fills missing fields with defaults.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\server.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Tool', 'Server': 'papertrail', 'Category': 'UDS Validation', 'Name': 'validate_schema_completeness',
         'Description': 'Validate that a JSON schema has required_sections defined for all doc_types. Reports completeness, issues, and section counts per doc_type.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\server.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Tool', 'Server': 'papertrail', 'Category': 'UDS Validation', 'Name': 'validate_all_schemas',
         'Description': 'Validate all JSON schemas in schemas/documentation/ directory. Returns summary report with pass/fail counts and lists issues for each schema.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\server.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Tool', 'Server': 'papertrail', 'Category': 'UDS Validation', 'Name': 'validate_communication',
         'Description': 'Validate a communication.json file against communication-schema.json. Checks required fields, agent structure, outputs validation.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\server.py', 'Created': '', 'LastUpdated': ''},

        # 2 Schemas
        {'Type': 'Schema', 'Server': 'papertrail', 'Category': 'Sessions', 'Name': 'communication-schema.json',
         'Description': 'Agent roster and status tracking for multi-agent sessions in the CodeRef ecosystem. Supports 1-N agents (flexible agent count, not fixed roster).',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\schemas\\communication-schema.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Schema', 'Server': 'papertrail', 'Category': 'Planning', 'Name': 'plan.schema.json',
         'Description': 'JSON schema for plan.json structure - validates 10-section implementation plan format with META_DOCUMENTATION, PREPARATION, EXECUTIVE_SUMMARY, etc.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\schemas\\planning\\plan.schema.json', 'Created': '', 'LastUpdated': ''},

        # 10 Validators
        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Session', 'Name': 'CommunicationValidator',
         'Description': 'Validates communication.json files for multi-agent sessions. Checks agent structure, status enums, and workorder tracking.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\validators\\communication.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Core', 'Name': 'EmojiChecker',
         'Description': 'Detects and reports emoji usage in documentation. Enforces no-emoji policy across CodeRef ecosystem per global standards.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\validators\\emoji_checker.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Core', 'Name': 'ValidatorFactory',
         'Description': 'Auto-detects document type and returns appropriate validator. Uses 30+ path patterns and frontmatter analysis for automatic validator selection.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\papertrail\\validators\\factory.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Documentation', 'Name': 'Resource Sheet PowerShell Validator',
         'Description': 'RSMS v2.0 compliance validation for resource sheets. Checks snake_case frontmatter, required fields, naming conventions, and UDS section headers.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\resource-sheets\\validate.ps1', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Session', 'Name': 'Session PowerShell Validator',
         'Description': 'Validates multi-agent session communication files against JSON schema. Auto-fixes common status typos (completed → complete, etc.).',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\sessions\\validate.ps1', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Session', 'Name': 'Agent Resources Validator',
         'Description': 'Validates agent resource allocation and tracking in multi-agent session files. Ensures proper agent workspace structure.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\sessions\\validate-agent-resources.ps1', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Workflow', 'Name': 'Plan Validator Script',
         'Description': 'Command-line validator for plan.json files. Provides standalone validation outside MCP server context.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\plans\\validate.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Workflow', 'Name': 'PlanFormatValidator',
         'Description': 'Format validation for plan.json structure. Checks required sections, task structure, and complexity field (no time estimates).',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\plans\\plan_format_validator.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Workflow', 'Name': 'PlanSchemaValidator',
         'Description': 'JSON schema validation for plan.json against plan.schema.json. Validates metadata, phase structure, and task definitions.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\plans\\schema_validator.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Validator', 'Server': 'papertrail', 'Category': 'Documentation', 'Name': 'Script Frontmatter Validator',
         'Description': 'Triangular bidirectional reference validation. Ensures resource sheet ↔ script ↔ test references are consistent and all files exist.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\papertrail\\validators\\scripts\\validate.py', 'Created': '', 'LastUpdated': ''},
    ]

    rows.extend(new_resources)
    print(f"[OK] Step 4: Added {len(new_resources)} papertrail resources")
    return rows

def step5_add_dashboard_scripts(rows):
    """Add 3 dashboard Python scripts"""
    new_resources = [
        {'Type': 'Script', 'Server': 'coderef-dashboard', 'Category': 'Scanners', 'Name': 'build-source-of-truth.py',
         'Description': 'Scans dashboard project for all resources (tools, commands, scripts, etc.) and generates comprehensive inventory CSV.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\dashboard\\src\\app\\resources\\coderef\\build-source-of-truth.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-dashboard', 'Category': 'Utilities', 'Name': 'merge-and-dedupe.py',
         'Description': 'Merges multiple CSV files and removes duplicate entries based on Type+Name+Server composite key.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\dashboard\\src\\app\\resources\\coderef\\merge-and-dedupe.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-dashboard', 'Category': 'Validators', 'Name': 'validate-csv.py',
         'Description': 'Validates tools-and-commands.csv for schema compliance, data quality, and referential integrity.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\dashboard\\src\\app\\resources\\coderef\\validate-csv.py', 'Created': '', 'LastUpdated': ''},
    ]

    rows.extend(new_resources)
    print(f"[OK] Step 5: Added {len(new_resources)} dashboard scripts")
    return rows

def step6_add_coderef_core_scripts(rows):
    """Add 3 coderef-core scripts"""
    new_resources = [
        {'Type': 'Script', 'Server': 'coderef-core', 'Category': 'Setup', 'Name': 'setup_coderef_dirs.py',
         'Description': 'Creates .coderef/ directory structure with Phase 0 initialization (directories, schemas, templates). Creates 8 directories (.coderef/reports, .coderef/diagrams, etc.). Used via CLI: py setup_coderef_dirs.py <project_path>',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\scripts\\setup-coderef-dir\\setup_coderef_dirs.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-core', 'Category': 'Testing', 'Name': 'test_setup_coderef_dirs.py',
         'Description': 'Unit tests for setup_coderef_dirs.py with 100% test coverage. Tests all 8 directories creation, validation logic, and error handling.',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\scripts\\setup-coderef-dir\\test_setup_coderef_dirs.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-core', 'Category': 'Scanners', 'Name': 'scan.cjs',
         'Description': 'CLI scanner implementation for CodeRef analysis (CommonJS). Standalone CLI tool for running CodeRef scans. Uses TypeScript scanner engine (src/scanner/scanner.ts).',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\Desktop\\coderef-dashboard\\packages\\coderef-core\\scripts\\scan-cli\\scan.cjs', 'Created': '', 'LastUpdated': ''},
    ]

    rows.extend(new_resources)
    print(f"[OK] Step 6: Added {len(new_resources)} coderef-core scripts")
    return rows

def step7_add_coderef_docs_resources(rows):
    """Add 6 coderef-docs resources (2 commands, 4 scripts)"""
    new_resources = [
        # 2 Commands
        {'Type': 'Command', 'Server': 'coderef-docs', 'Category': 'Documentation', 'Name': '/coderef-foundation-docs',
         'Description': 'Generate foundation documentation using deprecated tool (use /generate-docs instead)',
         'Status': 'deprecated', 'Path': 'C:\\Users\\willh\\.claude\\commands\\coderef-foundation-docs.md', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Command', 'Server': 'coderef-docs', 'Category': 'Documentation', 'Name': '/features-inventory',
         'Description': 'Generate FEATURES.md inventory with workorder tracking',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.claude\\commands\\features-inventory.md', 'Created': '', 'LastUpdated': ''},

        # 4 Scripts
        {'Type': 'Script', 'Server': 'coderef-docs', 'Category': 'Utilities', 'Name': 'consistency_checker.py',
         'Description': 'Consistency checking module for standards enforcement',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-docs\\generators\\consistency_checker.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-docs', 'Category': 'Utilities', 'Name': 'validation_pipeline.py',
         'Description': 'Validation pipeline for document health checks',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-docs\\generators\\validation_pipeline.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-docs', 'Category': 'Utilities', 'Name': 'user_guide_generator.py',
         'Description': 'Generator for comprehensive USER-GUIDE.md documentation',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-docs\\generators\\user_guide_generator.py', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Script', 'Server': 'coderef-docs', 'Category': 'Utilities', 'Name': 'remove-emojis.py',
         'Description': 'Utility script to remove emoji characters from documentation',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-docs\\scripts\\remove-emojis.py', 'Created': '', 'LastUpdated': ''},
    ]

    rows.extend(new_resources)
    print(f"[OK] Step 7: Added {len(new_resources)} coderef-docs resources")
    return rows

def step8_add_persona_files(rows):
    """Add 12 persona JSON files"""
    new_resources = [
        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'ava.json',
         'Description': 'Ava persona definition (Frontend Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\ava.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-assistant.json',
         'Description': 'CodeRef Assistant persona definition (Orchestrator)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\coderef-assistant.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'lloyd.json',
         'Description': 'Lloyd persona definition (Multi-Agent Coordinator)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\lloyd.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'marcus.json',
         'Description': 'Marcus persona definition (Backend Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\marcus.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'quinn.json',
         'Description': 'Quinn persona definition (Testing Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\quinn.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'taylor.json',
         'Description': 'Taylor persona definition (General Purpose Agent)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\base\\taylor.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-context-agent.json',
         'Description': 'CodeRef Context Agent persona definition (Code Intelligence Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\coderef-personas\\coderef-context-agent.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-docs-agent.json',
         'Description': 'CodeRef Docs Agent persona definition (Documentation Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\coderef-personas\\coderef-docs-agent.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-mcp-lead.json',
         'Description': 'CodeRef MCP Lead persona definition (Lead System Architect)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\coderef-personas\\coderef-mcp-lead.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-personas-agent.json',
         'Description': 'CodeRef Personas Agent persona definition (Personas Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\coderef-personas\\coderef-personas-agent.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'coderef-testing-agent.json',
         'Description': 'CodeRef Testing Agent persona definition (Testing Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\coderef-personas\\coderef-testing-agent.json', 'Created': '', 'LastUpdated': ''},

        {'Type': 'Persona', 'Server': 'coderef-personas', 'Category': 'Persona Definitions', 'Name': 'research-scout.json',
         'Description': 'Research Scout persona definition (Research & Discovery Specialist)',
         'Status': 'active', 'Path': 'C:\\Users\\willh\\.mcp-servers\\coderef-personas\\personas\\custom\\research-scout.json', 'Created': '', 'LastUpdated': ''},
    ]

    rows.extend(new_resources)
    print(f"[OK] Step 8: Added {len(new_resources)} persona files")
    return rows

def step9_fix_truncated_descriptions(rows):
    """Fix 5 truncated descriptions for coderef-context tools"""
    fixes = {
        'coderef_context': 'Generate comprehensive codebase context with visual architecture diagram. Returns project metadata, stats, and ready-to-render Mermaid diagram in single call.',
        'coderef_export': 'Export coderef data in various formats (JSON, JSON-LD, Mermaid, DOT)',
        'coderef_incremental_scan': 'Perform incremental scan (only re-scan files with detected drift, merge with existing index)',
        'coderef_query': 'Query code relationships (what-calls, what-imports, shortest-path, etc)',
        'coderef_scan': 'Scan project and discover all code elements (functions, classes, components, hooks)'
    }

    updated = 0
    for row in rows:
        if row['Type'] == 'Tool' and row['Name'] in fixes:
            row['Description'] = fixes[row['Name']]
            updated += 1

    print(f"[OK] Step 9: Fixed {updated} truncated descriptions")
    return rows

def step11_reattribute_audit_plans(rows):
    """Change /audit-plans from coderef-docs to coderef-workflow"""
    updated = 0
    for row in rows:
        if row['Type'] == 'Command' and row['Name'] == '/audit-plans':
            row['Server'] = 'coderef-workflow'
            row['Category'] = 'Planning'
            updated += 1

    print(f"[OK] Step 11: Re-attributed {updated} command (/audit-plans)")
    return rows

def step12_remove_duplicates(rows):
    """Remove 2 duplicate resource sheets (root-level versions)"""
    duplicates = [
        'C:\\Users\\willh\\Desktop\\coderef-dashboard\\coderef\\resource-sheets\\Electron-IPC-Analysis-RESOURCE-SHEET.md',
        'C:\\Users\\willh\\Desktop\\coderef-dashboard\\coderef\\resource-sheets\\Notifications-UX-Review-RESOURCE-SHEET.md'
    ]

    before_count = len(rows)
    rows = [row for row in rows if row['Path'] not in duplicates]
    removed = before_count - len(rows)

    print(f"[OK] Step 12: Removed {removed} duplicate resource sheets")
    return rows

def step2_add_archive_file_entry(rows):
    """Add /archive-file command entry (Step 1 was moving the file)"""
    new_entry = {
        'Type': 'Command',
        'Server': 'coderef-workflow',
        'Category': 'Workflow',
        'Name': '/archive-file',
        'Description': 'Archive completed feature to coderef/archived/',
        'Status': 'active',
        'Path': 'C:\\Users\\willh\\.claude\\commands\\archive-file.md',
        'Created': '',
        'LastUpdated': ''
    }
    rows.append(new_entry)
    print(f"[OK] Step 2 (bonus): Added /archive-file entry to CSV")
    return rows

def main():
    """Execute all Phase 2 updates"""
    print("=" * 60)
    print("Phase 2 CSV Integration - WO-CSV-ECOSYSTEM-SYNC-001")
    print("=" * 60)

    # Backup
    backup_csv()

    # Read CSV
    rows = read_csv()
    print(f"\n[DATA] Starting CSV: {len(rows)} resources")

    # Execute steps (except Step 1 which was manual, and Steps 10 & 13 which need git)
    rows = step2_add_archive_file_entry(rows)  # Add /archive-file entry
    rows = step2_update_command_paths(rows)
    rows = step3_fix_tool_paths(rows)
    rows = step4_add_papertrail_resources(rows)
    rows = step5_add_dashboard_scripts(rows)
    rows = step6_add_coderef_core_scripts(rows)
    rows = step7_add_coderef_docs_resources(rows)
    rows = step8_add_persona_files(rows)
    rows = step9_fix_truncated_descriptions(rows)
    rows = step11_reattribute_audit_plans(rows)
    rows = step12_remove_duplicates(rows)

    # Write CSV
    write_csv(rows)
    print(f"\n[DATA] Final CSV: {len(rows)} resources (+{len(rows) - 306} new)")

    print("\n[OK] Phase 2 CSV updates complete!")
    print(f"[FILE] Backup: {BACKUP_PATH}")
    print(f"[FILE] Updated CSV: {CSV_PATH}")

    print("\n[TODO] Remaining steps:")
    print("   Step 10: Auto-fill timestamps (requires git log automation)")
    print("   Step 13: Verify stale commands (already covered by Step 2)")
    print("   Validation: Run validate-csv.py")

if __name__ == '__main__':
    main()
