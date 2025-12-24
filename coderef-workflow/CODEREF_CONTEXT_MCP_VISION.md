# coderef-context MCP: Vision & Concrete Scenarios

**What happens when we build this system as described**

---

## Architecture After Implementation

```
┌─────────────────────────────────────────────────────────┐
│  Claude (Agent Implementation Task)                     │
└──────────┬──────────────────────────────────────────────┘
           │
           ├─ coderef-workflow MCP (Planning)
           │  ├─ /gather-context (req requirements)
           │  ├─ /create-plan (generate plan)
           │  └─ /coderef-foundation-docs (understand project)
           │
           └─ coderef-context MCP (Intelligence) ← NEW
              ├─ /scan (discover code elements)
              ├─ /query (real-time relationships)
              ├─ /impact (change analysis)
              ├─ /complexity (function metrics)
              └─ /patterns (test coverage, examples)
                    ↓
              @coderef/core CLI (subprocess)
```

---

## Concrete Scenario 1: Implementing User Auth Feature

### Step 1: Agent Gets Planning Context (Current System)

```
User: "I want to add OAuth authentication to my project"

coderef-workflow MCP returns:
{
  "goal": "Add OAuth authentication",
  "project_context": {
    "api_context": {
      "frameworks": ["Express"],
      "endpoints": 42,
      "auth_method": "JWT (deprecated)"
    },
    "technology_stack": ["Node.js", "TypeScript", "PostgreSQL"],
    "patterns": {
      "handlers": ["handle_auth", "on_login"],
      "services": ["AuthService", "UserService"],
      "error_types": ["AuthError", "ValidationError"]
    }
  },
  "similar_features": [
    {
      "name": "jwt-refresh-tokens",
      "goal": "Added JWT refresh token rotation",
      "workorder": "WO-JWT-001"
    }
  ]
}
```

### Step 2: Agent Scans Project (NEW - coderef-context)

```
Agent: "Let me understand the auth architecture"

Claude calls: /coderef-context/scan
Arguments: {
  "project_path": "/path/to/project",
  "languages": ["ts", "tsx", "js", "jsx"]
}

coderef-context MCP returns:
{
  "elements_found": 247,
  "breakdown": {
    "functions": 156,
    "classes": 52,
    "components": 28,
    "hooks": 11
  },
  "elements": [
    {
      "type": "class",
      "name": "AuthService",
      "file": "src/services/AuthService.ts",
      "line": 15,
      "exported": true,
      "methods": ["login", "logout", "refresh", "validate"]
    },
    {
      "type": "function",
      "name": "authenticate",
      "file": "src/handlers/auth.ts",
      "line": 42,
      "parameters": ["req", "res", "next"]
    },
    // ... 245 more elements
  ]
}

Agent now has: Complete map of project structure
```

### Step 3: Agent Queries Existing Auth (NEW - coderef-context)

```
Agent: "Show me everything related to authentication"

Claude calls: /coderef-context/query
Arguments: {
  "type": "what-imports",
  "target": "AuthService"
}

coderef-context MCP returns:
{
  "query": "what-imports AuthService",
  "results": [
    "src/handlers/auth.ts",
    "src/handlers/api.ts",
    "src/middleware/auth.ts",
    "tests/auth.test.ts"
  ],
  "count": 4
}

Claude calls: /coderef-context/query
Arguments: {
  "type": "what-calls",
  "target": "AuthService#login"
}

coderef-context MCP returns:
{
  "query": "what-calls AuthService#login",
  "results": [
    {
      "caller": "src/handlers/auth.ts#handleLogin",
      "line": 48
    },
    {
      "caller": "src/handlers/api.ts#apiAuth",
      "line": 127
    },
    // ... more callers
  ],
  "count": 6
}

Agent now has: Real-time understanding of current auth usage
```

### Step 4: Agent Analyzes Impact (NEW - coderef-context)

