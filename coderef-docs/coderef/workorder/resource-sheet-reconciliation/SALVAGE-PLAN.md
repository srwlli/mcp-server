# Resource Sheet Reconciliation - Salvage Plan

**Workorder:** WO-RESOURCE-SHEET-RECONCILIATION-001
**Created:** 2026-01-02
**Purpose:** Map TypeScript templates to Python module ports

---

## TypeScript System Audit

**Location:** `modules/resource-sheet/`
**Total Lines:** 7,380
**Salvageable:** 5,416 lines (73%)

###  Salvageable Components

#### 1. Module Templates (1,527 lines) - ✅ HIGH VALUE
**Action:** Port to Python dataclasses

| TypeScript File | Python Target | Lines | Category |
|----------------|---------------|-------|----------|
| `conditional/props.md` | `resource_sheet/modules/conditional/ui/props.py` | 76 | UI |
| `conditional/events.md` | `resource_sheet/modules/conditional/ui/events.py` | 46 | UI |
| `conditional/accessibility.md` | `resource_sheet/modules/conditional/ui/accessibility.py` | 64 | UI |
| `conditional/state.md` | `resource_sheet/modules/conditional/state/state_management.py` | 231 | State |
| `conditional/lifecycle.md` | `resource_sheet/modules/conditional/state/lifecycle.py` | 46 | State |
| `conditional/endpoints.md` | `resource_sheet/modules/conditional/network/endpoints.py` | 43 | Network |
| `conditional/auth.md` | `resource_sheet/modules/conditional/network/auth.py` | 50 | Network |
| `conditional/errors.md` | `resource_sheet/modules/conditional/network/errors.py` | 45 | Network |
| `conditional/routing.md` | `resource_sheet/modules/conditional/network/routing.py` | 45 | Network (deferred) |
| `conditional/validation.md` | `resource_sheet/modules/conditional/data/validation.py` | 50 | Data (deferred) |
| `conditional/persistence.md` | `resource_sheet/modules/conditional/data/persistence.py` | 56 | Data (deferred) |

**Phase 2 Scope (11 modules, 702 lines):**
- 3 UI: props, events, accessibility
- 2 State: state_management, lifecycle
- 4 Network: endpoints, auth, errors, retry (add retry from handoff)
- 2 Hooks: signature, side_effects (from handoff attempt)

**Deferred to Future:**
- routing, validation, persistence (lower priority)

#### 2. Documentation (3,523 lines) - ✅ KEEP AS-IS
**Action:** Reference only, don't port

| File | Lines | Status |
|------|-------|--------|
| `RESOURCE-SHEET-SYSTEM.md` | 1,462 | ✅ Keep - Master reference |
| `MODULE-CATEGORIES-GUIDE.md` | 777 | ✅ Keep - Kitchen analogy guide |
| `README.md` | 879 | ✅ Keep - Usage guide |
| `PROGRESS.md` | 187 | ✅ Update - Reconciliation notes |
| `types.ts` | 366 | ⚠️  Extract logic - Convert to Python TypedDict concepts |

#### 3. Detection/Classification (921 lines) - ⚠️ ENHANCE PYTHON
**Action:** Use logic to enhance existing Python detector

| TypeScript File | Enhancement Target | Action |
|-----------------|-------------------|--------|
| `detection/analyzer.ts` (300 lines) | `resource_sheet/detection/analyzer.py` | Extract characteristic detection patterns |
| `detection/classifier.ts` (243 lines) | `resource_sheet/detection/characteristics.py` | Add 8-priority classification logic |
| `detection/selector.ts` (378 lines) | `resource_sheet/modules/__init__.py` | Enhance module selection logic |

**Key Enhancements:**
- 8-priority classification levels (Priority 1-8)
- Confidence scoring for ambiguous elements
- Hybrid element support (multi-category)
- 24 user-friendly categories

#### 4. Composition/Output (845 lines) - ❌ ALREADY EXISTS IN PYTHON
**Action:** Skip - Python version already working

| TypeScript File | Python Equivalent | Status |
|-----------------|-------------------|--------|
| `composition/composer.ts` (507 lines) | `resource_sheet/composition/composer.py` (259 lines) | ✅ Exists |
| `output/markdown-generator.ts` (120 lines) | Part of composer.py | ✅ Exists |
| `output/schema-generator.ts` (107 lines) | Part of composer.py | ✅ Exists |
| `output/jsdoc-generator.ts` (111 lines) | Part of composer.py | ✅ Exists |

---

## Porting Strategy

### Phase 2: Port UI Modules (PORT-001)

**Template:** `modules/resource-sheet/conditional/props.md`

**Python Port:** `resource_sheet/modules/conditional/ui/props.py`

