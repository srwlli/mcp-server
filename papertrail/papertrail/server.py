"""
Papertrail MCP Server

Provides MCP tools for Universal Documentation Standards (UDS) validation.
Enables agents to validate documents against UDS schemas and get quality scores.
"""

from pathlib import Path
from typing import Any, Optional
import json

from mcp.server import Server
from mcp.types import Tool, TextContent

from papertrail.validators.factory import ValidatorFactory
from papertrail.tools.sync_schemas import SchemaSyncTool

# Initialize MCP server
app = Server("papertrail")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Papertrail MCP tools."""
    return [
        Tool(
            name="validate_stub",
            description="Validate a stub.json file against stub-schema.json. Checks required fields, format validation (stub_id, feature_name, dates), and optionally auto-fills missing fields with defaults. Returns validation results and optionally updated stub content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to stub.json file"
                    },
                    "auto_fill": {
                        "type": "boolean",
                        "description": "Auto-fill missing required fields with defaults (default: false)",
                        "default": False
                    },
                    "save": {
                        "type": "boolean",
                        "description": "Save updated stub to file if auto_fill is true (default: false)",
                        "default": False
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="validate_resource_sheet",
            description="Validate a resource sheet document against RSMS v2.0 schema. Checks snake_case frontmatter, required fields (subject, parent_project, category), naming convention (-RESOURCE-SHEET.md suffix), and recommended sections. Returns score (0-100), errors, and warnings. Use this for /create-resource-sheet workflow validation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to resource sheet file (must end with -RESOURCE-SHEET.md)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_resource_sheets",
            description="Validate all resource sheet documents in a directory against RSMS v2.0 standards. Automatically scans for files ending with -RESOURCE-SHEET.md. Returns summary with pass/fail counts, average score, and detailed results per file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to directory containing resource sheets"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="validate_document",
            description="Validate any document against UDS schema. Auto-detects document type (foundation, workorder, system, session, etc.) and returns validation results with score (0-100), errors, and warnings. For resource sheets, use validate_resource_sheet instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to document file (markdown or JSON)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_all_docs",
            description="Validate all documents in a directory recursively against UDS schemas. Returns summary with pass/fail counts and average score. For resource sheets only, use check_all_resource_sheets instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Absolute path to directory to scan"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Optional glob pattern (default: **/*.md)"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="validate_schema_completeness",
            description="Validate that a JSON schema has required_sections defined for all doc_types. Reports completeness, issues, and section counts per doc_type. Use this to ensure schema-template synchronization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Name of schema file (e.g., 'foundation-doc-frontmatter-schema.json')"
                    }
                },
                "required": ["schema_name"]
            }
        ),
        Tool(
            name="validate_all_schemas",
            description="Validate all JSON schemas in schemas/documentation/ directory. Returns summary report with pass/fail counts and lists issues for each schema. Use this for batch schema validation.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="validate_communication",
            description="Validate a communication.json file against communication-schema.json. Checks required fields, agent structure, outputs validation (files_created/files_modified must be arrays, not numbers), and prevents git_metrics objects. Returns validation results with errors and warnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to communication.json file"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle MCP tool calls."""

    if name == "validate_stub":
        return await validate_stub(arguments)
    elif name == "validate_resource_sheet":
        return await validate_resource_sheet(arguments)
    elif name == "check_all_resource_sheets":
        return await check_all_resource_sheets(arguments)
    elif name == "validate_document":
        return await validate_document(arguments)
    elif name == "check_all_docs":
        return await check_all_docs(arguments)
    elif name == "validate_schema_completeness":
        return await validate_schema_completeness(arguments)
    elif name == "validate_all_schemas":
        return await validate_all_schemas(arguments)
    elif name == "validate_communication":
        return await validate_communication(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def validate_stub(arguments: dict) -> list[TextContent]:
    """Validate a stub.json file."""
    file_path = Path(arguments["file_path"])
    auto_fill = arguments.get("auto_fill", False)
    save = arguments.get("save", False)

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention
    if not file_path.name == "stub.json":
        return [TextContent(
            type="text",
            text=f"Error: Stub file must be named 'stub.json'\n\nGot: {file_path.name}\n\nPlease rename the file to stub.json"
        )]

    try:
        from papertrail.validators.stub import StubValidator
        validator = StubValidator()

        # Validate
        is_valid, errors, warnings, updated_stub = validator.validate_file(file_path, auto_fill=auto_fill)

        # Save if requested
        if save and updated_stub and auto_fill:
            validator.save_stub(updated_stub, file_path)

        # Format response
        response = f"# Stub Validation: {file_path.parent.name}/stub.json\n\n"
        response += f"**Valid:** {'Yes [PASS]' if is_valid else 'No [FAIL]'}\n"
        response += f"**Auto-fill:** {'Enabled' if auto_fill else 'Disabled'}\n"
        if save and updated_stub:
            response += f"**Saved:** Yes (updated stub saved to file)\n"
        response += "\n"

        if errors:
            response += f"## Errors ({len(errors)})\n\n"
            for error in errors:
                response += f"- [ERROR] {error}\n"
            response += "\n**Fix these errors to achieve stub schema compliance.**\n"

        if warnings:
            response += f"\n## Warnings ({len(warnings)})\n\n"
            for warning in warnings:
                response += f"- [WARN] {warning}\n"

        if auto_fill and updated_stub:
            response += f"\n## Auto-filled Fields\n\n"
            response += "```json\n"
            response += json.dumps(updated_stub, indent=2, ensure_ascii=False)
            response += "\n```\n"
            if save:
                response += "\n[INFO] Updated stub has been saved to file.\n"
            else:
                response += "\n[INFO] Updated stub shown above. Use save=true to write to file.\n"

        if is_valid:
            response += "\n[PASS] Stub is valid and conforms to stub-schema.json!\n"
        else:
            response += f"\n[FAIL] Stub failed validation. Fix {len(errors)} error(s) above.\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating stub: {str(e)}"
        )]


