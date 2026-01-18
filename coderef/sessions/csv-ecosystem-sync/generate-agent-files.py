#!/usr/bin/env python3
"""
Generate agent files for CSV Ecosystem Sync session
Creates communication.json, instructions.json, and resources/index.md for each agent
"""

import json
from pathlib import Path

SESSION_PATH = Path(__file__).parent
CSV_PATH = r"C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\resources\coderef\tools-and-commands.csv"

# Agent configurations
AGENTS = {
    "coderef-assistant": {
        "path": r"C:\Users\willh\Desktop\assistant",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit assistant project for commands, scripts, workflows. Report discrepancies vs CSV.",
        "scope": "Assistant orchestrator project",
        "scan_targets": [".claude/commands/", "coderef/working/", "scripts/"]
    },
    "coderef-context": {
        "path": r"C:\Users\willh\.mcp-servers\coderef-context",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit coderef-context MCP server for tools, commands, scripts. Report discrepancies vs CSV.",
        "scope": "coderef-context MCP server",
        "scan_targets": ["server.py (tools)", ".claude/commands/", "scripts/"]
    },
    "coderef-workflow": {
        "path": r"C:\Users\willh\.mcp-servers\coderef-workflow",
        "phases": ["phase_1", "phase_3"],
        "role": "Phase 1: Audit coderef-workflow MCP server. Phase 3: Update workflow instructions to maintain CSV.",
        "scope": "coderef-workflow MCP server",
        "scan_targets": ["server.py (tools)", ".claude/commands/", "scripts/", "workflows/"],
        "phase_3_task": "Update workflow instructions to automatically maintain CSV when agents add/modify resources"
    },
    "coderef-docs": {
        "path": r"C:\Users\willh\.mcp-servers\coderef-docs",
        "phases": ["phase_1", "phase_2"],
        "role": "Phase 1: Audit coderef-docs MCP server. Phase 2: Integrate audit results into CSV, validate updates.",
        "scope": "coderef-docs MCP server",
        "scan_targets": ["server.py (tools)", ".claude/commands/", "scripts/", "validators/"],
        "phase_2_task": "Integrate all agent audit results into CSV"
    },
    "coderef-personas": {
        "path": r"C:\Users\willh\.mcp-servers\coderef-personas",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit coderef-personas MCP server for tools, commands, persona definitions. Report discrepancies vs CSV.",
        "scope": "coderef-personas MCP server",
        "scan_targets": ["server.py (tools)", ".claude/commands/", "personas/"]
    },
    "coderef-testing": {
        "path": r"C:\Users\willh\.mcp-servers\coderef-testing",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit coderef-testing MCP server for tools, commands, test scripts. Report discrepancies vs CSV.",
        "scope": "coderef-testing MCP server",
        "scan_targets": ["server.py (tools)", ".claude/commands/", "scripts/"]
    },
    "papertrail": {
        "path": r"C:\Users\willh\.mcp-servers\papertrail",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit papertrail MCP server for tools, validators, schemas. Report discrepancies vs CSV.",
        "scope": "papertrail MCP server",
        "scan_targets": ["server.py (tools)", "validators/", "schemas/"]
    },
    "coderef-core": {
        "path": r"C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core",
        "phases": ["phase_1"],
        "role": "Phase 1: Audit coderef-core package ONLY (dashboard agent handles rest of dashboard project). Report discrepancies vs CSV.",
        "scope": "coderef-core package ONLY (NOT full dashboard project)",
        "scan_targets": ["src/", "scripts/"],
        "note": "Scope: coderef-core package only. Dashboard agent handles rest of coderef-dashboard project."
    }
}

def create_communication_json(agent_id, config):
    """Generate communication.json for an agent"""
    workorder_id = f"WO-CSV-ECOSYSTEM-SYNC-001-{agent_id.upper().replace('-', '_')}"

    comm = {
        "workorder_id": workorder_id,
        "parent_session": "WO-CSV-ECOSYSTEM-SYNC-001",
        "agent_id": agent_id,
        "agent_path": config["path"],
        "role": config["role"],
        "status": "not_started",
        "scope": config["scope"],
        "tasks": [
            {
                "task_id": "task_1",
                "description": f"Scan {config['scope']} for all resources",
                "status": "not_started"
            },
            {
                "task_id": "task_2",
                "description": "Compare findings against CSV",
                "status": "not_started"
            },
            {
                "task_id": "task_3",
                "description": "Document discrepancies and new resources",
                "status": "not_started"
            },
            {
                "task_id": "task_4",
                "description": "Create audit report in outputs/",
                "status": "not_started"
            }
        ],
        "success_metrics": {
            "audit_completeness": {
                "baseline": f"Unknown resources in {config['scope']}",
                "target": f"100% of {config['scope']} resources cataloged",
                "status": "Not started"
            }
        },
        "resources": {
            "index": "resources/index.md"
        },
        "outputs": {
            "primary_output": f"outputs/{agent_id}-audit-report.json",
            "format": "json"
        },
        "phase_gate": {
            "required_for_phase_2": True,
            "criteria": [
                "All 4 tasks complete",
                "Audit report created",
                "communication.json updated"
            ]
        }
    }

    if config.get("note"):
        comm["notes"] = config["note"]

    return comm

