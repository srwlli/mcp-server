# API.md

**Date:** 2025-10-11
**Version:** 1.4.0

## API Overview

docs-mcp provides a Model Context Protocol (MCP) API for AI assistants to access documentation templates, changelog management, codebase consistency auditing, and implementation planning workflow. The API exposes 13 tool endpoints via JSON-RPC over stdio transport, enabling structured documentation generation, changelog tracking, standards compliance enforcement, and AI-assisted planning with automated validation.

**Project Reference:** docs-mcp is an MCP server providing structured access to POWER framework templates (README, Architecture, API, Components, Schema, User Guide) and a complete changelog management system with read, write, and agentic instruction capabilities.

**Architecture Reference:** Built on MCP SDK for Python with async I/O, stdio transport, file-based template storage, and JSON-based changelog system. Uses Generator Pattern with BaseGenerator, FoundationGenerator, and ChangelogGenerator classes. See ARCHITECTURE.md for system topology and data flow details.

## Protocol Details

### Transport Layer
- **Protocol:** Model Context Protocol (MCP) v1.0
- **Transport:** stdio (standard input/output)
- **Message Format:** JSON-RPC 2.0
- **Encoding:** UTF-8

### Communication Pattern
```
Client → JSON-RPC Request → stdio → Server
Server → JSON-RPC Response → stdio → Client
```

## Authentication & Authorization

**Authentication:** None (local-only access via stdio transport)
- No API keys, tokens, or credentials required
- Server inherits parent process permissions
- Access restricted to processes that can spawn the server

**Authorization:** Mixed access levels
- **Documentation tools:** Read-only file system access
- **Changelog tools:** Read/write access to CHANGELOG.json
- **Scope:** Restricted to project directories specified in parameters

## Rate Limits & Quotas

**Rate Limits:** None
- Local stdio transport has no artificial rate limiting
- Limited only by system I/O performance

**Quotas:** None
- Unlimited requests per time period
- No usage tracking or throttling

**Concurrency:**
- Single-threaded async event loop
- One request processed at a time (MCP model)
- No concurrent request handling

## API Endpoints

### Category 1: Documentation Generation (4 tools)

---

### 1. list_templates

Lists all available POWER framework documentation templates.

**Tool Name:** `list_templates`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "list_templates",
    "arguments": {}
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Available POWER Framework Templates:\n\n1. api\n2. architecture\n3. components\n4. readme\n5. schema\n6. user-guide\n\nTotal: 6 templates"
      }
    ]
  }
}
```

**Use Case:** Discover available documentation types before generating specific documents.

---

### 2. get_template

Retrieves the full content of a specific documentation template.

**Tool Name:** `get_template`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "template_name": {
      "type": "string",
      "description": "Name of template: readme, architecture, api, components, schema, or user-guide",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide"]
    }
  },
  "required": ["template_name"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_template",
    "arguments": {
      "template_name": "readme"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "=== README Template ===\n\nframework: POWER\npurpose: Generate README.md as the primary project documentation...\n..."
      }
    ]
  }
}
```

**Error Response Examples:**

*Template Not Found:*
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Template 'invalid' not found. Available: readme, architecture, api, components, schema, user-guide"
      }
    ]
  }
}
```

**Template Format:**
All templates follow POWER framework structure:
```
framework: POWER
purpose: [Document objective]
output: [Required format]
work: [Process steps]
examples: [Usage samples]
requirements: [Mandatory elements]
save_as: [Default filename]
store_as: [Reference name]
```

**Use Case:** Retrieve template content to guide documentation generation following POWER framework.

---

### 3. generate_foundation_docs

Generates all 6 foundation documents (README, ARCHITECTURE, API, COMPONENTS, SCHEMA, USER-GUIDE) for a project. Returns templates and generation plan - Claude will generate and save the actual documents.

**Tool Name:** `generate_foundation_docs`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "generate_foundation_docs",
    "arguments": {
      "project_path": "C:/Users/willh/my-project"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Foundation Documentation Generation Plan\n\nProject: C:/Users/willh/my-project\nOutput Directory: coderef/foundation-docs/\n\nTemplates to Generate:\n1. readme\n2. architecture\n3. api\n4. components\n5. schema\n6. user-guide\n\nGeneration Order:\nEach document will reference previous documents for context.\nTotal: 6 documents\n\n1. README.md\n   Purpose: Generate README.md as the primary project documentation...\n\n[Full template content for each document]\n\nNext Steps:\n1. Create output directory if needed\n2. Generate each document following the POWER framework\n3. Reference previous documents for context\n4. Save to coderef/foundation-docs/"
      }
    ]
  }
}
```

**Use Case:** Bootstrap comprehensive documentation suite for a new or undocumented project.

**Implementation Note:** This is a meta-tool that provides instructions and templates. The AI assistant analyzes the project and generates the actual markdown files.

---

### 4. generate_individual_doc

Generates a single documentation file for a project. Returns the template - Claude will generate and save the document.

**Tool Name:** `generate_individual_doc`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "template_name": {
      "type": "string",
      "description": "Name of template to generate",
      "enum": ["readme", "architecture", "api", "components", "schema", "user-guide"]
    }
  },
  "required": ["project_path", "template_name"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "generate_individual_doc",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "template_name": "api"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Individual Document Generation\n\nProject: C:/Users/willh/my-project\nTemplate: api\nOutput: coderef/foundation-docs/API.md\n\n=== API Template ===\n\nframework: POWER\npurpose: Generate API.md as the technical interface reference...\n\nNext Steps:\n1. Analyze project structure\n2. Generate API.md following POWER framework\n3. Save to coderef/foundation-docs/API.md"
      }
    ]
  }
}
```

**Use Case:** Generate or update a specific documentation file without regenerating the entire foundation docs suite.

---

### Category 2: Changelog Management (3 tools)

The **Changelog Trilogy** pattern: READ (get_changelog) + WRITE (add_changelog_entry) + INSTRUCT (update_changelog)

---

### 5. get_changelog (📖 READ)

Queries changelog history with optional filtering by version, change type, or breaking changes only.

**Tool Name:** `get_changelog`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "version": {
      "type": "string",
      "description": "Optional: Specific version to retrieve (e.g., '1.0.2')",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "change_type": {
      "type": "string",
      "description": "Optional: Filter by change type",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    },
    "breaking_only": {
      "type": "boolean",
      "description": "Optional: Only show breaking changes"
    }
  },
  "required": ["project_path"]
}
```

**Request Examples:**

*Full Changelog:*
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "get_changelog",
    "arguments": {
      "project_path": "C:/Users/willh/my-project"
    }
  }
}
```

*Specific Version:*
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "get_changelog",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "version": "1.0.2"
    }
  }
}
```

*Breaking Changes Only:*
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "get_changelog",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "breaking_only": true
    }
  }
}
```

*Filter by Change Type:*
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "get_changelog",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "change_type": "feature"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Changelog for my-project\n\nCurrent Version: 1.0.3\nTotal Versions: 2\n\n=== Version 1.0.3 (2025-10-09) ===\nSummary: Added update_changelog agentic workflow tool for self-documenting agents\nContributors: willh, Claude Code AI\n\nChanges:\n1. [FEATURE] Added update_changelog agentic workflow tool (MAJOR)\n   Files: server.py\n   Description: Implemented update_changelog MCP tool that provides structured instructions...\n\n=== Version 1.0.2 (2025-10-09) ===\n..."
      }
    ]
  }
}
```

**Use Case:** Review project history, check for breaking changes before upgrading, filter by feature additions.

---

### 6. add_changelog_entry (✍️ WRITE)

Adds a new changelog entry to the project's CHANGELOG.json file.