async def validate_resource_sheet(arguments: dict) -> list[TextContent]:
    """Validate a resource sheet against RSMS v2.0 schema."""
    file_path = Path(arguments["file_path"])

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention
    if not file_path.name.endswith("-RESOURCE-SHEET.md"):
        return [TextContent(
            type="text",
            text=f"Error: Resource sheet must end with -RESOURCE-SHEET.md\n\nGot: {file_path.name}\n\nPlease rename the file to follow the convention: {{Subject}}-RESOURCE-SHEET.md"
        )]

    try:
        # Force use of ResourceSheetValidator
        from papertrail.validators.resource_sheet import ResourceSheetValidator
        validator = ResourceSheetValidator()

        # Validate
        result = validator.validate_file(file_path)

        # Format response with RSMS v2.0 specific messaging
        response = f"# RSMS v2.0 Validation: {file_path.name}\n\n"
        response += f"**Valid:** {'Yes ✅' if result.valid else 'No ❌'}\n"
        response += f"**Score:** {result.score}/100\n"
        response += f"**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0\n\n"

        if result.errors:
            response += f"## Errors ({len(result.errors)})\n\n"
            for error in result.errors:
                response += f"- [{error.severity.value}] {error.message}"
                if error.field:
                    response += f" (field: {error.field})"
                response += "\n"
            response += "\n**Fix these errors to achieve RSMS v2.0 compliance.**\n"

        if result.warnings:
            response += f"\n## Warnings ({len(result.warnings)})\n\n"
            for warning in result.warnings:
                response += f"- {warning}\n"
            response += "\n**Address warnings to improve documentation quality.**\n"

        if result.valid and result.score >= 90:
            response += "\n✅ **Resource sheet is RSMS v2.0 compliant!**\n"
        elif result.valid:
            response += f"\n⚠️ **Resource sheet validates but has warnings (score: {result.score}/100). Consider addressing warnings.**\n"
        else:
            response += f"\n❌ **Resource sheet failed validation (score: {result.score}/100). Fix errors above.**\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating resource sheet: {str(e)}"
        )]


