#!/usr/bin/env python3
"""
Personas MCP Server

Provides expert agent personas that influence how AI approaches problems.
"""

__version__ = "0.1.0"
__mcp_version__ = "1.0"

import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from src.persona_manager import PersonaManager
from src.generators.todo_list_generator import TodoListGenerator
from src.trackers.plan_execution_tracker import PlanExecutionTracker
from src.executors.interactive_plan_executor import InteractivePlanExecutor
from src.models import CustomPersonaInput
from src.validators import PersonaValidator
from src.persona_generator import PersonaGenerator

# Get server directory and personas directory
SERVER_DIR = Path(__file__).parent
PERSONAS_DIR = SERVER_DIR / "personas"

# Initialize persona manager
persona_manager = PersonaManager(PERSONAS_DIR)

# Initialize Phase 1 components (Lloyd Integration)
todo_generator = TodoListGenerator()
plan_tracker = PlanExecutionTracker()
plan_executor = InteractivePlanExecutor()

# Create MCP server
app = Server("personas-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available persona management tools."""
    return [
        Tool(
            name="use_persona",
            description="Activate an expert persona to gain specialized knowledge and behavior. Returns the persona's system prompt and expertise.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the persona to activate (e.g., 'mcp-expert')",
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_active_persona",
            description="Get information about the currently active persona.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="clear_persona",
            description="Deactivate the current persona and return to default state.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_personas",
            description="List all available personas with their descriptions.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # Phase 1: Lloyd Integration tools
        Tool(
            name="generate_todo_list",
            description="Convert plan task breakdown to TodoWrite format for Lloyd. Part of docs-expert v2.0 Phase 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_path": {
                        "type": "string",
                        "description": "Path to plan.json file"
                    },
                    "workorder_id": {
                        "type": "string",
                        "description": "Workorder ID (e.g., WO-AUTH-001)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["all", "remaining"],
                        "description": "Generate todos for 'all' tasks or 'remaining' incomplete tasks (default: all)"
                    }
                },
                "required": ["plan_path", "workorder_id"]
            }
        ),
        Tool(
            name="track_plan_execution",
            description="Sync plan progress with todo status in real-time. Part of docs-expert v2.0 Phase 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_path": {
                        "type": "string",
                        "description": "Path to plan.json file"
                    },
                    "workorder_id": {
                        "type": "string",
                        "description": "Workorder ID (e.g., WO-AUTH-001)"
                    },
                    "todo_status": {
                        "type": "array",
                        "description": "Array of todo objects with current status",
                        "items": {"type": "object"}
                    }
                },
                "required": ["plan_path", "workorder_id", "todo_status"]
            }
        ),
        Tool(
            name="execute_plan_interactive",
            description="Execute plan with guided step-by-step or batch mode. Part of docs-expert v2.0 Phase 1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_path": {
                        "type": "string",
                        "description": "Path to plan.json file"
                    },
                    "workorder_id": {
                        "type": "string",
                        "description": "Workorder ID (e.g., WO-AUTH-001)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["step-by-step", "batch"],
                        "description": "Execution mode: 'step-by-step' (interactive) or 'batch' (all todos) (default: step-by-step)"
                    }
                },
                "required": ["plan_path", "workorder_id"]
            }
        ),
        # Custom Persona Creation (WO-CREATE-CUSTOM-PERSONA-001)
        Tool(
            name="create_custom_persona",
            description="Create a custom persona through guided workflow with automatic system prompt generation and validation. Users provide expertise, communication style, and use cases - the system generates a complete persona definition.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Unique persona name (alphanumeric, hyphens, underscores only, 3-50 chars)",
                        "pattern": "^[a-z0-9_-]+$"
                    },
                    "description": {
                        "type": "string",
                        "description": "One-sentence description of persona's role and expertise (20-200 chars)"
                    },
                    "expertise": {
                        "type": "array",
                        "description": "List of expertise areas (3-10 items)",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 10
                    },
                    "use_cases": {
                        "type": "array",
                        "description": "List of use cases where this persona is helpful (3-10 items)",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 10
                    },
                    "communication_style": {
                        "type": "string",
                        "description": "How this persona communicates (20-200 chars)"
                    },
                    "problem_solving": {
                        "type": "string",
                        "description": "Problem-solving approach (optional, max 200 chars)"
                    },
                    "tool_usage": {
                        "type": "string",
                        "description": "How persona uses tools (optional, max 200 chars)"
                    },
                    "specializations": {
                        "type": "array",
                        "description": "Optional specialized sub-areas (max 5)",
                        "items": {"type": "string"},
                        "maxItems": 5
                    },
                    "key_principles": {
                        "type": "array",
                        "description": "Optional guiding principles (max 10)",
                        "items": {"type": "string"},
                        "maxItems": 10
                    },
                    "example_responses": {
                        "type": "object",
                        "description": "Optional example question-answer pairs (max 3)",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["name", "description", "expertise", "use_cases", "communication_style"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "use_persona":
        return await handle_use_persona(arguments)
    elif name == "get_active_persona":
        return await handle_get_active_persona(arguments)
    elif name == "clear_persona":
        return await handle_clear_persona(arguments)
    elif name == "list_personas":
        return await handle_list_personas(arguments)
    # Phase 1: Lloyd Integration tools
    elif name == "generate_todo_list":
        return await handle_generate_todo_list(arguments)
    elif name == "track_plan_execution":
        return await handle_track_plan_execution(arguments)
    elif name == "execute_plan_interactive":
        return await handle_execute_plan_interactive(arguments)
    # Custom Persona Creation (WO-CREATE-CUSTOM-PERSONA-001)
    elif name == "create_custom_persona":
        return await handle_create_custom_persona(arguments)
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]


async def handle_use_persona(arguments: dict) -> list[TextContent]:
    """
    Activate a persona.

    Args:
        arguments: {"name": "persona-name"}

    Returns:
        Persona system prompt and metadata
    """
    persona_name = arguments.get("name")

    if not persona_name:
        return [TextContent(
            type="text",
            text="Error: 'name' parameter is required"
        )]

    try:
        # Activate persona
        persona = persona_manager.activate_persona(persona_name)

        # Build response with system prompt and metadata
        response = f"""# Persona Activated: {persona.name}

**Version:** {persona.version}
**Description:** {persona.description}

---

## System Prompt

{persona.system_prompt}

---

## Expertise Areas

{chr(10).join(f"- {item}" for item in persona.expertise)}

## Use Cases

{chr(10).join(f"- {item}" for item in persona.use_cases)}

## Communication Style

{persona.behavior.communication_style}

## Problem-Solving Approach

{persona.behavior.problem_solving}

---

✅ Persona '{persona.name}' is now active. You should adopt this persona's expertise, communication style, and problem-solving approach for all subsequent interactions.
"""

        return [TextContent(type="text", text=response)]

    except FileNotFoundError as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error activating persona '{persona_name}': {str(e)}"
        )]


