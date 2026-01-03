# Module Reference - Resource Sheet System

**Version:** 1.0.0
**Last Updated:** 2026-01-03
**Workorder:** WO-RESOURCE-SHEET-CONSOLIDATION-001

---

## Purpose

Technical reference for the composable module system underlying unified resource sheets. Learn how modules are selected, structured, and assembled to generate element-specific documentation.

---

## Overview

The resource sheet system uses **~30-40 composable modules** organized into two categories:

- **Universal Modules (4):** Always included regardless of element type
- **Conditional Modules (11+):** Selected based on element type characteristics

Each module defines a **documentation section** with auto-fill logic, validation rules, and content schema.

---

## Module Categories

### Universal Modules (Always Included)

#### 1. Architecture Module
**Purpose:** Document component hierarchy, integration points, and data flow

**Content Schema:**
```markdown
## Architecture Overview

**Element Type:** {detected_type}
**Classification:** {top-level-widget|stateful-container|...}

### Component Hierarchy
{auto-filled from dependency graph}

### Integration Points
{auto-filled from imports/exports}

### Data Flow
{semi-auto-filled from state analysis}
```

**Auto-Fill Rate:** 70-90%
- ✅ Component hierarchy (graph imports/exports)
- ✅ Integration points (graph dependencies)
- ⚠️ Data flow (requires state ownership analysis)

**Validation Rules:**
- Must include element type classification
- Must document at least 1 integration point
- Hierarchy must match actual code structure

---

#### 2. Integration Module
**Purpose:** Document external dependencies, API contracts, and system boundaries

**Content Schema:**
```markdown
## Integration Contracts

### External Dependencies
| Dependency | Type | Contract | Version |
|------------|------|----------|---------|
{auto-filled from package.json + imports}

### API Contracts
{auto-filled from TypeScript interfaces}

### Event Contracts
| Event | Trigger | Payload | Side Effects |
|-------|---------|---------|--------------|
{auto-filled from event handler analysis}
```

**Auto-Fill Rate:** 60-80%
- ✅ External dependencies (package.json + graph)
- ✅ API contracts (TypeScript types)
- ⚠️ Event side effects (manual review required)

**Validation Rules:**
- Must document all external integrations
- Event payloads must match TypeScript signatures
- Version constraints required for external deps

---

#### 3. Testing Module (Stub)
**Purpose:** Placeholder for test strategy documentation

**Content Schema:**
```markdown
## Testing Strategy

### Unit Tests
TODO: Document unit test coverage

### Integration Tests
TODO: Document integration test scenarios

### Edge Cases
TODO: Document known edge cases
```

**Auto-Fill Rate:** 0% (manual only)
- ❌ Unit test coverage (requires manual input)
- ❌ Integration scenarios (requires manual input)
- ❌ Edge cases (requires domain knowledge)

**Validation Rules:**
- Section must exist but content optional
- Low auto-fill acceptable for testing module

---

#### 4. Performance Module (Stub)
**Purpose:** Placeholder for performance considerations

**Content Schema:**
```markdown
## Performance Considerations

### Performance Limits
TODO: Document performance constraints

### Optimization Opportunities
TODO: Document known bottlenecks

### Profiling Notes
TODO: Add profiling data
```

**Auto-Fill Rate:** 10-30%
- ⚠️ Performance limits (may extract from comments)
- ❌ Optimization opportunities (manual)
- ❌ Profiling notes (manual)

**Validation Rules:**
- Section must exist but content optional
- Can remain as stub for non-critical components

---

### Conditional Modules (Selected by Element Type)

#### 5. Composition Module
**When Selected:** UI components, stateful containers, top-level widgets
**Detection Pattern:** JSX/TSX files, React components, Vue components

**Content Schema:**
```markdown
## Component Composition

### Props Interface
{auto-filled from TypeScript props type}

### Children Contracts
{auto-filled from JSX analysis}

### Render Behavior
{semi-auto-filled from render logic}
```

**Auto-Fill Rate:** 80-95%

---

#### 6. Events Module
**When Selected:** UI components, custom hooks, eventing systems
**Detection Pattern:** Event handlers, callbacks, listeners

