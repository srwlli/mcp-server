# Components Reference

**Project:** coderef-personas
**Framework:** Python MCP Server (no UI components)
**Version:** 1.5.0
**Date:** 2025-12-30
**Status:**  Production

---

## Purpose

This document inventories the modular software components in the coderef-personas MCP server. Since this is a backend MCP server (not a UI project), "components" refer to Python modules, classes, and generators that provide reusable functionality.

---

## Overview

The coderef-personas project is organized into **6 primary component categories**:

1. **Core Server** - MCP server implementation (`server.py`)
2. **Data Models** - Pydantic schemas (`src/models.py`)
3. **Persona Management** - Persona loading and activation (`src/persona_manager.py`)
4. **Lloyd Integration** - Todo generation and plan tracking (`src/generators/`, `src/trackers/`, `src/executors/`)
5. **Custom Persona Creation** - Validation and generation (`src/validators.py`, `src/persona_generator.py`)
6. **MCP Tool Handlers** - Tool implementations (`server.py` async handlers)

All components follow Python best practices with type hints, docstrings, and Pydantic validation.

---

## What You'll Find Here

### Component Categories

- **Core Components** - Server, state management, persona loading
- **Data Components** - Pydantic models for personas, tasks, todos
- **Generator Components** - Todo list generation, plan execution
- **Validator Components** - Multi-stage persona validation
- **Handler Components** - MCP tool request handlers

### Usage Patterns

- Import patterns for each component
- Initialization examples
- Common use cases

### State Management

- PersonaState (runtime persona tracking)
- Stateless vs stateful components

---

## Core Components

### 1. MCP Server (`server.py`)

**Purpose:** Main MCP server implementation using `mcp.server` Python SDK.

**Location:** `server.py:1-792`

**Key Responsibilities:**
- Tool registration (`list_tools()`)
- Tool invocation (`call_tool()`)
- Stdio communication with MCP clients

**Usage:**

```python
# Start the server
python -m coderef-personas.server

# Or via MCP configuration
# ~/.mcp.json includes server configuration
```

**Dependencies:**
- `mcp.server` - MCP Python SDK
- `mcp.types` - Tool and TextContent types
- `src.persona_manager` - Persona loading
- `src.models` - Data models

**Tool Handlers:**
- `handle_use_persona()`
- `handle_get_active_persona()`
- `handle_clear_persona()`
- `handle_list_personas()`
- `handle_generate_todo_list()`
- `handle_track_plan_execution()`
- `handle_execute_plan_interactive()`
- `handle_create_custom_persona()`

---

### 2. PersonaManager (`src/persona_manager.py`)

**Purpose:** Manages persona loading, activation, and state tracking.

**Location:** `src/persona_manager.py`

**Key Responsibilities:**
- Load personas from JSON files
- Activate/deactivate personas
- Track active persona state
- Scan `personas/` directories (base/, custom/, coderef-personas/)

**Usage:**

```python
from pathlib import Path
from src.persona_manager import PersonaManager

# Initialize
personas_dir = Path("personas")
manager = PersonaManager(personas_dir)

# List available personas
personas = manager.list_available_personas()
# Returns: ['lloyd', 'ava', 'marcus', 'quinn', 'taylor', ...]

# Activate a persona
persona = manager.activate_persona("lloyd")
# Returns: PersonaDefinition with full system prompt

# Get active persona
active = manager.get_active_persona()
# Returns: PersonaDefinition or None

# Clear persona
manager.clear_persona()
```

**State Management:**

Uses `PersonaState` to track active persona:

```python
class PersonaState(BaseModel):
    active_persona: Optional[PersonaDefinition] = None
    activated_at: Optional[datetime] = None
```

---

## Data Components

### 3. Pydantic Models (`src/models.py`)

**Purpose:** Type-safe data models with validation.

**Location:** `src/models.py:1-144`

**Models:**