async def handle_get_active_persona(arguments: dict) -> list[TextContent]:
    """
    Get currently active persona info.

    Returns:
        Active persona name and metadata, or message if no persona is active
    """
    active_persona = persona_manager.get_active_persona()

    if not active_persona:
        return [TextContent(
            type="text",
            text="No persona is currently active. Use 'use_persona' to activate a persona."
        )]

    response = f"""# Active Persona: {active_persona.name}

**Version:** {active_persona.version}
**Description:** {active_persona.description}
**Activated:** {persona_manager.state.activated_at.strftime('%Y-%m-%d %H:%M:%S') if persona_manager.state.activated_at else 'Unknown'}

## Current Expertise

{chr(10).join(f"- {item}" for item in active_persona.expertise)}

You are currently operating with the {active_persona.name} persona active.
"""

    return [TextContent(type="text", text=response)]


async def handle_clear_persona(arguments: dict) -> list[TextContent]:
    """
    Clear active persona.

    Returns:
        Confirmation message
    """
    active_name = persona_manager.get_active_persona_name()

    if not active_name:
        return [TextContent(
            type="text",
            text="No persona was active."
        )]

    persona_manager.clear_persona()

    return [TextContent(
        type="text",
        text=f"✅ Persona '{active_name}' has been deactivated. Returning to default behavior."
    )]