**Content Schema:**
```markdown
## Event Handling

### Event Contracts
| Event | Trigger | Payload | Handler |
|-------|---------|---------|---------|
{auto-filled from event handler analysis}

### Callback Signatures
{auto-filled from TypeScript function types}
```

**Auto-Fill Rate:** 70-85%

---

#### 7. Accessibility Module
**When Selected:** UI components, design system elements
**Detection Pattern:** aria-* attributes, role attributes, semantic HTML

**Content Schema:**
```markdown
## Accessibility

### ARIA Contracts
{auto-filled from aria-* attributes}

### Keyboard Navigation
{semi-auto-filled from onKey* handlers}

### Screen Reader Support
{manual}
```

**Auto-Fill Rate:** 40-60%

---

#### 8. State Management Module
**When Selected:** Stateful containers, global state layer, custom hooks
**Detection Pattern:** useState, useReducer, Redux, Zustand, Context

**Content Schema:**
```markdown
## State Management

### State Ownership
| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
{auto-filled from useState/useReducer analysis}

### State Transitions
{semi-auto-filled from state update calls}
```

**Auto-Fill Rate:** 50-70%

---

#### 9. Lifecycle Module
**When Selected:** Stateful containers, custom hooks
**Detection Pattern:** useEffect, useLayoutEffect, lifecycle methods

**Content Schema:**
```markdown
## Lifecycle Management

### Effects
| Effect | Dependencies | Cleanup | Trigger |
|--------|--------------|---------|---------|
{auto-filled from useEffect analysis}

### Initialization
{semi-auto-filled from constructor/mount logic}
```

**Auto-Fill Rate:** 60-80%

---

#### 10. Persistence Module
**When Selected:** Persistence subsystems, global state layer
**Detection Pattern:** localStorage, sessionStorage, indexedDB, cache

**Content Schema:**
```markdown
## Data Persistence

### Storage Keys Catalog
| Key | Type | Persistence | Default | Validation |
|-----|------|-------------|---------|------------|
{auto-filled from storage API calls}

### Hydration Strategy
{semi-auto-filled from initialization logic}
```

**Auto-Fill Rate:** 50-70%

---

#### 11. Endpoints Module
**When Selected:** API clients, network layers
**Detection Pattern:** fetch, axios, HTTP methods

**Content Schema:**
```markdown
## API Endpoints

### Endpoint Catalog
| Method | Path | Payload | Response | Auth |
|--------|------|---------|----------|------|
{auto-filled from fetch/axios calls}

### Request/Response Contracts
{auto-filled from TypeScript types}
```

**Auto-Fill Rate:** 70-90%

---

#### 12. Authentication Module
**When Selected:** API clients, permission systems
**Detection Pattern:** auth tokens, OAuth, JWT, authorization headers

**Content Schema:**
```markdown
## Authentication & Authorization

### Auth Mechanisms
{auto-filled from auth header analysis}

### Permission Contracts
{semi-auto-filled from permission checks}
```

**Auto-Fill Rate:** 40-60%

---

#### 13. Retry Module
**When Selected:** API clients, network layers
**Detection Pattern:** retry logic, exponential backoff, timeout handling

**Content Schema:**
```markdown
## Retry & Resilience

### Retry Strategy
{semi-auto-filled from retry logic analysis}

### Timeout Configuration
{auto-filled from timeout constants}
```

**Auto-Fill Rate:** 30-50%

---

#### 14. Error Handling Module
**When Selected:** API clients, error boundaries, critical components
**Detection Pattern:** try/catch, ErrorBoundary, error handlers

**Content Schema:**
```markdown
## Error Handling

### Error Contracts
| Error Type | Recovery | User Impact | Logging |
|------------|----------|-------------|---------|
{semi-auto-filled from error handler analysis}

### Failure Recovery Paths
{manual}
```

**Auto-Fill Rate:** 40-60%

---

#### 15. Signature Module
**When Selected:** Custom hooks
**Detection Pattern:** Hook naming convention (useXxx)

**Content Schema:**
```markdown
## Hook Signature

### Parameters
{auto-filled from TypeScript function signature}

### Return Value
{auto-filled from TypeScript return type}

### Usage Contract
{manual}
```

