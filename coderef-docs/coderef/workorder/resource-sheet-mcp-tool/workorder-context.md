# Resource Sheet MCP Tool - Workorder Context (Source of Truth)

**Workorder ID:** WO-RESOURCE-SHEET-MCP-001
**Feature:** resource-sheet-mcp-tool
**Target Project:** coderef-docs MCP server
**Status:** Planning
**Created:** 2026-01-02

---

## Executive Summary

Migrate resource sheet documentation system from assistant slash commands to a universal MCP tool using **composable module architecture** instead of rigid templates. Enable any project to generate authoritative technical documentation through intelligent code analysis and module composition.

---

## Problem Statement

### Current State
- Resource sheet templates exist as slash commands in assistant project only
- 20 rigid templates with massive duplication
- Manual process: agent follows template checklist by hand
- No cross-project access
- No automation or auto-fill capabilities

### Pain Points
1. **Duplication:** "State" definition copied across 10+ templates
2. **Rigidity:** Can't mix concerns or adapt to hybrid elements
3. **Maintenance:** Updating one concept requires changing multiple templates
4. **Access:** Only available in assistant project
5. **Manual:** 3-4 hours per resource sheet, fully human-driven

---

## Solution Architecture

### Core Innovation: Composable Module System

**Instead of 20 templates, use ~30-40 small modules that compose intelligently.**

#### Three-Step Workflow

```
Step 1: WHAT IS THIS?
  → Analyze code, detect characteristics

Step 2: PICK VARIABLES
  → Match characteristics to required modules

Step 3: ASSEMBLE
  → Compose modules into documentation
```

---

## Module-Based Architecture

### Universal Modules (Always Included)

| Module ID | Purpose | Output |
|-----------|---------|--------|
| `architecture` | Component hierarchy, dependencies | Markdown section + schema |
| `integration` | How it connects to other code | Integration points table |
| `testing` | Test patterns, coverage, mocks | Testing strategy section |
| `performance` | Limits, bottlenecks, budgets | Performance section |

### Conditional Modules (Based on Code Analysis)

| Module ID | Triggers | Applies To |
|-----------|----------|------------|
| `endpoints` | Has `fetch()` calls | API clients, services |
| `auth` | Manages JWT/tokens | Auth services, API clients |
| `retry` | Network operations | API clients (even if missing) |
| `errors` | Has error handling | All error-prone code |
| `state` | Has `useState`/class state | Components, containers |
| `lifecycle` | Component lifecycle methods | React components |
| `props` | React props interface | Components |
| `events` | Event handlers | Interactive components |
| `accessibility` | Has JSX | UI components |
| `persistence` | Uses localStorage/IndexedDB | State management |
| `versioning` | Persisted data | Storage systems |
| `side_effects` | `useEffect`/side effects | Hooks |
| `cleanup` | Cleanup logic | Hooks, subscriptions |
| `dependencies` | Dependency arrays | Hooks |
| `signature` | Function/hook signature | Utilities, hooks |
| `store_shape` | Redux/Zustand store | Global state |
| `actions` | Redux actions | Global state |
| `selectors` | Derived state | Global state |
| `middleware` | Store middleware | Global state |
| `variants` | Visual variants | Design system |
| `theming` | Theme tokens | Styled components |
| `caching` | Cache strategy | Data fetchers |
| `rate_limiting` | Request throttling | API clients |

**Total: ~30-40 modules** (composable, no duplication)

---

## Detection Logic (Step 1: WHAT IS THIS?)

### Code Analysis Questions

```javascript
const characteristics = {
  // Structure
  is_class: boolean,
  is_function: boolean,
  is_component: boolean,
  is_hook: boolean,

  // Behavior
  makes_network_calls: boolean,
  manages_state: boolean,
  handles_auth: boolean,
  has_error_handling: boolean,
  has_retry_logic: boolean,

  // UI
  has_jsx: boolean,
  has_props: boolean,
  has_events: boolean,

  // Storage
  uses_local_storage: boolean,
  uses_indexed_db: boolean,
  uses_global_state: boolean,

  // Data
  has_types: boolean,
  has_schema: boolean,
  has_validation: boolean,

  // Testing
  has_tests: boolean,
  has_mocks: boolean
};
```

### Detection Methods

```typescript
// Use coderef_scan output
function detectCharacteristics(scanResult) {
  return {
    makes_network_calls: scanResult.imports.includes('fetch') ||
                         scanResult.imports.includes('axios'),
    manages_state: scanResult.hooks.includes('useState') ||
                   scanResult.hooks.includes('useReducer'),
    has_jsx: scanResult.exports.some(e => e.type === 'component'),
    uses_local_storage: scanResult.code.includes('localStorage'),
    // ... more detection rules
  };
}
```

