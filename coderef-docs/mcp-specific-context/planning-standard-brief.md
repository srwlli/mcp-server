# Feature Implementation Planning Standard - Brief Guide

## Core Principles

### Rules
- **No time factors** - All agentic (AI executes autonomously without deadlines)
- **No business considerations** - Pure technical focus
- **Complete specifications** - Zero ambiguity, no TBD or "figure out later"
- **Architecture compliance** - Follow existing project patterns

---

## Task ID System

### Purpose
The task ID structure (PREFIX-NNN) serves several purposes:

1. **Traceability** - Links tasks to specific lines in the plan and file locations
2. **Dependencies** - Shows task ordering and relationships
3. **Progress Tracking** - Checkbox-style completion tracking
4. **Cross-referencing** - Easy to reference in discussions ("Let's review SETUP-001")
5. **Consistency** - Mirrors architectural pattern naming

### Standard Prefixes

- **SETUP-NNN**: Project setup, dependencies, configuration, scaffolding
- **DB-NNN**: Database schema, migrations, seeds, queries
- **API-NNN**: HTTP endpoints, request/response handling, API contracts
- **LOGIC-NNN**: Business logic, algorithms, data processing, validation
- **UI-NNN**: User interface components, screens, forms, styling
- **TEST-NNN**: Unit tests, integration tests, E2E tests, test data
- **SEC-NNN**: Security implementations, validations, access control
- **DOC-NNN**: Documentation, API specs, user guides, inline comments
- **DEPLOY-NNN**: Deployment scripts, CI/CD, environment configuration
- **REFACTOR-NNN**: Code cleanup, restructuring (for refactoring projects)

### Format Rules
- **Sequential numbering**: 001, 002, 003 (not 1, 2, 3)
- **Unique IDs**: No duplicates within a plan
- **Imperative verbs**: Start with action (Create, Add, Implement, Update, Fix)
- **Specific locations**: Include file name or component
- **Example**: `SETUP-001: Add pyjwt==2.8.0 to requirements.txt for JWT authentication`

---

## Plan Structure

Every implementation plan includes:

### 1. Executive Summary
- **Purpose**: What problem does this solve?
- **Value proposition**: Why is this important?
- **Real-world analogy**: Explain to non-technical person
- **Use case**: When/how would someone use this?
- **Output**: What artifacts does this create?

### 2. Risk Assessment
- **Overall risk**: Low / Medium / High
- **Complexity**: Low / Medium / High / Very High
- **Scope**: Small / Medium / Large - X files affected
- **Risk factors**: File system, dependencies, performance, security, breaking changes
- **Mitigation**: Strategy for each high-risk item

### 3. Current State Analysis
- **Affected files**: Every file to be created or modified (with line numbers when known)
- **Dependencies**: Existing internal, existing external, new external, new internal
- **Architecture context**: How this fits into existing system

### 4. Key Features
- **Primary features** (3-5): Core functionality
- **Secondary features** (2-3): Supporting capabilities
- **Edge case handling** (2-3): Special scenarios
- **Configuration options** (1-2): User-configurable aspects

### 5. Implementation Phases (with Task IDs)

#### Standard Phase Structure:

**Phase 1: Foundation** (15-25% of effort)
- SETUP tasks: Dependencies, configuration, scaffolding
- DB tasks: Schema, migrations
- Completion: All files exist, code compiles

**Phase 2: Core Implementation** (40-50% of effort)
- LOGIC tasks: Business logic
- API tasks: Endpoints
- UI tasks: Components
- Completion: Happy path works end-to-end

**Phase 3: Edge Cases & Security** (20-25% of effort)
- Error handling
- SEC tasks: Validations, sanitization
- Performance optimizations
- Completion: All edge cases handled

**Phase 4: Testing** (15-20% of effort)
- TEST tasks: Unit, integration, E2E
- Manual validation
- Completion: All tests pass

**Phase 5: Documentation & Deployment** (5-10% of effort)
- DOC tasks: API docs, guides
- DEPLOY tasks: CI/CD, configuration
- Completion: Ready to deploy

### 6. Testing Strategy
- **Unit tests**: Individual functions/methods (3-5 per function)
- **Integration tests**: Components working together (5-10 workflows)
- **E2E tests**: Full user journeys (3-5 critical paths, if UI)
- **Edge cases**: 5-10 scenarios covering:
  - Empty/null input
  - Invalid input
  - Boundary conditions
  - Concurrent access
  - Resource exhaustion
  - External dependency failure
  - Security (injection, XSS, etc.)
  - State issues

### 7. Success Criteria

Quantifiable metrics across 4 categories:

**Functional Requirements** (5-8 criteria)
- Core functionality works
- Example: "POST /login returns 200 with valid JWT token"