```
Agent: "What happens if I add OAuth alongside JWT?"

Claude calls: /coderef-context/impact
Arguments: {
  "project_path": "/path/to/project",
  "element": "AuthService",
  "operation": "modify"
}

coderef-context MCP returns:
{
  "element": "AuthService",
  "direct_dependents": 6,
  "indirect_dependents": 24,
  "affected_modules": [
    "handlers/auth",
    "middleware/auth",
    "routes/api",
    "tests/auth.test.ts"
  ],
  "risk_level": "HIGH",
  "recommendations": [
    "Update 6 direct callers",
    "Review 24 indirect dependencies",
    "Add backward compatibility for JWT",
    "Update tests (currently 73% coverage)"
  ]
}

Agent now has: Impact analysis before coding
```

### Step 5: Agent Checks Complexity (NEW - coderef-context)

```
Agent: "How complex is the AuthService?"

Claude calls: /coderef-context/complexity
Arguments: {
  "element": "AuthService",
  "file": "src/services/AuthService.ts"
}

coderef-context MCP returns:
{
  "element": "AuthService",
  "metrics": {
    "lines_of_code": 342,
    "cyclomatic_complexity": 8,
    "methods_count": 4,
    "dependencies": 5,
    "dependents": 24,
    "test_coverage": 73
  },
  "risk_level": "MEDIUM",
  "assessment": "Large service, good coverage, moderate complexity"
}

Agent now has: Complexity baseline
```

### Step 6: Agent Finds Similar Patterns (NEW - coderef-context)

```
Agent: "How did we implement the JWT auth? Show similar patterns"

Claude calls: /coderef-context/patterns
Arguments: {
  "type": "authentication",
  "limit": 5
}

coderef-context MCP returns:
{
  "patterns": [
    {
      "name": "JWT Strategy",
      "file": "src/services/AuthService.ts",
      "lines": "120-160",
      "description": "JWT token generation and validation",
      "usage_count": 6
    },
    {
      "name": "Session Middleware",
      "file": "src/middleware/auth.ts",
      "lines": "15-45",
      "description": "Express middleware for auth",
      "usage_count": 12
    }
  ],
  "test_coverage": {
    "auth_tests": "src/tests/auth.test.ts",
    "coverage_percentage": 73,
    "gaps": [
      "OAuth provider error handling",
      "Token refresh edge cases",
      "Multi-device logout"
    ]
  }
}

Agent now has: Proven patterns to follow
```

### Step 7: Agent Implements with Intelligence

```
Agent: "Based on all this analysis, here's my plan:

1. Extend AuthService with OAuth methods alongside JWT
   - Keep JWT for backward compatibility (24 dependents)
   - Add oauthLogin, oauthCallback methods
   - Risk: MEDIUM (already assessed)

2. Update middleware to detect auth type
   - Existing 12 usages of middleware
   - Non-breaking change pattern

3. Tests needed:
   - OAuth flow (new)
   - JWT + OAuth coexistence (edge case)
   - Backward compatibility (critical)
   - Current gap: 27% uncovered paths

4. Implementation order:
   - AuthService changes first (24 dependents waiting)
   - Middleware next (12 usages)
   - Handlers last (6 direct callers)
   - Tests after each phase"
```

**Result**: Agent makes informed decisions. Implementation is better planned.

---

## Concrete Scenario 2: Refactoring Decision

```
Agent: "I found a bug in SessionManager. Can I refactor it?"

Claude calls: /coderef-context/impact
Arguments: {
  "element": "SessionManager",
  "operation": "refactor"
}

Returns:
{
  "element": "SessionManager",
  "dependents": 47,
  "risk_level": "CRITICAL",
  "affected_files": [
    "src/handlers/auth.ts",
    "src/handlers/session.ts",
    "src/middleware/session.ts",
    "src/services/UserService.ts",
    "src/routes/api.ts",
    "tests/session.test.ts",
    // ... 41 more files
  ]
}

Agent: "This touches 47 functions. Instead of refactoring:
1. I'll add a wrapper function around SessionManager
2. New OAuth code uses wrapper (safe)
3. Gradual migration path for existing code
4. Risk: LOW (backward compatible)"

Then: /coderef-context/query
Arguments: {
  "type": "shortest-path",
  "source": "oauthLogin",
  "target": "SessionManager"
}

Returns: Dependency chain showing exactly where to inject.
```