**Tool Name:** `add_changelog_entry`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "version": {
      "type": "string",
      "description": "Version number (e.g., '1.0.3')",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "change_type": {
      "type": "string",
      "description": "Type of change",
      "enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]
    },
    "severity": {
      "type": "string",
      "description": "Severity level",
      "enum": ["critical", "major", "minor", "patch"]
    },
    "title": {
      "type": "string",
      "description": "Short title of the change"
    },
    "description": {
      "type": "string",
      "description": "Detailed description of what changed"
    },
    "files": {
      "type": "array",
      "description": "List of affected files",
      "items": {"type": "string"}
    },
    "reason": {
      "type": "string",
      "description": "Why this change was made"
    },
    "impact": {
      "type": "string",
      "description": "Impact on users/system"
    },
    "breaking": {
      "type": "boolean",
      "description": "Whether this is a breaking change (default: false)"
    },
    "migration": {
      "type": "string",
      "description": "Migration guide (if breaking)"
    },
    "summary": {
      "type": "string",
      "description": "Version summary (for new versions)"
    },
    "contributors": {
      "type": "array",
      "description": "List of contributors",
      "items": {"type": "string"}
    }
  },
  "required": ["project_path", "version", "change_type", "severity", "title", "description", "files", "reason", "impact"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "add_changelog_entry",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "version": "1.0.3",
      "change_type": "feature",
      "severity": "major",
      "title": "Added new feature X",
      "description": "Implemented feature X with capabilities Y and Z...",
      "files": ["server.py", "lib/feature.py"],
      "reason": "Users requested ability to...",
      "impact": "Users can now...",
      "breaking": false,
      "contributors": ["willh", "Claude Code AI"]
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Changelog entry added successfully!\n\nVersion: 1.0.3\nChange: Added new feature X\nType: feature (major)\nFiles: 2\n\nChangelog saved to: C:/Users/willh/my-project/coderef/changelog/CHANGELOG.json"
      }
    ]
  }
}
```

**Error Response Examples:**

*Invalid Version Format:*
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: Version must match pattern: X.Y.Z (e.g., '1.0.3')"
      }
    ]
  }
}
```

*Schema Validation Failed:*
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: Schema validation failed:\n- 'files' is a required property"
      }
    ]
  }
}
```

**Use Case:** Programmatically document changes after making modifications to a project.

---

### 7. update_changelog (🤖 INSTRUCT - Agentic Workflow)

Meta-tool that provides structured instructions for agents to autonomously document their changes. This is the **INSTRUCT** component of the Changelog Trilogy.

**Tool Name:** `update_changelog`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to the project directory"
    },
    "version": {
      "type": "string",
      "description": "Version number (e.g., '1.0.3')",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    }
  },
  "required": ["project_path", "version"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "update_changelog",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "version": "1.0.3"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Changelog Update Instructions for Version 1.0.3\n\nYou are about to document changes to C:/Users/willh/my-project.\n\nFollow these steps:\n\nSTEP 1: Analyze Your Changes\n- Review the modifications you made to the project\n- Identify all affected files\n- Understand the scope and impact of changes\n\nSTEP 2: Determine Change Details\n- change_type: bugfix | enhancement | feature | breaking_change | deprecation | security\n- severity: critical | major | minor | patch\n- breaking: true/false (Does this break existing functionality?)\n\nSTEP 3: Call add_changelog_entry\nUse the add_changelog_entry tool with:\n- project_path: 'C:/Users/willh/my-project'\n- version: '1.0.3'\n- change_type: [your analysis]\n- severity: [your analysis]\n- title: [concise summary]\n- description: [detailed explanation]\n- files: [list of modified files]\n- reason: [why this change was made]\n- impact: [effect on users/system]\n- breaking: [true/false]\n- migration: [if breaking, provide guide]\n- contributors: [your name + any collaborators]\n\nExample call:\nadd_changelog_entry(\n  project_path='C:/Users/willh/my-project',\n  version='1.0.3',\n  change_type='feature',\n  severity='major',\n  title='Added X capability',\n  description='Implemented X with...',\n  files=['file1.py', 'file2.py'],\n  reason='Enable users to...',\n  impact='Users can now...',\n  breaking=false,\n  contributors=['YourName']\n)\n\nNow proceed with your analysis and execute add_changelog_entry."
      }
    ]
  }
}
```

**Agentic Workflow:**
```
┌─────────────────────────────────────────────────────────┐
│ Agent makes changes to project                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Agent: update_changelog(project_path, version)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Tool: Returns structured 3-step instructions            │
│   • Step 1: Analyze your changes                        │
│   • Step 2: Determine type/severity                     │
│   • Step 3: Call add_changelog_entry                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Agent: Analyzes context autonomously                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Agent: add_changelog_entry(...contextual details...)    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Changelog updated! ✅                                    │
└─────────────────────────────────────────────────────────┘
```

**Design Pattern:** This is a **meta-tool** that orchestrates agentic workflows by providing instructions rather than executing. This enables:
- ✅ **Agentic autonomy** - Agents analyze their own changes
- ✅ **Flexibility** - Agents choose execution method
- ✅ **Single responsibility** - update_changelog orchestrates, add_changelog_entry executes

**Use Case:** Enable AI agents to self-document their work without explicit prompting. The agent receives instructions, analyzes the context, and autonomously executes add_changelog_entry.

---

### Category 3: Consistency Management (2 tools)

The **Consistency Trilogy** pattern: ESTABLISH (establish_standards) + AUDIT (audit_codebase) + ENFORCE (check_consistency - coming soon)

---

### 8. establish_standards (📋 ESTABLISH - Run Once)

Scans codebase to discover UI/UX/behavior patterns and generates standards documentation. Creates 4 markdown files in `coderef/standards/` directory. Run ONCE per project to establish baseline standards for consistency validation.

**Tool Name:** `establish_standards`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "scan_depth": {
      "type": "string",
      "enum": ["quick", "standard", "deep"],
      "description": "Analysis depth: quick (common patterns, ~1-2 min), standard (comprehensive, ~3-5 min), deep (exhaustive, ~10-15 min)",
      "default": "standard"
    },
    "focus_areas": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["ui_components", "behavior_patterns", "ux_flows", "all"]
      },
      "description": "Areas to analyze: ui_components (buttons, modals, forms), behavior_patterns (errors, loading), ux_flows (navigation, permissions), or all",
      "default": ["all"]
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tools/call",
  "params": {
    "name": "establish_standards",
    "arguments": {
      "project_path": "C:/Users/willh/my-react-app",
      "scan_depth": "standard",
      "focus_areas": ["all"]
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Standards establishment completed successfully!\n\nProject: my-react-app\nScan Depth: standard\nFocus Areas: all\n\n📊 RESULTS:\n\nFiles Created: 4\nTotal Patterns Discovered: 47\n  • UI Patterns: 23\n  • Behavior Patterns: 12\n  • UX Patterns: 8\nComponents Indexed: 15\n\n📁 STANDARDS DOCUMENTS:\n  • UI-STANDARDS.md\n  • BEHAVIOR-STANDARDS.md\n  • UX-PATTERNS.md\n  • COMPONENT-INDEX.md\n\n📂 Location: C:/Users/willh/my-react-app/coderef/standards/\n\nThese standards documents can now be used with:\n  • Tool #9: audit_codebase - Find violations of standards\n  • Tool #10: check_consistency - Quality gate for new code"
      }
    ]
  }
}
```

**Output Files:**
- `coderef/standards/UI-STANDARDS.md` - Button sizes/variants, modal configurations, colors, typography
- `coderef/standards/BEHAVIOR-STANDARDS.md` - Error handling patterns, loading states, toast messages
- `coderef/standards/UX-PATTERNS.md` - Navigation patterns, accessibility (ARIA), offline handling
- `coderef/standards/COMPONENT-INDEX.md` - Component inventory with usage counts and props

**Use Case:** Bootstrap standards documentation for an existing project. Run once to establish baseline, then use audit_codebase (Tool #9) to find violations.

---

### 9. audit_codebase (🔍 AUDIT - Run Periodically)

Audits codebase for standards violations using established standards documents. Scans all source files, compares against standards, and generates comprehensive compliance report with violations, severity levels, and fix suggestions.

**Tool Name:** `audit_codebase`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "standards_dir": {
      "type": "string",
      "description": "Path to standards directory (relative to project root)",
      "default": "coderef/standards"
    },
    "severity_filter": {
      "type": "string",
      "enum": ["critical", "major", "minor", "all"],
      "description": "Filter violations by severity level",
      "default": "all"
    },
    "scope": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["ui_patterns", "behavior_patterns", "ux_patterns", "all"]
      },
      "description": "Which areas to audit: ui_patterns, behavior_patterns, ux_patterns, or all",
      "default": ["all"]
    },
    "generate_fixes": {
      "type": "boolean",
      "description": "Include automated fix suggestions in report",
      "default": true
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "tools/call",
  "params": {
    "name": "audit_codebase",
    "arguments": {
      "project_path": "C:/Users/willh/my-react-app",
      "standards_dir": "coderef/standards",
      "severity_filter": "all",
      "scope": ["all"],
      "generate_fixes": true
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Codebase audit completed successfully!\n\nProject: my-react-app\nStandards: coderef/standards\nSeverity Filter: all\nScope: all\n\n📊 AUDIT RESULTS:\n\nCompliance Score: 85/100 (B)\nStatus: ✅ PASSING\n\nViolations Found: 12\n  • Critical: 0\n  • Major: 5\n  • Minor: 7\n\nScan Duration: 3.2 seconds\nFiles Scanned: 143\n\n📁 AUDIT REPORT:\n  • C:/Users/willh/my-react-app/coderef/audits/AUDIT-REPORT-2025-10-10-153045.md\n\nNext steps:\n  1. Review the audit report at AUDIT-REPORT-2025-10-10-153045.md\n  2. Address critical and major violations first\n  3. Use the fix suggestions in the report\n  4. Re-run audit_codebase to verify fixes"
      }
    ]
  }
}
```

