# CONSTANTS.md - constants.py Authoritative Reference

**File:** `constants.py`
**Category:** Configuration / Centralized Constants
**Lines:** 382
**Enums:** 18
**Path Classes:** 5
**Version:** 1.2.0
**Status:** ✅ Production
**Generated:** 2026-01-02
**Workorder:** WO-RESOURCE-SHEET-P1-001

---

## 1. Purpose & Scope

**What It Does:**
`constants.py` centralizes all hardcoded paths, file names, enums, and magic strings for the coderef-workflow MCP server. Provides a single source of truth for configuration values across all tools and generators.

**Key Innovation:**
Eliminates magic strings and hardcoded paths throughout the codebase by providing typed enums and path constants. Enables easy configuration changes and prevents typos.

**What It Returns:**
N/A - Pure constants module (exports via `__all__`)

**Dependencies:**
- **enum.Enum** - Enum base class
- **pathlib.Path** - File path types

**Core Categories (4 domains):**
```
1. Path & File Constants (3 classes, 28 paths/files)
   └─ Paths, PlanningPaths, Files

2. Workflow Enums (18 enums, 100+ values)
   └─ Template/Changelog/Standards/Audit/Planning/Inventory/Dependency/API/Database/Config/Test/Docs types

3. Context Expert System (5 constants, 3 enums)
   └─ Expert paths, status, capabilities, resource types, domains

4. Security & Validation (7 constants)
   └─ Path limits, regex patterns, exclude lists, size limits
```

**Performance:**
- Import time: <1ms (static constant definitions)
- Memory overhead: Negligible (enum singletons)
- Zero runtime performance impact (compile-time constants)

---

## 2. State Ownership & Source of Truth (Canonical)

| State | Owner | Type | Persistence | Source of Truth |
|-------|-------|------|-------------|-----------------|
| **Path Constants** | Paths class | str | Static (hardcoded) | `constants.py` class attributes |
| **File Constants** | Files class | str | Static (hardcoded) | `constants.py` class attributes |
| **Enums** | Enum classes | str | Static (enum members) | `constants.py` enum definitions |
| **Validation Regex** | Module-level | str | Static (module constants) | `constants.py` PATTERN variables |
| **Security Limits** | Module-level | int/list | Static (module constants) | `constants.py` MAX_* / EXCLUDE_* variables |

**Key Insight:** constants.py is **100% stateless** - all values are static compile-time constants. No runtime state or computation.

---

## 3. Architecture & Data Flow

### Module Organization