def create_instructions_json(agent_id, config):
    """Generate instructions.json for an agent"""
    workorder_id = f"WO-CSV-ECOSYSTEM-SYNC-001-{agent_id.upper().replace('-', '_')}"

    instructions = {
        "workorder_id": workorder_id,
        "agent_id": agent_id,
        "phases": config["phases"],
        "role": config["role"],
        "context": {
            "problem": "CSV may not accurately reflect current state of ecosystem resources",
            "solution": f"Audit {config['scope']} and report all discrepancies",
            "impact": "CSV becomes accurate single source of truth"
        },
        "execution_steps": {
            "step_1": "READ resources/index.md to access CSV and session documents",
            "step_2": "READ communication.json for task list",
            "step_3": f"SCAN {config['scope']} for all resources: {', '.join(config['scan_targets'])}",
            "step_4": "COMPARE findings against CSV",
            "step_5": "DOCUMENT discrepancies (missing, outdated, incorrect) and new resources",
            "step_6": f"CREATE outputs/{agent_id}-audit-report.json",
            "step_7": "UPDATE communication.json after each task"
        },
        "audit_scope": {
            "scan_targets": config["scan_targets"],
            "resource_types": ["Tool", "Command", "Script", "Validator", "Schema", "Workflow"],
            "comparison_fields": ["Type", "Server", "Name", "Path", "Description"]
        },
        "output_requirements": {
            "file": f"outputs/{agent_id}-audit-report.json",
            "format": "json",
            "template": "See phase_1_output_template in session instructions.json"
        },
        "phase_gate_checklist": [
            "All 4 tasks status='complete'",
            "Audit report created and validated",
            "communication.json updated"
        ]
    }

    return instructions

def create_resources_index(agent_id, config):
    """Generate resources/index.md for an agent"""
    return f"""# Resources Index - {agent_id} Agent

## Session Documents
- [Master Communication](../../../csv-ecosystem-sync/communication.json)
- [Master Instructions](../../../csv-ecosystem-sync/instructions.json)
- [Agent Communication](../communication.json)
- [Agent Instructions](../instructions.json)

## Primary CSV
- **Source of Truth:** `{CSV_PATH}`
- **Current State:** 306 resources, 9 types, 7 servers, 100% data quality

## Project Scope
- **Agent Home:** `{config['path']}`
- **Scope:** {config['scope']}
- **Scan Targets:** {', '.join(config['scan_targets'])}

## Audit Checklist
- [ ] Scan project for all resources
- [ ] Compare findings against CSV
- [ ] Document discrepancies (missing, outdated, incorrect)
- [ ] Identify new resources not in CSV
- [ ] Create audit report in outputs/

## Output
- `outputs/{agent_id}-audit-report.json`

**Session Path:** `C:\\Users\\willh\\.mcp-servers\\coderef\\sessions\\csv-ecosystem-sync\\{agent_id}`
**Phase:** {', '.join(config['phases'])}
"""

def main():
    print("Generating agent files for CSV Ecosystem Sync session...")

    # Skip coderef-dashboard (already created manually)
    agents_to_generate = {k: v for k, v in AGENTS.items() if k != "coderef-dashboard"}

    for agent_id, config in agents_to_generate.items():
        agent_dir = SESSION_PATH / agent_id
        print(f"\nGenerating files for {agent_id}...")

        # Create communication.json
        comm_path = agent_dir / "communication.json"
        with open(comm_path, 'w', encoding='utf-8') as f:
            json.dump(create_communication_json(agent_id, config), f, indent=2)
        print(f"  [OK] {comm_path.name}")

        # Create instructions.json
        inst_path = agent_dir / "instructions.json"
        with open(inst_path, 'w', encoding='utf-8') as f:
            json.dump(create_instructions_json(agent_id, config), f, indent=2)
        print(f"  [OK] {inst_path.name}")

        # Create resources/index.md
        resources_dir = agent_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        index_path = resources_dir / "index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(create_resources_index(agent_id, config))
        print(f"  [OK] resources/{index_path.name}")

    print(f"\n[OK] Generated files for {len(agents_to_generate)} agents")
    print("\nSession structure complete!")
    print(f"Session path: {SESSION_PATH}")

if __name__ == "__main__":
    main()