**Output Format:**
Generates timestamped markdown audit report in `coderef/audits/` with:
- **Executive Summary**: Compliance score (0-100), letter grade (A-F), passing status (80+ threshold)
- **Compliance by Category**: UI patterns, behavior patterns, UX patterns
- **Violations by Severity**: Critical, major, minor with file locations and line numbers
- **Violations by File**: Grouped by file path, sorted by violation count
- **Fix Recommendations**: Actionable remediation steps with code examples
- **Scan Metadata**: Duration, files scanned, standards files used

**Violation Severity Levels:**
- **Critical** (-10 pts each): Missing ARIA attributes, security issues, broken user flows
- **Major** (-5 pts each): Non-standard UI components, missing loading states, inconsistent error handling
- **Minor** (-1 pt each): Undocumented colors, non-standard error messages, style inconsistencies

**Use Case:** Run periodically (weekly/monthly) or before releases to ensure codebase consistency. Compare compliance scores over time to track improvement.

**Error Responses:**

*Standards Not Found:*
```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: Standards directory not found: C:/Users/willh/my-react-app/coderef/standards\n\nSuggestion: Run establish_standards tool first to generate standards documents"
      }
    ]
  }
}
```

**Consistency Trilogy Workflow:**
```
┌─────────────────────────────────────────────────────────┐
│ 1. establish_standards (Tool #8) - Run ONCE            │
│    → Creates: UI-STANDARDS.md, BEHAVIOR-STANDARDS.md   │
│              UX-PATTERNS.md, COMPONENT-INDEX.md         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. audit_codebase (Tool #9) - Run PERIODICALLY         │
│    → Scans codebase against standards                  │
│    → Generates compliance report                        │
│    → Identifies violations with fix suggestions         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Fix violations and improve compliance score         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Re-run audit_codebase to verify improvements        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. check_consistency (Tool #10) - Coming soon          │
│    → Quality gate for new code during development      │
└─────────────────────────────────────────────────────────┘
```

---

### Category 4: Planning Workflow Tools (4 tools)

The **Planning Workflow** pattern: TEMPLATE (get_planning_template) + ANALYZE (analyze_project_for_planning) + VALIDATE (validate_implementation_plan) + REVIEW (generate_plan_review_report)

---

### 10. get_planning_template (📋 TEMPLATE - Reference)

Returns the feature implementation planning template or specific sections for AI reference during plan creation.

**Tool Name:** `get_planning_template`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "section": {
      "type": "string",
      "enum": ["all", "0_preparation", "1_executive_summary", "2_risk_assessment", "3_current_state_analysis", "4_key_features", "5_task_id_system", "6_implementation_phases", "7_testing_strategy", "8_success_criteria", "9_implementation_checklist"],
      "description": "Which section to return (default: 'all')",
      "default": "all"
    }
  },
  "required": []
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 13,
  "method": "tools/call",
  "params": {
    "name": "get_planning_template",
    "arguments": {
      "section": "all"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 13,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Feature Implementation Planning Template v1.1.0\n\nStructure:\n- 0_preparation: Foundation docs, standards, patterns\n- 1_executive_summary: Feature overview, value prop, use cases\n- 2_risk_assessment: Complexity, risks, mitigation\n- 3_current_state_analysis: Affected files, dependencies\n- 4_key_features: Core capabilities\n- 5_task_id_system: Task prefix and format\n- 6_implementation_phases: Phased tasks with dependencies\n- 7_testing_strategy: Unit, integration, edge cases\n- 8_success_criteria: Measurable success metrics\n- 9_implementation_checklist: Complete task list\n\n[Full template JSON structure...]"
      }
    ]
  }
}
```

**Use Case:** Reference template structure before creating implementation plan. View specific sections to understand requirements.

---

### 11. analyze_project_for_planning (🔍 ANALYZE - Step 1)

Analyzes project to discover foundation docs, coding standards, reference components, and patterns. Automates section 0 (Preparation) of planning template. Run before creating implementation plans.

**Tool Name:** `analyze_project_for_planning`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory to analyze"
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 14,
  "method": "tools/call",
  "params": {
    "name": "analyze_project_for_planning",
    "arguments": {
      "project_path": "C:/Users/willh/my-project"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 14,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"foundation_docs\": {\n    \"available\": [\"README.md\", \"ARCHITECTURE.md\", \"API.md\"],\n    \"missing\": [\"COMPONENTS.md\", \"SCHEMA.md\"]\n  },\n  \"coding_standards\": {\n    \"available\": [\"BEHAVIOR-STANDARDS.md\"],\n    \"missing\": [\"COMPONENT-PATTERN.md\"]\n  },\n  \"reference_components\": {\n    \"primary\": \"generators/changelog_generator.py\",\n    \"secondary\": [\"generators/base_generator.py\"]\n  },\n  \"key_patterns_identified\": [\n    \"ErrorResponse factory pattern (ARCH-001)\",\n    \"Handler registry pattern (QUA-002)\",\n    \"TypedDict return types (QUA-001)\"\n  ],\n  \"technology_stack\": {\n    \"language\": \"Python 3.11+\",\n    \"framework\": \"MCP SDK\",\n    \"testing\": \"pytest\",\n    \"dependencies\": [\"mcp\", \"pathlib\", \"json\"]\n  },\n  \"project_structure\": {\n    \"root_files\": [\"server.py\", \"tool_handlers.py\"],\n    \"key_directories\": [\"generators/\", \"templates/\", \"coderef/\"]\n  },\n  \"gaps_and_risks\": [\n    \"Missing COMPONENTS.md documentation\",\n    \"No test coverage for new feature\"\n  ]\n}"
      }
    ]
  }
}
```

**Performance:** ~80ms for small projects (<200 files), ~1-2 seconds for medium projects (200-1000 files)

**Use Case:** Gather project context before creating implementation plan. Discovers what standards, patterns, and docs exist to inform planning.

---

### 12. validate_implementation_plan (✅ VALIDATE - Step 2)