---

## Module Selection (Step 2: PICK VARIABLES)

### Selection Rules

```javascript
function selectModules(characteristics) {
  const modules = [];

  // Always include
  modules.push('architecture', 'integration', 'testing', 'performance');

  // Network operations
  if (characteristics.makes_network_calls) {
    modules.push('endpoints', 'errors', 'retry');
  }

  // Authentication
  if (characteristics.manages_auth) {
    modules.push('auth');
  }

  // State management
  if (characteristics.manages_state) {
    modules.push('state');
    if (characteristics.is_component) {
      modules.push('lifecycle');
    }
  }

  // UI components
  if (characteristics.has_jsx) {
    modules.push('props', 'events', 'accessibility');
  }

  // Storage
  if (characteristics.uses_local_storage || characteristics.uses_indexed_db) {
    modules.push('persistence', 'versioning');
  }

  // Hooks
  if (characteristics.is_hook) {
    modules.push('signature', 'side_effects', 'cleanup', 'dependencies');
  }

  // Global state
  if (characteristics.uses_global_state) {
    modules.push('store_shape', 'actions', 'selectors');
  }

  return modules;
}
```

---

## Module Definition Schema

### Module Structure

```typescript
interface DocumentationModule {
  // Identity
  id: string;                    // 'endpoints', 'auth', 'state'
  name: string;                  // "Endpoint Catalog"
  description: string;           // "Documents all API endpoints"

  // When to include
  triggers: {
    required_when: string[];     // ['makes_network_calls']
    optional_when: string[];     // ['has_caching']
    incompatible_with: string[]; // ['is_hook'] (endpoints don't apply to hooks)
  };

  // What to generate
  templates: {
    markdown: {
      section_title: string;     // "## Endpoint Catalog"
      content: TemplateString;   // Markdown template
      auto_fill: (data) => string;
      manual_prompts: Question[];
    };
    schema: {
      definition: SchemaTemplate;
      validation_rules: ValidationRules;
    };
    jsdoc: {
      patterns: JSDocTemplate[];
      examples: CodeExample[];
    };
  };

  // How to extract data
  extraction: {
    from_coderef_scan: (scanData) => ModuleData;
    from_ast: (ast) => ModuleData;
    from_user: Question[];
    validation: (data) => ValidationResult;
  };
}
```

---

## Example: `endpoints` Module

```typescript
const endpointsModule: DocumentationModule = {
  id: 'endpoints',
  name: 'Endpoint Catalog',
  description: 'Documents all API endpoints with request/response schemas',

  triggers: {
    required_when: ['makes_network_calls'],
    optional_when: [],
    incompatible_with: ['is_hook', 'is_component']
  },

  templates: {
    markdown: {
      section_title: '## Endpoint Catalog',
      content: `