**Auto-Fill Rate:** 85-95%

---

## Module Selection Logic

### Selection Algorithm

```python
def select_modules(element_type: str, code_characteristics: dict) -> list[Module]:
    """
    Select appropriate modules based on element type and code analysis.

    Args:
        element_type: Detected element type (1 of 20)
        code_characteristics: Boolean flags from code analysis

    Returns:
        List of module objects to include in resource sheet
    """
    modules = []

    # Step 1: Always add universal modules
    modules.extend([
        ArchitectureModule(),
        IntegrationModule(),
        TestingModule(),
        PerformanceModule()
    ])

    # Step 2: Add conditional modules based on characteristics
    if code_characteristics['has_jsx']:
        modules.append(CompositionModule())

    if code_characteristics['has_event_handlers']:
        modules.append(EventsModule())

    if code_characteristics['has_aria_attributes']:
        modules.append(AccessibilityModule())

    if code_characteristics['has_state_management']:
        modules.append(StateManagementModule())

    if code_characteristics['has_lifecycle_hooks']:
        modules.append(LifecycleModule())

    if code_characteristics['has_storage_calls']:
        modules.append(PersistenceModule())

    if code_characteristics['has_http_calls']:
        modules.append(EndpointsModule())

    if code_characteristics['has_auth_logic']:
        modules.append(AuthenticationModule())

    if code_characteristics['has_retry_logic']:
        modules.append(RetryModule())

    if code_characteristics['has_error_handling']:
        modules.append(ErrorHandlingModule())

    if code_characteristics['is_custom_hook']:
        modules.append(SignatureModule())

    return modules
```

### Element Type to Module Mapping

| Element Type | Universal | Conditional Modules |
|--------------|-----------|---------------------|
| Top-Level Widgets | 4 | composition, events, accessibility, state, lifecycle |
| Stateful Containers | 4 | composition, events, state, lifecycle, persistence |
| Global State Layer | 4 | state, persistence |
| Custom Hooks | 4 | signature, side_effects, lifecycle |
| API Client | 4 | endpoints, auth, retry, errors |
| Data Models | 4 | (none - minimal conditional) |
| Persistence Subsystem | 4 | persistence, errors |
| Eventing/Messaging | 4 | events, errors |
| Routing/Navigation | 4 | state, lifecycle |
| File/Tree Primitives | 4 | (none - minimal conditional) |

---

## Module Composition Rules

### Ordering
1. **Header Metadata** (generated, not a module)
2. **Executive Summary** (synthesized from all modules)
3. **Architecture Module** (always first)
4. **Integration Module** (always second)
5. **Conditional Modules** (sorted by relevance)
6. **Testing Module** (always second-to-last)
7. **Performance Module** (always last)

### Cross-Module References
- **State Management → Persistence:** State ownership table includes persistence column
- **Events → Accessibility:** Event contracts reference keyboard/screen reader impact
- **Architecture → Integration:** Integration points reference hierarchy elements

### Auto-Fill Coordination
- Graph queries run once, data shared across all modules
- TypeScript type extraction shared between Composition, Events, Endpoints modules
- Code analysis results (useState, useEffect) cached and reused

---

## Extension Points

### Adding New Modules

```python
from resource_sheet.core.module import Module

class CustomModule(Module):
    """New module for specialized documentation."""

    @property
    def name(self) -> str:
        return "custom_section"

    @property
    def auto_fill_rate(self) -> float:
        return 0.6  # 60% auto-fill target

    def should_include(self, characteristics: dict) -> bool:
        """Determine if this module applies to current element."""
        return characteristics.get('has_custom_pattern', False)

    def generate_content(self, context: dict) -> str:
        """Generate markdown content for this module."""
        # Auto-fill logic here
        return self._render_template(context)
```

### Customizing Auto-Fill Logic

```python
# In module implementation
def extract_auto_fill_data(self, graph_data: dict, code_ast: dict) -> dict:
    """
    Extract auto-fillable data from graph and AST.

    Args:
        graph_data: Dependency graph from coderef-context
        code_ast: AST analysis from code parser

    Returns:
        Dict of auto-fillable content
    """
    return {
        'dependencies': graph_data.get('imports', []),
        'state_vars': code_ast.get('state_declarations', []),
        'event_handlers': code_ast.get('event_handlers', [])
    }
```

