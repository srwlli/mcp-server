# Architecture

## Dependency Graph

```mermaid

graph LR
    file_C__Users_willh__mcp_servers_coderef_personas_update_lloyd_phased_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_load_lloyd["load_lloyd"]:::fileStyle
    file_Path["Path"]:::fileStyle
    file_open["open"]:::fileStyle
    file_load["load"]:::fileStyle
    file_save_lloyd["save_lloyd"]:::fileStyle
    file_dump["dump"]:::fileStyle
    file_print["print"]:::fileStyle
    file_phase1_add_ecosystem_overview["phase1_add_ecosystem_overview"]:::fileStyle
    file_find["find"]:::fileStyle
    file_C__Users_willh__mcp_servers_coderef_personas_update_lloyd_complete_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_find_section_end["find_section_end"]:::fileStyle
    file_len["len"]:::fileStyle
    file_insert_after_section["insert_after_section"]:::fileStyle
    file_phase2_add_personas_details["phase2_add_personas_details"]:::fileStyle
    file_mcp["mcp"]:::fileStyle
    file_protocol["protocol"]:::fileStyle
    file_lines["lines"]:::fileStyle
    file_server["server"]:::fileStyle
    file_platform["platform"]:::fileStyle
    file_independent["independent"]:::fileStyle
    file_Stateless["Stateless"]:::fileStyle
    file_phase3_add_docs_details["phase3_add_docs_details"]:::fileStyle
    file_tools["tools"]:::fileStyle
    file_pattern["pattern"]:::fileStyle
    file_Generation["Generation"]:::fileStyle
    file_templates["templates"]:::fileStyle
    file_Management["Management"]:::fileStyle
    file_update_changelog["update_changelog"]:::fileStyle
    file_audit["audit"]:::fileStyle
    file_gate["gate"]:::fileStyle
    file_Workflows["Workflows"]:::fileStyle
    file_requirements["requirements"]:::fileStyle
    file_patterns["patterns"]:::fileStyle
    file_plan["plan"]:::fileStyle
    file_loop["loop"]:::fileStyle
    file_Tracking["Tracking"]:::fileStyle
    file_metrics["metrics"]:::fileStyle
    file_Coordination["Coordination"]:::fileStyle
    file_scoping["scoping"]:::fileStyle
    file_Inventory["Inventory"]:::fileStyle
    file_Patterns["Patterns"]:::fileStyle
    file_factory["factory"]:::fileStyle
    file_logging["logging"]:::fileStyle
    file_hardening["hardening"]:::fileStyle
    file_phase4_add_coderef_details["phase4_add_coderef_details"]:::fileStyle
    file_filters["filters"]:::fileStyle
    file_analysis["analysis"]:::fileStyle
    file_parameter["parameter"]:::fileStyle
    file_configuration["configuration"]:::fileStyle
    file_Simplified["Simplified"]:::fileStyle
    file_changes["changes"]:::fileStyle
    file_independently["independently"]:::fileStyle
    file_phase5_add_workflow["phase5_add_workflow"]:::fileStyle
    file_Workflow["Workflow"]:::fileStyle
    file_phase6_add_insights["phase6_add_insights"]:::fileStyle
    file_correctly["correctly"]:::fileStyle
    file_client["client"]:::fileStyle
    file_standalone["standalone"]:::fileStyle
    file_Composition["Composition"]:::fileStyle
    file_tracking["tracking"]:::fileStyle
    file_handling["handling"]:::fileStyle
    file_safety["safety"]:::fileStyle
    file_Observability["Observability"]:::fileStyle
    file_YOU["YOU"]:::fileStyle
    file_workflow["workflow"]:::fileStyle
    file_usage["usage"]:::fileStyle
    file_persona["persona"]:::fileStyle
    file_phase7_update_expertise["phase7_update_expertise"]:::fileStyle
    file_append["append"]:::fileStyle
    file_phase8_update_timestamp["phase8_update_timestamp"]:::fileStyle
    file_strftime["strftime"]:::fileStyle
    file_now["now"]:::fileStyle
    file_main["main"]:::fileStyle
    file_phase_func["phase_func"]:::fileStyle
    file_C__Users_willh__mcp_servers_coderef_personas_update_lloyd_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_injection["injection"]:::fileStyle
    file_INFLUENCE["INFLUENCE"]:::fileStyle
    file_system_prompt["system_prompt"]:::fileStyle
    file_exit["exit"]:::fileStyle
    file_C__Users_willh__mcp_servers_coderef_personas_server_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_PersonaManager["PersonaManager"]:::fileStyle
    file_components["components"]:::fileStyle
    file_TodoListGenerator["TodoListGenerator"]:::fileStyle
    file_PlanExecutionTracker["PlanExecutionTracker"]:::fileStyle
    file_InteractivePlanExecutor["InteractivePlanExecutor"]:::fileStyle
    file_Server["Server"]:::fileStyle
    file_list_tools["list_tools"]:::fileStyle
    file_Tool["Tool"]:::fileStyle
    file_Creation["Creation"]:::fileStyle
    file_call_tool["call_tool"]:::fileStyle
    file_handle_use_persona["handle_use_persona"]:::fileStyle
    file_handle_get_active_persona["handle_get_active_persona"]:::fileStyle
    file_handle_clear_persona["handle_clear_persona"]:::fileStyle
    file_handle_list_personas["handle_list_personas"]:::fileStyle
    file_handle_generate_todo_list["handle_generate_todo_list"]:::fileStyle
    file_handle_track_plan_execution["handle_track_plan_execution"]:::fileStyle
    file_handle_execute_plan_interactive["handle_execute_plan_interac..."]:::fileStyle
    file_handle_create_custom_persona["handle_create_custom_persona"]:::fileStyle
    file_TextContent["TextContent"]:::fileStyle

    %% Style definitions
    classDef functionStyle fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef classStyle fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef componentStyle fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef fileStyle fill:#f5f5f5,stroke:#616161,stroke-width:2px


 Diagram Summary:
   Format: mermaid
   Nodes: 100
   Edges: 0
   Direction: LR
     Truncated: Yes (original size: 100)

 Tip: Render at https://mermaid.live or in GitHub markdown

```


