# ============================================================================
# ADD THIS TO MANAGEMENT_TOOLS (around line 230, after compare_test_runs)
# ============================================================================

    {
        "name": "generate_testing_proof",
        "description": "Generate structured testing proof report comparing plan to implementation. Documents what was tested, why, how, and what it proves. Includes plan vs implementation comparison.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Absolute path to project directory"
                },
                "feature_name": {
                    "type": "string",
                    "description": "Feature name (folder in coderef/workorder/)"
                },
                "test_results": {
                    "type": "array",
                    "description": "List of test cases with what/why/how/result/proof",
                    "items": {
                        "type": "object"
                    }
                },
                "commands_run": {
                    "type": "array",
                    "description": "Optional list of commands executed",
                    "items": {
                        "type": "object"
                    }
                },
                "before_after": {
                    "type": "object",
                    "description": "Optional before/after comparison data"
                }
            },
            "required": ["project_path", "feature_name", "test_results"]
        }
    }

# ============================================================================
# ADD THIS TO handle_tool_call routing (around line 340, after validate_test_health)
# ============================================================================

        elif name == "generate_testing_proof":
            return await handle_generate_testing_proof(arguments)

# ============================================================================
# ADD THIS HANDLER FUNCTION (after handle_validate_test_health, before main())
# ============================================================================

async def handle_generate_testing_proof(args: Dict[str, Any]) -> List[TextContent]:
    """Handle generate_testing_proof tool call - generate testing proof report."""
    from src.proof_generator import TestingProofGenerator

    project_path = args.get("project_path")
    feature_name = args.get("feature_name")
    test_results = args.get("test_results", [])
    commands_run = args.get("commands_run", [])
    before_after = args.get("before_after")

    logger.info(f"Generating testing proof report for {feature_name}")

    try:
        generator = TestingProofGenerator(project_path, feature_name)

        report = generator.generate_proof_report(
            test_results=test_results,
            commands_run=commands_run,
            before_after=before_after
        )

        output_path = generator.save_report(report)

        result = {
            "status": "success",
            "report_path": str(output_path),
            "report_preview": report[:500] + "..." if len(report) > 500 else report
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        logger.error(f"Error generating testing proof: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
