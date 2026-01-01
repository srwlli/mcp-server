# Architecture

## Dependency Graph

```mermaid

graph LR
    file_C__Users_willh__mcp_servers_coderef_workflow_validation_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_boundaries["boundaries"]:::fileStyle
    file_validate_project_path_input["validate_project_path_input"]:::fileStyle
    file_isinstance["isinstance"]:::fileStyle
    file_ValueError["ValueError"]:::fileStyle
    file_len["len"]:::fileStyle
    file_bytes["bytes"]:::fileStyle
    file_validate_version_format["validate_version_format"]:::fileStyle
    file_validate["validate"]:::fileStyle
    file_match["match"]:::fileStyle
    file_validate_template_name_input["validate_template_name_input"]:::fileStyle
    file_templates["templates"]:::fileStyle
    file_validate_changelog_inputs["validate_changelog_inputs"]:::fileStyle
    file_change_type["change_type"]:::fileStyle
    file_severity["severity"]:::fileStyle
    file_all["all"]:::fileStyle
    file_Functions["Functions"]:::fileStyle
    file_validate_scan_depth["validate_scan_depth"]:::fileStyle
    file_depth["depth"]:::fileStyle
    file_list["list"]:::fileStyle
    file_validate_focus_areas["validate_focus_areas"]:::fileStyle
    file_validate_severity_filter["validate_severity_filter"]:::fileStyle
    file_by["by"]:::fileStyle
    file_validate_audit_scope["validate_audit_scope"]:::fileStyle
    file_validate_severity_threshold["validate_severity_threshold"]:::fileStyle
    file_threshold["threshold"]:::fileStyle
    file_values["values"]:::fileStyle
    file_validate_file_list["validate_file_list"]:::fileStyle
    file_paths["paths"]:::fileStyle
    file_is_absolute["is_absolute"]:::fileStyle
    file_Path["Path"]:::fileStyle
    file_traversal["traversal"]:::fileStyle
    file_reuse["reuse"]:::fileStyle
    file_validate_section_name["validate_section_name"]:::fileStyle
    file_validate_plan_file_path["validate_plan_file_path"]:::fileStyle
    file_resolve["resolve"]:::fileStyle
    file_is_relative_to["is_relative_to"]:::fileStyle
    file_validate_plan_json_structure["validate_plan_json_structure"]:::fileStyle
    file_validate_feature_name_input["validate_feature_name_input"]:::fileStyle
    file_underscores["underscores"]:::fileStyle
    file_validate_workorder_id["validate_workorder_id"]:::fileStyle
    file_validate_risk_inputs["validate_risk_inputs"]:::fileStyle
    file_project_path["project_path"]:::fileStyle
    file_proposed_change["proposed_change"]:::fileStyle
    file_options["options"]:::fileStyle
    file_go["go"]:::fileStyle
    file_enumerate["enumerate"]:::fileStyle
    file_get["get"]:::fileStyle
    file_validate_resource_path["validate_resource_path"]:::fileStyle
    file_path["path"]:::fileStyle
    file_exists["exists"]:::fileStyle
    file_validate_expert_id["validate_expert_id"]:::fileStyle
    file_validate_resource_type["validate_resource_type"]:::fileStyle
    file_resource["resource"]:::fileStyle
    file_validate_expert_domain["validate_expert_domain"]:::fileStyle
    file_specialization["specialization"]:::fileStyle
    file_validate_expert_capabilities["validate_expert_capabilities"]:::fileStyle
    file_validate_context_expert_inputs["validate_context_expert_inputs"]:::fileStyle
    file_resource_path["resource_path"]:::fileStyle
    file_resource_type["resource_type"]:::fileStyle
    file_expert_id["expert_id"]:::fileStyle
    file_domain["domain"]:::fileStyle
    file_capabilities["capabilities"]:::fileStyle
    file_C__Users_willh__mcp_servers_coderef_workflow_uds_helpers_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_Standard["Standard"]:::fileStyle
    file_get_server_version["get_server_version"]:::fileStyle
    file_gracefully["gracefully"]:::fileStyle
    file_read_text["read_text"]:::fileStyle
    file_search["search"]:::fileStyle
    file_generate_uds_header["generate_uds_header"]:::fileStyle
    file_title["title"]:::fileStyle
    file_ID["ID"]:::fileStyle
    file_name["name"]:::fileStyle
    file_status["status"]:::fileStyle
    file_version["version"]:::fileStyle
    file_strftime["strftime"]:::fileStyle
    file_utcnow["utcnow"]:::fileStyle
    file_generate_uds_footer["generate_uds_footer"]:::fileStyle
    file_review["review"]:::fileStyle
    file_review_days["review_days"]:::fileStyle
    file_flag["flag"]:::fileStyle
    file_timedelta["timedelta"]:::fileStyle
    file_C__Users_willh__mcp_servers_coderef_workflow_type_defs_py["C:\Users\willh\.mcp-servers..."]:::fileStyle
    file_server["server"]:::fileStyle
    file_TypedDicts["TypedDicts"]:::fileStyle
    file_type["type"]:::fileStyle
    file_position["position"]:::fileStyle
    file_names["names"]:::fileStyle
    file_extension["extension"]:::fileStyle
    file_license["license"]:::fileStyle
    file_affected["affected"]:::fileStyle
    file_score["score"]:::fileStyle
    file_dependencies["dependencies"]:::fileStyle
    file_Transitive["Transitive"]:::fileStyle
    file_managers["managers"]:::fileStyle
    file_documentation["documentation"]:::fileStyle
    file_found["found"]:::fileStyle
    file_percentage["percentage"]:::fileStyle
    file_constraints["constraints"]:::fileStyle
    file_validators["validators"]:::fileStyle

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

### Functions (5721)

- **`randomstring()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:40
- **`helpTestDataType()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:182
- **`Python()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/is64bit.py:6
- **`os()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/is64bit.py:10
- **`maketemp()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:10
- **`_cleanup_function()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:20
- **`getcleanupfunction()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:32
- **`find_ado_path()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:36
- **`makeadopackage()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:43
- **`makemdb()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/setuptestframework.py:62
- **`try_connection()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/tryconnection.py:1
- **`try_operation_with_expected_exception()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/tryconnection.py:21
- **`getIndexedValue()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:58
- **`make_COM_connecter()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:66
- **`connect()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:77
- **`format_parameters()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:120
- **`_configure_parameter()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:158
- **`ado_direction_name()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/ado_consts.py:47
- **`ado_type_name()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/ado_consts.py:170
- **`standardErrorHandler()`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/apibase.py:24