async def handle_list_personas(arguments: dict) -> list[TextContent]:
    """
    List all available personas.

    Returns:
        List of personas with descriptions
    """
    available_personas = persona_manager.list_available_personas()

    if not available_personas:
        return [TextContent(
            type="text",
            text="No personas found. Check that persona JSON files exist in the personas/base/ directory."
        )]

    # Build detailed list
    response_lines = ["# Available Personas\n"]

    for persona_name in available_personas:
        try:
            info = persona_manager.get_persona_info(persona_name)
            response_lines.append(f"## {info['name']} (v{info['version']})")
            response_lines.append(f"\n**Description:** {info['description']}\n")
            response_lines.append("**Expertise:**")
            response_lines.extend(f"- {item}" for item in info['expertise'][:5])  # Show first 5
            if len(info['expertise']) > 5:
                response_lines.append(f"- ... and {len(info['expertise']) - 5} more")
            response_lines.append("")
        except Exception as e:
            response_lines.append(f"## {persona_name}")
            response_lines.append(f"Error loading info: {str(e)}\n")

    response_lines.append(f"\n**Total:** {len(available_personas)} persona(s) available")
    response_lines.append("\nUse `use_persona` to activate a persona.")

    return [TextContent(type="text", text="\n".join(response_lines))]


async def handle_generate_todo_list(arguments: dict) -> list[TextContent]:
    """
    Generate todo list from plan task breakdown.

    Part of docs-expert v2.0 Phase 1: Lloyd Integration
    """
    plan_path = arguments.get("plan_path")
    workorder_id = arguments.get("workorder_id")
    mode = arguments.get("mode", "all")

    if not plan_path or not workorder_id:
        return [TextContent(
            type="text",
            text="Error: 'plan_path' and 'workorder_id' are required"
        )]

    try:
        result = todo_generator.generate_todo_list(plan_path, workorder_id, mode)

        # Format response
        response = f"""# Todo List Generated

**Workorder:** {result['workorder_id']}
**Total Tasks:** {result['total_tasks']}
**Mode:** {result['mode']}
**Generated:** {result['generated_at']}

## Todos

```json
{chr(10).join(f"{i+1}. {todo['content']}" for i, todo in enumerate(result['todos']))}
```

✅ {result['summary']}

## Next Steps

Pass these todos to TodoWrite for Lloyd to execute:
- Use TodoWrite tool with the todos array
- Lloyd will track progress as tasks complete
- Use track_plan_execution to sync progress back to plan
"""

        return [TextContent(type="text", text=response)]

    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating todo list: {str(e)}")]


async def handle_track_plan_execution(arguments: dict) -> list[TextContent]:
    """
    Track plan execution progress by syncing with todo status.

    Part of docs-expert v2.0 Phase 1: Lloyd Integration
    """
    plan_path = arguments.get("plan_path")
    workorder_id = arguments.get("workorder_id")
    todo_status = arguments.get("todo_status")

    if not plan_path or not workorder_id or not todo_status:
        return [TextContent(
            type="text",
            text="Error: 'plan_path', 'workorder_id', and 'todo_status' are required"
        )]

    try:
        result = plan_tracker.track_plan_execution(plan_path, workorder_id, todo_status)

        # Format response
        progress = result['plan_status']
        response = f"""# Plan Execution Tracking

**Workorder:** {result['workorder_id']}
**Progress:** {progress['completed']}/{progress['total_tasks']} tasks ({progress['progress_percent']:.1f}%)
**Synced:** {result['synced_at']}

## Status Breakdown

- ✅ Completed: {progress['completed']}
- 🚧 In Progress: {progress['in_progress']}
- ⏳ Pending: {progress['pending']}

## Task Details

{chr(10).join(f"Task {t['task_id']}: {t['status']}" + (f" (completed: {t['completed_at']})" if t.get('completed_at') else "") for t in result['task_details'][:10])}

{f"... and {len(result['task_details']) - 10} more tasks" if len(result['task_details']) > 10 else ""}

✅ {result['summary']}

Plan file updated: {result['updated_plan_path']}
"""

        return [TextContent(type="text", text=response)]

    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error tracking execution: {str(e)}")]