```python
# Core persona models
PersonaDefinition      # Complete persona spec
PersonaBehavior        # Communication/problem-solving patterns
PersonaState           # Runtime state

# Custom persona creation
CustomPersonaInput     # User input for create_custom_persona

# Lloyd integration
TaskExecutionStatus    # Task status tracking
TaskProgress           # Plan-level progress stats
TodoMetadata           # Todo-to-workorder traceability
```

**Usage:**

```python
from src.models import PersonaDefinition, PersonaBehavior

# Create persona programmatically
persona = PersonaDefinition(
    name="test-persona",
    version="1.0.0",
    parent=None,
    description="Test persona for examples",
    system_prompt="You are a test persona...",
    expertise=["Testing", "Examples", "Documentation"],
    use_cases=["Test cases", "Example code", "Documentation"],
    behavior=PersonaBehavior(
        communication_style="Clear and concise",
        problem_solving="Example-driven",
        tool_usage="Minimal",
        guidance_pattern=None
    ),
    created_at="2025-12-30T00:00:00Z",
    updated_at="2025-12-30T00:00:00Z"
)

# Validate and serialize
persona_json = persona.model_dump_json(indent=2)
```

---

## Generator Components

### 4. TodoListGenerator (`src/generators/todo_list_generator.py`)

**Purpose:** Convert plan.json task breakdown to TodoWrite format.

**Location:** `src/generators/todo_list_generator.py`

**Key Method:**

```python
def generate_todo_list(
    plan_path: str,
    workorder_id: str,
    mode: str = "all"
) -> dict:
    """
    Generate TodoWrite-compatible task list from plan.json.

    Args:
        plan_path: Path to plan.json file
        workorder_id: Workorder ID (e.g., "WO-AUTH-001")
        mode: "all" or "remaining" (incomplete tasks only)

    Returns:
        {
            "workorder_id": "WO-AUTH-001",
            "total_tasks": 12,
            "mode": "all",
            "todos": [
                {
                    "content": "WO-AUTH-001 | SETUP-001: Initialize project",
                    "status": "pending",
                    "activeForm": "Initializing project"
                },
                ...
            ],
            "generated_at": "2025-12-30T14:23:15",
            "summary": "Generated 12 todos from plan.json (all tasks)"
        }
    """
```

**Usage:**

```python
from src.generators.todo_list_generator import TodoListGenerator

generator = TodoListGenerator()
result = generator.generate_todo_list(
    plan_path="coderef/workorder/auth-system/plan.json",
    workorder_id="WO-AUTH-SYSTEM-001",
    mode="all"
)

# Pass to TodoWrite tool
todos = result["todos"]
```

---

### 5. PlanExecutionTracker (`src/trackers/plan_execution_tracker.py`)

**Purpose:** Sync plan.json progress with TodoWrite status.

**Location:** `src/trackers/plan_execution_tracker.py`

**Key Method:**

```python
def track_plan_execution(
    plan_path: str,
    workorder_id: str,
    todo_status: list
) -> dict:
    """
    Update plan.json with current todo status.

    Args:
        plan_path: Path to plan.json file
        workorder_id: Workorder ID
        todo_status: Array of todo objects with current status

    Returns:
        {
            "workorder_id": "WO-AUTH-001",
            "plan_status": {
                "total_tasks": 12,
                "completed": 8,
                "in_progress": 2,
                "pending": 2,
                "progress_percent": 66.7
            },
            "task_details": [...],
            "synced_at": "2025-12-30T14:25:30",
            "updated_plan_path": "path/to/plan.json",
            "summary": "Plan synced successfully with 12 tasks tracked"
        }
    """
```

---

### 6. InteractivePlanExecutor (`src/executors/interactive_plan_executor.py`)

**Purpose:** Execute plan with step-by-step or batch mode guidance.

**Location:** `src/executors/interactive_plan_executor.py`

**Key Method:**