Validates implementation plan JSON against quality checklist. Scores 0-100 and identifies issues by severity. Enables iterative review loops until plan quality reaches threshold (≥90 recommended).

**Tool Name:** `validate_implementation_plan`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "plan_file_path": {
      "type": "string",
      "description": "Path to plan JSON file (must be within project directory)"
    }
  },
  "required": ["project_path", "plan_file_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 15,
  "method": "tools/call",
  "params": {
    "name": "validate_implementation_plan",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "plan_file_path": "feature-auth-plan.json"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 15,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"score\": 88,\n  \"validation_result\": \"PASS_WITH_WARNINGS\",\n  \"approved\": false,\n  \"issues\": [\n    {\n      \"severity\": \"minor\",\n      \"section\": \"6_implementation_phases\",\n      \"issue\": \"Task AUTH-003 description is only 18 words (minimum 20 recommended)\",\n      \"suggestion\": \"Expand task description to include more implementation details\"\n    },\n    {\n      \"severity\": \"minor\",\n      \"section\": \"7_testing_strategy\",\n      \"issue\": \"Only 4 edge cases listed (5-10 recommended)\",\n      \"suggestion\": \"Add more edge case scenarios (e.g., null inputs, boundary conditions)\"\n    }\n  ],\n  \"checklist_results\": {\n    \"structure\": {\"passed\": 10, \"failed\": 0},\n    \"completeness\": {\"passed\": 15, \"failed\": 0},\n    \"quality\": {\"passed\": 18, \"failed\": 2},\n    \"autonomy\": {\"passed\": 8, \"failed\": 0}\n  }\n}"
      }
    ]
  }
}
```

**Scoring Algorithm:**
```
Score = 100 - (10 × critical_issues + 5 × major_issues + 1 × minor_issues)
```

**Result Types:**
- **PASS** (score ≥ 90): Plan approved for implementation
- **PASS_WITH_WARNINGS** (85 ≤ score < 90): Plan acceptable, minor improvements recommended
- **NEEDS_REVISION** (70 ≤ score < 85): Plan needs refinement before implementation
- **FAIL** (score < 70): Plan has critical issues, significant rework required

**Validation Categories:**
- **Structure:** All required sections (0-9) present and properly formatted
- **Completeness:** No placeholders, all fields filled, task IDs present
- **Quality:** Task descriptions ≥20 words, success criteria measurable, 5-10 edge cases
- **Autonomy:** Plan implementable without clarification, zero ambiguity

**Performance:** < 20ms (fast JSON validation, suitable for iterative review loops)

**Use Case:** Validate plan quality during creation. Iterate until score ≥ 90 before presenting to user.

---

### 13. generate_plan_review_report (📄 REVIEW - Step 3)

Generates markdown review report from validation results. Formats score, issues by severity, and actionable recommendations into user-friendly report.

**Tool Name:** `generate_plan_review_report`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "plan_file_path": {
      "type": "string",
      "description": "Path to plan JSON file"
    },
    "output_path": {
      "type": "string",
      "description": "Path where to save the markdown report"
    }
  },
  "required": ["project_path", "plan_file_path", "output_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 16,
  "method": "tools/call",
  "params": {
    "name": "generate_plan_review_report",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "plan_file_path": "feature-auth-plan.json",
      "output_path": "review-report.md"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 16,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "✅ Review report generated successfully!\n\nPlan: feature-auth-plan.json\nScore: 88/100 (PASS_WITH_WARNINGS)\nReport: C:/Users/willh/my-project/review-report.md\n\nSummary:\n- Issues found: 2 (0 critical, 0 major, 2 minor)\n- Approval status: Not approved (score < 90)\n- Recommendation: Address minor issues to reach approval threshold"
      }
    ]
  }
}
```

**Report Format:**
Generated markdown report includes:
- **Summary**: Score, result type, approval status
- **Critical Issues**: Show-stoppers that must be fixed
- **Major Issues**: Significant problems requiring attention
- **Minor Issues**: Small improvements for quality
- **Recommendations**: Actionable steps to improve score
- **Approval Status**: APPROVED FOR IMPLEMENTATION or NOT APPROVED with explanation

**Performance:** < 5ms (fast report formatting)

**Use Case:** Format validation results for user review. Present plan quality in readable format before execution.

---

**Planning Workflow Pattern (6 Steps):**
```
┌─────────────────────────────────────────────────────────┐
│ User: "Create implementation plan for feature X"        │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 1: analyze_project_for_planning                    │
│   → Discovers foundation docs, standards, patterns      │
│   → Returns: PreparationSummaryDict (section 0 done!)   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 2: AI generates plan using template + analysis     │
│   → Fills all 10 sections of planning template          │
│   → Saves to: feature-X-plan.json                       │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 3: validate_implementation_plan                     │
│   → Scores plan (0-100)                                 │
│   → Returns: Score, issues, approval status             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ REVIEW LOOP: If score < 90                              │
│   → AI analyzes issues                                  │
│   → AI refines plan to fix issues                       │
│   → Re-validate (iterate up to 5 times)                 │
│   → Continue until score ≥ 90                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 4: generate_plan_review_report                     │
│   → Formats validation results as markdown              │
│   → Shows score, issues, recommendations                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 5: USER APPROVAL GATE ◄── MANDATORY                │
│   → User reviews plan and report                        │
│   → User approves OR requests changes                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 6: Execute approved plan                           │
│   → AI implements following approved plan               │
│   → Updates checklist as tasks complete                 │
└─────────────────────────────────────────────────────────┘
```

**Key Principles:**
- **Automation:** analyze_project_for_planning reduces planning time by 60-70%
- **Quality:** Validation ensures plans score ≥90 before user sees them
- **Iterative:** Review loop prevents flawed plans from reaching execution
- **User Control:** Mandatory approval gate gives final authority

---

### Category 5: Project Inventory (2 tools)

---

### 14. inventory_manifest (📦 INVENTORY - File Catalog)

Generates comprehensive project file inventory manifest. Creates detailed catalog of all project files with metadata (size, lines, category, risk level, dependencies), categorizes files using universal taxonomy, calculates project metrics, and saves manifest to `coderef/inventory/manifest.json`.

