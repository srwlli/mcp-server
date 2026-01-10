# Create Context Index

**Workorder ID:** WO-CONTEXT-INDEX-001
**Created:** 2026-01-04
**Status:** Not Started

---

## Purpose

Identify and catalog all reference sheets, documentation files, and other context-rich files across coderef projects that are useful for AI agent context.

---

## Agents Involved

| Agent | Project | Output |
|-------|---------|--------|
| orchestrator | Aggregator | master-context-index.md |
| assistant-coderef-system | coderef-system | coderef-system-index.md |
| assistant-coderef-dashboard | coderef-dashboard | coderef-dashboard-index.md |
| assistant-coderef-core | coderef-core package | coderef-core-index.md |

---

## How It Works

1. **3 Assistant agents** search their assigned project directories for context files
2. **Each agent creates** a simple file list (no descriptions) organized by category
3. **Orchestrator aggregates** all project indexes into a master catalog
4. **Output files** list all discoverable context files for future reference

---

## Files

- **communication.json** - Agent roster, status tracking, output paths
- **instructions.json** - Consolidated instructions for orchestrator + agents
- **README.md** - This file (user documentation)
- **master-context-index.md** - Orchestrator's aggregated catalog
- **coderef-system-index.md** - Files found in coderef-system project
- **coderef-dashboard-index.md** - Files found in coderef-dashboard project
- **coderef-core-index.md** - Files found in coderef-core package

---

## What Agents Search For

**File Types:**
- Markdown files (*.md)
- JSON schemas (*-schema.json)
- Templates (*-template.*)
- Text files (*.txt)
- Documentation folders (docs/, .coderef/, coderef/)

**Specific Files:**
- CLAUDE.md (AI context documentation)
- README.md (project documentation)
- ARCHITECTURE.md (architecture docs)
- API.md (API documentation)
- resource-sheet-*.md (resource sheets)
- reference-*.md (reference guides)
- guide-*.md (guides)
- quickref.md (quick references)
- standards/* (standards documentation)

---

## Output Format

Each project index will be organized by category:

```markdown
# {Project Name} - Context File Index

**Project Path:** {path}
**Generated:** {date}
**Total Files:** {count}

---

## Documentation

- path/to/README.md
- path/to/CLAUDE.md

## Schemas

- path/to/schema.json

## Templates

- path/to/template.md

## Reference Sheets

- path/to/reference.md

## Guides

- path/to/guide.md

## Standards

- path/to/standard.md

## Other

- path/to/notes.txt

---

**Note:** All paths are relative to project root.
```

---

## Execution Steps

### For Agents:

1. Navigate to your project directory (see communication.json)
2. Search for all matching file patterns
3. Organize files by category
4. Create simple list (NO descriptions) in your output file
5. Update your status in communication.json to "complete"

### For Orchestrator:

1. Wait for all 3 agents to complete
2. Read all 3 project index files
3. Combine into master-context-index.md
4. Add summary statistics
5. Update orchestrator.status to "complete"

---

## Project Paths

- **coderef-system**: `C:\Users\willh\Desktop\projects\coderef-system`
- **coderef-dashboard**: `C:\Users\willh\Desktop\coderef-dashboard`
- **coderef-core**: `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core`

---

## Expected Output

After completion, you'll have:

1. **3 project-specific indexes** - Simple file lists for each project
2. **1 master index** - Aggregated catalog across all projects
3. **Complete catalog** - All context-useful files discovered and organized

This index will help agents quickly find relevant documentation, schemas, templates, and reference materials when working on tasks.

---

## Current Status

**Not Started** - Agents have not begun execution yet.

Check `communication.json` for real-time progress tracking.

---

**Session Directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\create-context-index\`
