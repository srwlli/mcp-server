"""
Pydantic models for persona definitions and state management.

Updated in v2.0 Phase 1 to support Lloyd Integration:
- TaskExecutionStatus: Track task completion status
- TaskProgress: Track overall plan progress
- TodoMetadata: Metadata for todo integration
"""

from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json


class PersonaBehavior(BaseModel):
    """Defines how a persona communicates and solves problems."""
    communication_style: str
    problem_solving: str
    tool_usage: str
    guidance_pattern: Optional[str] = None


class PersonaDefinition(BaseModel):
    """Schema for persona JSON files."""
    name: str
    version: str
    parent: Optional[str] = None
    description: str
    system_prompt: str
    expertise: List[str]
    use_cases: List[str]
    behavior: PersonaBehavior
    specializations: Optional[List[str]] = None
    example_responses: Optional[Dict[str, str]] = None
    key_principles: Optional[List[str]] = None
    created_at: str
    updated_at: str


class PersonaState(BaseModel):
    """Tracks currently active persona."""
    active_persona: Optional[PersonaDefinition] = None
    activated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if any persona is currently active."""
        return self.active_persona is not None

    def get_name(self) -> Optional[str]:
        """Get the name of the active persona."""
        return self.active_persona.name if self.active_persona else None

    def clear(self):
        """Reset to no active persona."""
        self.active_persona = None
        self.activated_at = None


# ===== v2.0 Phase 1: Lloyd Integration Schemas =====


class TaskExecutionStatus(BaseModel):
    """
    Execution status for a single task.

    Added in v2.0 Phase 1 for real-time progress tracking.
    """
    status: Literal["pending", "in_progress", "completed"]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: Optional[str] = None


class TaskProgress(BaseModel):
    """
    Overall progress statistics for a plan.

    Added in v2.0 Phase 1 for plan-wide progress tracking.
    """
    total_tasks: int
    completed: int
    in_progress: int
    pending: int
    progress_percent: float


class TodoMetadata(BaseModel):
    """
    Metadata embedded in todos for workorder traceability.

    Added in v2.0 Phase 1 for Lloyd integration.
    """
    workorder_id: str
    task_id: int
    plan_section: str = "implementation"
    acceptance_criteria: List[str] = []
    files: List[str] = []
    estimated_time: Optional[str] = None
    dependencies: List[int] = []


# ===== Custom Persona Creation (WO-CREATE-CUSTOM-PERSONA-001) =====


class CustomPersonaInput(BaseModel):
    """
    Input schema for creating custom personas via create_custom_persona tool.

    Users provide high-level inputs (expertise, communication style, use cases)
    and the system generates a complete PersonaDefinition with system prompt.

    Added in custom persona feature (WO-CREATE-CUSTOM-PERSONA-001).
    Updated to handle MCP array parameter serialization (accepts strings or arrays).
    """
    name: str = Field(..., description="Unique persona name (alphanumeric, hyphens, underscores only)", pattern=r"^[a-z0-9_-]+$", min_length=3, max_length=50)
    description: str = Field(..., description="One-sentence description of persona's role and expertise", min_length=20, max_length=200)
    expertise: Union[str, List[str]] = Field(..., description="List of expertise areas (3-10 items) as array or comma-separated string")
    use_cases: Union[str, List[str]] = Field(..., description="List of use cases (3-10 items) as array or comma-separated string")
    communication_style: str = Field(..., description="How this persona communicates (e.g., 'Professional, technical, references specific tools')", min_length=20, max_length=200)
    problem_solving: Optional[str] = Field(None, description="Problem-solving approach (e.g., 'Uses docs-mcp workflows, follows existing patterns')", max_length=200)
    tool_usage: Optional[str] = Field(None, description="How persona uses tools (e.g., 'Leverages docs-mcp tools effectively')", max_length=200)
    specializations: Optional[Union[str, List[str]]] = Field(None, description="Optional specialized sub-areas (max 5) as array or comma-separated string")
    key_principles: Optional[Union[str, List[str]]] = Field(None, description="Optional guiding principles (max 10) as array or comma-separated string")
    example_responses: Optional[Dict[str, str]] = Field(None, description="Optional example question-answer pairs (max 3)")

    @field_validator('expertise', 'use_cases', 'specializations', 'key_principles', mode='before')
    @classmethod
    def parse_string_arrays(cls, v):
        """Convert string arrays to List[str] for MCP parameter compatibility."""
        if isinstance(v, str):
            # Try JSON array first
            if v.strip().startswith('['):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Try comma-separated
            if ',' in v:
                return [item.strip() for item in v.split(',') if item.strip()]
            # Single item
            return [v.strip()] if v.strip() else []
        return v
