# Knowledge Files for Lloyd GPT

Upload these files to the GPT's Knowledge section to enhance its planning capabilities.

## Required Files

### 1. start-feature-workflow.md
**Source**: `docs-mcp/.claude/commands/start-feature.md`
**Purpose**: Full workflow documentation showing the complete planning pipeline

### 2. gather-context-workflow.md
**Source**: `docs-mcp/.claude/commands/gather-context.md`
**Purpose**: Context gathering questions and flow

### 3. plan-template.json
**Source**: Create from `docs-mcp/schemas/plan.schema.json`
**Purpose**: Structure template for implementation plans

### 4. deliverables-template.md
**Source**: Example from any completed feature's DELIVERABLES.md
**Purpose**: Template for tracking deliverables

## Optional Enhancement Files

### 5. example-context.json
**Purpose**: Sample completed context.json to show expected output format
**Content**: Real example from a completed feature

### 6. example-plan.json
**Purpose**: Sample completed plan.json showing full structure
**Content**: Real example with all 10 sections populated

### 7. lloyd-persona.json
**Source**: `personas-mcp/personas/base/lloyd.json`
**Purpose**: Full Lloyd persona definition for reference

## File Preparation

Before uploading, ensure files are:
- Under 20MB each (GPT limit)
- In readable format (MD, JSON, TXT)
- Free of sensitive information
- Named descriptively

## Upload Checklist

| File | Status | Notes |
|------|--------|-------|
| start-feature-workflow.md | [ ] | Copy from docs-mcp |
| gather-context-workflow.md | [ ] | Copy from docs-mcp |
| plan-template.json | [ ] | Create simplified version |
| deliverables-template.md | [ ] | Copy example |
| example-context.json | [ ] | Optional |
| example-plan.json | [ ] | Optional |

## Updating Knowledge Files

When workflows change in the main repository:
1. Re-export updated files
2. Remove old versions from GPT Knowledge
3. Upload new versions
4. Test GPT to verify it uses new content