```python
"""
Props Module - React/Vue component props documentation.

WO-RESOURCE-SHEET-RECONCILIATION-001/PORT-001

Conditional module for components with props/parameters.
"""

from ....types import DocumentationModule, ModuleTriggers

def auto_fill_props(data: dict) -> str:
    """Auto-fill props section from element metadata."""
    props = data.get("metadata", {}).get("props", [])

    if not props:
        return "No props detected.\n\n"

    # Generate props interface
    content = "```typescript\n"
    content += f"interface {data['name']}Props {{\n"
    for prop in props:
        required = "" if prop.get("required") else "?"
        content += f"  {prop['name']}{required}: {prop['type']};\n"
    content += "}\n```\n\n"

    # Generate props table
    content += "| Prop | Type | Required | Default | Description |\n"
    content += "|------|------|----------|---------|-------------|\n"
    for prop in props:
        req = "Yes" if prop.get("required") else "No"
        default = prop.get("default", "-")
        desc = prop.get("description", "TODO")
        content += f"| {prop['name']} | `{prop['type']}` | {req} | {default} | {desc} |\n"

    return content


props_module = DocumentationModule(
    id="props",
    name="Props & Configuration",
    category="ui",
    description="Component props interface and validation",
    triggers=ModuleTriggers(
        required_when=["has_props", "is_component"],
        optional_when=[],
        incompatible_with=[]
    ),
    auto_fill_function=auto_fill_props,
    template="""
## Props Reference

### Props Interface

{auto_fill_content}

{manual_prompt: Explain prop design decisions:
- Why these props? Why required vs optional?
- Could any props be derived or merged?
- Are there too many props (> 10)?}

### Prop Validation

{manual_prompt: Explain validation strategy:
- Runtime validation (PropTypes, Zod)?
- TypeScript compile-time only?
- Custom validation logic?}
""",
    manual_sections=[
        "Prop design rationale",
        "Validation strategy",
        "Usage examples"
    ]
)
```

### Directory Structure After Porting

```
resource_sheet/modules/
├── __init__.py (ModuleRegistry + register_all_modules)
├── universal/
│   ├── __init__.py
│   ├── architecture.py ✅ (Phase 1)
│   ├── integration.py ✅ (Phase 1)
│   ├── testing.py ✅ (Phase 1 stub)
│   └── performance.py ✅ (Phase 1 stub)
└── conditional/
    ├── __init__.py (NEW)
    ├── ui/
    │   ├── __init__.py (NEW)
    │   ├── props.py (NEW - PORT-001)
    │   ├── events.py (NEW - PORT-001)
    │   └── accessibility.py (NEW - PORT-001)
    ├── state/
    │   ├── __init__.py (NEW)
    │   ├── state_management.py (NEW - PORT-002)
    │   └── lifecycle.py (NEW - PORT-002)
    ├── network/
    │   ├── __init__.py (NEW)
    │   ├── endpoints.py (NEW - PORT-003)
    │   ├── auth.py (NEW - PORT-003)
    │   ├── retry.py (NEW - PORT-003)
    │   └── errors.py (NEW - PORT-003)
    └── hooks/
        ├── __init__.py (NEW)
        ├── signature.py (NEW - PORT-004)
        └── side_effects.py (NEW - PORT-004)
```

---

## Module Triggers Mapping

Based on TypeScript templates and Python Phase 1 patterns:

| Module | Triggers (required_when) | Optional | Incompatible |
|--------|--------------------------|----------|--------------|
| **props** | `has_props`, `is_component` | - | - |
| **events** | `has_event_handlers` | - | - |
| **accessibility** | `has_aria_attributes` | `is_component` | - |
| **state_management** | `manages_state` | - | - |
| **lifecycle** | `has_lifecycle_methods` | - | - |
| **endpoints** | `makes_network_calls` | - | - |
| **auth** | `handles_auth` | - | - |
| **retry** | `has_retry_logic` | - | - |
| **errors** | `has_error_handling` | - | - |
| **signature** (hook) | `is_hook` | - | - |
| **side_effects** (hook) | `is_hook` | - | - |

---

## Success Criteria

### Module Porting
- ✅ All 11 modules follow `DocumentationModule` dataclass pattern
- ✅ Each has `auto_fill_*()` function
- ✅ Each has `template` string with manual prompts
- ✅ Triggers match TypeScript specs

### Detection Enhancement
- ✅ 3 new characteristics added: `has_event_handlers`, `has_aria_attributes`, `has_lifecycle_methods`
- ✅ types.py updated with new fields
- ✅ 20+ total characteristics detected

### Registry Integration
- ✅ ModuleRegistry fixed (dataclass access, not dict)
- ✅ All 15 modules registered
- ✅ Module selection works with new triggers

### Testing
- ✅ 24 tests passing (13 existing + 11 new)
- ✅ React component test selects 8+ modules
- ✅ API service test selects network modules
- ✅ Auto-fill rate 60%+ on 5 samples

---

## Audit Complete ✅

**Salvageable:** 5,416 lines (73%)
**Porting Required:** 11 modules (~700 lines of templates → ~1,100 lines of Python)
**Documentation to Keep:** 3,523 lines as reference
**Detection to Enhance:** 3 new characteristics + classification logic

**Estimated Effort:** 4-6 hours for complete reconciliation

**Next:** Begin PORT-001 (3 UI modules)
