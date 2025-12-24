Create a git release with tag and changelog-based release notes.

This command helps create a proper git release for the current project.

## Workflow

1. **Get Version**: Ask user for version number (e.g., "1.5.0")
2. **Extract Release Notes**: Read CHANGELOG.json for this version
3. **Create Tag**: Create annotated git tag with release notes
4. **Push Tag**: Push tag to remote

## Step-by-Step Instructions

### Step 1: Get Version

Use AskUserQuestion to get the release version:

```
Question: "What version number for this release? (e.g., 1.5.0)"
Header: "Version"
multiSelect: false
Options: [
  {"label": "Patch bump (1.x.Y)", "description": "Bug fixes only"},
  {"label": "Minor bump (1.Y.x)", "description": "New features, backward compatible"},
  {"label": "Major bump (Y.x.x)", "description": "Breaking changes"}
]
```

User types their version in the "Other" field, or selects a bump type and you calculate the next version.

### Step 2: Extract Release Notes

Call `mcp__coderef-docs__get_changelog` to get changes for this version:

```python
mcp__docs_mcp__get_changelog({
    "project_path": <current_working_directory>,
    "version": <version_from_step_1>
})
```

Format the changes into release notes:

```
# Release {version}

## Changes

- {change 1 title}: {description}
- {change 2 title}: {description}

## Contributors

- {contributor list}
```

### Step 3: Create Annotated Tag

Run git commands to create the tag:

```bash
# Create annotated tag with release notes
git tag -a v{version} -m "Release {version}

{release_notes_from_step_2}

Generated with [Claude Code](https://claude.ai/code)"
```

### Step 4: Push Tag

Push the tag to remote:

```bash
git push origin v{version}
```

### Step 5: Output Summary

```
Release Created: v{version}

Tag: v{version}
Pushed: origin/v{version}

Changes Included:
- {change 1}
- {change 2}

Next Steps:
- Create GitHub release from tag (if using GitHub)
- Announce the release
- Update version in package.json/pyproject.toml if needed
```

## When to Use

Use /git-release when:
- You've completed a set of features/fixes and want to tag a release
- You want to generate release notes from the changelog
- You need a standardized release process

## Prerequisites

- Changes documented in CHANGELOG.json (use /update-docs or /add-changelog)
- Clean working directory (no uncommitted changes)
- Git remote configured

## Related Commands

- `/update-docs` - Update changelog after feature completion
- `/add-changelog` - Add manual changelog entry
- `/get-changelog` - View changelog history