```
constants.py (382 lines)
├─ Module docstring (lines 1-6)
├─ Imports (lines 8-9)
├─ __all__ exports (lines 11-59) - 49 exported names
│
├─ SECTION 1: Path & File Constants (lines 62-103)
│  ├─ Paths class (10 path constants)
│  │  ├─ CODEREF = 'coderef'
│  │  ├─ FOUNDATION_DOCS = 'coderef/foundation-docs'
│  │  ├─ CHANGELOG_DIR = 'coderef/changelog'
│  │  ├─ TEMPLATES_DIR = 'templates/power'
│  │  ├─ TOOL_TEMPLATES_DIR = 'templates/tools'
│  │  ├─ STANDARDS_DIR = 'coderef/standards'
│  │  ├─ AUDITS_DIR = 'coderef/audits'
│  │  ├─ CONTEXT_DIR = 'coderef'
│  │  ├─ INVENTORY_DIR = 'coderef/inventory'
│  │  └─ RISK_ASSESSMENTS_DIR = 'coderef/risk-assessments'
│  │
│  └─ Files class (18 file name constants)
│     ├─ README = 'README.md'
│     ├─ ARCHITECTURE = 'ARCHITECTURE.md'
│     ├─ API = 'API.md'
│     ├─ COMPONENTS = 'COMPONENTS.md'
│     ├─ SCHEMA = 'SCHEMA.md'
│     ├─ USER_GUIDE = 'USER-GUIDE.md'
│     ├─ CHANGELOG = 'CHANGELOG.json'
│     ├─ UI_STANDARDS = 'UI-STANDARDS.md'
│     ├─ BEHAVIOR_STANDARDS = 'BEHAVIOR-STANDARDS.md'
│     ├─ UX_PATTERNS = 'UX-PATTERNS.md'
│     ├─ COMPONENT_INDEX = 'COMPONENT-INDEX.md'
│     ├─ AUDIT_REPORT = 'AUDIT-REPORT-{timestamp}.md'
│     ├─ INVENTORY_MANIFEST = 'manifest.json'
│     ├─ INVENTORY_API_MANIFEST = 'api.json'
│     ├─ INVENTORY_DATABASE_MANIFEST = 'database.json'
│     ├─ INVENTORY_CONFIG_MANIFEST = 'config.json'
│     ├─ INVENTORY_TESTS_MANIFEST = 'tests.json'
│     └─ WORKORDER_LOG = 'workorder-log.txt'
│
├─ SECTION 2: Workflow Enums (lines 105-330)
│  ├─ TemplateNames (7 values)
│  ├─ ChangeType (6 values)
│  ├─ Severity (4 values)
│  ├─ ScanDepth (3 values)
│  ├─ FocusArea (4 values)
│  ├─ AuditSeverity (4 values)
│  ├─ AuditScope (4 values)
│  ├─ SeverityThreshold (3 values + values() method)
│  ├─ ValidationSeverity (3 values)
│  ├─ PlanStatus (5 values)
│  ├─ FileCategory (7 values)
│  ├─ RiskLevel (4 values)
│  ├─ AnalysisDepth (3 values)
│  ├─ PackageManager (4 values)
│  ├─ DependencyType (4 values)
│  ├─ VulnerabilitySeverity (4 values)
│  ├─ APIFramework (4 values)
│  ├─ HTTPMethod (7 values)
│  ├─ DatabaseSystem (4 values)
│  ├─ DatabaseType (2 values)
│  ├─ ORMFramework (3 values)
│  ├─ ConfigFormat (5 values)
│  ├─ TestFramework (5 values)
│  └─ DocumentationType (6 values)
│
├─ SECTION 3: Validation & Security Constants (lines 177-186)
│  ├─ MAX_PATH_LENGTH = 1000
│  ├─ TEMPLATE_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
│  ├─ VERSION_PATTERN = r'^\d+\.\d+\.\d+$'
│  ├─ EXCLUDE_DIRS = ['node_modules', '.git', 'dist', ...]
│  ├─ MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
│  └─ ALLOWED_FILE_EXTENSIONS = ['.tsx', '.jsx', '.ts', '.js', '.css', '.scss', '.less']
│
├─ SECTION 4: Planning Workflow Constants (lines 188-196)
│  └─ PlanningPaths class (4 path constants)
│     ├─ TEMPLATE_PATH = Path('mcp-specific-context') / 'feature-implementation-planning-standard.json'
│     ├─ TEMPLATE_AI_PATH = Path('coderef') / 'context' / 'planning-template-for-ai.json'
│     ├─ PLANS_DIR = Path('plans')
│     ├─ REVIEWS_DIR = Path('coderef') / 'planning-reviews'
│     └─ WORKING_DIR = Path('coderef') / 'workorder'
│
└─ SECTION 5: Context Expert System (lines 331-382)
   ├─ ContextExpertPaths class (5 path constants)
   ├─ ContextExpertStatus enum (3 values)
   ├─ ContextExpertCapability enum (3 values)
   ├─ ResourceType enum (2 values)
   ├─ ExpertDomain enum (8 values)
   ├─ EXPERT_ID_PATTERN = r'^CE-[a-zA-Z0-9_-]+-\d{3}$'
   └─ OrchestratorPaths class (2 path constants)
```

---

## 4. Constant Categories

### Category 1: Path Constants (3 classes, 15 paths)

**Paths Class (10 paths)**
- **Purpose:** Standard directory locations
- **Usage:** `from constants import Paths; path = project_root / Paths.FOUNDATION_DOCS`
- **Examples:**
  - `Paths.CODEREF` → `'coderef'` (base directory)
  - `Paths.FOUNDATION_DOCS` → `'coderef/foundation-docs'`
  - `Paths.TEMPLATES_DIR` → `'templates/power'`
  - `Paths.STANDARDS_DIR` → `'coderef/standards'`
  - `Paths.RISK_ASSESSMENTS_DIR` → `'coderef/risk-assessments'`

**PlanningPaths Class (5 paths)**
- **Purpose:** Planning workflow-specific paths
- **Usage:** `from constants import PlanningPaths; template = PlanningPaths.TEMPLATE_AI_PATH`
- **Examples:**
  - `PlanningPaths.TEMPLATE_AI_PATH` → `Path('coderef/context/planning-template-for-ai.json')`
  - `PlanningPaths.WORKING_DIR` → `Path('coderef/workorder')` (active features)
  - `PlanningPaths.REVIEWS_DIR` → `Path('coderef/planning-reviews')`