async def check_all_resource_sheets(arguments: dict) -> list[TextContent]:
    """Validate all resource sheets in a directory."""
    directory = Path(arguments["directory"])

    # Hardcode pattern for resource sheets
    pattern = "**/*-RESOURCE-SHEET.md"

    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]

    try:
        # Find all resource sheets
        files = list(directory.glob(pattern))

        if not files:
            return [TextContent(
                type="text",
                text=f"No resource sheets found in: {directory}\n\nLooking for files ending with: -RESOURCE-SHEET.md"
            )]

        # Validate each resource sheet
        from papertrail.validators.resource_sheet import ResourceSheetValidator
        validator = ResourceSheetValidator()

        results = []
        total_score = 0
        passed = 0
        failed = 0

        for file_path in files:
            try:
                result = validator.validate_file(file_path)

                results.append({
                    "file": file_path.name,
                    "valid": result.valid,
                    "score": result.score,
                    "errors": len(result.errors),
                    "warnings": len(result.warnings)
                })

                total_score += result.score
                if result.valid:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                results.append({
                    "file": file_path.name,
                    "valid": False,
                    "score": 0,
                    "error": str(e)
                })
                failed += 1

        # Format summary
        avg_score = total_score / len(results) if results else 0

        response = f"# RSMS v2.0 Batch Validation: {directory.name}\n\n"
        response += f"**Total Resource Sheets:** {len(results)}\n"
        response += f"**Passed:** {passed} ✅\n"
        response += f"**Failed:** {failed} ❌\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n"
        response += f"**Standard:** Resource Sheet Metadata Standards (RSMS) v2.0\n\n"

        response += "## Results\n\n"
        for r in results:
            status = "✅" if r["valid"] else "❌"
            response += f"{status} **{r['file']}** - Score: {r['score']}/100"
            if "error" in r:
                response += f" (Error: {r['error']})"
            elif r["errors"] > 0:
                response += f" ({r['errors']} errors, {r['warnings']} warnings)"
            response += "\n"

        if passed == len(results):
            response += "\n✅ **All resource sheets are RSMS v2.0 compliant!**\n"
        elif failed > 0:
            response += f"\n⚠️ **{failed} resource sheet(s) failed validation. Use validate_resource_sheet to see detailed errors.**\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error checking resource sheets: {str(e)}"
        )]


async def validate_document(arguments: dict) -> list[TextContent]:
    """Validate a single document against UDS schema."""
    file_path = Path(arguments["file_path"])
    
    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]
    
    try:
        # Auto-detect validator type
        validator = ValidatorFactory.get_validator(file_path)
        
        # Validate
        result = validator.validate_file(file_path)
        
        # Format response
        response = f"# Validation Results: {file_path.name}\n\n"
        response += f"**Valid:** {'Yes' if result.valid else 'No'}\n"
        response += f"**Score:** {result.score}/100\n"
        if result.completeness is not None:
            response += f"**Completeness:** {result.completeness}%\n"
        response += f"**Category:** {validator.doc_category}\n\n"
        
        if result.errors:
            response += f"## Errors ({len(result.errors)})\n\n"
            for error in result.errors:
                response += f"- [{error.severity.value}] {error.message}"
                if error.field:
                    response += f" (field: {error.field})"
                response += "\n"
        
        if result.warnings:
            response += f"\n## Warnings ({len(result.warnings)})\n\n"
            for warning in result.warnings:
                response += f"- {warning}\n"
        
        if result.valid and not result.errors:
            response += "\n✅ Document validates successfully!\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating document: {str(e)}"
        )]