---

## Concrete Scenario 3: Risk Assessment During Review

```
Agent: "Let me review the OAuth implementation for risks"

Claude calls: /coderef-context/query
Arguments: {
  "type": "what-calls",
  "target": "oauthCallback"
}

Returns: 3 callers found

For each caller, Agent calls: /coderef-context/impact
Arguments: {
  "element": "oauthCallback",
  "from": "specific_caller"
}

Agent generates: "Risk assessment:
✅ Direct callers (3) - reviewed
✅ Indirect dependents (12) - analyzed
✅ Test coverage (85% for OAuth paths)
⚠️  Error handling in session edge case
⚠️  Token expiration not tested in concurrent requests"
```

---

## What Changes for the User

### Before (Current)

```
User: "Implement OAuth"
  ↓
Claude gets planning doc (static)
  ↓
Claude implements somewhat blindly
  ↓
Risk of missing dependencies/implications
```

### After (With coderef-context)

```
User: "Implement OAuth"
  ↓
Claude gets planning doc (static)
  ↓
Claude scans project (/scan)
  ↓
Claude queries existing auth (/query)
  ↓
Claude analyzes impact (/impact)
  ↓
Claude checks complexity (/complexity)
  ↓
Claude finds patterns (/patterns)
  ↓
Claude implements with full intelligence
  ↓
Risk is minimized (all implications understood)
```

---

## System Capabilities Gained

| Capability | Before | After |
|-----------|--------|-------|
| **Understand codebase structure** | Static doc | Real-time scan |
| **Know what calls what** | Guessing | Precise query |
| **Analyze change impact** | No capability | Full analysis |
| **Assess function complexity** | Rough estimation | Metric-based |
| **Find similar patterns** | Manual search | Automated discovery |
| **Detect edge cases** | No capability | Pattern-based detection |
| **Validate decisions** | No way | Query-based validation |

---

## File Structure After Implementation

```
C:\Users\willh\.mcp-servers\

├── coderef-workflow/
│   ├── server.py
│   ├── generators/
│   ├── CODEREF_INTEGRATION_GUIDE.md
│   ├── CODEREF_CONTEXT_MCP_VISION.md  ← This file
│   └── ...
│
└── coderef-context/                    ← NEW SERVER
    ├── server.py                       ← MCP entry point
    ├── tool_handlers.py                ← Tool implementations
    ├── constants.py
    ├── logger_config.py
    ├── cli_wrapper.py                  ← Wraps @coderef/core subprocess calls
    ├── pyproject.toml
    ├── package.json
    ├── README.md                       ← Usage guide
    ├── TOOLS_REFERENCE.md              ← Tool specs
    └── examples/                       ← Usage examples
        ├── scan_example.py
        ├── query_example.py
        └── impact_example.py
```

---

## MCP Tools Specification

### Tool 1: /coderef-scan
```python
def scan(
    project_path: str,
    languages: List[str] = ['ts', 'tsx', 'js', 'jsx'],
    exclude_dirs: List[str] = ['node_modules', 'dist']
) -> Dict[str, Any]:
    """
    Scan project and return all code elements.

    Returns:
      {
        "elements_found": int,
        "breakdown": {"functions": int, "classes": int, ...},
        "elements": List[ElementData]
      }
    """
```

### Tool 2: /coderef-query
```python
def query(
    project_path: str,
    query_type: Literal['what-calls', 'what-calls-me', 'shortest-path', ...],
    target: str,
    source: str = None,
    max_depth: int = 10
) -> Dict[str, Any]:
    """
    Execute relationship query on project.

    Returns:
      {
        "query": str,
        "results": List[Dict],
        "count": int
      }
    """
```