**Tool Name:** `inventory_manifest`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory to inventory"
    },
    "analysis_depth": {
      "type": "string",
      "enum": ["quick", "standard", "deep"],
      "description": "Analysis depth: quick (basic metadata only), standard (+ categorization & basic dependencies), deep (+ full dependency parsing). Default: standard",
      "default": "standard"
    },
    "exclude_dirs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Optional: List of directory names to exclude (e.g., node_modules, .git). Default: common exclusions"
    },
    "max_file_size": {
      "type": "integer",
      "description": "Optional: Maximum file size to process in bytes. Default: 10MB",
      "minimum": 0
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 17,
  "method": "tools/call",
  "params": {
    "name": "inventory_manifest",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "analysis_depth": "standard"
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 17,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"manifest_path\": \"coderef/inventory/manifest.json\",\n  \"files_analyzed\": 143,\n  \"project_name\": \"my-project\",\n  \"analysis_depth\": \"standard\",\n  \"metrics\": {\n    \"total_files\": 143,\n    \"total_size\": 524288,\n    \"total_lines\": 12450,\n    \"file_categories\": {\n      \"core\": 2,\n      \"source\": 87,\n      \"template\": 5,\n      \"config\": 12,\n      \"test\": 23,\n      \"docs\": 14\n    },\n    \"risk_distribution\": {\n      \"low\": 112,\n      \"medium\": 25,\n      \"high\": 5,\n      \"critical\": 1\n    },\n    \"language_breakdown\": {\n      \"Python\": 87,\n      \"JavaScript\": 15,\n      \"Markdown\": 14,\n      \"JSON\": 12,\n      \"YAML\": 8\n    }\n  },\n  \"success\": true\n}"
      }
    ]
  }
}
```

**Manifest Structure** (saved to `coderef/inventory/manifest.json`):
```json
{
  "project_name": "my-project",
  "project_path": "C:/Users/willh/my-project",
  "generated_at": "2025-10-14T15:30:22.123456",
  "analysis_depth": "standard",
  "metrics": {
    "total_files": 143,
    "total_size": 524288,
    "total_lines": 12450,
    "file_categories": {...},
    "risk_distribution": {...},
    "language_breakdown": {...}
  },
  "files": [
    {
      "path": "server.py",
      "name": "server.py",
      "extension": ".py",
      "size": 12450,
      "lines": 497,
      "category": "core",
      "risk_level": "high",
      "dependencies": ["mcp", "pathlib", "json"],
      "last_modified": "2025-10-14T14:22:15",
      "language": "Python"
    }
  ]
}
```

**File Categories** (Universal Taxonomy):
- **core**: Core infrastructure (server, main entry points)
- **source**: Source code files (business logic, modules)
- **template**: Templates and static resources
- **config**: Configuration files
- **test**: Test files
- **docs**: Documentation files

**Risk Levels** (Calculated based on size, complexity, sensitivity):
- **low**: Small, simple files with minimal impact
- **medium**: Moderate complexity or moderate impact
- **high**: Complex or high-impact files
- **critical**: Critical infrastructure or security-sensitive (e.g., .env, credentials)

**Analysis Depth Options:**
- **quick**: Basic metadata only (size, lines, timestamps) - fastest
- **standard**: + File categorization + Basic dependency detection - recommended
- **deep**: + Full dependency parsing for all supported languages - most comprehensive

**Performance:**
- **quick**: ~1-2 seconds for 200 files
- **standard**: ~3-5 seconds for 200 files
- **deep**: ~5-10 seconds for 200 files

**Use Cases:**
- **Project X-ray**: Get comprehensive overview of project structure and composition
- **Dependency Analysis**: Understand which external packages are used
- **Risk Assessment**: Identify high-risk or security-sensitive files
- **Documentation**: Generate file catalogs for project documentation
- **Onboarding**: Help new team members understand project structure

**Supported Languages** (Dependency Analysis):
- Python (.py): import/from statements
- JavaScript/TypeScript (.js, .ts, .jsx, .tsx): import/require/dynamic imports
- More languages coming in future iterations

---

### 15. dependency_inventory (🔐 SECURITY - Dependency Analysis)

Analyzes project dependencies across multiple package ecosystems with integrated security vulnerability scanning. Detects package managers (npm, pip, cargo, composer), parses dependency manifests, scans for vulnerabilities via OSV API, checks for outdated packages, and generates comprehensive dependency report saved to `coderef/inventory/dependencies.json`.

**Tool Name:** `dependency_inventory`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory to analyze"
    },
    "scan_security": {
      "type": "boolean",
      "description": "Enable security vulnerability scanning via OSV API. Default: true",
      "default": true
    },
    "ecosystems": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["npm", "pip", "cargo", "composer", "all"]
      },
      "description": "Package ecosystems to analyze. Default: ['all']",
      "default": ["all"]
    },
    "include_transitive": {
      "type": "boolean",
      "description": "Include transitive dependencies (requires lockfiles). Default: false",
      "default": false
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 18,
  "method": "tools/call",
  "params": {
    "name": "dependency_inventory",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "scan_security": true,
      "ecosystems": ["all"],
      "include_transitive": false
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 18,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"manifest_path\": \"coderef/inventory/dependencies.json\",\n  \"package_managers\": [\"npm\", \"pip\"],\n  \"total_dependencies\": 127,\n  \"vulnerable_count\": 3,\n  \"outdated_count\": 18,\n  \"metrics\": {\n    \"total_dependencies\": 127,\n    \"direct_count\": 45,\n    \"dev_count\": 82,\n    \"outdated_count\": 18,\n    \"vulnerable_count\": 3,\n    \"critical_vulnerabilities\": 0,\n    \"high_vulnerabilities\": 1,\n    \"medium_vulnerabilities\": 2,\n    \"low_vulnerabilities\": 0,\n    \"ecosystem_breakdown\": {\"npm\": 85, \"pip\": 42}\n  },\n  \"success\": true\n}"
      }
    ]
  }
}
```

**Dependency Manifest Structure** (saved to `coderef/inventory/dependencies.json`):
```json
{
  "project_name": "my-project",
  "project_path": "C:/Users/willh/my-project",
  "generated_at": "2025-10-15T00:15:22.123456",
  "package_managers": ["npm", "pip"],
  "dependencies": {
    "npm": {
      "direct": [
        {
          "name": "express",
          "version": "4.18.2",
          "type": "direct",
          "ecosystem": "npm",
          "latest_version": "4.19.0",
          "outdated": true,
          "license": "MIT",
          "vulnerabilities": [],
          "vulnerability_count": 0
        }
      ],
      "dev": [
        {
          "name": "jest",
          "version": "29.5.0",
          "type": "dev",
          "ecosystem": "npm",
          "latest_version": "29.7.0",
          "outdated": true,
          "license": "MIT",
          "vulnerabilities": ["CVE-2024-12345"],
          "vulnerability_count": 1,
          "severity": "medium"
        }
      ]
    },
    "pip": {
      "direct": [
        {
          "name": "flask",
          "version": "2.3.0",
          "type": "direct",
          "ecosystem": "pip",
          "latest_version": "3.0.0",
          "outdated": true,
          "license": "BSD-3-Clause",
          "vulnerabilities": [],
          "vulnerability_count": 0
        }
      ]
    }
  },
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "package_name": "jest",
      "ecosystem": "npm",
      "severity": "medium",
      "summary": "Prototype pollution in jest config loader",
      "affected_versions": "<29.6.0",
      "fixed_version": "29.6.0",
      "cvss_score": 5.3,
      "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-12345"]
    }
  ],
  "metrics": {
    "total_dependencies": 127,
    "direct_count": 45,
    "dev_count": 82,
    "outdated_count": 18,
    "vulnerable_count": 3,
    "critical_vulnerabilities": 0,
    "high_vulnerabilities": 1,
    "medium_vulnerabilities": 2,
    "low_vulnerabilities": 0,
    "license_breakdown": {
      "MIT": 98,
      "BSD-3-Clause": 15,
      "Apache-2.0": 14
    },
    "ecosystem_breakdown": {
      "npm": 85,
      "pip": 42
    }
  }
}
```

**Package Ecosystems** (Multi-Ecosystem Support):
- **npm** (Node.js): Parses `package.json` for direct, dev, and peer dependencies
- **pip** (Python): Parses `requirements.txt` and `pyproject.toml` for dependencies
- **cargo** (Rust): Parses `Cargo.toml` for direct and dev dependencies
- **composer** (PHP): Parses `composer.json` for direct and dev dependencies

**Dependency Types**:
- **direct**: Production dependencies (required for runtime)
- **dev**: Development dependencies (testing, building, tooling)
- **peer**: Peer dependencies (npm only - expected to be provided by consumer)
- **transitive**: Indirect dependencies (requires lockfiles: package-lock.json, Cargo.lock, etc.)

