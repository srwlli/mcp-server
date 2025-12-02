"""Constants and definitions for CodeRef MCP Service."""

# CodeRef Type Designators (26 total)
TYPE_DESIGNATORS = {
    'F': 'File',
    'D': 'Directory',
    'C': 'Class',
    'Fn': 'Function',
    'Cl': 'Closure',
    'M': 'Method',
    'V': 'Variable',
    'S': 'Statement',
    'T': 'Type/Interface',
    'A': 'Alias',
    'Cfg': 'Configuration',
    'H': 'Hook',
    'Ctx': 'Context',
    'R': 'Route',
    'Q': 'Query',
    'I': 'Import',
    'Doc': 'Documentation',
    'Gen': 'Generator',
    'Dep': 'Dependency',
    'E': 'Enum',
    'WIP': 'Work in Progress',
    'Async': 'Async Function',
    'Comp': 'Component',
    'ML': 'Machine Learning Model',
    'DB': 'Database Schema',
    'SEC': 'Security-related',
}

# Metadata Categories (8 categories)
METADATA_CATEGORIES = [
    'status',          # active, deprecated, experimental
    'security',        # public, internal, restricted
    'performance',     # critical, high, medium, low
    'complexity',      # simple, moderate, complex
    'coverage',        # percentage or status
    'maintenance',     # stable, active, abandoned
    'compatibility',   # versions or platforms
    'documentation',   # complete, partial, missing
]

# Relationship Types (5+ types)
RELATIONSHIP_TYPES = [
    'imports',         # A imports B
    'calls',           # A calls B
    'depends-on',      # A depends on B
    'tests',           # A tests B
    'implements',      # A implements B
    'overrides',       # A overrides B
    'extends',         # A extends B
]

# MCP Tool Names (6 tools)
MCP_TOOLS = [
    'mcp__coderef__query',                    # Tool 1: Query code elements
    'mcp__coderef__analyze',                  # Tool 2: Analyze impact/coverage
    'mcp__coderef__validate',                 # Tool 3: Validate references
    'mcp__coderef__uds_compliance_check',     # Tool 4: UDS compliance
    'mcp__coderef__generate_with_uds',        # Tool 5: Generate docs with UDS
    'mcp__coderef__batch_validate',           # Tool 6: Batch validation
]

# Performance Targets (milliseconds)
PERFORMANCE_TARGETS = {
    'query': 500,
    'analyze': 500,
    'validate': 200,
    'uds_compliance': 300,
    'generate_docs': 1000,
    'batch_validate': 500,
}

# CodeRef Reference Format Pattern
CODEREF_PATTERN = r'^@(\w+)/(.+)#(.+):(\d+)(?:\{(.+)\})?$'

# Service Configuration
SERVICE_NAME = 'coderef-mcp'
SERVICE_VERSION = '1.0.0'
PROTOCOL_VERSION = '2024.11'

# Baseline Metrics
BASELINE_ELEMENTS_COUNT = 281
BASELINE_RELATIONSHIPS_COUNT = 1000
TEST_TARGET_CASES = 150
TEST_COVERAGE_TARGET = 0.90