**Quality Requirements** (4-6 criteria)
- Code style compliance (linter passes)
- Test coverage (> 80% for new code)
- Type safety (type checker passes)
- Documentation completeness
- No code duplication (< 5%)

**Performance Requirements** (3-5 criteria, if applicable)
- API response time (< 200ms P95)
- Database query performance (< 50ms)
- Memory usage (< 500MB)
- Concurrent users supported

**Security Requirements** (3-5 criteria, if applicable)
- Password hashing (bcrypt cost >= 10)
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- Token security (httpOnly cookies, HTTPS)

### 8. Implementation Checklist

Organized by phase with checkboxes:

```
## Pre-Implementation
☐ Review plan for completeness
☐ Get stakeholder approval
☐ Create feature branch

## Phase 1: Foundation
☐ SETUP-001: [Task description]
☐ SETUP-002: [Task description]
☐ DB-001: [Task description]

## Phase 2: Core Implementation
☐ LOGIC-001: [Task description]
☐ API-001: [Task description]
☐ UI-001: [Task description]

## Phase 3: Edge Cases & Security
☐ SEC-001: [Task description]
☐ [Error handling tasks]

## Phase 4: Testing
☐ TEST-001: [Task description]
☐ TEST-002: [Task description]

## Phase 5: Documentation
☐ DOC-001: Update README
☐ DOC-002: Update API docs

## Finalization
☐ All tests passing
☐ Code review completed
☐ Merge to main
☐ Deploy to production
```

---

## Quality Checklist

Before starting implementation:

### Completeness
- ☐ No placeholder text ([TBD], [to be determined])
- ☐ All task IDs follow PREFIX-NNN format
- ☐ Every task has imperative verb (Create, Add, Implement)
- ☐ All affected files listed
- ☐ Dependencies specified (with versions for external)
- ☐ 5+ edge cases defined with expected behavior

### Quality
- ☐ Success criteria are measurable (numbers, not subjective)
- ☐ Task descriptions are specific (file names, exact changes)
- ☐ Phases have clear completion criteria
- ☐ Effort estimates are realistic
- ☐ Security considerations addressed if handling sensitive data

### Autonomy
- ☐ AI can implement without asking questions
- ☐ Every decision has been made upfront
- ☐ Edge cases have defined expected behavior
- ☐ Clear review gates (when to pause for approval)

---

## Common Mistakes to Avoid

❌ **Vague tasks**: "SETUP-001: Set up authentication"
✅ **Specific tasks**: "SETUP-001: Install pyjwt==2.8.0 and bcrypt==4.0.1 in requirements.txt"

❌ **Subjective criteria**: "System is fast and secure"
✅ **Measurable criteria**: "Login endpoint < 200ms P95, passwords hashed with bcrypt cost>=10"

❌ **Missing edge cases**: Only testing happy path
✅ **Comprehensive**: Happy path + 7 edge cases (empty input, invalid tokens, concurrent access, etc.)

❌ **No dependencies**: Using libraries without listing them
✅ **Complete dependencies**: "NEW EXTERNAL: pyjwt==2.8.0 (add to requirements.txt)"

❌ **Circular dependencies**: Phase 1 depends on Phase 3
✅ **Sequential phases**: Phase 1 (DB) → Phase 2 (API) → Phase 3 (UI) → Phase 4 (Tests)

---

## Usage

### When to Create a Plan
**Always create for:**
- New features (significant new capability)
- Major refactoring (5+ files)
- Architecture changes
- Database schema changes
- Security enhancements

**Optional for:**
- Bug fixes (unless complex)
- Minor refactoring
- Documentation updates
- Configuration changes

### Planning Time Investment
- **Simple feature**: 2-3 hours planning
- **Medium feature**: 4-6 hours planning
- **Complex feature**: 6-8 hours planning

**Note**: Time invested in planning prevents 2-3x time in rework and missed requirements during implementation.

---

## Quick Reference

| Section | Key Question | Output |
|---------|-------------|---------|
| Executive Summary | What are we building? | 5 sentences: purpose, value, analogy, use case, output |
| Risk Assessment | What could go wrong? | Risk levels + mitigation strategies |
| Current State | What exists today? | Affected files + dependencies |
| Key Features | What does it do? | 6-10 user-facing features |
| Task IDs | What work is needed? | PREFIX-NNN tasks (SETUP, DB, API, LOGIC, UI, TEST, SEC, DOC, DEPLOY) |
| Phases | What order? | 4-6 phases with completion criteria |
| Testing | How to validate? | Unit + integration + E2E + 5+ edge cases |
| Success Criteria | When is it done? | Quantifiable metrics (functional, quality, performance, security) |
| Checklist | Track progress | All task IDs with checkboxes |

---

**Version**: 1.0.0
**Created**: 2025-10-10
**Applicability**: Any language, any framework, any project
**Reference**: See `feature-implementation-planning-standard.json` for detailed guidance