**Security Scanning** (OSV API Integration):
- **Vulnerability Detection**: Scans all ecosystems via [OSV.dev](https://osv.dev) database
- **CVE Identification**: Returns CVE IDs, severity levels, CVSS scores
- **Fix Recommendations**: Identifies fixed versions and upgrade paths
- **Severity Levels**: Critical (CVSS 9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.1-3.9)
- **Performance**: ~200-500ms per ecosystem (parallel API requests)

**Version Analysis**:
- **Latest Version Check**: Queries package registries (npm Registry, PyPI, crates.io, Packagist)
- **Outdated Detection**: Compares installed vs latest versions
- **Semantic Versioning**: Respects version constraints and ranges
- **Update Recommendations**: Flags packages needing updates

**Performance:**
- **Without Security Scan**: ~1-2 seconds for 100 dependencies
- **With Security Scan**: ~3-5 seconds for 100 dependencies (OSV API latency)
- **Multi-Ecosystem**: Parallel processing across detected package managers

**Use Cases:**
- **Security Audit**: Identify vulnerable dependencies and CVEs
- **Dependency Review**: Track outdated packages and update candidates
- **License Compliance**: Audit dependency licenses for compatibility
- **Onboarding**: Understand project's dependency footprint
- **CI/CD Integration**: Automate security scanning in build pipelines
- **Supply Chain Security**: Monitor dependency health over time

**Supported Manifest Files**:
- **npm**: `package.json` (required), `package-lock.json` (optional for transitive)
- **pip**: `requirements.txt`, `pyproject.toml`, `Pipfile`
- **cargo**: `Cargo.toml` (required), `Cargo.lock` (optional for transitive)
- **composer**: `composer.json` (required), `composer.lock` (optional for transitive)

**External API Dependencies**:
- **OSV API** (https://api.osv.dev/v1/query): Vulnerability database (all ecosystems)
- **npm Registry** (https://registry.npmjs.org/): Package metadata and versions
- **PyPI API** (https://pypi.org/pypi/): Python package metadata
- **crates.io API**: Rust package metadata
- **Packagist API**: PHP package metadata

**Error Handling:**

*No Package Managers Detected:*
```json
{
  "jsonrpc": "2.0",
  "id": 18,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: No package managers detected in project\n\nSuggestion: Ensure project contains at least one of: package.json, requirements.txt, Cargo.toml, composer.json"
      }
    ]
  }
}
```

*OSV API Failure (Non-Fatal):*
```json
{
  "jsonrpc": "2.0",
  "id": 18,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "⚠️ Security scanning partially failed\n\n127 dependencies analyzed\nVulnerability scan failed for npm ecosystem (OSV API timeout)\nAll other ecosystems scanned successfully\n\nManifest saved to: coderef/inventory/dependencies.json"
      }
    ]
  }
}
```

**Security Considerations:**
- **API Rate Limits**: OSV API has no official rate limits (as of 2025-10)
- **Privacy**: Package names/versions sent to external APIs (OSV, npm, PyPI)
- **Network Required**: Requires internet access for vulnerability scanning and version checks
- **Offline Mode**: Set `scan_security=false` to skip external API calls (no vulnerabilities, no latest versions)

---

### 16. api_inventory (🔌 API ENDPOINTS - Multi-Framework Discovery)

Discovers API endpoints across multiple frameworks (FastAPI, Flask, Express, GraphQL) using AST parsing and regex extraction. Parses OpenAPI/Swagger documentation for coverage analysis. Generates comprehensive API manifest with endpoint metadata, documentation status, and framework breakdown saved to `coderef/inventory/api.json`.

**Tool Name:** `api_inventory`

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_path": {
      "type": "string",
      "description": "Absolute path to project directory to analyze"
    },
    "frameworks": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["fastapi", "flask", "express", "graphql", "all"]
      },
      "description": "Which API frameworks to detect. Default: ['all']",
      "default": ["all"]
    },
    "include_graphql": {
      "type": "boolean",
      "description": "Whether to parse GraphQL schemas. Default: false",
      "default": false
    },
    "scan_documentation": {
      "type": "boolean",
      "description": "Whether to scan for OpenAPI/Swagger documentation files. Default: true",
      "default": true
    }
  },
  "required": ["project_path"]
}
```

**Request Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 19,
  "method": "tools/call",
  "params": {
    "name": "api_inventory",
    "arguments": {
      "project_path": "C:/Users/willh/my-project",
      "frameworks": ["all"],
      "include_graphql": false,
      "scan_documentation": true
    }
  }
}
```