async def handle_execute_plan_interactive(arguments: dict) -> list[TextContent]:
    """
    Execute plan with guided step-by-step or batch mode.

    Part of docs-expert v2.0 Phase 1: Lloyd Integration
    """
    plan_path = arguments.get("plan_path")
    workorder_id = arguments.get("workorder_id")
    mode = arguments.get("mode", "step-by-step")

    if not plan_path or not workorder_id:
        return [TextContent(
            type="text",
            text="Error: 'plan_path' and 'workorder_id' are required"
        )]

    try:
        result = plan_executor.execute_plan_interactive(plan_path, workorder_id, mode)

        if mode == "batch":
            # Batch mode response
            response = f"""# Batch Execution Mode

**Workorder:** {result['workorder_id']}
**Total Tasks:** {result['total_tasks']}

## Instructions

{result['instructions']['what_to_do']}

**Tracking:** {result['instructions']['how_to_track']}
**Completion:** {result['instructions']['completion']}

## All Todos Generated

{chr(10).join(f"{i+1}. {todo['content']}" for i, todo in enumerate(result['todos'][:10]))}

{f"... and {len(result['todos']) - 10} more todos" if len(result['todos']) > 10 else ""}

✅ {result['summary']}
"""
        else:
            # Step-by-step mode response
            current = result['current_task']
            guidance = result['guidance']
            progress = result['progress']

            response = f"""# Interactive Execution - Task {progress['current']}/{progress['total_tasks']}

**Workorder:** {result['workorder_id']}
**Progress:** {progress['completed']}/{progress['total_tasks']} completed ({progress['percent']:.1f}%)

## Current Task

**Task {current['task_number']}:** {current['description']}

**Files to Modify:**
{chr(10).join(f"- {f}" for f in current['files']) if current['files'] else "No specific files"}

**Acceptance Criteria:**
{chr(10).join(f"- {c}" for c in current['acceptance_criteria']) if current['acceptance_criteria'] else "No specific criteria"}

**Estimated Time:** {current.get('estimated_time', 'Not specified')}

## Guidance

**What to do:**
{guidance['what_to_do']}

**How to do it:**
{guidance['how_to_do_it']}

**Acceptance test:**
{guidance['acceptance_test']}

{'⚠️ **WARNING:** Dependencies not met! Complete blocking tasks first.' if not guidance['dependencies_met'] else '✅ Dependencies met, ready to proceed.'}

## Next Actions

- {result['actions']['mark_complete']}
- {result['actions']['get_next']}

✅ {result['summary']}
"""

        return [TextContent(type="text", text=response)]

    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing plan: {str(e)}")]