**Files Class (18 file names)**
- **Purpose:** Standard file name constants
- **Usage:** `from constants import Files; path = project_root / Files.README`
- **Examples:**
  - `Files.README` → `'README.md'`
  - `Files.CHANGELOG` → `'CHANGELOG.json'`
  - `Files.AUDIT_REPORT` → `'AUDIT-REPORT-{timestamp}.md'` (template string)
  - `Files.WORKORDER_LOG` → `'workorder-log.txt'`

---

### Category 2: Workflow Enums (18 enums, 100+ values)

**Documentation Enums (TemplateNames, 7 values)**
```python
class TemplateNames(str, Enum):
    README = 'readme'
    ARCHITECTURE = 'architecture'
    API = 'api'
    COMPONENTS = 'components'
    MY_GUIDE = 'my-guide'
    SCHEMA = 'schema'
    USER_GUIDE = 'user-guide'
```

**Changelog Enums (2 enums, 10 values)**
```python
class ChangeType(str, Enum):
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    BREAKING_CHANGE = 'breaking_change'
    DEPRECATION = 'deprecation'
    SECURITY = 'security'

class Severity(str, Enum):
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'
    PATCH = 'patch'
```

**Standards & Audit Enums (4 enums, 15 values)**
```python
class ScanDepth(str, Enum):
    QUICK = 'quick'
    STANDARD = 'standard'
    DEEP = 'deep'

class FocusArea(str, Enum):
    UI_COMPONENTS = 'ui_components'
    BEHAVIOR_PATTERNS = 'behavior_patterns'
    UX_FLOWS = 'ux_flows'
    ALL = 'all'

class AuditSeverity(str, Enum):
    CRITICAL = 'critical'  # Must fix immediately
    MAJOR = 'major'  # Should fix soon
    MINOR = 'minor'  # Style improvement
    ALL = 'all'  # Filter for all

class SeverityThreshold(str, Enum):
    CRITICAL = 'critical'  # Fail only on critical
    MAJOR = 'major'  # Fail on critical + major (default)
    MINOR = 'minor'  # Fail on any violation
```

**Planning Enums (3 enums, 11 values)**
```python
class ValidationSeverity(Enum):
    CRITICAL = 'critical'  # -10 points
    MAJOR = 'major'  # -5 points
    MINOR = 'minor'  # -1 point

class PlanStatus(Enum):
    DRAFT = 'draft'
    REVIEWING = 'reviewing'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    IMPLEMENTED = 'implemented'

class FileCategory(str, Enum):
    CORE = 'core'  # Core infrastructure
    SOURCE = 'source'  # Business logic
    TEMPLATE = 'template'  # Templates
    CONFIG = 'config'  # Configuration
    TEST = 'test'  # Tests
    DOCS = 'docs'  # Documentation
    UNKNOWN = 'unknown'
```

**Inventory Enums (3 enums, 11 values)**
```python
class RiskLevel(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class AnalysisDepth(str, Enum):
    QUICK = 'quick'  # Basic metadata
    STANDARD = 'standard'  # Categorization
    DEEP = 'deep'  # Full parsing

class PackageManager(str, Enum):
    NPM = 'npm'
    PIP = 'pip'
    CARGO = 'cargo'
    COMPOSER = 'composer'
```

**Dependency Enums (2 enums, 8 values)**
```python
class DependencyType(str, Enum):
    DIRECT = 'direct'
    DEV = 'dev'
    PEER = 'peer'
    TRANSITIVE = 'transitive'

class VulnerabilitySeverity(str, Enum):
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
```

**API Enums (2 enums, 11 values)**
```python
class APIFramework(str, Enum):
    FASTAPI = 'fastapi'
    FLASK = 'flask'
    EXPRESS = 'express'
    GRAPHQL = 'graphql'

class HTTPMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
```

**Database Enums (3 enums, 9 values)**
```python
class DatabaseSystem(str, Enum):
    POSTGRESQL = 'postgresql'
    MYSQL = 'mysql'
    MONGODB = 'mongodb'
    SQLITE = 'sqlite'

class DatabaseType(str, Enum):
    SQL = 'sql'
    NOSQL = 'nosql'

class ORMFramework(str, Enum):
    SQLALCHEMY = 'sqlalchemy'
    SEQUELIZE = 'sequelize'
    MONGOOSE = 'mongoose'
```

