Create a custom persona through a guided workflow with automatic system prompt generation and validation.

Use this command to create specialized expert personas tailored to your unique needs.

## How It Works

1. Provide persona details (name, description, expertise, use cases, communication style)
2. System validates inputs through 3-stage validation (schema → semantic → quality)
3. System generates comprehensive system prompt using templates
4. Persona saved to `personas/custom/{name}.json`
5. Ready to activate with `use_persona(name)`

## Required Fields

- **name**: Unique persona name (lowercase, alphanumeric, hyphens, underscores, 3-50 chars)
- **description**: One-sentence role description (20-200 chars)
- **expertise**: List of 3-10 expertise areas
- **use_cases**: List of 3-10 use cases
- **communication_style**: How persona communicates (20-200 chars)

## Optional Fields

- **problem_solving**: Problem-solving approach (max 200 chars)
- **tool_usage**: How persona uses tools (max 200 chars)
- **specializations**: List of specialized sub-areas (max 5)
- **key_principles**: List of guiding principles (max 10)
- **example_responses**: Example Q&A pairs (max 3)

## Example Usage

```
mcp__personas-mcp__create_custom_persona({
  "name": "api-expert",
  "description": "REST API design and development specialist focusing on best practices and scalability",
  "expertise": [
    "RESTful API architecture",
    "OpenAPI specification",
    "API security (OAuth, JWT)",
    "Rate limiting and throttling",
    "API versioning strategies"
  ],
  "use_cases": [
    "Designing new API endpoints",
    "Reviewing API architecture",
    "Implementing authentication flows",
    "Optimizing API performance",
    "Writing API documentation"
  ],
  "communication_style": "Professional and technical, uses concrete examples and references industry standards like REST, OpenAPI, and OAuth specifications"
})
```

## Tips for Creating Quality Personas

1. **Be Specific**: Use detailed expertise areas, not generic ones
2. **Define Clear Use Cases**: Specify exactly when this persona is valuable
3. **Describe Communication**: How should this persona sound and behave?
4. **Add Context**: Use optional fields (problem_solving, tool_usage) for richer personas
5. **Provide Examples**: Example responses help clarify persona behavior

## After Creation

Once created, you can:

1. **Activate the persona**: `use_persona('your-persona-name')`
2. **List all personas**: `list_personas()` (includes custom personas)
3. **Create a shortcut**: Add a slash command in `.claude/commands/{name}.md`

---

**Ready to create your custom persona?** Call the MCP tool above with your persona details!
