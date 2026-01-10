# CodeRef Scanner Integration

**Workorder ID:** WO-SCANNER-001
**Created:** 2026-01-04
**Status:** Not Started

---

## Purpose

Build a full functioning CodeRef scanner on the dashboard by integrating coderef-core scanning logic into the UI, enabling users to scan codebases directly from the dashboard interface.

---

## Agents Involved

| Agent | Role | Output |
|-------|------|--------|
| orchestrator | Coordinate scanner integration across packages and verify end-to-end functionality | orchestrator-output.json |
| coderef-system | Implement coderef package integration layer | coderef-system-output.json |
| coderef-core | Expose core scanning functionality for dashboard consumption | coderef-core-output.json |
| dashboard-scanner | Build UI scanner component consuming coderef-core | dashboard-scanner-output.json |

---

## How It Works

1. **Agents read** communication.json to find their assigned task
2. **Agents follow** instructions.json for step-by-step guidance
3. **Agents create** output files at their designated paths
4. **Orchestrator aggregates** all agent outputs into final synthesis

---

## Files

- **communication.json** - Agent roster, status tracking, output paths
- **instructions.json** - Consolidated instructions for orchestrator + agents
- **README.md** - This file (user documentation)
- **orchestrator-output.json** - Orchestrator's aggregated output
- **coderef-system-output.json** - Integration layer implementation details
- **coderef-core-output.json** - Core scanning API documentation
- **dashboard-scanner-output.json** - UI component implementation details

---

## Execution Steps

### For Agents:

1. Navigate to your agent path (see table above)
2. Open `communication.json`
3. Find your entry in the `agents[]` array
4. Read `instructions.json` → follow `agent_instructions` section
5. Execute your specific task:
   - **coderef-system**: Ensure coderef package bridges coderef-core to dashboard
   - **coderef-core**: Expose core scanning functionality
   - **dashboard-scanner**: Create basic UI component with scan button
6. Create output at your `output_file` path
7. Update your `status` in communication.json: "not_started" → "complete"

### For Orchestrator:

1. Wait for all agents to complete
2. Read all agent output files
3. Follow `orchestrator_instructions` in instructions.json
4. Verify integration works end-to-end
5. Create aggregated output at `orchestrator.output_file` path
6. Update `orchestrator.status` in communication.json

---

## Phase 1 Tasks (Simple & Incremental)

This is **Phase 1** - we're keeping it simple and adding one step at a time.

### coderef-system Agent
- Read coderef-core to understand scanning functions
- Create simple export/re-export if needed
- Document the API surface for dashboard consumption

### coderef-core Agent
- Identify the main scanning entry point (likely `scan()` or similar)
- Ensure it's exported and callable from outside packages
- Document function signature and expected inputs/outputs

### dashboard-scanner Agent
- Create a simple React component in scanner directory
- Import the scanning function from coderef-core (via coderef package)
- Add a button that triggers the scan (hardcoded path for now)
- Display scan results in a simple `<pre>` tag

---

## Current Status

**Not Started** - Agents have not begun execution yet.

Check `communication.json` for real-time progress tracking.

---

## Next Steps (Future Phases)

After Phase 1 completes successfully:
- Phase 2: Add path input field and file browser
- Phase 3: Display results in structured UI (not just `<pre>`)
- Phase 4: Add filtering, sorting, and search capabilities
- Phase 5: Persist scan results and history

---

**Session Directory:** `C:\Users\willh\.mcp-servers\coderef\sessions\coderef-scanner-integration\`
**Agent Paths:**
- coderef-system: `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef`
- coderef-core: `C:\Users\willh\Desktop\coderef-dashboard\packages\coderef-core`
- dashboard-scanner: `C:\Users\willh\Desktop\coderef-dashboard\packages\dashboard\src\app\scanner`