**Configuration & Test Enums (3 enums, 15 values)**
```python
class ConfigFormat(str, Enum):
    JSON = 'json'
    YAML = 'yaml'
    TOML = 'toml'
    INI = 'ini'
    ENV = 'env'

class TestFramework(str, Enum):
    PYTEST = 'pytest'
    UNITTEST = 'unittest'
    JEST = 'jest'
    MOCHA = 'mocha'
    VITEST = 'vitest'

class DocumentationType(str, Enum):
    MARKDOWN = 'markdown'
    RESTRUCTURED_TEXT = 'restructured_text'
    ASCIIDOC = 'asciidoc'
    HTML = 'html'
    ORGMODE = 'orgmode'
    PLAINTEXT = 'plaintext'
```

---

### Category 3: Context Expert System (5 constants, 3 enums)

**ContextExpertPaths Class**
```python
class ContextExpertPaths:
    ROOT = 'coderef/experts'
    EXPERTS = 'coderef/experts'
    CACHE = 'coderef/experts/cache'
    INDEX = 'coderef/experts/index.json'
    REGISTRY = 'coderef/experts/experts.json'
```

**ContextExpertStatus Enum**
```python
class ContextExpertStatus(str, Enum):
    ACTIVE = 'active'      # Expert ready
    STALE = 'stale'        # Needs refresh
    ARCHIVED = 'archived'  # No longer active
```

**ContextExpertCapability Enum**
```python
class ContextExpertCapability(str, Enum):
    ANSWER_QUESTIONS = 'answer_questions'
    REVIEW_CHANGES = 'review_changes'
    GENERATE_DOCS = 'generate_docs'
```

**ResourceType Enum**
```python
class ResourceType(str, Enum):
    FILE = 'file'           # Single file expert
    DIRECTORY = 'directory' # Directory expert
```

**ExpertDomain Enum**
```python
class ExpertDomain(str, Enum):
    UI = 'ui'           # Components, styling
    DB = 'db'           # Schemas, migrations
    SCRIPT = 'script'   # Build scripts
    DOCS = 'docs'       # Documentation
    API = 'api'         # API endpoints
    CORE = 'core'       # Business logic
    TEST = 'test'       # Testing
    INFRA = 'infra'     # Infrastructure
```

**OrchestratorPaths Class**
```python
class OrchestratorPaths:
    ROOT = 'C:\\Users\\willh\\.mcp-servers'
    WORKORDER_LOG = 'coderef/workorder-log.txt'
```

---

### Category 4: Security & Validation Constants (7 constants)

**Path Limits**
```python
MAX_PATH_LENGTH = 1000  # Maximum allowed path length
```

**Regex Patterns**
```python
TEMPLATE_NAME_PATTERN = r'^[a-zA-Z0-9_-]+$'  # Alphanumeric, hyphens, underscores
VERSION_PATTERN = r'^\d+\.\d+\.\d+$'  # Semantic versioning (e.g., 1.2.3)
EXPERT_ID_PATTERN = r'^CE-[a-zA-Z0-9_-]+-\d{3}$'  # Context Expert ID format
```

**Security Exclusions**
```python
EXCLUDE_DIRS = [
    'node_modules', '.git', 'dist', 'build', '.next', 'out', 'coverage',
    '__pycache__', '.venv', 'venv', 'vendor'
]
```

**File Size Limits**
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB - skip files larger
```

**Allowed Extensions**
```python
ALLOWED_FILE_EXTENSIONS = [
    '.tsx', '.jsx', '.ts', '.js', '.css', '.scss', '.less'
]
```

---

## 5. Usage Patterns

### Pattern 1: Path Construction

```python
from pathlib import Path
from constants import Paths, Files

# Build path to foundation docs
project_root = Path("/path/to/project")
foundation_docs_dir = project_root / Paths.FOUNDATION_DOCS
# → /path/to/project/coderef/foundation-docs

# Build path to specific file
readme_path = foundation_docs_dir / Files.README
# → /path/to/project/coderef/foundation-docs/README.md

# Build path to changelog
changelog_dir = project_root / Paths.CHANGELOG_DIR
changelog_file = changelog_dir / Files.CHANGELOG
# → /path/to/project/coderef/changelog/CHANGELOG.json
```

---

### Pattern 2: Enum Validation

```python
from constants import ChangeType, Severity