**Success Response Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 19,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"manifest_path\": \"coderef/inventory/api.json\",\n  \"frameworks\": [\"fastapi\", \"flask\"],\n  \"total_endpoints\": 48,\n  \"documented_endpoints\": 32,\n  \"documentation_coverage\": 67,\n  \"metrics\": {\n    \"total_endpoints\": 48,\n    \"documented_endpoints\": 32,\n    \"documentation_coverage\": 67,\n    \"frameworks_detected\": [\"fastapi\", \"flask\"],\n    \"framework_breakdown\": {\n      \"fastapi\": 35,\n      \"flask\": 13\n    },\n    \"method_breakdown\": {\n      \"GET\": 22,\n      \"POST\": 15,\n      \"PUT\": 7,\n      \"DELETE\": 4\n    },\n    \"rest_endpoints\": 48,\n    \"graphql_endpoints\": 0\n  },\n  \"success\": true\n}"
      }
    ]
  }
}
```

**API Manifest Structure** (saved to `coderef/inventory/api.json`):
```json
{
  "project_name": "my-project",
  "project_path": "C:/Users/willh/my-project",
  "generated_at": "2025-10-15T01:30:22.123456",
  "frameworks": ["fastapi", "flask"],
  "endpoints": [
    {
      "path": "/api/users/{id}",
      "method": "GET",
      "framework": "fastapi",
      "file": "api/routes/users.py",
      "line": 45,
      "function": "get_user",
      "parameters": ["id", "include_details"],
      "documented": true,
      "doc_coverage": 100,
      "description": "Retrieve user by ID",
      "summary": "Get User",
      "tags": ["users"],
      "deprecated": false
    }
  ],
  "metrics": {
    "total_endpoints": 48,
    "documented_endpoints": 32,
    "documentation_coverage": 67,
    "frameworks_detected": ["fastapi", "flask"],
    "framework_breakdown": {"fastapi": 35, "flask": 13},
    "method_breakdown": {"GET": 22, "POST": 15, "PUT": 7, "DELETE": 4},
    "rest_endpoints": 48,
    "graphql_endpoints": 0
  }
}
```

**Framework Detection Methods**:
- **FastAPI (Python)**: AST parsing of `@app.get`, `@app.post`, etc. decorators
- **Flask (Python)**: AST parsing of `@app.route` decorators with methods parameter
- **Express (JavaScript)**: Regex matching of `app.get()`, `app.post()`, etc.
- **GraphQL**: Regex parsing of `.graphql` files for Query and Mutation types

**Documentation Coverage Analysis**:
- **OpenAPI/Swagger Parsing**: Scans for `openapi.yaml`, `swagger.json`, `openapi.json`
- **Coverage Calculation**: Matches OpenAPI docs to source endpoints
- **Doc Score**: 0-100 percentage of documented vs undocumented endpoints
- **Metadata Extraction**: Description, summary, tags, deprecated flag from OpenAPI

**Endpoint Metadata**:
- **Path**: Endpoint route (e.g., `/api/users/{id}`)
- **Method**: HTTP verb (GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD)
- **Framework**: Detected framework (fastapi, flask, express, graphql)
- **Location**: File path and line number where endpoint is defined
- **Function**: Handler function name
- **Parameters**: List of function parameters
- **Documentation**: Whether endpoint has docstring/comments
- **OpenAPI Fields**: Description, summary, tags, deprecated status (if available)

**Performance:**
- **Small Projects** (<50 endpoints): ~200-500ms
- **Medium Projects** (50-200 endpoints): ~1-2 seconds
- **Large Projects** (200+ endpoints): ~2-5 seconds
- **With OpenAPI Parsing**: +100-300ms overhead

**Use Cases:**
- **API Documentation**: Generate comprehensive endpoint catalog
- **Coverage Analysis**: Track which endpoints lack documentation
- **API Auditing**: Identify undocumented or deprecated endpoints
- **Framework Migration**: Understand endpoint distribution before refactoring
- **OpenAPI Compliance**: Verify all endpoints have OpenAPI/Swagger docs

**Framework-Specific Features:**

*FastAPI:*
- Extracts: Path parameters, query parameters, request body
- Supports: All HTTP methods, async/sync handlers
- Documentation: Docstrings and OpenAPI integration

*Flask:*
- Extracts: Route methods parameter, URL variables
- Supports: Multiple methods per route
- Documentation: Docstrings and function comments

*Express:*
- Extracts: Route definitions, middleware chains
- Supports: All HTTP methods, router objects
- Documentation: JSDoc comments and OpenAPI

*GraphQL:*
- Extracts: Query and Mutation types from .graphql schemas
- Supports: Type definitions, resolvers
- Documentation: Schema descriptions and comments

**Error Handling:**

*No Frameworks Detected:*
```json
{
  "jsonrpc": "2.0",
  "id": 19,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error: No API frameworks detected in project\n\nSuggestion: Ensure project contains FastAPI, Flask, Express, or GraphQL code"
      }
    ]
  }
}
```

*OpenAPI Parse Failure (Non-Fatal):*
```json
{
  "jsonrpc": "2.0",
  "id": 19,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "⚠️ OpenAPI documentation parsing failed\n\n48 endpoints discovered\nOpenAPI file found but parsing failed (invalid YAML syntax)\nDocumentation coverage calculation skipped\n\nManifest saved to: coderef/inventory/api.json"
      }
    ]
  }
}
```

**Dependencies:**
- **pyyaml**: Required for OpenAPI/Swagger YAML parsing
- Install: `pip install pyyaml>=6.0`

**Supported Files:**
- **Python**: `*.py` files with FastAPI/Flask decorators
- **JavaScript**: `*.js`, `*.ts` files with Express routes
- **GraphQL**: `*.graphql`, `*.gql` schema files
- **OpenAPI**: `openapi.yaml`, `openapi.json`, `swagger.json`

---

## Error Handling

### Error Response Pattern

All errors are returned as successful JSON-RPC responses with error messages in the TextContent:

```json
{
  "jsonrpc": "2.0",
  "id": <request_id>,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Error <operation>: <error_message>"
      }
    ]
  }
}
```

**Design Rationale:** Server never crashes on tool errors; all exceptions are caught and returned as TextContent messages.

### Common Error Types

| Error Type | Cause | Example Message |
|------------|-------|-----------------|
| **Invalid Version** | Version doesn't match X.Y.Z pattern | `Error: Version must match pattern: X.Y.Z` |
| **Template Not Found** | Invalid template name or missing file | `Template 'xyz' not found. Available: readme, architecture, ...` |
| **Changelog Not Found** | No CHANGELOG.json exists in project | `Changelog not found at: project/coderef/changelog/CHANGELOG.json` |
| **Schema Validation** | Entry doesn't match schema | `Schema validation failed: 'files' is required` |
| **File Read Error** | Permission or I/O error | `Error reading template: Permission denied` |
| **JSON Parse Error** | Malformed CHANGELOG.json | `Error parsing changelog: Invalid JSON` |

---

## Data Types & Schemas

### Changelog JSON Schema

**Location:** `coderef/changelog/schema.json`

**Structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["project", "changelog_version", "current_version", "entries"],
  "properties": {
    "$schema": {"type": "string"},
    "project": {"type": "string"},
    "changelog_version": {"type": "string"},
    "current_version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["version", "date", "summary", "changes", "contributors"],
        "properties": {
          "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
          "date": {"type": "string", "format": "date"},
          "summary": {"type": "string"},
          "changes": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "type", "severity", "title", "description", "files", "reason", "impact", "breaking"],
              "properties": {
                "id": {"type": "string", "pattern": "^change-[0-9]{3}$"},
                "type": {"enum": ["bugfix", "enhancement", "feature", "breaking_change", "deprecation", "security"]},
                "severity": {"enum": ["critical", "major", "minor", "patch"]},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
                "reason": {"type": "string"},
                "impact": {"type": "string"},
                "breaking": {"type": "boolean"},
                "migration": {"type": "string"}
              }
            }
          },
          "contributors": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

**Example CHANGELOG.json:**
```json
{
  "$schema": "./schema.json",
  "project": "my-project",
  "changelog_version": "1.0",
  "current_version": "1.0.3",
  "entries": [
    {
      "version": "1.0.3",
      "date": "2025-10-09",
      "summary": "Added feature X",
      "changes": [
        {
          "id": "change-001",
          "type": "feature",
          "severity": "major",
          "title": "Added feature X",
          "description": "Implemented...",
          "files": ["server.py"],
          "reason": "Enable users to...",
          "impact": "Users can now...",
          "breaking": false
        }
      ],
      "contributors": ["willh"]
    }
  ]
}
```

---

## Change Types Reference

| Type | When to Use | Example |
|------|------------|---------|
| `bugfix` | Fixed a bug or error | "Fixed crash when..." |
| `enhancement` | Improved existing functionality | "Improved performance of..." |
| `feature` | Added new functionality | "Added support for..." |
| `breaking_change` | Incompatible API changes | "Changed API signature..." |
| `deprecation` | Marked features for removal | "Deprecated X in favor of Y" |
| `security` | Security patches | "Patched vulnerability..." |

## Severity Levels Reference

| Severity | Impact | Example |
|----------|--------|---------|
| `critical` | System broken, data loss risk | "Fixed data corruption bug" |
| `major` | Significant feature impact | "Added new MCP tool" |
| `minor` | Small improvements | "Improved error messages" |
| `patch` | Cosmetic, docs-only | "Fixed typo in template" |

---

## Usage Examples

### Example 1: Complete Documentation Setup

**Scenario:** Bootstrap documentation for a new project

```python
# Step 1: Discover available templates
list_templates()
# Returns: 6 templates available

# Step 2: Generate all foundation docs
generate_foundation_docs(project_path="C:/Users/willh/my-project")
# Returns: Generation plan with all 6 templates

# Step 3: Agent analyzes project and generates docs
# Creates: README.md, ARCHITECTURE.md, API.md, COMPONENTS.md, SCHEMA.md, USER-GUIDE.md
```

---

### Example 2: Update Single Documentation File

**Scenario:** Regenerate API.md after adding new endpoints

```python
# Generate individual document
generate_individual_doc(
    project_path="C:/Users/willh/my-project",
    template_name="api"
)
# Returns: API template and instructions
# Agent generates updated API.md
```

---

### Example 3: Changelog Query and Update

**Scenario:** Review breaking changes and add new entry

```python
# Step 1: Check for breaking changes
get_changelog(
    project_path="C:/Users/willh/my-project",
    breaking_only=true
)
# Returns: List of all breaking changes

# Step 2: Add new changelog entry
add_changelog_entry(
    project_path="C:/Users/willh/my-project",
    version="1.0.4",
    change_type="feature",
    severity="major",
    title="Added webhook support",
    description="Implemented webhook system with...",
    files=["server.py", "webhooks.py"],
    reason="Enable real-time notifications",
    impact="Users can now receive instant updates",
    breaking=false,
    contributors=["willh"]
)
# Returns: ✅ Changelog entry added successfully!
```

---

### Example 4: Agentic Self-Documentation

**Scenario:** Agent autonomously documents its own changes

```python
# Agent makes changes to project
# ...changes made...

# Agent calls update_changelog for instructions
update_changelog(
    project_path="C:/Users/willh/my-project",
    version="1.0.4"
)
# Returns: 3-step instructions

# Agent analyzes its own changes
# Agent determines: type=feature, severity=major, files=[...], etc.

