"""
CodeRef Extensions for Template Engine

Provides integration with CodeRef MCP servers:
- coderef-context: Code intelligence (scan, query, impact)
- git: Git statistics (stats, files, contributors)
- workflow: Workflow data (plan, tasks, progress)
"""

from .coderef_context import CodeRefContextExtension
from .git_integration import GitExtension
from .workflow import WorkflowExtension

__all__ = [
    "CodeRefContextExtension",
    "GitExtension",
    "WorkflowExtension",
]
