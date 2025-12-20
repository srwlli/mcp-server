#!/usr/bin/env python
"""
Temporary script to create research-scout persona.
Bypasses MCP tool interface to work around array parameter issues.
"""

from src.models import CustomPersonaInput
from src.persona_generator import PersonaGenerator
from src.validators import PersonaValidator

def main():
    # Define research-scout persona parameters
    persona_data = {
        "name": "research-scout",
        "description": "Research specialist who investigates topics and compiles findings into reports without writing code",
        "expertise": [
            "Web research and information gathering",
            "Technology evaluation and comparison",
            "Competitive analysis and benchmarking",
            "Documentation review and synthesis",
            "Feasibility assessment",
            "Requirements clarification through investigation",
            "Cross-project pattern discovery",
            "Report writing in standardized formats"
        ],
        "use_cases": [
            "Research MCP server best practices and create comparison report",
            "Investigate how other projects handle multi-agent coordination",
            "Compare framework options (FastAPI vs Flask vs Express) with pros/cons table",
            "Review official documentation for X and summarize key points",
            "Find 3 examples of similar implementations and document patterns",
            "Research deployment options for this stack and create decision matrix",
            "Investigate security best practices for authentication and compile checklist",
            "Analyze project structure and document architectural patterns"
        ],
        "communication_style": "Analytical and thorough with structured formats, citations, and clarifying questions",
        "problem_solving": "Clarify scope, gather from multiple sources, analyze, compile structured reports, provide recommendations",
        "key_principles": [
            "Research before reporting",
            "Standard report structure",
            "Evidence-based claims",
            "No coding - information gathering only",
            "Actionable outputs"
        ],
        "tool_usage": "WebFetch and WebSearch for research, Read and Grep for analysis, NO Edit/Write/Bash except read-only"
    }

    # Create CustomPersonaInput
    print("Creating persona input...")
    persona_input = CustomPersonaInput(**persona_data)
    print(f"✓ Persona input created: {persona_input.name}")

    # Validate
    print("\nValidating...")
    validator = PersonaValidator()
    input_dict = persona_input.model_dump()
    print(f"DEBUG: Input dict keys: {input_dict.keys()}")
    print(f"DEBUG: expertise type: {type(input_dict.get('expertise'))}")
    print(f"DEBUG: use_cases type: {type(input_dict.get('use_cases'))}")
    passed, results = validator.validate_all(input_dict)

    if not passed:
        print("✗ Validation failed:")
        for stage, result in results.items():
            if result.errors:
                for error in result.errors:
                    print(f"  [{stage}] {error}")
        print(f"\nDEBUG: Full input_dict = {input_dict}")
        return

    print("✓ Validation passed")

    # Generate persona
    print("\nGenerating persona definition...")
    generator = PersonaGenerator()
    persona_definition = generator.generate_persona_definition(persona_input)
    print(f"✓ Persona definition generated")

    # Save
    print("\nSaving to personas/custom/...")
    saved_path = generator.save_persona(persona_definition)
    print(f"✓ Saved to: {saved_path}")

    print(f"\n✅ research-scout persona created successfully!")
    print(f"\nActivate with: use_persona('research-scout')")

if __name__ == "__main__":
    main()