def create_changelog_entry(change_type: str, severity: str):
    """Create changelog entry with validation."""
    # Validate change_type
    if change_type not in [e.value for e in ChangeType]:
        raise ValueError(f"Invalid change_type: {change_type}")

    # Validate severity
    if severity not in [e.value for e in Severity]:
        raise ValueError(f"Invalid severity: {severity}")

    return {
        "type": change_type,
        "severity": severity,
        # ...
    }

# Usage
entry = create_changelog_entry(
    ChangeType.FEATURE,  # ✅ Type-safe enum value
    Severity.MAJOR
)
```

---

### Pattern 3: Enum Iteration

```python
from constants import HTTPMethod, SeverityThreshold

# Get all HTTP methods
all_methods = [method.value for method in HTTPMethod]
# → ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

# Get all severity thresholds (using custom values() method)
all_thresholds = SeverityThreshold.values()
# → ['critical', 'major', 'minor']

# Iterate over enums
for method in HTTPMethod:
    print(f"Method: {method.name} = {method.value}")
# Output:
# Method: GET = GET
# Method: POST = POST
# ...
```

---

### Pattern 4: Template String Formatting

```python
from datetime import datetime
from constants import Files

# Format audit report filename
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
report_filename = Files.AUDIT_REPORT.format(timestamp=timestamp)
# → 'AUDIT-REPORT-20260102-153045.md'
```

---

### Pattern 5: Security Validation

```python
from constants import MAX_PATH_LENGTH, TEMPLATE_NAME_PATTERN, EXCLUDE_DIRS
import re

def validate_path(path: str) -> bool:
    """Validate path against security constraints."""
    # Check length
    if len(path) > MAX_PATH_LENGTH:
        return False

    # Check for excluded directories
    path_parts = path.split('/')
    if any(part in EXCLUDE_DIRS for part in path_parts):
        return False

    return True

def validate_template_name(name: str) -> bool:
    """Validate template name format."""
    return bool(re.match(TEMPLATE_NAME_PATTERN, name))

# Usage
validate_path("coderef/foundation-docs/README.md")  # ✅ True
validate_path("node_modules/some-package/index.js")  # ❌ False (excluded dir)
validate_template_name("my-template")  # ✅ True
validate_template_name("my template")  # ❌ False (space not allowed)
```

---

## 6. Integration Points

### 6.1 Called By (Consumers)

**All Tool Handlers:**
- `tool_handlers.py` - Uses path constants, enums for validation

**All Generators:**
- `generators/plan_generator.py` - Uses PlanningPaths, ValidationSeverity
- `generators/plan_validator.py` - Uses ValidationSeverity, PlanStatus
- `generators/changelog_generator.py` - Uses ChangeType, Severity
- `generators/standards_generator.py` - Uses ScanDepth, FocusArea

**All Inventory Modules:**
- `generators/dependency_inventory.py` - Uses PackageManager, DependencyType, VulnerabilitySeverity
- `generators/api_inventory.py` - Uses APIFramework, HTTPMethod
- `generators/database_inventory.py` - Uses DatabaseSystem, DatabaseType, ORMFramework
- `generators/config_inventory.py` - Uses ConfigFormat
- `generators/test_inventory.py` - Uses TestFramework
- `generators/documentation_inventory.py` - Uses DocumentationType

**Validation Modules:**
- `validators.py` - Uses validation constants (MAX_PATH_LENGTH, patterns)

---

## 7. Maintenance & Evolution

### 7.1 Adding New Constants

**Process:**
1. Add constant to appropriate class/enum
2. Add to `__all__` list
3. Document in docstring
4. Update this resource sheet

**Example: Adding New Enum Value**
```python
# Step 1: Add to enum
class ChangeType(str, Enum):
    BUGFIX = 'bugfix'
    ENHANCEMENT = 'enhancement'
    FEATURE = 'feature'
    BREAKING_CHANGE = 'breaking_change'
    DEPRECATION = 'deprecation'
    SECURITY = 'security'
    REFACTOR = 'refactor'  # NEW

# Step 2: Already in __all__ (ChangeType)

# Step 3: Document
"""
REFACTOR - Code refactoring without behavior changes
"""

