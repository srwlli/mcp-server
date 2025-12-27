# Persona Creation Flow Form

## REQUIRED FIELDS

### 1. Basic Identity
┌─────────────────────────────────────────────────────────┐
│ **Name** (required)                                      │
│ Pattern: lowercase, alphanumeric, hyphens, underscores   │
│ Length: 3-50 characters                                  │
│ Example: "widget-architect", "code-reviewer"             │
│                                                          │
│ Input: _________________________________                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Description** (required)                               │
│ Length: 20-200 characters                                │
│ One-sentence summary of role and expertise              │
│ Example: "Expert in widget architecture and lifecycle    │
│          management for CodeRef Dashboard"               │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

### 2. Expertise & Knowledge
┌─────────────────────────────────────────────────────────┐
│ **Expertise Areas** (required, 3-10 items)              │
│ Format: Comma-separated or JSON array                    │
│ Example: "Widget lifecycle management, Bundle systems,   │
│          Error isolation patterns, ..."                  │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Use Cases** (required, 3-10 items)                    │
│ Format: Comma-separated or JSON array                    │
│ Example: "Review widget implementations, Debug          │
│          integration issues, Optimize performance, ..."  │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

### 3. Behavior & Communication
┌─────────────────────────────────────────────────────────┐
│ **Communication Style** (required)                       │
│ Length: 20-200 characters                                │
│ How does this persona communicate?                       │
│ Example: "Technical and precise with architecture-       │
│          focused guidance and concrete examples"         │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

## OPTIONAL FIELDS

┌─────────────────────────────────────────────────────────┐
│ **Problem-Solving Approach** (optional)                  │
│ Length: max 200 characters                               │
│ How does this persona approach problems?                 │
│ Example: "Analyzes code, traces lifecycle, validates     │
│          contracts, recommends improvements"             │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Tool Usage** (optional)                                │
│ Length: max 200 characters                               │
│ What tools does this persona use?                        │
│ Example: "Read source files, grep for violations,        │
│          analyze bundles, validate types"                │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Specializations** (optional, max 5 items)              │
│ Format: Comma-separated or JSON array                    │
│ Deep expertise areas within main expertise               │
│ Example: "IIFE bundle analysis, Lifecycle hook           │
│          validation, ErrorBoundary integration"          │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Key Principles** (optional, max 10 items)              │
│ Format: Comma-separated or JSON array                    │
│ Core beliefs and non-negotiables                         │
│ Example: "Enforce contracts, Error isolation required,   │
│          Settings drive renders, Analyze bundles"        │
│                                                          │
│ Input: ________________________________________________   │
│        ________________________________________________   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ **Example Responses** (optional, max 3 Q&A pairs)        │
│ Format: JSON object {"question": "answer"}               │
│ Concrete examples of persona in action                   │
│                                                          │
│ Q1: _____________________________________________        │
│ A1: _____________________________________________        │
│                                                          │
│ Q2: _____________________________________________        │
│ A2: _____________________________________________        │
│                                                          │
│ Q3: _____________________________________________        │
│ A3: _____________________________________________        │
└─────────────────────────────────────────────────────────┘
```

---

## Widget Architect - Filled Example

For reference, here's how we filled it for `widget-architect`:

| Field | Value |
|-------|-------|
| **Name** | `widget-architect` |
| **Description** | Expert in CodeRef Dashboard widget architecture, lifecycle management, and system integration |
| **Expertise** | Widget lifecycle management, IIFE bundle system and esbuild, Global namespace management, Core package API integration, ErrorBoundary patterns, Settings propagation, Widget validation and review, Performance optimization |
| **Use Cases** | Review widget implementations for architecture compliance, Guide new widget development from template to deployment, Validate widget error handling and lifecycle hooks, Optimize widget bundle size and load performance, Debug widget integration and script loading issues, Design widget settings and state management, Recommend widget testing patterns and coverage, Analyze widget dependencies and core API usage |
| **Communication Style** | Technical and precise with architecture-focused guidance and concrete examples |
| **Problem-Solving** | Analyze code, trace lifecycle, validate contracts, recommend improvements |
| **Tool Usage** | Read source files, grep for violations, analyze bundles, validate types |
| **Specializations** | IIFE bundle analysis, Lifecycle hook validation, ErrorBoundary integration, Settings propagation patterns, Core API consumption |
| **Key Principles** | Enforce architecture through contracts, Error isolation is non-negotiable, Settings drive re-renders, Analyze bundles for size, Prevent namespace pollution, Lifecycle hooks must complete, Type safety across boundaries, Testing essential for plugins |

---

## Input Format Options

### Arrays Can Be Provided As:

**Option 1: Comma-separated string**
```
expertise: Widget lifecycle management, Bundle systems, Error patterns
```

**Option 2: JSON array**
```
expertise: ["Widget lifecycle management", "Bundle systems", "Error patterns"]
```

Both formats are automatically parsed and converted.

---

## Key Validation Rules

| Field | Required? | Min | Max | Format |
|-------|-----------|-----|-----|--------|
| name | ✅ | 3 | 50 | lowercase alphanumeric, hyphens, underscores |
| description | ✅ | 20 | 200 | plain text |
| expertise | ✅ | 3 items | 10 items | array or CSV |
| use_cases | ✅ | 3 items | 10 items | array or CSV |
| communication_style | ✅ | 20 | 200 | plain text |
| problem_solving | ❌ | — | 200 | plain text |
| tool_usage | ❌ | — | 200 | plain text |
| specializations | ❌ | — | 5 items | array or CSV |
| key_principles | ❌ | — | 10 items | array or CSV |
| example_responses | ❌ | — | 3 pairs | JSON object |

---

## How to Use This Form

1. **Print this form** or display it digitally
2. **Fill in all REQUIRED fields** (marked with ✅)
3. **Optionally fill in** any OPTIONAL fields that apply
4. **Follow the format guidelines** for arrays (comma-separated or JSON)
5. **Validate against the rules table** before submitting
6. **Use the widget-architect example** as a reference for quality

## Next Steps

Once filled out, provide the completed form to create the custom persona using the `mcp__personas-mcp__create_custom_persona` tool.