### Classes (3399)

- **`CommonDBTests`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:44
- **`XtendString`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1022
- **`XtendInt`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1025
- **`XtendFloat`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1028
- **`TestADOwithSQLServer`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1063
- **`TestADOwithAccessDB`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1211
- **`TestADOwithMySql`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1243
- **`TestADOwithPostgres`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1309
- **`TimeConverterInterfaceTest`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1372
- **`TestPythonTimeConverter`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1415
- **`TestPythonDateTimeConverter`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1459
- **`cleanup_manager`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/adodbapitest.py:1522
- **`DatabaseAPI20Test`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/dbapi20.py:86
- **`mytest`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/dbapi20.py:101
- **`test_adodbapi`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/test/test_adodbapi_dbapi20.py:88
- **`Connection`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:212
- **`Cursor`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/adodbapi.py:519
- **`Error`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/apibase.py:38
- **`Warning`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/apibase.py:47
- **`InterfaceError`** - C:/Users/willh/.mcp-servers/coderef-workflow/.venv/Lib/site-packages/adodbapi/apibase.py:51

### Components (0)

_No components found_

## Module Organization

### `C:\Users\willh\.mcp-servers\coderef-workflow/`
- Elements: 242

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages/`
- Elements: 340

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\adodbapi/`
- Elements: 153

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\adodbapi\test/`
- Elements: 169

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\annotated_types/`
- Elements: 44

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\anyio/`
- Elements: 124

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\anyio\_backends/`
- Elements: 441

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\anyio\_core/`
- Elements: 407

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\anyio\abc/`
- Elements: 128

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\anyio\streams/`
- Elements: 111

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\attr/`
- Elements: 250

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\certifi/`
- Elements: 5

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\cffi/`
- Elements: 640

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\click/`
- Elements: 606

### `C:\Users\willh\.mcp-servers\coderef-workflow\.venv\Lib\site-packages\colorama/`
- Elements: 77


## Design Patterns

_No patterns detected_

---
**Generated from:** `.coderef/index.json`, `.coderef/diagrams/dependencies.mmd`
**Date:** 2025-12-31