---

## Validation Integration

Each module implements validation rules enforced by the 4-gate pipeline:

### Gate 1: Structural Validation
```python
def validate_structure(self) -> list[ValidationIssue]:
    """Check if required sections/tables present."""
    issues = []
    if not self.has_required_table():
        issues.append(ValidationIssue(
            severity='major',
            message='Missing required table for module'
        ))
    return issues
```

### Gate 2: Content Quality
```python
def validate_content(self) -> list[ValidationIssue]:
    """Check for placeholders, hedging, voice violations."""
    issues = []
    if self.has_placeholders_in_critical_sections():
        issues.append(ValidationIssue(
            severity='major',
            message='Placeholders in critical sections'
        ))
    return issues
```

### Gate 3: Element-Specific Validation
```python
def validate_element_requirements(self, element_type: str) -> list[ValidationIssue]:
    """Check element-type-specific requirements."""
    issues = []
    if element_type == 'stateful-container' and not self.has_state_ownership_table():
        issues.append(ValidationIssue(
            severity='critical',
            message='Stateful container missing state ownership table'
        ))
    return issues
```

### Gate 4: Auto-Fill Threshold
```python
def check_auto_fill_rate(self) -> float:
    """Calculate actual auto-fill percentage."""
    total_fields = len(self.get_all_fields())
    auto_filled = len([f for f in self.get_all_fields() if f.is_auto_filled()])
    return auto_filled / total_fields if total_fields > 0 else 0.0
```

---

## Performance Considerations

### Module Selection Performance
- **Target:** <100ms for element type detection + module selection
- **Typical:** 50-80ms
- **Optimization:** Cache detection results, lazy module initialization

### Auto-Fill Performance
- **Target:** <2s for all auto-fill data extraction
- **Typical:** 1-1.5s
- **Optimization:** Parallel graph queries, shared AST parsing

### Total Generation Time
- **Target:** <3s end-to-end (detection + selection + assembly)
- **Typical:** 2-2.5s
- **Speedup:** 150-300x faster than manual documentation (5 min vs 30-60 min)

---

## Best Practices

### Module Design
✅ **Do:**
- Keep modules focused on single responsibility
- Share extracted data across modules (DRY principle)
- Provide graceful degradation if auto-fill fails
- Document auto-fill rate honestly

❌ **Don't:**
- Create overlapping modules (state vs lifecycle)
- Hardcode element-type-specific logic in universal modules
- Skip validation for conditional modules
- Promise 100% auto-fill (unrealistic)

### Module Selection
✅ **Do:**
- Use code characteristics (boolean flags) for selection
- Allow manual override of module selection
- Document why each module was included
- Test edge cases (hybrid components)

❌ **Don't:**
- Rely solely on filename/path detection
- Include modules "just in case"
- Skip modules for complex components
- Force all 15 modules on every element

---

## Troubleshooting

### "Module not selected for element type"
```
→ Check code characteristics detection
→ Verify element type mapping includes module
→ Manually specify modules with --modules flag
→ Review detection patterns in element-type-mapping.json
```

### "Auto-fill rate below 60%"
```
→ Check if .coderef/index.json exists and is fresh
→ Verify graph queries returning data
→ Review TypeScript type extraction
→ Some modules legitimately have low auto-fill (testing, performance)
```

### "Module validation failed"
```
→ Check required tables/sections present
→ Verify no placeholders in critical sections
→ Review element-specific requirements
→ Run writing standards post-processor
```

---

## Next Steps

- **User Guide:** [RESOURCE-SHEET-USER-GUIDE.md](../user/RESOURCE-SHEET-USER-GUIDE.md)
- **Element Catalog:** [ELEMENT-TYPE-CATALOG.md](ELEMENT-TYPE-CATALOG.md)
- **Quick Reference:** [QUICK-REFERENCE-CARD.md](../user/QUICK-REFERENCE-CARD.md)