### Tool 3: /coderef-impact
```python
def impact(
    project_path: str,
    element: str,
    operation: Literal['modify', 'delete', 'refactor'] = 'modify'
) -> Dict[str, Any]:
    """
    Analyze impact of changing/deleting element.

    Returns:
      {
        "element": str,
        "direct_dependents": int,
        "indirect_dependents": int,
        "affected_modules": List[str],
        "risk_level": Literal['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        "recommendations": List[str]
      }
    """
```

### Tool 4: /coderef-complexity
```python
def complexity(
    project_path: str,
    element: str,
    file: str = None
) -> Dict[str, Any]:
    """
    Get complexity metrics for code element.

    Returns:
      {
        "element": str,
        "metrics": {
          "lines_of_code": int,
          "cyclomatic_complexity": int,
          "methods_count": int,
          "dependencies": int,
          "dependents": int,
          "test_coverage": float
        },
        "risk_level": str,
        "assessment": str
      }
    """
```

### Tool 5: /coderef-patterns
```python
def patterns(
    project_path: str,
    pattern_type: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find code patterns and examples.

    Returns:
      {
        "patterns": List[Dict],
        "test_coverage": Dict,
        "recommendations": List[str]
      }
    """
```

---

## Development Roadmap for coderef-context

### Week 1: Foundation (MVP)
- [ ] Set up MCP server structure
- [ ] Wrap /coderef-scan command
- [ ] Wrap /coderef-query command
- [ ] Wrap /coderef-impact command
- [ ] Basic error handling

### Week 2: Enhancement
- [ ] Add /coderef-complexity tool
- [ ] Add /coderef-patterns tool
- [ ] Add caching layer (avoid re-scans)
- [ ] Comprehensive logging

### Week 3: Integration & Polish
- [ ] Integration tests
- [ ] Documentation
- [ ] Example usage scripts
- [ ] Register in .mcp.json

---

## How Agents Use It (Real Example)

```python
# What the agent sees in Claude Code:

Available Tools:
├─ coderef-workflow MCP
│  └─ /coderef-foundation-docs
├─ coderef-context MCP          ← NEW
│  ├─ /scan
│  ├─ /query
│  ├─ /impact
│  ├─ /complexity
│  └─ /patterns

# During task execution:

Agent thinking: "I need to implement feature X. Let me gather intelligence."

# Calls tool
→ Use tool: coderef-context /scan project_path="/path/to/project"
← Get: 247 code elements with structure

Agent thinking: "What's already there for feature X?"

# Calls tool
→ Use tool: coderef-context /query
  type="what-imports" target="FeatureX"
← Get: 12 existing imports of FeatureX

Agent thinking: "What if I modify FeatureX?"

# Calls tool
→ Use tool: coderef-context /impact
  element="FeatureX" operation="modify"
← Get: 47 indirect dependents, CRITICAL risk

Agent thinking: "OK, need careful approach. Show me the pattern..."

# Calls tool
→ Use tool: coderef-context /patterns
  pattern_type="feature_extension"
← Get: Similar patterns from project history

Agent: "I understand. Here's my plan: [informed decision based on intelligence]"
```

---

## The Key Difference This Makes

**Without coderef-context**:
- Agent implements based on planning doc alone
- Misses dependencies, implications, risks
- Quality: 60-70%

**With coderef-context**:
- Agent analyzes live project state before implementing
- Understands impact, dependencies, patterns
- Makes informed tradeoff decisions
- Quality: 85-95%

---

## Summary: What Happens

1. **Architecture becomes cleaner**
   - coderef-workflow = Planning & documentation
   - coderef-context = Code intelligence & queries
   - Separation of concerns

2. **Agents become smarter**
   - Real-time project understanding
   - Impact analysis before coding
   - Risk assessment built-in

3. **Implementation quality improves**
   - Better decisions = better code
   - Fewer surprises/dependencies missed
   - More robust refactoring

4. **Development cost is low**
   - ~1 week of work
   - Wrapping existing CLI (no new analysis)
   - High ROI

5. **System grows intelligently**
   - Can add more tools as needed
   - CLI is independent from Python
   - Easy to iterate

---

**This is the next logical evolution of the system.**
