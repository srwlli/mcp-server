# DELIVERABLES: create-custom-persona

**Project**: personas-mcp
**Feature**: create-custom-persona
**Workorder**: WO-CREATE-CUSTOM-PERSONA-001
**Status**: 🚧 Not Started
**Generated**: 2025-10-23

---

## Executive Summary

**Goal**: Enable users to create custom personas by providing expertise areas, communication style, and behavior preferences through a guided template workflow, with automatic system prompt generation and validation

**Description**: Implement a persona customization system that allows users to define new expert personas without writing JSON manually. Users provide high-level inputs (expertise areas, communication style, tool preferences, use cases) through an interactive guided process, and the system generates a complete persona definition with a comprehensive system prompt. The feature includes validation, template-based generation, storage in personas/custom/, and a /create-persona slash command for easy access.

---

## Implementation Phases

### Phase 0: Setup & Foundation (4.5 hours)
- [ ] SETUP-001: Create personas/custom/ directory structure
- [ ] SETUP-002: Create templates/ directory for persona templates
- [ ] MODEL-001: Define CustomPersonaInput Pydantic schema in src/models.py
- [ ] MODEL-002: Create JSON schema for custom persona input validation in templates/custom_persona_schema.json

**Deliverables:**
- personas/custom/ directory created
- templates/ directory created
- CustomPersonaInput Pydantic schema
- JSON schema for validation

### Phase 1: Template & Validation (8.5 hours)
- [ ] TEMPLATE-001: Design system prompt template with {{placeholders}} in templates/persona_template.txt
- [ ] TEMPLATE-002: Create template renderer with {{placeholder}} substitution logic
- [ ] VALIDATE-001: Implement JSON schema validation in src/validators.py
- [ ] VALIDATE-002: Implement semantic validation (expertise coherence, use case relevance)
- [ ] VALIDATE-003: Implement quality validation (completeness checks, best practices)
- [ ] VALIDATE-004: Implement uniqueness check to prevent name conflicts with base personas

**Deliverables:**
- System prompt template with placeholders
- Template rendering engine
- Multi-stage validation pipeline (schema, semantic, quality)
- Uniqueness validation

### Phase 2: Generation & Handler (8.5 hours)
- [ ] GENERATE-001: Create PersonaGenerator class in src/persona_generator.py
- [ ] GENERATE-002: Implement system prompt generation using template + user inputs
- [ ] GENERATE-003: Implement persona metadata generation (version, timestamps, created_by)
- [ ] HANDLER-001: Add create_custom_persona tool definition to server.py list_tools()
- [ ] HANDLER-002: Implement handle_create_custom_persona in server.py with guided workflow
- [ ] HANDLER-003: Integrate validation pipeline in handler (schema → semantic → quality)
- [ ] HANDLER-004: Implement file save logic to personas/custom/{name}.json
- [ ] CMD-001: Create /create-persona slash command in .claude/commands/create-persona.md

**Deliverables:**
- PersonaGenerator class
- System prompt generation
- Metadata generation
- create_custom_persona MCP tool
- Guided workflow implementation
- /create-persona slash command

### Phase 3: Testing & Documentation (5.5 hours)
- [ ] TEST-001: Write unit tests for CustomPersonaInput schema validation
- [ ] TEST-002: Write unit tests for template rendering logic
- [ ] TEST-003: Write unit tests for validation pipeline (schema, semantic, quality)
- [ ] TEST-004: Write integration test for complete persona creation workflow
- [ ] DOC-001: Update README.md with create_custom_persona tool documentation
- [ ] DOC-002: Update CLAUDE.md with custom persona creation workflow
- [ ] DOC-003: Create CUSTOMIZATION-GUIDE.md with examples and best practices

**Deliverables:**
- Unit tests for schemas and validation
- Integration tests for workflow
- Updated README.md and CLAUDE.md
- CUSTOMIZATION-GUIDE.md

---

## Metrics

### Code Changes
- **Lines of Code Added**: TBD
- **Lines of Code Deleted**: TBD
- **Net LOC**: TBD
- **Files Modified**: TBD

### Commit Activity
- **Total Commits**: TBD
- **First Commit**: TBD
- **Last Commit**: TBD
- **Contributors**: TBD