async def check_all_docs(arguments: dict) -> list[TextContent]:
    """Validate all documents in a directory."""
    directory = Path(arguments["directory"])
    pattern = arguments.get("pattern", "**/*.md")
    
    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]
    
    try:
        # Find all matching files
        files = list(directory.glob(pattern))
        
        if not files:
            return [TextContent(
                type="text",
                text=f"No files found matching pattern: {pattern}"
            )]
        
        # Validate each file
        results = []
        total_score = 0
        passed = 0
        failed = 0
        
        for file_path in files:
            try:
                validator = ValidatorFactory.get_validator(file_path)
                result = validator.validate_file(file_path)
                
                results.append({
                    "file": str(file_path.relative_to(directory)),
                    "valid": result.valid,
                    "score": result.score,
                    "category": validator.doc_category,
                    "errors": len(result.errors),
                    "warnings": len(result.warnings)
                })
                
                total_score += result.score
                if result.valid:
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                results.append({
                    "file": str(file_path.relative_to(directory)),
                    "valid": False,
                    "score": 0,
                    "category": "unknown",
                    "error": str(e)
                })
                failed += 1
        
        # Format summary
        avg_score = total_score / len(results) if results else 0
        
        response = f"# Validation Summary: {directory.name}\n\n"
        response += f"**Total Files:** {len(results)}\n"
        response += f"**Passed:** {passed}\n"
        response += f"**Failed:** {failed}\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n\n"
        
        response += "## Results\n\n"
        for r in results:
            status = "✅" if r["valid"] else "❌"
            response += f"{status} **{r['file']}** - Score: {r['score']}/100"
            if "error" in r:
                response += f" (Error: {r['error']})"
            elif r["errors"] > 0:
                response += f" ({r['errors']} errors, {r['warnings']} warnings)"
            response += f"\n"
        
        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error checking documents: {str(e)}"
        )]


async def validate_schema_completeness(arguments: dict) -> list[TextContent]:
    """Validate a single schema for completeness."""
    schema_name = arguments["schema_name"]

    try:
        tool = SchemaSyncTool()
        report = tool.generate_schema_report(schema_name)

        return [TextContent(type="text", text=report)]

    except FileNotFoundError as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating schema: {str(e)}"
        )]


async def validate_all_schemas(arguments: dict) -> list[TextContent]:
    """Validate all schemas in directory."""
    try:
        tool = SchemaSyncTool()
        report = tool.validate_all_schemas()

        return [TextContent(type="text", text=report)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating schemas: {str(e)}"
        )]


async def validate_communication(arguments: dict) -> list[TextContent]:
    """Validate a communication.json file."""
    file_path = Path(arguments["file_path"])

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention
    if not file_path.name == "communication.json":
        return [TextContent(
            type="text",
            text=f"Error: File must be named 'communication.json'\n\nGot: {file_path.name}\n\nPlease rename the file to communication.json"
        )]

    try:
        from papertrail.validators.communication import CommunicationValidator
        validator = CommunicationValidator()

        # Validate
        is_valid, errors, warnings = validator.validate_file(file_path)

        # Format response
        response = f"# Communication Validation: {file_path.parent.name}/communication.json\n\n"
        response += f"**Valid:** {'Yes ✅ [PASS]' if is_valid else 'No ❌ [FAIL]'}\n\n"

        if errors:
            response += f"## Errors ({len(errors)})\n\n"
            for error in errors:
                response += f"- ❌ {error}\n"
            response += "\n"

        if warnings:
            response += f"## Warnings ({len(warnings)})\n\n"
            for warning in warnings:
                response += f"- ⚠️  {warning}\n"
            response += "\n"

        if is_valid:
            response += "✅ **Communication file is valid!**\n\n"
            response += "All agents have correct structure:\n"
            response += "- outputs.files_created[] is an array ✓\n"
            response += "- outputs.files_modified[] is an array ✓\n"
            response += "- outputs.workorders_created[] is an array ✓\n"
            response += "- No git_metrics object ✓\n"

        return [TextContent(type="text", text=response)]

    except FileNotFoundError as e:
        return [TextContent(
            type="text",
            text=f"Error: Schema not found. Make sure communication-schema.json exists.\n\n{str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating communication.json: {str(e)}"
        )]


