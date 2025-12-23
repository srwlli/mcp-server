# workorder-mcp

Enterprise-Grade MCP Server for Feature Lifecycle Management and Workflow Orchestration

## Overview

**workorder-mcp** is a specialized MCP server that handles the workflow orchestration side of feature development, including:

- **Context Gathering** - Collect requirements and feature specifications
- **Planning** - Generate detailed implementation plans with task breakdowns
- **Execution** - Orchestrate task execution and progress tracking
- **Deliverables** - Track metrics and completion status
- **Archiving** - Manage completed features

## Relationship to docs-mcp

This is a sister MCP to **docs-mcp**, which handles pure documentation generation. Together they provide a complete feature lifecycle system:

| Server | Purpose | Tools |
|--------|---------|-------|
| **docs-mcp** | Documentation generation & standards | 10 documentation tools |
| **workorder-mcp** | Workflow orchestration | 30 workflow management tools |

Both MCPs share access to the same `coderef/workflow` folder, enabling seamless coordination between documentation and execution phases.

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv sync
```

## Running

```bash
python server.py
```

## Architecture

- **server.py** - MCP entry point and tool registration
- **src/** - Tool implementations
- **generators/** - Planning and analysis generators
- **coderef/working/** - Feature working directories

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov
```

## License

MIT

## Authors

- willh
- Claude Code AI
