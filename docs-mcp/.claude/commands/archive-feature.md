Archive completed features from coderef/working/ to coderef/archived/.

Ask the user for the feature name, then call the `mcp__docs-mcp__archive_feature` tool with:
- project_path: current working directory
- feature_name: the user-provided feature name
- force: false (unless user explicitly requests to skip confirmation)

This tool:
1. **Checks completion status** by reading DELIVERABLES.md status line
2. **Prompts for confirmation** if status != Complete (unless force=True)
3. **Moves entire folder** from coderef/working/{feature-name}/ to coderef/archived/{feature-name}/
4. **Updates archive index** at coderef/archived/index.json with metadata

**Status Handling**:
- ✅ Complete → Archives immediately without confirmation
- 🚧 In Progress / Not Started → Prompts user for confirmation
- UNKNOWN (no DELIVERABLES.md) → Prompts user for confirmation

**What gets archived**:
- Entire feature folder with ALL files preserved
- plan.json, DELIVERABLES.md, communication.json, context.json
- All implementation artifacts and working files

**Archive Index**:
Creates/updates coderef/archived/index.json with:
- feature_name: Display name from plan.json META_DOCUMENTATION
- folder_name: Directory name (feature slug)
- archived_at: ISO 8601 timestamp

**Error Handling**:
- Feature not found in working/ → Error
- Feature already exists in archived/ → Error (prevents duplicates)
- Move operation failure → Error with detailed message
- Index update failure → Warning (archive succeeds but index not updated)

**Safety Features**:
- Uses shutil.move() for atomic folder relocation
- Verifies destination exists after move
- No data loss - all files preserved
- Prompts before archiving incomplete work

**When to use**:
Run this command AFTER completing feature implementation and running /update-deliverables.
For best results, ensure DELIVERABLES.md shows status "Complete" before archiving.

**Force Mode**:
To archive without confirmation prompt (skip status check):
Call tool with force=True parameter

Returns:
- Archived path (relative to project root)
- File count (number of files archived)
- Previous status (from DELIVERABLES.md)
- Archive timestamp
- Index update confirmation