async def handle_create_custom_persona(arguments: dict) -> list[TextContent]:
    """
    Create a custom persona with guided workflow and validation.

    Part of custom persona feature (WO-CREATE-CUSTOM-PERSONA-001).

    Args:
        arguments: Persona input data (name, description, expertise, use_cases, etc.)

    Returns:
        Success message with persona details or validation errors
    """
    try:
        # Create CustomPersonaInput from arguments
        persona_input = CustomPersonaInput(**arguments)

        # Validate persona input (multi-stage validation)
        validator = PersonaValidator()
        passed, results = validator.validate_all(persona_input.model_dump())

        # Collect all errors and warnings
        all_errors = []
        all_warnings = []

        for stage_name, result in results.items():
            if result.errors:
                all_errors.extend([f"[{stage_name}] {error}" for error in result.errors])
            if result.warnings:
                all_warnings.extend([f"[{stage_name}] {warning}" for warning in result.warnings])

        # If validation failed, return errors
        if not passed:
            error_msg = "# Persona Creation Failed\n\n"
            error_msg += "**Validation Errors:**\n\n"
            error_msg += "\n".join(f"- {error}" for error in all_errors)

            if all_warnings:
                error_msg += "\n\n**Warnings:**\n\n"
                error_msg += "\n".join(f"- {warning}" for warning in all_warnings)

            return [TextContent(type="text", text=error_msg)]

        # Generate persona
        generator = PersonaGenerator()
        persona_definition = generator.generate_persona_definition(persona_input)

        # Save persona to personas/custom/
        saved_path = generator.save_persona(persona_definition)

        # Build success response
        response = f"""# ✅ Custom Persona Created Successfully

**Name:** {persona_definition.name}
**Version:** {persona_definition.version}
**Description:** {persona_definition.description}
**Saved to:** {saved_path}

## Persona Details

**Expertise Areas ({len(persona_definition.expertise)}):**
{chr(10).join(f"- {item}" for item in persona_definition.expertise)}

**Use Cases ({len(persona_definition.use_cases)}):**
{chr(10).join(f"- {item}" for item in persona_definition.use_cases)}

**Communication Style:**
{persona_definition.behavior.communication_style}

**Problem-Solving Approach:**
{persona_definition.behavior.problem_solving}

**Tool Usage:**
{persona_definition.behavior.tool_usage}
"""

        # Add optional fields if present
        if persona_definition.specializations:
            response += f"\n**Specializations ({len(persona_definition.specializations)}):**\n"
            response += "\n".join(f"- {item}" for item in persona_definition.specializations) + "\n"

        if persona_definition.key_principles:
            response += f"\n**Key Principles ({len(persona_definition.key_principles)}):**\n"
            response += "\n".join(f"- {item}" for item in persona_definition.key_principles) + "\n"

        if persona_definition.example_responses:
            response += f"\n**Example Responses ({len(persona_definition.example_responses)}):**\n"
            for q, a in list(persona_definition.example_responses.items())[:2]:  # Show first 2
                response += f"\nQ: {q}\nA: {a}\n"

        # Add validation warnings if any
        if all_warnings:
            response += "\n## ⚠️ Validation Warnings\n\n"
            response += "Your persona was created successfully, but consider these recommendations:\n\n"
            response += "\n".join(f"- {warning}" for warning in all_warnings)
            response += "\n"

        # Add next steps
        response += f"""
## Next Steps

1. **Activate your persona:**
   ```
   use_persona('{persona_definition.name}')
   ```

2. **List all personas (including custom):**
   ```
   list_personas()
   ```

3. **Create a slash command** (optional):
   Create `.claude/commands/{persona_definition.name}.md` with:
   ```
   Activate the {persona_definition.name} persona

   mcp__personas-mcp__use_persona(name: "{persona_definition.name}")
   ```

✅ Your custom persona is ready to use!
"""

        return [TextContent(type="text", text=response)]

    except Exception as e:
        # Handle unexpected errors
        error_response = f"""# Error Creating Custom Persona

An unexpected error occurred:

```
{str(e)}
```

Please check your inputs and try again. All required fields must be provided:
- name (3-50 chars, lowercase, alphanumeric/hyphens/underscores)
- description (20-200 chars)
- expertise (3-10 items)
- use_cases (3-10 items)
- communication_style (20-200 chars)
"""
        return [TextContent(type="text", text=error_response)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