async def validate_claude_md(arguments: dict) -> list[TextContent]:
    """Validate a CLAUDE.md file against claude-md-frontmatter-schema.json."""
    file_path = Path(arguments["file_path"])

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention
    if not file_path.name == "CLAUDE.md":
        return [TextContent(
            type="text",
            text=f"Error: File must be named 'CLAUDE.md', got: {file_path.name}"
        )]

    try:
        from validators.claude_md_helpers import (
            extract_yaml_frontmatter,
            count_lines,
            extract_markdown_headers,
            get_required_sections,
            calculate_compliance_score,
            format_validation_response
        )
        import jsonschema

        # Extract YAML frontmatter
        frontmatter, body = extract_yaml_frontmatter(file_path)

        # Load schema
        schema_path = Path(__file__).parent / "schemas" / "documentation" / "claude-md-frontmatter-schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Validate frontmatter against schema
        errors = []
        warnings = []

        try:
            jsonschema.validate(instance=frontmatter, schema=schema)
            is_valid = True
        except jsonschema.ValidationError as e:
            is_valid = False
            errors.append(f"Schema validation failed: {e.message}")

        # Calculate line count
        line_count = count_lines(file_path)

        # Check line budget based on file_type
        file_type = frontmatter.get("file_type", "project")
        if file_type == "project":
            target_min, target_max = 530, 600
        else:  # child
            target_min, target_max = 300, 400

        # Check line budget compliance
        if line_count < target_min:
            warnings.append(f"Line count below target: {line_count} < {target_min}")
        elif line_count > target_max:
            errors.append(f"Line count exceeds budget: {line_count} > {target_max}")

        # Check required sections (parse markdown headers)
        required_sections = get_required_sections(file_type)
        found_sections = extract_markdown_headers(body)
        missing_sections = set(required_sections) - set(found_sections)

        if missing_sections:
            for section in missing_sections:
                errors.append(f"Missing required section: {section}")

        # Calculate compliance score (0-100)
        score = calculate_compliance_score(
            line_count=line_count,
            target_min=target_min,
            target_max=target_max,
            sections_found=len(found_sections),
            sections_required=len(required_sections),
            errors=len(errors),
            warnings=len(warnings)
        )

        # Format response
        response = format_validation_response(
            file_path=file_path,
            is_valid=is_valid,
            score=score,
            line_count=line_count,
            target_range=(target_min, target_max),
            errors=errors,
            warnings=warnings,
            file_type=file_type
        )

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating CLAUDE.md: {str(e)}"
        )]


async def check_all_claude_md(arguments: dict) -> list[TextContent]:
    """Batch validate all CLAUDE.md files in directory."""
    directory = Path(arguments["directory"])

    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]

    try:
        # Find all CLAUDE.md files recursively
        claude_md_files = list(directory.rglob("CLAUDE.md"))

        if not claude_md_files:
            return [TextContent(
                type="text",
                text=f"No CLAUDE.md files found in: {directory}"
            )]

        # Validate each file
        from validators.claude_md_helpers import extract_score_from_result

        results = []
        for file_path in claude_md_files:
            result = await validate_claude_md({"file_path": str(file_path)})
            results.append((file_path, result))

        # Calculate summary stats
        total_files = len(results)
        passed_files = sum(1 for _, result in results if "[PASS]" in result[0].text)
        failed_files = total_files - passed_files

        # Calculate average score (parse scores from results)
        scores = [extract_score_from_result(result[0]) for _, result in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Format summary response
        response = f"# CLAUDE.md Validation Summary\n\n"
        response += f"**Directory:** {directory}\n"
        response += f"**Files Scanned:** {total_files}\n"
        response += f"**Passed:** {passed_files} ({passed_files/total_files*100:.1f}%)\n"
        response += f"**Failed:** {failed_files} ({failed_files/total_files*100:.1f}%)\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n\n"

        # Add detailed results per file
        response += "## Detailed Results\n\n"
        for file_path, result in results:
            try:
                rel_path = file_path.relative_to(directory)
            except ValueError:
                rel_path = file_path
            response += f"### {rel_path}\n\n"
            response += result[0].text + "\n\n---\n\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error batch validating CLAUDE.md files: {str(e)}"
        )]