```python
def execute_plan_interactive(
    plan_path: str,
    workorder_id: str,
    mode: str = "step-by-step"
) -> dict:
    """
    Execute plan with guided execution.

    Args:
        plan_path: Path to plan.json file
        workorder_id: Workorder ID
        mode: "step-by-step" or "batch"

    Returns:
        # step-by-step mode
        {
            "workorder_id": "WO-AUTH-001",
            "current_task": {
                "task_number": 3,
                "description": "Implement auth middleware",
                "files": ["src/middleware/auth.ts"],
                "acceptance_criteria": [...]
            },
            "guidance": {
                "what_to_do": "Create middleware...",
                "how_to_do_it": "1. Import...",
                "acceptance_test": "JWT validation works",
                "dependencies_met": true
            },
            "progress": {
                "current": 3,
                "total_tasks": 12,
                "completed": 2,
                "percent": 16.7
            },
            "actions": {
                "mark_complete": "Update todo status to 'completed'",
                "get_next": "Call execute_plan_interactive again"
            },
            "summary": "Task 3 ready for execution"
        }

        # batch mode
        {
            "workorder_id": "WO-AUTH-001",
            "total_tasks": 12,
            "todos": [...],
            "instructions": {
                "what_to_do": "Execute all tasks autonomously",
                "how_to_track": "Update todo status as each completes",
                "completion": "Call track_plan_execution when finished"
            },
            "summary": "Batch mode activated with 12 todos"
        }
    """
```

---

## Validator Components

### 7. PersonaValidator (`src/validators.py`)

**Purpose:** Multi-stage validation for custom persona creation.

**Location:** `src/validators.py`

**Key Method:**

```python
def validate_all(persona_data: dict) -> tuple[bool, dict]:
    """
    Run all validation stages on persona input.

    Stages:
    1. Schema validation (field types, patterns, lengths)
    2. Semantic validation (uniqueness, meaningful content)
    3. Quality validation (best practices, recommendations)

    Args:
        persona_data: Dictionary with persona fields

    Returns:
        (passed: bool, results: dict)

        results = {
            "schema": ValidationResult(errors=[], warnings=[]),
            "semantic": ValidationResult(errors=[], warnings=[]),
            "quality": ValidationResult(errors=[], warnings=[])
        }
    """
```

**Usage:**

```python
from src.validators import PersonaValidator

validator = PersonaValidator()
passed, results = validator.validate_all({
    "name": "api-expert",
    "description": "REST API design specialist",
    "expertise": ["REST", "OpenAPI", "Security"],
    "use_cases": ["Design endpoints", "Review APIs"],
    "communication_style": "Technical and example-driven"
})

if not passed:
    # Collect errors
    errors = []
    for stage, result in results.items():
        errors.extend(result.errors)
    print(f"Validation failed: {errors}")
```

---

### 8. PersonaGenerator (`src/persona_generator.py`)

**Purpose:** Generate PersonaDefinition from CustomPersonaInput.

**Location:** `src/persona_generator.py`

**Key Methods:**

```python
def generate_persona_definition(
    persona_input: CustomPersonaInput
) -> PersonaDefinition:
    """
    Generate complete PersonaDefinition with system prompt.

    Uses template-based system prompt generation with:
    - {{name}}, {{description}} placeholders
    - {{expertise}}, {{use_cases}} lists
    - {{communication_style}}, {{problem_solving}}, {{tool_usage}}
    - Conditional sections for specializations, key_principles

    Returns:
        PersonaDefinition ready for JSON serialization
    """

def save_persona(persona_def: PersonaDefinition) -> str:
    """
    Save PersonaDefinition to personas/custom/{name}.json.

    Returns:
        Saved file path
    """
```

**Usage:**

```python
from src.models import CustomPersonaInput
from src.persona_generator import PersonaGenerator

# Create input
persona_input = CustomPersonaInput(
    name="api-expert",
    description="REST API design specialist",
    expertise=["REST", "OpenAPI", "Security"],
    use_cases=["Design endpoints", "Review APIs"],
    communication_style="Technical and example-driven"
)

# Generate and save
generator = PersonaGenerator()
persona_def = generator.generate_persona_definition(persona_input)
saved_path = generator.save_persona(persona_def)
# Returns: "personas/custom/api-expert.json"
```

---

## State Management Patterns

### Stateless Components

Most components are **stateless** (no persistent state between calls):

