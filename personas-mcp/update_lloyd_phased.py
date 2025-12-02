#!/usr/bin/env python3
"""
Update Lloyd persona with comprehensive MCP ecosystem knowledge - PHASED APPROACH
"""

import json
from pathlib import Path

def load_lloyd():
    """Load Lloyd persona JSON"""
    lloyd_path = Path("personas/base/lloyd-expert.json")
    with open(lloyd_path, "r", encoding="utf-8") as f:
        return json.load(f), lloyd_path

def save_lloyd(lloyd, lloyd_path):
    """Save Lloyd persona JSON"""
    with open(lloyd_path, "w", encoding="utf-8") as f:
        json.dump(lloyd, f, indent=2, ensure_ascii=False)
    print(f"[SAVED] Lloyd persona written to {lloyd_path}")

def phase1_add_ecosystem_overview(lloyd):
    """Phase 1: Add ecosystem overview section"""
    print("\n[PHASE 1] Adding ecosystem overview...")

    overview = """

## Deep Understanding: The 3-Server MCP Ecosystem

You have comprehensive knowledge of the user's complete MCP ecosystem. This is CRITICAL context for your coordination work.

### The Big Picture: Connected Intelligence Network

The user has built a **three-layer MCP ecosystem**:

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

This ecosystem enables expert-guided workflows across documentation, planning, and code analysis.
"""

    # Insert after training section
    system_prompt = lloyd["system_prompt"]
    insertion_marker = "\n\n## Your Core Identity"
    insert_pos = system_prompt.find(insertion_marker)

    if insert_pos == -1:
        print("[ERROR] Could not find insertion point")
        return False

    lloyd["system_prompt"] = (
        system_prompt[:insert_pos] +
        overview +
        system_prompt[insert_pos:]
    )

    print("[SUCCESS] Phase 1 complete: Ecosystem overview added")
    return True

# Main execution
if __name__ == "__main__":
    lloyd, lloyd_path = load_lloyd()

    # Phase 1: Add ecosystem overview
    if phase1_add_ecosystem_overview(lloyd):
        save_lloyd(lloyd, lloyd_path)
        print("\n[COMPLETE] Phase 1 done! Lloyd now has ecosystem overview.")
        print(f"   System prompt size: {len(lloyd['system_prompt'])} characters")
        print("\nNext: Run phases 2-7 to add detailed server knowledge")
    else:
        print("\n[FAILED] Phase 1 failed")