async def validate_skill(arguments: dict) -> list[TextContent]:
    """Validate a skill.md file against skill-frontmatter-schema.json."""
    file_path = Path(arguments["file_path"])

    if not file_path.exists():
        return [TextContent(
            type="text",
            text=f"Error: File not found: {file_path}"
        )]

    # Enforce naming convention (must be .md file)
    if not file_path.suffix == ".md":
        return [TextContent(
            type="text",
            text=f"Error: Skill file must be .md file, got: {file_path.suffix}"
        )]

    try:
        from validators.claude_md_helpers import (
            extract_yaml_frontmatter,
            count_lines,
            is_kebab_case,
            check_for_step_headers,
            calculate_skill_compliance_score,
            format_skill_validation_response
        )
        import jsonschema

        # Extract YAML frontmatter
        frontmatter, body = extract_yaml_frontmatter(file_path)

        # Load schema
        schema_path = Path(__file__).parent / "schemas" / "documentation" / "skill-frontmatter-schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Validate frontmatter against schema
        errors = []
        warnings = []

        try:
            jsonschema.validate(instance=frontmatter, schema=schema)
            is_valid = True
        except jsonschema.ValidationError as e:
            is_valid = False
            errors.append(f"Schema validation failed: {e.message}")

        # Check required frontmatter fields
        if "name" not in frontmatter:
            errors.append("Missing required field: name")
        elif not is_kebab_case(frontmatter["name"]):
            errors.append(f"Skill name must be kebab-case, got: {frontmatter['name']}")

        if "description" not in frontmatter:
            errors.append("Missing required field: description")

        # Calculate line count
        line_count = count_lines(file_path)
        target_min, target_max = 300, 500

        # Check line budget
        if line_count < target_min:
            warnings.append(f"Line count below target: {line_count} < {target_min}")
        elif line_count > target_max:
            errors.append(f"Line count exceeds budget: {line_count} > {target_max}")

        # Check content structure (has step headers, verification section)
        has_steps = check_for_step_headers(body)
        has_verification = "## Verification" in body

        if not has_steps:
            warnings.append("Content should have step-by-step structure (## Step 1:, ## Step 2:, etc.)")
        if not has_verification:
            warnings.append("Missing ## Verification section (how to verify success)")

        # Calculate compliance score
        score = calculate_skill_compliance_score(
            line_count=line_count,
            target_min=target_min,
            target_max=target_max,
            has_required_fields=("name" in frontmatter and "description" in frontmatter),
            has_steps=has_steps,
            has_verification=has_verification,
            errors=len(errors),
            warnings=len(warnings)
        )

        # Format response
        response = format_skill_validation_response(
            file_path=file_path,
            is_valid=is_valid,
            score=score,
            line_count=line_count,
            target_range=(target_min, target_max),
            errors=errors,
            warnings=warnings,
            frontmatter=frontmatter
        )

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error validating skill: {str(e)}"
        )]


async def check_all_skills(arguments: dict) -> list[TextContent]:
    """Batch validate all skill.md files in .claude/skills/ directory."""
    directory = Path(arguments["directory"])

    if not directory.exists():
        return [TextContent(
            type="text",
            text=f"Error: Directory not found: {directory}"
        )]

    try:
        # Find all .md files in skills directory (not recursive for skills)
        skill_files = list(directory.glob("*.md"))

        # Also check subdirectories (for skills with directory structure)
        skill_files.extend(list(directory.glob("*/skill.md")))

        if not skill_files:
            return [TextContent(
                type="text",
                text=f"No skill files found in: {directory}"
            )]

        # Validate each file
        from validators.claude_md_helpers import extract_score_from_result

        results = []
        for file_path in skill_files:
            result = await validate_skill({"file_path": str(file_path)})
            results.append((file_path, result))

        # Calculate summary stats
        total_files = len(results)
        passed_files = sum(1 for _, result in results if "[PASS]" in result[0].text)
        failed_files = total_files - passed_files
        scores = [extract_score_from_result(result[0]) for _, result in results]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Format summary response
        response = f"# Skill Validation Summary\n\n"
        response += f"**Directory:** {directory}\n"
        response += f"**Skills Scanned:** {total_files}\n"
        response += f"**Passed:** {passed_files} ({passed_files/total_files*100:.1f}%)\n"
        response += f"**Failed:** {failed_files} ({failed_files/total_files*100:.1f}%)\n"
        response += f"**Average Score:** {avg_score:.1f}/100\n\n"

        # Add detailed results per file
        response += "## Detailed Results\n\n"
        for file_path, result in results:
            response += f"### {file_path.name}\n\n"
            response += result[0].text + "\n\n---\n\n"

        return [TextContent(type="text", text=response)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error batch validating skills: {str(e)}"
        )]


if __name__ == "__main__":
    import asyncio
    import mcp.server.stdio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(main())
