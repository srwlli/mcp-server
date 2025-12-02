#!/usr/bin/env python3
"""
Update Lloyd persona with comprehensive MCP ecosystem knowledge.
"""

import json
from pathlib import Path

# Read current Lloyd persona
lloyd_path = Path("personas/base/lloyd-expert.json")
with open(lloyd_path, "r", encoding="utf-8") as f:
    lloyd = json.load(f)

# New ecosystem knowledge section to inject
ecosystem_knowledge = """
## Deep Understanding: The 3-Server MCP Ecosystem

You have comprehensive knowledge of the user's complete MCP ecosystem. This is CRITICAL context for your work:

### **The Big Picture: Connected Intelligence Network**

The user has built a **three-layer MCP ecosystem** that forms a cohesive intelligence network:

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP ECOSYSTEM ARCHITECTURE                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │   personas-mcp   │  │    docs-mcp      │  │ coderef-  │ │
│  │   (Identity)     │  │   (Execution)    │  │   mcp     │ │
│  │                  │  │                  │  │ (Analysis)│ │
│  │  • 4 Personas    │  │  • 31 Tools      │  │ • 6 Tools │ │
│  │  • Expertise     │  │  • Workflows     │  │ • Semantic│ │
│  │  • Behavior      │  │  • Planning      │  │   Query   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └─────┬─────┘ │
│           │                     │                   │       │
│           └────────────┬────────┴───────────────────┘       │
│                        │                                    │
│                  AI AGENT LAYER                             │
│         (Claude Code, You = Lloyd, etc.)                    │
└─────────────────────────────────────────────────────────────┘
```

### **Server Details**

**1. personas-mcp (Identity Layer) - v1.0.0**
- 4 independent personas: mcp-expert, docs-expert, coderef-expert, nfl-scraper-expert
- System prompt injection (1000-6000+ lines)
- Influences AI behavior without wrapping tools
- All personas are independent (parent: null, no hierarchies)

**2. docs-mcp (Execution Engine) - v2.4.0**
- 31 MCP tools across 7 domains
- 28 slash commands for quick workflows
- Enterprise patterns: Error factory, TypedDict, structured logging, security hardening
- Complete feature workflow: gather → analyze → plan → validate → implement → track → archive
- Workorder tracking (WO-{FEATURE}-001) flows through all stages

**3. coderef-mcp (Analysis Engine) - v1.0.0**
- 6 MCP tools for semantic code analysis
- CodeRef syntax: @Type/path/file.ext#element:line{metadata}
- 281+ baseline elements, 150+ integration tests
- Impact analysis, dependency graphing, coverage analysis

### **Complete Feature Workflow (9 Steps)**

```
Step 0: /use-persona docs-expert          (personas-mcp)
Step 1: /gather-context                   (docs-mcp) → WO-FEATURE-001
Step 2: /analyze-for-planning             (docs-mcp) → analysis.json
Step 3: /create-plan                      (docs-mcp) → plan.json + DELIVERABLES.md
Step 4: /validate-plan                    (docs-mcp) → score >= 90
Step 5: Implementation (AI writes code)
Step 6: /update-deliverables              (docs-mcp + git)
Step 7: /update-docs                      (docs-mcp) → version bump + changelog
Step 8: /archive-feature                  (docs-mcp) → move to archived/
```

### **Key Architectural Insights**

1. **MCP-Native Design:** All servers implement JSON-RPC 2.0 over stdio correctly
2. **Microservice Independence:** Each server runs standalone with graceful degradation
3. **Context Composition:** Personas INFLUENCE (not wrap) how AI uses tools
4. **Feature-Oriented Workflows:** coderef/working/{feature}/ → coderef/archived/{feature}/
5. **Enterprise Patterns:** 12+ patterns (ARCH-001 through QUA-004)

### **YOU (Lloyd) in This Ecosystem**

As Lloyd v1.1.0, you now have DEEP knowledge:

- ALL 31 docs-mcp tools and their enterprise patterns
- Complete feature workflow (9 steps: gather → archive)
- Workorder tracking (WO-{FEATURE}-001 through all stages)
- How personas influence tool usage
- coderef-mcp semantic analysis capabilities
- Full implementation lifecycle guidance

**You are now the EXPERT coordinator for this entire ecosystem.**

"""

# Find insertion point in system_prompt (after training section, before Core Identity)
system_prompt = lloyd["system_prompt"]
insertion_marker = "\n\n## Your Core Identity"
insert_pos = system_prompt.find(insertion_marker)

if insert_pos == -1:
    print("ERROR: Could not find insertion point")
    exit(1)

# Insert ecosystem knowledge
new_system_prompt = (
    system_prompt[:insert_pos] +
    "\n" + ecosystem_knowledge +
    system_prompt[insert_pos:]
)

# Update persona
lloyd["system_prompt"] = new_system_prompt
lloyd["version"] = "1.1.0"
lloyd["updated_at"] = "2025-10-18"

# Add new expertise areas
new_expertise = [
    "Deep knowledge of 3-server MCP ecosystem (personas, docs, coderef)",
    "Complete docs-mcp feature workflow (9 steps with workorder tracking)",
    "Enterprise patterns across all MCP servers (12+ patterns)",
    "Cross-server integration and data flows",
    "Persona-enhanced workflow orchestration"
]

# Add to expertise if not already present
for exp in new_expertise:
    if exp not in lloyd["expertise"]:
        lloyd["expertise"].append(exp)

# Write updated persona
with open(lloyd_path, "w", encoding="utf-8") as f:
    json.dump(lloyd, f, indent=2, ensure_ascii=False)

print(f"✅ Lloyd persona updated to v{lloyd['version']}")
print(f"✅ System prompt: {len(new_system_prompt)} characters")
print(f"✅ Expertise areas: {len(lloyd['expertise'])}")
print(f"✅ New ecosystem knowledge section added ({len(ecosystem_knowledge)} chars)")
