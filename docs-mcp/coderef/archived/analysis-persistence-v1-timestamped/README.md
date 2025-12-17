# Analysis Persistence v1 - Timestamped Cache Implementation

## Status: ARCHIVED (2025-10-14)

This directory contains documentation for the original timestamped cache implementation of analysis persistence, which was replaced with the feature-specific pattern in v1.4.4.

## Original Design (Implemented but Replaced)

### Pattern
- **Location**: `coderef/analysis-cache/analysis-{timestamp}.json`
- **Timestamp Format**: `YYYYMMDD-HHMMSS` (e.g., `analysis-20251014-153022.json`)
- **Behavior**: Each analysis created a new timestamped file (no overwriting)

### Implementation
```python
# Original code from tool_handlers.py (lines ~1180-1235)
# Created timestamped cache directory and saved analysis with timestamp
cache_dir = project_path_obj / 'coderef' / 'analysis-cache'
cache_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
analysis_file = cache_dir / f'analysis-{timestamp}.json'
```

### Metadata Structure
```json
{
  "_metadata": {
    "saved_to": "coderef/analysis-cache/analysis-20251014-153022.json",
    "generated_at": "2025-10-14T15:30:22.123456"
  }
}
```

### Rationale
- Followed Pattern 2 (project-wide snapshots) similar to audit reports
- Enabled historical analysis comparison
- Provided audit trail of when analyses were run
- Allowed caching for team workflows

## Why It Was Replaced

### Naming Convention Mismatch
The timestamped cache pattern didn't match the project's existing conventions:
- **Feature artifacts** use Pattern 1: `coderef/working/{feature_name}/` without timestamps
  - `context.json` (from /gather-context)
  - `plan.json` (from /create-plan)
- **Project snapshots** use Pattern 2: timestamped files in dedicated directories
  - `coderef/audits/audit-{timestamp}.md`

Analysis is a **feature artifact**, not a project snapshot, so it should follow Pattern 1.

### Data Accumulation Concerns
- 1.6 KB per file
- Potential for hundreds of files over time
- No automatic cleanup mechanism (see Future Enhancement below)

### Workflow Integration
Analysis is part of the feature planning workflow:
1. Gather context → `context.json`
2. Analyze project → `analysis.json` (should be per-feature)
3. Create plan → `plan.json`

All three should live together in the same feature folder.

## Redesign (v1.4.4 Current Implementation)

### New Pattern
- **Location**: `coderef/working/{feature_name}/analysis.json`
- **Parameter**: Optional `feature_name` parameter
- **Behavior**:
  - With `feature_name`: Saves to feature folder (overwrites if exists)
  - Without `feature_name`: Returns without saving (backward compatible)

### Benefits
1. **Consistent naming**: Matches context.json/plan.json pattern
2. **Integrated workflow**: All feature artifacts in one folder
3. **No accumulation**: Single analysis.json per feature (overwrites)
4. **Backward compatible**: Optional parameter, zero breaking changes

## Future Enhancement (Stashed Plan)

### Timestamped Cache with Automatic Cleanup (5-file limit)

If timestamped cache is needed in the future, here's the plan that was stashed:

#### Design
- Keep timestamped cache pattern: `coderef/analysis-cache/analysis-{timestamp}.json`
- Implement automatic cleanup to maintain max 5 files
- Delete oldest files when limit exceeded

#### Implementation Approach
```python
def _cleanup_old_analyses(cache_dir: Path, max_files: int = 5):
    """Keep only the N most recent analysis files."""
    analysis_files = sorted(
        cache_dir.glob('analysis-*.json'),
        key=lambda p: p.stat().st_mtime,
        reverse=True  # Newest first
    )

    # Delete files beyond the limit
    for old_file in analysis_files[max_files:]:
        old_file.unlink()
        logger.info(f"Deleted old analysis file: {old_file.name}")
```

#### When to Use This
- If users need historical analysis comparison (not feature-specific)
- If team workflows require project-wide analysis caching
- If audit trails of analysis runs are important

#### Why It Wasn't Implemented
User decided to go with feature-specific pattern instead:
> "stop. second thought. run it everytime for now. part of the workflow."
> "i want the analysis files saved to the feature folder without a timestamp"

## Migration Notes

### For Users
No migration needed. The v1.4.4 redesign is backward compatible:
- If you were using analyze_project_for_planning without `feature_name`, it still works (returns without saving)
- If you have old `analysis-cache/` files, they won't interfere (different directory)

### For Developers
If you need to restore timestamped cache pattern:
1. Revert `tool_handlers.py` changes in `handle_analyze_project_for_planning`
2. Update `server.py` tool schema to remove `feature_name` parameter
3. Update CLAUDE.md to document timestamped pattern
4. Consider implementing 5-file cleanup from stashed plan above

## Timeline

- **v1.4.4 (Initial)**: Implemented timestamped cache (`analysis-{timestamp}.json`)
- **v1.4.4 (Redesign)**: Replaced with feature-specific pattern (`{feature_name}/analysis.json`)
- **Date**: 2025-10-14
- **Reason**: Naming convention consistency and workflow integration

## References

- Original PR/Issue: [Link if applicable]
- Design Discussion: Conversation on 2025-10-14 about naming patterns
- Test Coverage: `tests/unit/handlers/test_analysis_feature_specific.py` (6 test cases)

---

**Note**: This archive exists for reference only. The current implementation uses feature-specific pattern. If you need timestamped cache behavior, refer to the "Future Enhancement" section above for the planned 5-file cleanup approach.