| Endpoint | Method | Request | Response | Errors |
|----------|--------|---------|----------|--------|
{{#each endpoints}}
| {{path}} | {{method}} | {{request_schema}} | {{response_schema}} | {{errors}} |
{{/each}}
      `,
      auto_fill: (data) => {
        // Fill table from extracted endpoint data
      },
      manual_prompts: [
        'Are there additional endpoints not detected in code?',
        'Any deprecated endpoints to document?'
      ]
    },
    schema: {
      definition: {
        endpoints: {
          type: 'array',
          items: {
            path: 'string',
            method: 'string',
            request_schema: 'object',
            response_schema: 'object'
          }
        }
      }
    },
    jsdoc: {
      patterns: [
        '/** @endpoint {{method}} {{path}} */',
        '/** @param {{request_schema}} */',
        '/** @returns {{response_schema}} */'
      ]
    }
  },

  extraction: {
    from_coderef_scan: (scanData) => {
      // Find all fetch/axios calls
      // Extract URL patterns
      // Detect request/response types
    },
    from_user: [
      { question: 'Endpoint path?', type: 'string' },
      { question: 'HTTP method?', type: 'enum', options: ['GET', 'POST', 'PUT', 'DELETE'] }
    ],
    validation: (data) => {
      // Ensure all endpoints have path, method, schemas
    }
  }
};
```

---

## Composition Example: AuthService

### Step 1: Detection
```javascript
analyze(AuthService.ts) → {
  makes_network_calls: true,    // fetch() detected
  manages_auth: true,            // JWT tokens found
  has_error_handling: true,      // try/catch blocks
  has_retry_logic: false,        // no retry code
  is_class: true,
  has_jsx: false,
  manages_state: false
}
```

### Step 2: Module Selection
```javascript
selectedModules = [
  'architecture',      // universal
  'integration',       // universal
  'testing',           // universal
  'performance',       // universal
  'endpoints',         // makes_network_calls = true
  'auth',              // manages_auth = true
  'errors',            // has_error_handling = true
  'retry'              // makes_network_calls = true (even though missing)
]
```

### Step 3: Assembly
```markdown
# AuthService - Authoritative Documentation

## 1. Architecture [architecture module]
Class-based API service
Dependencies: axios, jwt-decode

## 2. Endpoint Catalog [endpoints module]
| Endpoint | Method | Request | Response |
| /login   | POST   | {email, password} | {token} |
...

## 3. Auth Strategy [auth module]
JWT tokens in Authorization header
Refresh flow with 15min expiry

## 4. Error Taxonomy [errors module]
| Error | Status | Message | Recovery |
| AuthError | 401 | "Please log in" | Redirect |
...

## 5. Retry Logic ⚠️ [retry module]
⚠️ NOT DETECTED IN CODE
Please document backoff strategy, max attempts

## 6. Integration Points [integration module]
Used by: LoginForm, App.tsx
Emits: auth:login, auth:logout

## 7. Testing Strategy [testing module]
Mock fetch responses
Coverage: 85%

## 8. Performance [performance module]
Avg response: 200ms
Timeout: 10s
```

---

## MCP Tool Interface

### Tool Signature

```typescript
mcp__coderef-docs__generate_resource_sheet({
  // Required
  element_name: string,          // "AuthService"
  project_path: string,          // "/path/to/project"

  // Optional
  element_type?: string,         // Manual override (skip auto-detection)
  mode: 'reverse-engineer' | 'template' | 'refresh',
  auto_analyze: boolean,         // Use coderef_scan for auto-fill (default: true)
  output_path?: string,          // Where to save (default: coderef/foundation-docs/)
  validate_against_code: boolean // Compare docs to code (default: true)
})
```

### Mode Behaviors

**`reverse-engineer`** (Existing Code)
- Runs `coderef_scan` to analyze code
- Detects characteristics
- Selects modules
- Auto-fills 60-70% from code
- Flags gaps for human review
- Validates extracted data

**`template`** (New Code)
- User specifies element type or characteristics
- Selects modules based on intent
- Returns empty templates
- Provides checklists
- No auto-fill (nothing to analyze)

**`refresh`** (Update Existing)
- Reads existing resource sheet
- Re-scans code for changes
- Detects drift (docs vs code)
- Suggests updates
- Preserves manual sections

---

## Output Format

### Three Files Generated

**1. Markdown** (`coderef/foundation-docs/ELEMENT-NAME.md`)
```markdown
---
element: AuthService
type: API Service
modules: [architecture, endpoints, auth, errors, retry, integration, testing, performance]
auto_fill_rate: 68%
generated: 2026-01-02
---

# AuthService - Authoritative Documentation

[Composed sections from selected modules]
```

**2. JSON Schema** (`coderef/schemas/element-name.schema.json`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AuthService",
  "type": "object",
  "properties": {
    "endpoints": { ... },
    "auth": { ... },
    "errors": { ... }
  }
}
```

**3. JSDoc Enhancements** (inline in source file)
```typescript
/**
 * AuthService handles authentication and token management
 * @see coderef/foundation-docs/AUTH-SERVICE.md
 *
 * @module AuthService
 * @category API Client
 *
 * @example
 * const auth = new AuthService();
 * await auth.login({email, password});
 */
```

---

## Implementation Phases

### Phase 1: Core Modules (Week 1)
**Goal:** Define and implement 10 universal modules

Modules:
- architecture
- integration
- testing
- performance
- state
- errors
- props
- events

**Deliverable:** Module definition system working

---

### Phase 2: Specialized Modules (Week 2)
**Goal:** Add domain-specific modules

Modules:
- endpoints
- auth
- retry
- persistence
- lifecycle
- side_effects
- accessibility
- variants

**Deliverable:** 20-25 modules total

---

### Phase 3: Detection & Composition (Week 3)
**Goal:** Intelligent module selection

Features:
- Code analysis via coderef_scan
- Characteristic detection
- Module selection rules
- Composition engine

**Deliverable:** Auto-detection working

---

### Phase 4: MCP Tool Integration (Week 4)
**Goal:** Expose as MCP tool

Features:
- Tool registration in coderef-docs
- Parameter validation
- Mode switching (reverse-engineer, template, refresh)
- Output file writing

**Deliverable:** Tool callable from any project

---

### Phase 5: Testing & Validation (Week 5)
**Goal:** Ensure quality and accuracy

Tests:
- Module composition correctness
- Auto-fill accuracy (60%+ target)
- Detection reliability (90%+ common cases)
- Generated doc validation

**Deliverable:** Production-ready tool

---

## Success Criteria

### Must-Have
- [ ] Tool callable from any project via MCP
- [ ] ~30-40 composable modules defined
- [ ] Auto-detection works for 90%+ common element types
- [ ] Auto-fill achieves 60%+ completion from code analysis
- [ ] Generated docs pass UDS validation
- [ ] All 3 output formats generated (markdown, schema, JSDoc)
- [ ] Backward compatibility with assistant slash commands

### Nice-to-Have
- [ ] Bulk generation (document entire directory)
- [ ] Drift detection (docs vs code comparison)
- [ ] Custom module creation by users
- [ ] Template preview before generation
- [ ] Integration with /create-plan workflow

---

## Migration Strategy

### Backward Compatibility

**Keep assistant slash commands:**
```bash
# Still works in assistant project
/create-resource-sheet AuthService

# But internally calls MCP tool
→ mcp__coderef-docs__generate_resource_sheet(...)
```

**Map old template references:**
```javascript
// Legacy template ID → Module composition
const legacyMapping = {
  'template-1-widget': ['architecture', 'props', 'state', 'events', 'accessibility'],
  'template-5-api-client': ['architecture', 'endpoints', 'auth', 'retry', 'errors'],
  // ... map all 20 templates
};
```

---

## File Structure

### In coderef-docs MCP Server

```
C:\Users\willh\.mcp-servers\coderef-docs\
├── src/
│   ├── tools/
│   │   └── generate-resource-sheet.ts    # MCP tool implementation
│   ├── modules/
│   │   ├── index.ts                       # Module registry
│   │   ├── universal/
│   │   │   ├── architecture.ts
│   │   │   ├── integration.ts
│   │   │   ├── testing.ts
│   │   │   └── performance.ts
│   │   ├── ui/
│   │   │   ├── props.ts
│   │   │   ├── events.ts
│   │   │   ├── accessibility.ts
│   │   │   └── variants.ts
│   │   ├── state/
│   │   │   ├── state.ts
│   │   │   ├── lifecycle.ts
│   │   │   ├── persistence.ts
│   │   │   └── versioning.ts
│   │   ├── network/
│   │   │   ├── endpoints.ts
│   │   │   ├── auth.ts
│   │   │   ├── retry.ts
│   │   │   ├── errors.ts
│   │   │   ├── caching.ts
│   │   │   └── rate-limiting.ts
│   │   └── hooks/
│   │       ├── signature.ts
│   │       ├── side-effects.ts
│   │       ├── cleanup.ts
│   │       └── dependencies.ts
│   ├── detection/
│   │   ├── analyze.ts                     # Code analysis
│   │   ├── characteristics.ts             # Detection rules
│   │   └── selection.ts                   # Module selection
│   └── composition/
│       ├── compose.ts                     # Module composition
│       ├── markdown.ts                    # Markdown generator
│       ├── schema.ts                      # JSON schema generator
│       └── jsdoc.ts                       # JSDoc generator
├── templates/
│   └── module-templates/
│       ├── markdown/                      # Markdown templates per module
│       ├── schema/                        # Schema templates per module
│       └── jsdoc/                         # JSDoc templates per module
├── tests/
│   ├── modules/                           # Module tests
│   ├── detection/                         # Detection tests
│   └── integration/                       # End-to-end tests
└── coderef/
    └── workorder/
        └── resource-sheet-mcp-tool/
            ├── context.json
            ├── communication.json
            ├── workorder-context.md       # THIS FILE (source of truth)
            ├── info.md                    # Example output
            └── info2.md                   # Planning doc
```

---

## Technical Decisions

### Decision 1: Modules Over Templates
**Chosen:** ~30-40 composable modules
**Rejected:** 20 rigid templates
**Reason:** Eliminates duplication, enables flexible composition, easier maintenance

### Decision 2: Auto-Detection Required
**Chosen:** Analyze code to detect characteristics
**Rejected:** User manually specifies all modules
**Reason:** Reduces cognitive load, faster workflow, fewer mistakes

### Decision 3: Three Output Formats
**Chosen:** Markdown + JSON Schema + JSDoc
**Rejected:** Single format
**Reason:** Different audiences (humans, tools, IDEs), complementary coverage

### Decision 4: Integration with coderef_scan
**Chosen:** Use existing coderef_scan for code analysis
**Rejected:** Build custom AST parser
**Reason:** Reuse proven analysis, consistent with ecosystem

### Decision 5: Gradual Auto-Fill
**Chosen:** Auto-fill what's detectable, flag gaps for human
**Rejected:** 100% automated or 100% manual
**Reason:** Balances speed with quality, captures tribal knowledge

---

## Dependencies

### Required Tools
- `coderef_scan` - Code analysis and element extraction
- `validate_document` - UDS validation for generated docs
- `get_template` - Load module templates

### Optional Integrations
- `/create-plan` - Generate resource sheets during planning
- `/update-deliverables` - Track documentation metrics
- `check_document_health` - Score resource sheet completeness

---

## Testing Strategy

### Unit Tests
- Each module generates valid output
- Detection rules match expected characteristics
- Composition produces correct structure

### Integration Tests
- End-to-end: code → detection → selection → composition → output
- All 3 formats generated correctly
- Auto-fill percentage meets 60%+ target

### Validation Tests
- Generated markdown passes UDS validation
- JSON schema is valid JSON Schema Draft 7
- JSDoc comments are syntactically correct

### Real-World Tests
- Test on 20 different element types (1 per old template)
- Test on hybrid elements (e.g., component + API client)
- Test on poorly-documented legacy code

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Analysis time | < 5 seconds | Time to run coderef_scan + detection |
| Generation time | < 10 seconds | Time to compose and write 3 files |
| Auto-fill rate | 60-70% | % of sections auto-filled from code |
| Detection accuracy | 90%+ | % of correct element type detection |
| Module selection accuracy | 95%+ | % of correct module selection |

---

## Known Limitations

### Cannot Auto-Fill
- Design rationale (why decisions were made)
- Common pitfalls (tribal knowledge)
- Performance notes (production observations)
- Migration notes (historical context)

### Detection Challenges
- Hybrid elements (component + API client)
- Non-standard patterns (custom hooks with JSX)
- Legacy code without types
- Highly dynamic code (runtime config)

### Scope Boundaries
- Does not generate code (only documentation)
- Does not refactor existing docs (use refresh mode)
- Does not validate code quality (only documents what exists)

---

## Future Enhancements

### Phase 2 Features
- Custom module creation by users
- Module marketplace/sharing
- Visual documentation preview
- Integration with CI/CD (auto-generate on commit)
- Bulk generation (entire codebase)

### Advanced Detection
- ML-based element classification
- Pattern recognition from similar codebases
- Semantic code analysis (not just AST)

### Ecosystem Integration
- Auto-update docs when code changes
- Link resource sheets to git blame (who knows what)
- Generate dependency graphs from integration modules

---

## Questions for User

Before proceeding with implementation:

1. **Module Count:** Start with 15 core modules or go straight to 30-40?
2. **Auto-Fill Target:** Is 60-70% acceptable or aim higher?
3. **Template Format:** Handlebars, Mustache, or custom template engine?
4. **Storage:** Module definitions in TypeScript or JSON?
5. **Validation:** Strict (fail if missing sections) or lenient (warn only)?

---

## Next Steps

### Immediate (This Week)
1. Review this workorder-context.md with user
2. Get approval on module-based architecture
3. Define 10-15 core modules
4. Implement detection logic proof-of-concept

### Short-Term (Next 2 Weeks)
1. Build module definition system
2. Implement composition engine
3. Integrate with coderef_scan
4. Create MCP tool interface

### Long-Term (Next Month)
1. Complete all ~30-40 modules
2. Test on real codebases
3. Validate auto-fill accuracy
4. Launch as production MCP tool

---

## References

### Related Workorders
- WO-RESOURCE-SHEET-SYSTEM-001 (assistant slash commands - completed)

### Documentation
- `.claude/commands/create-resource-sheet.md` - Original template instructions
- `.claude/commands/resource-sheet-catalog.md` - 20 template catalog (deprecated)
- `coderef/workorder/resource-sheet-system/DELIVERABLES.md` - Example output

### External Resources
- UDS (Universal Documentation Standards) - coderef-docs validation framework
- CodeRef scan output format - Element extraction schema
- JSON Schema Draft 7 specification

---

**This document is the authoritative source of truth for WO-RESOURCE-SHEET-MCP-001.**

**Last Updated:** 2026-01-02
**Maintained By:** CodeRef Assistant (Orchestrator)
**Status:** Ready for planning phase