# Step 4: Update CONSTANTS.md (this file)
```

---

### 7.2 Versioning Strategy

**Current Version:** 1.2.0

**Versioning Rules:**
- **Major (x.0.0):** Remove constants, change enum values (breaking)
- **Minor (1.x.0):** Add new constants, add new enum values
- **Patch (1.2.x):** Documentation updates only

**Example:**
- v1.2.0 → v1.3.0: Add ORMFramework.TYPEORM (minor)
- v1.3.0 → v2.0.0: Remove deprecated ScanDepth.SHALLOW (major)
- v2.0.0 → v2.0.1: Fix docstring typo (patch)

---

### 7.3 Recent Changes (v1.2.0)

**Added:**
- Context Expert System constants (ContextExpertPaths, ContextExpertStatus, ContextExpertCapability, ResourceType, ExpertDomain)
- Orchestrator constants (OrchestratorPaths)
- EXPERT_ID_PATTERN regex

**Modified:**
- PlanningPaths.WORKING_DIR updated from 'coderef/working' to 'coderef/workorder'

**Removed:**
- None (no breaking changes)

---

## 8. Best Practices

### 8.1 Using Constants

**DO:**
```python
# ✅ Import and use constants
from constants import Paths, ChangeType

foundation_dir = project_root / Paths.FOUNDATION_DOCS
change_type = ChangeType.FEATURE.value

# ✅ Use enum values for type safety
def create_change(change_type: ChangeType):
    return {"type": change_type.value}
```

**DON'T:**
```python
# ❌ Hardcode paths
foundation_dir = project_root / "coderef/foundation-docs"  # Magic string

# ❌ Hardcode enum values
change_type = "feature"  # No type safety
```

---

### 8.2 Enum Usage

**DO:**
```python
# ✅ Use enum members for comparisons
if change_type == ChangeType.FEATURE:
    ...

# ✅ Iterate over enum
for method in HTTPMethod:
    print(method.value)
```

**DON'T:**
```python
# ❌ Compare strings directly
if change_type == "feature":  # Typo-prone
    ...
```

---

## 9. Quick Reference

### 9.1 Most Used Constants

**Top 10 by Usage Frequency:**
1. **Paths.CODEREF** - Base directory
2. **Paths.FOUNDATION_DOCS** - Foundation docs location
3. **Files.README** - README.md filename
4. **ChangeType** - Changelog entry types
5. **Severity** - Changelog severity levels
6. **PlanningPaths.WORKING_DIR** - Active feature directory
7. **Files.CHANGELOG** - Changelog filename
8. **SeverityThreshold** - Consistency check thresholds
9. **HTTPMethod** - REST API methods
10. **PackageManager** - Dependency analysis

---

### 9.2 Constant Hierarchy

```
Path Constants
├─ Paths (10 paths)
├─ PlanningPaths (5 paths)
├─ ContextExpertPaths (5 paths)
└─ OrchestratorPaths (2 paths)

File Constants
└─ Files (18 file names)

Workflow Enums
├─ Documentation (TemplateNames)
├─ Changelog (ChangeType, Severity)
├─ Standards (ScanDepth, FocusArea, AuditSeverity, AuditScope, SeverityThreshold)
├─ Planning (ValidationSeverity, PlanStatus)
├─ Inventory (FileCategory, RiskLevel, AnalysisDepth)
├─ Dependency (PackageManager, DependencyType, VulnerabilitySeverity)
├─ API (APIFramework, HTTPMethod)
├─ Database (DatabaseSystem, DatabaseType, ORMFramework)
├─ Configuration (ConfigFormat)
├─ Test (TestFramework)
└─ Documentation (DocumentationType)

Context Expert Enums
├─ ContextExpertStatus
├─ ContextExpertCapability
├─ ResourceType
└─ ExpertDomain

Validation/Security Constants
├─ MAX_PATH_LENGTH
├─ TEMPLATE_NAME_PATTERN
├─ VERSION_PATTERN
├─ EXPERT_ID_PATTERN
├─ EXCLUDE_DIRS
├─ MAX_FILE_SIZE
└─ ALLOWED_FILE_EXTENSIONS
```

---

## 10. Related Resources

### 10.1 Related Files

- **type_defs.py** - Uses enum values for TypedDict field validation
- **validators.py** - Uses validation constants (MAX_PATH_LENGTH, patterns)
- **tool_handlers.py** - Uses path constants, file names
- **generators/*.py** - Uses domain-specific enums

### 10.2 Generated Artifacts

- **coderef/schemas/constants-schema.json** - JSON Schema for constants
- **coderef/.jsdoc/constants-jsdoc.txt** - JSDoc usage examples

---

**Generated by:** Resource Sheet MCP Tool v1.0
**Workorder:** WO-RESOURCE-SHEET-P1-001
**Task:** SHEET-008
**Timestamp:** 2026-01-02
**Maintained by:** willh, Claude Code AI