### Time Investment
- **Days Elapsed**: TBD
- **Hours Spent (Wall Clock)**: TBD

---

## Task Completion Checklist

### Setup & Foundation (4 tasks)
- [ ] SETUP-001: Create personas/custom/ directory structure
- [ ] SETUP-002: Create templates/ directory for persona templates
- [ ] MODEL-001: Define CustomPersonaInput Pydantic schema in src/models.py
- [ ] MODEL-002: Create JSON schema for custom persona input validation

### Template & Validation (6 tasks)
- [ ] TEMPLATE-001: Design system prompt template with {{placeholders}}
- [ ] TEMPLATE-002: Create template renderer with {{placeholder}} substitution logic
- [ ] VALIDATE-001: Implement JSON schema validation in src/validators.py
- [ ] VALIDATE-002: Implement semantic validation (expertise coherence, use case relevance)
- [ ] VALIDATE-003: Implement quality validation (completeness checks, best practices)
- [ ] VALIDATE-004: Implement uniqueness check to prevent name conflicts

### Generation & Handler (8 tasks)
- [ ] GENERATE-001: Create PersonaGenerator class in src/persona_generator.py
- [ ] GENERATE-002: Implement system prompt generation using template + user inputs
- [ ] GENERATE-003: Implement persona metadata generation (version, timestamps, created_by)
- [ ] HANDLER-001: Add create_custom_persona tool definition to server.py list_tools()
- [ ] HANDLER-002: Implement handle_create_custom_persona with guided workflow
- [ ] HANDLER-003: Integrate validation pipeline in handler
- [ ] HANDLER-004: Implement file save logic to personas/custom/{name}.json
- [ ] CMD-001: Create /create-persona slash command

### Testing & Documentation (7 tasks)
- [ ] TEST-001: Write unit tests for CustomPersonaInput schema validation
- [ ] TEST-002: Write unit tests for template rendering logic
- [ ] TEST-003: Write unit tests for validation pipeline
- [ ] TEST-004: Write integration test for complete persona creation workflow
- [ ] DOC-001: Update README.md with create_custom_persona tool documentation
- [ ] DOC-002: Update CLAUDE.md with custom persona creation workflow
- [ ] DOC-003: Create CUSTOMIZATION-GUIDE.md with examples and best practices

**Total Tasks**: 25
**Estimated Hours**: 20

---

## Files Created/Modified

### New Files
- `personas/custom/.gitkeep` - Custom persona directory
- `templates/persona_template.txt` - System prompt template
- `templates/custom_persona_schema.json` - Input validation schema
- `src/persona_generator.py` - System prompt generation logic
- `src/validators.py` - Custom persona validation rules
- `.claude/commands/create-persona.md` - Slash command
- `tests/test_models.py` - Unit tests for schemas
- `tests/test_persona_generator.py` - Unit tests for generation
- `tests/test_validators.py` - Unit tests for validation
- `tests/integration/test_create_custom_persona.py` - Integration tests
- `CUSTOMIZATION-GUIDE.md` - User guide for custom personas

### Modified Files
- `src/persona_manager.py` - Add custom/ directory support
- `src/models.py` - Add CustomPersonaInput schema
- `server.py` - Add create_custom_persona tool and handler
- `README.md` - Document new feature
- `CLAUDE.md` - Update with customization workflow

---

## Success Criteria

### Functional Requirements
- ✅ Users can create custom personas via MCP tool
- ✅ System prompt generated from template
- ✅ Multi-stage validation works (schema → semantic → quality)
- ✅ Custom personas activate correctly via use_persona
- ✅ /create-persona slash command available

### Quality Requirements
- ✅ Test coverage >= 90% for new code
- ✅ No naming conflicts with base personas
- ✅ Generated prompts are coherent (manual review of 5+ personas)

### User Experience Requirements
- ✅ Creation takes <5 minutes
- ✅ Clear error messages with actionable feedback

### Documentation Requirements
- ✅ Feature documented in README.md
- ✅ CUSTOMIZATION-GUIDE.md exists with examples

---

## Notes

*This deliverables report was automatically generated from plan.json.*
*Use `/update-deliverables` to populate metrics from git history after implementation.*

**Last Updated**: 2025-10-23