- TodoListGenerator
- PlanExecutionTracker
- InteractivePlanExecutor
- PersonaValidator
- PersonaGenerator

**Usage:**
```python
# Create new instance per operation
generator = TodoListGenerator()
result = generator.generate_todo_list(...)
```

---

### Stateful Components

**PersonaManager** maintains runtime state:

```python
class PersonaManager:
    def __init__(self, personas_dir: Path):
        self.personas_dir = personas_dir
        self.state = PersonaState()  # Runtime state

    def activate_persona(self, name: str) -> PersonaDefinition:
        persona = self.load_persona(name)
        self.state.active_persona = persona  # Update state
        self.state.activated_at = datetime.now()
        return persona
```

**State Persistence:**
- State is **session-scoped** (cleared on server restart)
- No database or file persistence
- Active persona tracked in memory only

---

## Copy-Paste Examples

### Example 1: Load and Activate a Persona

```python
from pathlib import Path
from src.persona_manager import PersonaManager

# Initialize manager
personas_dir = Path("personas")
manager = PersonaManager(personas_dir)

# Activate Lloyd persona
lloyd = manager.activate_persona("lloyd")

# Access persona details
print(f"Activated: {lloyd.name} v{lloyd.version}")
print(f"Expertise: {', '.join(lloyd.expertise[:3])}")
print(f"System Prompt Preview: {lloyd.system_prompt[:200]}...")
```

---

### Example 2: Generate TodoWrite List from Plan

```python
from src.generators.todo_list_generator import TodoListGenerator

generator = TodoListGenerator()
result = generator.generate_todo_list(
    plan_path="coderef/workorder/auth-system/plan.json",
    workorder_id="WO-AUTH-SYSTEM-001",
    mode="all"
)

# Extract todos for TodoWrite
todos = result["todos"]
print(f"Generated {len(todos)} todos")

# First todo
print(f"First task: {todos[0]['content']}")
```

---

### Example 3: Create Custom Persona Programmatically

```python
from src.models import CustomPersonaInput
from src.validators import PersonaValidator
from src.persona_generator import PersonaGenerator

# Define persona
persona_input = CustomPersonaInput(
    name="devops-expert",
    description="DevOps specialist focusing on CI/CD and infrastructure automation",
    expertise=[
        "Docker containerization",
        "Kubernetes orchestration",
        "GitHub Actions CI/CD",
        "Terraform infrastructure as code",
        "AWS cloud services"
    ],
    use_cases=[
        "Setting up CI/CD pipelines",
        "Containerizing applications",
        "Managing Kubernetes deployments",
        "Implementing infrastructure as code"
    ],
    communication_style="Practical and automation-focused, references DevOps best practices"
)

# Validate
validator = PersonaValidator()
passed, results = validator.validate_all(persona_input.model_dump())

if not passed:
    print("Validation failed!")
    for stage, result in results.items():
        if result.errors:
            print(f"[{stage}] {result.errors}")
else:
    # Generate and save
    generator = PersonaGenerator()
    persona_def = generator.generate_persona_definition(persona_input)
    saved_path = generator.save_persona(persona_def)

    print(f" Persona created: {saved_path}")
    print(f"Name: {persona_def.name}")
    print(f"Version: {persona_def.version}")
```

---

## Additional Resources

- **[API.md](API.md)** - MCP tool schemas and endpoints
- **[SCHEMA.md](SCHEMA.md)** - Pydantic data models and validation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design patterns
- **[README.md](../README.md)** - User-facing documentation
- **[CLAUDE.md](../CLAUDE.md)** - AI context and implementation guide

---

## Footer

**Last Updated:** 2025-12-30
**Document Version:** 1.0.0
**Framework:** Python MCP Server
**Maintained By:** willh, Claude Code AI

**AI Usage Note:** This project has no UI components. "Components" refer to modular Python classes and generators. All components use type hints and Pydantic validation for type safety. Import components directly from `src.*` modules.

**Testing:** Components are designed for unit testing. Each component is stateless (except PersonaManager) and can be tested independently with mock inputs.