# Agent executes add_changelog_entry autonomously
add_changelog_entry(
    project_path="C:/Users/willh/my-project",
    version="1.0.4",
    # ...parameters determined by agent's analysis...
)
# Returns: ✅ Changelog updated!
```

---

## Client Integration

### Python Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_docs_mcp():
    server_params = StdioServerParameters(
        command="python",
        args=["C:\\Users\\willh\\.mcp-servers\\docs-mcp\\server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List templates
            result = await session.call_tool("list_templates", {})
            print(result.content[0].text)

            # Get changelog
            result = await session.call_tool("get_changelog", {
                "project_path": "C:/Users/willh/my-project"
            })
            print(result.content[0].text)

            # Add changelog entry
            result = await session.call_tool("add_changelog_entry", {
                "project_path": "C:/Users/willh/my-project",
                "version": "1.0.4",
                "change_type": "feature",
                "severity": "major",
                "title": "Added X",
                "description": "Implemented X...",
                "files": ["server.py"],
                "reason": "Enable Y",
                "impact": "Users can Z",
                "contributors": ["willh"]
            })
            print(result.content[0].text)

asyncio.run(use_docs_mcp())
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "docs-mcp": {
      "command": "python",
      "args": ["C:\\Users\\willh\\.mcp-servers\\docs-mcp\\server.py"]
    }
  }
}
```

**Configuration File Location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

---

## Performance Characteristics

### Response Times
- **list_templates:** < 10ms (directory scan, ~6 files)
- **get_template:** < 20ms (file read, ~5-10KB files)
- **generate_foundation_docs:** < 50ms (read 6 templates)
- **generate_individual_doc:** < 20ms (read 1 template)
- **get_changelog:** < 30ms (JSON parse + filter, ~50KB file)
- **add_changelog_entry:** < 40ms (JSON parse + schema validation + write)
- **update_changelog:** < 5ms (instruction generation only)

**Factors:**
- Local file system I/O (no network latency)
- Small file sizes (< 50KB typical)
- No caching (fresh reads each request)
- Single-threaded async (no parallelization)
- Schema validation overhead for changelog operations

### Scalability
- **Templates:** Scales linearly with number of .txt files
- **Changelog:** Scales linearly with number of entries (~O(n) for filtering)
- **Concurrent Requests:** Single-threaded (one at a time)
- **Memory:** Minimal (< 10MB typical, no persistent caching)

---

## Versioning

**API Version:** 1.1.0
**MCP Protocol:** 1.0
**Server Version:** 1.1.0 (see README.md)

**Version History:**
- **1.1.0:** Interactive HTML tool reference
- **1.0.9:** AI assistant context documentation (CLAUDE.md)
- **1.0.7:** Architecture refactoring (modular handlers, logging, type safety, error factory)
- **1.0.6:** Phase 2 refactoring (constants extraction, input validation layer)
- **1.0.3:** Added update_changelog agentic workflow tool
- **1.0.2:** Added changelog management system (get_changelog, add_changelog_entry)
- **1.0.0:** Initial release with documentation generation tools

**Versioning Policy:**
- **Major version (1.x.x):** Breaking changes to tool schemas or behavior
- **Minor version (x.1.x):** New tools or backward-compatible features
- **Patch version (x.x.1):** Bug fixes, no API changes

**Backward Compatibility:**
- Tool names are stable (no renames without major version bump)
- Input schemas are additive (new optional fields only)
- Output format (TextContent) is stable
- Changelog JSON schema may add optional fields (backward compatible)

---

## Security Considerations

### Access Control
- **Authentication:** None required (local-only stdio transport)
- **Authorization:** Mixed access
  - Documentation tools: Read-only
  - Changelog tools: Read/write to `coderef/changelog/CHANGELOG.json`
- **Scope:** Restricted to project paths specified in parameters

### Input Validation
- **Template Names:** Restricted to enum
- **Version Format:** Validated against pattern `^[0-9]+\.[0-9]+\.[0-9]+$`
- **Change Type/Severity:** Restricted to enums
- **No Path Traversal:** Uses pathlib, validates inputs, no arbitrary paths
- **Schema Validation:** Changelog entries validated against JSON schema

### File System Safety
- **Documentation Tools:** Read-only access
- **Changelog Tools:** Write access limited to `coderef/changelog/CHANGELOG.json`
- **Predefined Paths:** Only accesses `templates/power/` and project-specific `coderef/changelog/`
- **Error Handling:** File errors return messages, never expose sensitive paths

### Transport Security
- **stdio Only:** No network exposure
- **Local Process:** Inherits parent process permissions
- **No Remote Access:** Cannot be accessed over network

**Risk Assessment:** Low-medium risk for local AI assistant integration. Changelog tools have write access but limited to specific directory structure.

---

## Troubleshooting

### Issue: Changelog Not Found

**Symptom:** `Changelog not found at: ...`

**Causes:**
- Project doesn't have `coderef/changelog/CHANGELOG.json`
- Incorrect project_path

**Resolution:**
1. Verify project_path is absolute path to project root
2. Initialize changelog: Create `coderef/changelog/` directory
3. Create CHANGELOG.json with minimal structure:
   ```json
   {
     "$schema": "./schema.json",
     "project": "my-project",
     "changelog_version": "1.0",
     "current_version": "1.0.0",
     "entries": []
   }
   ```

---

### Issue: Schema Validation Failed

**Symptom:** `Schema validation failed: ...`

**Causes:**
- Missing required fields in add_changelog_entry
- Invalid enum values
- Incorrect data types

**Resolution:**
1. Check error message for specific missing field
2. Verify all required parameters: project_path, version, change_type, severity, title, description, files, reason, impact
3. Validate enum values match exactly (case-sensitive)
4. Ensure version matches pattern: X.Y.Z

---

### Issue: Template Not Found

**Symptom:** `Template 'xyz' not found`

**Causes:**
- Invalid template name
- Template file missing

**Resolution:**
1. Use valid template names: readme, architecture, api, components, schema, user-guide
2. Use list_templates to see available options
3. Verify `templates/power/{name}.txt` exists

---

## Related Documentation

- **README.md:** Project overview, installation, quick start, troubleshooting
- **ARCHITECTURE.md:** System topology, generator pattern, meta-tool pattern, changelog trilogy design
- **COMPONENTS.md:** (Future) Component-level documentation
- **SCHEMA.md:** (Future) Complete data schema documentation
- **quickref.md:** Quick reference with all 7 tools and examples
- **user-guide.md:** Comprehensive user guide with best practices

---

## AI Integration Notes

This API is optimized for AI assistant integration. Key patterns for AI clients:

### Tool Discovery
1. Use `list_templates()` to discover available templates
2. Inspect tool schemas via MCP tool listing for input validation
3. Use `get_changelog()` to understand project history

### Workflow Composition

**Documentation Generation:**
1. **Discovery → Retrieval → Generation:** List templates → Get template → Generate docs
2. **Foundation Docs:** Use generate_foundation_docs for complete suite
3. **Individual Docs:** Use generate_individual_doc for specific updates

**Changelog Management:**
1. **Query → Analyze → Update:** Get changelog → Review history → Add entry
2. **Agentic Self-Documentation:** update_changelog → analyze changes → add_changelog_entry
3. **Breaking Change Review:** get_changelog(breaking_only=true) before major releases

### Error Handling
- All errors return TextContent (never exceptions to client)
- Error messages include actionable guidance
- Safe for speculative execution (documentation tools are read-only)
- Changelog tools validate before writing

### Meta-Tool Pattern (update_changelog)
- Tool **instructs** rather than **executes**
- Enables autonomous agent self-documentation
- Agent analyzes context and determines appropriate parameters
- Follow 3-step workflow: Analyze → Determine → Execute

### Performance Optimization
- No caching needed (responses are fast < 50ms)
- Batch template retrievals if generating multiple docs
- No rate limiting concerns for local stdio transport
- Changelog queries filter efficiently (< 30ms)

---

**🤖 This API documentation was generated using the docs-mcp POWER framework API template**

**Architecture Note (v1.0.7+):** The server implementation uses a modular handler registry pattern with comprehensive logging, type safety (TypedDict), consistent error responses (ErrorResponse factory), and boundary validation. See ARCHITECTURE.md for complete design patterns and module documentation.

---

**Maintained by:** willh, Claude Code AI
**Last updated:** 2025-10-11
**Version:** 1.4.0
**Related tools:** 13 MCP tools for documentation, changelog management, consistency auditing, and planning workflow
