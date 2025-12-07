"""
Context Expert data models.

TypedDict definitions for the context expert system (v3.0.0).
These models define the structure for context experts that maintain
deep knowledge about specific files or directories in a codebase.
"""

from typing import TypedDict, Optional, List, Dict, Any


class GitHistoryEntry(TypedDict):
    """Git commit affecting a resource."""
    commit_hash: str
    author: str
    date: str  # ISO 8601 timestamp
    message: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int


class CodeStructure(TypedDict):
    """Code structure analysis for a resource."""
    functions: List[str]       # Function/method names
    classes: List[str]         # Class names
    imports: List[str]         # Import statements
    exports: List[str]         # Exported symbols
    line_count: int
    complexity_score: float    # 0-100 estimated complexity


class RelationshipContext(TypedDict):
    """Relationship data for a resource."""
    dependencies: List[str]    # Files this resource imports from
    dependents: List[str]      # Files that import this resource
    test_files: List[str]      # Associated test files
    doc_files: List[str]       # Associated documentation
    config_files: List[str]    # Related configuration files


class UsagePattern(TypedDict):
    """How/where a resource is used."""
    call_sites: List[str]      # Where functions/classes are called from
    usage_count: int           # Total usage occurrences
    hot_paths: List[str]       # Critical execution paths
    last_modified: str         # ISO 8601 timestamp


class ExpertOnboarding(TypedDict):
    """Lloyd's briefing data for an expert."""
    assigned_docs: List[str]   # Docs the expert should read
    domain_scope: str          # Domain specialization (ui, db, api, etc.)
    briefing_notes: str        # Custom briefing from Lloyd
    onboarded_at: str          # ISO 8601 timestamp
    onboarded_by: str          # Agent ID that onboarded (usually Lloyd)


class ContextExpertDefinition(TypedDict):
    """Complete definition for a context expert."""
    # Identity
    expert_id: str             # Unique ID: CE-{resource-slug}-NNN
    name: str                  # Human-readable name
    version: str               # Schema version (1.0.0)
    created_at: str            # ISO 8601 timestamp
    updated_at: str            # ISO 8601 timestamp

    # Resource assignment
    resource_type: str         # "file" or "directory"
    resource_path: str         # Relative path from project root
    resource_hash: str         # SHA256 of resource content (for change detection)

    # Deep context
    code_structure: CodeStructure
    git_history: List[GitHistoryEntry]
    relationships: RelationshipContext
    usage_patterns: UsagePattern

    # Documentation context
    inline_docs: Optional[str]       # Extracted docstrings/comments
    related_docs: List[str]          # Paths to related documentation

    # Expert capabilities
    capabilities: List[str]          # ["answer_questions", "review_changes", "generate_docs"]
    expertise_areas: List[str]       # Auto-generated from code analysis
    domain: str                      # Domain: ui, db, api, core, test, etc.

    # Onboarding (from Lloyd)
    onboarding: Optional[ExpertOnboarding]

    # Assignment metadata
    assignment_type: str             # "manual" or "auto_suggested"
    assigned_by: Optional[str]       # Agent ID that assigned this expert
    workorder_id: Optional[str]      # Associated workorder

    # Status
    status: str                      # "active", "stale", "archived"
    last_refreshed: str              # ISO 8601 timestamp
    staleness_score: float           # 0-100, how outdated the context is


class ContextExpertIndex(TypedDict):
    """Index of all context experts in a project."""
    version: str                     # Schema version
    generated_at: str                # ISO 8601 timestamp
    total_experts: int
    experts: List[Dict[str, Any]]    # Summary entries (id, path, status, staleness)
    auto_suggestions: List[Dict[str, Any]]  # Suggested candidates


class ExpertSuggestion(TypedDict):
    """Auto-discovered expert candidate."""
    resource_path: str
    resource_type: str               # "file" or "directory"
    suggestion_reason: str           # Why this was suggested
    criteria_matched: List[str]      # Which criteria matched
    confidence_score: float          # 0-1 confidence
    metrics: Dict[str, Any]          # Supporting metrics