## Core Components

### Functions (102)

- **`execute_plan_interactive()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:28
- **`_execute_batch_mode()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:93
- **`_execute_step_by_step_mode()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:124
- **`_check_dependencies()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:199
- **`_generate_guidance()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:254
- **`get_next_task()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:327
- **`get_execution_summary()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:346
- **`generate_quick_plan()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/quick_plan_generator.py:33
- **`_generate_tasks()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/quick_plan_generator.py:144
- **`generate_todo_list()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/todo_list_generator.py:22
- **`generate_from_quick_plan()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/todo_list_generator.py:235
- **`track_plan_execution()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/trackers/plan_execution_tracker.py:22
- **`identify_blockers()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/trackers/plan_execution_tracker.py:232
- **`parse_string_arrays()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:129
- **`render()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:26
- **`_render_conditionals()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:56
- **`replace_section()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:61
- **`_render_variables()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:86
- **`replace_var()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:88
- **`generate_persona()`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:261

### Classes (53)

- **`InteractivePlanExecutor`** - C:/Users/willh/.mcp-servers/coderef-personas/src/executors/interactive_plan_executor.py:16
- **`QuickPlanGenerator`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/quick_plan_generator.py:18
- **`TodoListGenerator`** - C:/Users/willh/.mcp-servers/coderef-personas/src/generators/todo_list_generator.py:13
- **`PlanExecutionTracker`** - C:/Users/willh/.mcp-servers/coderef-personas/src/trackers/plan_execution_tracker.py:13
- **`PersonaBehavior`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:16
- **`PersonaDefinition`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:24
- **`PersonaState`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:41
- **`TaskExecutionStatus`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:63
- **`TaskProgress`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:75
- **`TodoMetadata`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:88
- **`CustomPersonaInput`** - C:/Users/willh/.mcp-servers/coderef-personas/src/models.py:106
- **`TemplateRenderer`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:22
- **`PersonaGenerator`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_generator.py:95
- **`PersonaManager`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_manager.py:13
- **`PersonaManager`** - C:/Users/willh/.mcp-servers/coderef-personas/src/persona_manager_backup2.py:13
- **`ValidationResult`** - C:/Users/willh/.mcp-servers/coderef-personas/src/validators.py:21
- **`PersonaValidator`** - C:/Users/willh/.mcp-servers/coderef-personas/src/validators.py:37
- **`TestFullPlanningWorkflow`** - C:/Users/willh/.mcp-servers/coderef-personas/tests/integration/test_phase1_workflows.py:70
- **`TestLloydCoordination`** - C:/Users/willh/.mcp-servers/coderef-personas/tests/integration/test_phase1_workflows.py:235
- **`TestEdgeCases`** - C:/Users/willh/.mcp-servers/coderef-personas/tests/integration/test_phase1_workflows.py:345

### Components (0)

_No components found_

## Module Organization

### `C:\Users\willh\.mcp-servers\coderef-personas/`
- Elements: 28

### `C:\Users\willh\.mcp-servers\coderef-personas\src/`
- Elements: 59

### `C:\Users\willh\.mcp-servers\coderef-personas\src\executors/`
- Elements: 9

### `C:\Users\willh\.mcp-servers\coderef-personas\src\generators/`
- Elements: 22

### `C:\Users\willh\.mcp-servers\coderef-personas\src\trackers/`
- Elements: 8

### `C:\Users\willh\.mcp-servers\coderef-personas\tests/`
- Elements: 251

### `C:\Users\willh\.mcp-servers\coderef-personas\tests\integration/`
- Elements: 26


## Design Patterns

_No patterns detected_

---
**Generated from:** `.coderef/index.json`, `.coderef/diagrams/dependencies.mmd`
**Date:** 2025-12-31
