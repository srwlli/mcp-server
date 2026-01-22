# SKILL.md Template and Standards (v1.0.0)

**Purpose:** Template and standards for creating skill.md files in the CodeRef ecosystem
**Applies to:** Reusable workflows, specialized capabilities, one-off tasks
**Created:** 2026-01-22
**Workorder:** WO-CLAUDE-MD-STANDARDS-001

---

## Executive Summary

**Skills** are specialized workflows that Claude Code can invoke to perform specific tasks. They are user-triggered (via `/skill-name`) or auto-loaded based on context.

**Core Principles:**
1. **Focused on execution** - One specific task, not general knowledge
2. **Lean and actionable** - 300-500 lines (leaner than CLAUDE.md)
3. **YAML frontmatter required** - name, description, allowed-tools
4. **Self-contained** - Can include scripts, references, assets in skill directory

**Based on:**
- Research of skill.md best practices (Phase 1)
- Anthropic Claude Code documentation
- Analysis of existing skills (coderef-scanner, sync-nav)

---

## 1. When to Use Skills vs CLAUDE.md

### Decision Tree

```
Is this a ONE-TIME task or RECURRING workflow?
├─ ONE-TIME → Skill (e.g., "/migrate-database")
└─ RECURRING → Consider frequency
    ├─ EVERY SESSION → CLAUDE.md (e.g., project architecture)
    └─ SOME SESSIONS → Skill (e.g., "/deploy-production")

Is this GENERAL KNOWLEDGE or SPECIFIC CAPABILITY?
├─ GENERAL → CLAUDE.md (e.g., "how our system works")
└─ SPECIFIC → Skill (e.g., "deploy to AWS")

Is this CONTEXT or INSTRUCTIONS?
├─ CONTEXT → CLAUDE.md (e.g., "our tech stack")
└─ INSTRUCTIONS → Skill (e.g., "run these 10 commands")
```

**See also:** skills-vs-claude-decision-tree.md for full decision guide

### Examples

| Use Case | Use Skill? | Reason |
|----------|-----------|--------|
| Deploy to production | ✅ Yes | One-off task, specific instructions |
| Project architecture overview | ❌ No (CLAUDE.md) | General knowledge, needed every session |
| Run database migration | ✅ Yes | Infrequent, multi-step, risky (needs confirmation) |
| Code style guide | ❌ No (linter config) | Deterministic rules, not LLM instructions |
| Generate API docs | ✅ Yes | One-off task, specific workflow |
| Integration points | ❌ No (CLAUDE.md) | General knowledge, needed for context |
| Scan codebase for patterns | ✅ Yes | Specific task, tool-intensive |
| Recent changes | ❌ No (CLAUDE.md) | Context that may be referenced frequently |

---

## 2. Skill File Structure

### Basic Skill (Single File)

```
.claude/
└── skills/
    └── deploy-production.md         # Skill file with YAML frontmatter
```

### Advanced Skill (Directory)

```
.claude/
└── skills/
    └── deploy-production/
        ├── skill.md                 # Main skill file (required)
        ├── scripts/
        │   ├── pre-deploy.sh        # Pre-deployment checks
        │   └── deploy.sh            # Deployment script
        ├── references/
        │   └── aws-config.json      # Reference configuration
        └── assets/
            └── deployment-diagram.png # Visual aids
```

**Note:** Directory name matches skill name (invoked as `/deploy-production`)

---

## 3. YAML Frontmatter (Required)

### Minimal Example

```yaml
---
name: deploy-production
description: Deploy application to AWS production environment with health checks
---
```

### Full Example

```yaml
---
name: deploy-production
description: Deploy application to AWS production environment with health checks
allowed-tools:
  - Bash
  - Read
  - WebFetch
model: sonnet
context: |
  This skill should be used when the user explicitly requests a production deployment.
  It requires AWS credentials to be configured in the environment.
tags:
  - deployment
  - aws
  - production
---
```

### Field Reference

| Field | Required | Type | Purpose | Example |
|-------|----------|------|---------|---------|
| **name** | ✅ Yes | string | Skill identifier (used in `/skill-name`) | `deploy-production` |
| **description** | ✅ Yes | string | What this skill does (shown in skill list) | `Deploy to AWS production` |
| **allowed-tools** | ⚠️ Optional | array | Tools this skill can use | `[Bash, Read, Write]` |
| **model** | ⚠️ Optional | string | Preferred model (`sonnet`, `opus`, `haiku`) | `sonnet` |
| **context** | ⚠️ Optional | string | When to use this skill | `Use when user says "deploy"` |
| **tags** | ⚠️ Optional | array | Categorization tags | `[deployment, aws]` |

### Field Guidelines

**name:**
- Lowercase with hyphens (kebab-case)
- Descriptive and unique
- Matches directory name (if using directory structure)
- Examples: `deploy-production`, `scan-codebase`, `generate-api-docs`

**description:**
- One sentence, action-oriented
- Start with verb (Deploy, Scan, Generate, etc.)
- Include key details (target, outcome)
- Max 100 characters

**allowed-tools:**
- List ONLY tools this skill actually uses
- Omit if skill uses all tools (default behavior)
- Useful for restricting risky operations (e.g., deployment skill only allows Bash + Read)

**model:**
- `haiku` - Fast, simple tasks (file operations, basic analysis)
- `sonnet` - Default, balanced (most workflows)
- `opus` - Complex reasoning (architectural decisions, refactoring)

**context:**
- When should Claude invoke this skill?
- What triggers this skill? (user phrases, file patterns, etc.)
- What prerequisites are needed? (env vars, configs, etc.)

---

## 4. Line Budget Standards

### Target Range
- **Minimum:** 200 lines (very simple skills)
- **Target:** 300-500 lines (ideal range)
- **Maximum:** 600 lines (hard limit)

### Why Leaner Than CLAUDE.md?

**Skills are execution-focused:**
- Specific instructions for one task
- No need for ecosystem overview
- No need for architecture explanation
- No need for integration guide (CLAUDE.md covers that)

**If skill exceeds 600 lines:**
1. Break into multiple skills (e.g., `/deploy-staging` + `/deploy-production`)
2. Extract detailed docs to `references/` directory
3. Use progressive disclosure (point to external docs)

---

## 5. Skill Content Structure

### Template

```markdown
---
name: [skill-name]
description: [One-sentence description]
allowed-tools: [Bash, Read, Write, ...]
model: sonnet
context: |
  [When to use this skill]
tags: [tag1, tag2, tag3]
---

# [Skill Name]

**Purpose:** [2-3 sentences explaining what this skill does]

**When to use:** [1-2 sentences on when to invoke this skill]

**Prerequisites:** [List any required env vars, configs, or setup]

---

## Step 1: [First Step Name]

[Instructions for step 1]

**Commands:**
```bash
[command 1]
[command 2]
```

**Expected output:**
```
[expected output]
```

**On error:**
- [Error 1]: [How to fix]
- [Error 2]: [How to fix]

---

## Step 2: [Second Step Name]

[Instructions for step 2]

[... repeat for each step ...]

---

## Verification

**How to verify success:**
1. [Verification step 1]
2. [Verification step 2]

**Rollback procedure (if needed):**
```bash
[rollback commands]
```

---

## Resources

- **Script:** `scripts/[script-name].sh` (if applicable)
- **Config:** `references/[config-name].json` (if applicable)
- **Docs:** [External documentation URL] (if applicable)
```

---

## 6. Example Skills

### Example 1: Simple Skill (Deployment)

**File:** `.claude/skills/deploy-staging.md`

```markdown
---
name: deploy-staging
description: Deploy application to staging environment with automated tests
allowed-tools:
  - Bash
  - Read
model: sonnet
context: |
  Use when user says "deploy to staging" or "test deployment".
  Requires STAGING_URL environment variable.
tags:
  - deployment
  - staging
  - testing
---

# Deploy to Staging

**Purpose:** Deploy current branch to staging environment and run smoke tests.

**When to use:** Before deploying to production, when testing new features.

**Prerequisites:**
- `STAGING_URL` environment variable set
- AWS CLI configured
- Git working directory clean (no uncommitted changes)

---

## Step 1: Pre-Deployment Checks

Verify environment and git status.

**Commands:**
```bash
# Check STAGING_URL is set
echo "Staging URL: $STAGING_URL"

# Check git status
git status

# Check AWS credentials
aws sts get-caller-identity
```

**Expected output:**
- STAGING_URL shows valid URL
- Git working directory clean
- AWS credentials valid

**On error:**
- Missing STAGING_URL: Set with `export STAGING_URL=https://staging.example.com`
- Uncommitted changes: Commit or stash changes
- Invalid AWS credentials: Run `aws configure`

---

## Step 2: Run Tests

Run full test suite before deploying.

**Commands:**
```bash
npm run test
npm run lint
npm run typecheck
```

**Expected output:**
- All tests pass
- No linting errors
- No type errors

**On error:**
- Test failures: Fix failing tests before deploying
- Linting errors: Run `npm run lint:fix`
- Type errors: Fix type issues

---

## Step 3: Build Application

Build production bundle.

**Commands:**
```bash
npm run build
```

**Expected output:**
- Build completes without errors
- `dist/` directory created

---

## Step 4: Deploy to Staging

Deploy build to AWS S3 + CloudFront.

**Commands:**
```bash
# Sync build to S3
aws s3 sync dist/ s3://staging-bucket/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id STAGING_DIST_ID \
  --paths "/*"
```

**Expected output:**
- Files uploaded to S3
- CloudFront invalidation created

---

## Step 5: Run Smoke Tests

Verify deployment succeeded.

**Commands:**
```bash
# Wait for CloudFront invalidation
sleep 30

# Check homepage loads
curl -f $STAGING_URL

# Run E2E smoke tests
npm run test:e2e:staging
```

**Expected output:**
- Homepage returns 200 OK
- Smoke tests pass

**On error:**
- 404 or 500 errors: Check S3 bucket and CloudFront distribution
- Smoke test failures: Check application logs, rollback if needed

---

## Verification

**How to verify success:**
1. Visit $STAGING_URL in browser - should load without errors
2. Check staging logs: `aws logs tail /aws/lambda/staging-app --follow`
3. Run manual smoke test: Login, create item, delete item

**Rollback procedure:**
```bash
# Get previous S3 version
aws s3api list-object-versions \
  --bucket staging-bucket \
  --prefix index.html

# Restore previous version (use VersionId from above)
aws s3api copy-object \
  --bucket staging-bucket \
  --copy-source staging-bucket/index.html?versionId=VERSION_ID \
  --key index.html
```

---

## Resources

- **Staging URL:** $STAGING_URL
- **S3 Bucket:** staging-bucket
- **CloudFront Distribution:** STAGING_DIST_ID
- **Logs:** https://console.aws.amazon.com/cloudwatch/logs
```

**Line count:** ~180 lines
**Assessment:** ✅ Within budget, clear steps, good error handling

---

### Example 2: Complex Skill (Codebase Analysis)

**File:** `.claude/skills/coderef-scanner/skill.md`

```markdown
---
name: coderef-scanner
description: Analyze codebase using coderef-core integration for functions, classes, components, dependencies
allowed-tools:
  - Read
  - mcp__coderef-context__coderef_scan
  - mcp__coderef-context__coderef_query
  - mcp__coderef-context__coderef_complexity
model: sonnet
context: |
  Use when user asks to analyze codebase structure, find dependencies,
  or understand code complexity. NOT for file search (use Glob/Grep).
tags:
  - analysis
  - codebase
  - dependencies
---

# CodeRef Scanner

**Purpose:** Analyze codebase structure using pre-generated `.coderef/` data for functions, classes, components, dependencies, and complexity metrics.

**When to use:**
- User asks "what's in this codebase?" or "how does X depend on Y?"
- Need to understand code structure before refactoring
- Want to find high-complexity functions
- **NOT for keyword search** (use Grep instead)

**Prerequisites:**
- `.coderef/index.json` must exist (run coderef_scan first if missing)
- Project uses supported languages (TS, TSX, JS, JSX)

---

## Step 1: Check for Existing Index

Before scanning, check if `.coderef/index.json` already exists.

**Commands:**
```typescript
// Use Read tool
Read('.coderef/index.json')
```

**Expected output:**
- If exists: Skip to Step 3 (use existing index)
- If missing: Proceed to Step 2 (scan project)

---

## Step 2: Scan Project (if needed)

Scan project to generate `.coderef/` files.

**Commands:**
```typescript
// Use coderef_scan MCP tool
mcp__coderef-context__coderef_scan({
  project_path: process.cwd(),
  languages: ['ts', 'tsx', 'js', 'jsx'],
  use_ast: true  // 99% accuracy vs 85% regex
})
```

**Expected output:**
```json
{
  "status": "success",
  "files_scanned": 150,
  "elements_found": 450,
  "output_path": ".coderef/index.json"
}
```

**On error:**
- "No TypeScript files found": Verify languages parameter
- "AST parse error": Check for syntax errors in source files

---

## Step 3: Query Code Elements

Use `.coderef/index.json` to answer user questions.

**Query types:**

### Find all functions
```typescript
Read('.coderef/index.json')
// Filter by element_type: "function"
```

### Find dependencies of X
```typescript
mcp__coderef-context__coderef_query({
  project_path: process.cwd(),
  query_type: 'depends-on',
  target: 'AuthService',
  max_depth: 3
})
```

### Find what calls X
```typescript
mcp__coderef-context__coderef_query({
  project_path: process.cwd(),
  query_type: 'calls-me',
  target: 'authenticateUser'
})
```

**Expected output:**
- List of code elements matching query
- File paths and line numbers
- Dependency graph (for relationship queries)

---

## Step 4: Analyze Complexity

Find high-complexity functions that need refactoring.

**Commands:**
```typescript
// Get complexity for specific function
mcp__coderef-context__coderef_complexity({
  project_path: process.cwd(),
  element: 'handleUserAuth'
})
```

**Expected output:**
```json
{
  "element": "handleUserAuth",
  "cyclomatic_complexity": 15,
  "cognitive_complexity": 22,
  "lines_of_code": 120,
  "risk_level": "high"
}
```

**Complexity guidelines:**
- 1-10: Low complexity (easy to maintain)
- 11-20: Medium complexity (consider refactoring)
- 21+: High complexity (refactor recommended)

---

## Step 5: Present Results

Format results for user.

**Report structure:**
1. **Summary:** Total elements, files scanned, languages
2. **Top-level elements:** Exported functions, classes, components
3. **Dependencies:** External packages, internal modules
4. **Complexity hotspots:** Functions with complexity >15
5. **Recommendations:** Suggested refactorings

---

## Verification

**How to verify results:**
1. Spot-check: Pick 3 random functions, verify they exist in codebase
2. Dependency check: Verify reported dependencies match import statements
3. Complexity check: Manually count branches in high-complexity function

**On drift detection:**
If user reports results don't match code:
```typescript
// Re-scan to update index
mcp__coderef-context__coderef_incremental_scan({
  project_path: process.cwd()
})
```

---

## Resources

- **Index:** `.coderef/index.json` - Master element index
- **Graph:** `.coderef/graph.json` - Dependency graph
- **Complexity:** `.coderef/complexity.json` - Complexity metrics
- **Docs:** `coderef-context/CLAUDE.md` - Full MCP server documentation
```

**Line count:** ~220 lines
**Assessment:** ✅ Within budget, comprehensive, tool-focused

---

## 7. Validation Checklist

Use this checklist before committing a new skill:

### YAML Frontmatter
- [ ] `name` field present (kebab-case, unique)
- [ ] `description` field present (one sentence, action-oriented)
- [ ] `allowed-tools` specified (if restricting tools)
- [ ] `model` specified (if preferring specific model)
- [ ] `context` explains when to use skill
- [ ] `tags` help categorize skill

### Line Budget
- [ ] Total lines ≤ 600 (run `wc -l skill.md`)
- [ ] Target range: 300-500 lines
- [ ] If >600 lines, split into multiple skills or extract to references/

### Content Structure
- [ ] Purpose section explains what skill does
- [ ] Prerequisites listed (env vars, configs, setup)
- [ ] Steps numbered sequentially (Step 1, Step 2, etc.)
- [ ] Each step has Commands, Expected Output, and Error Handling
- [ ] Verification section explains how to confirm success
- [ ] Rollback procedure (if skill has side effects)

### Execution Quality
- [ ] Commands are copy-pasteable (no placeholders like `YOUR_VALUE_HERE`)
- [ ] Error messages include actionable fixes
- [ ] Dangerous operations clearly marked (e.g., "⚠️ This will delete production data")
- [ ] Verification steps are specific (not "check if it works")

### Resources
- [ ] External scripts referenced (if in `scripts/` directory)
- [ ] Configuration files referenced (if in `references/` directory)
- [ ] External documentation linked (if applicable)

---

## 8. Common Mistakes

### Mistake 1: Vague Instructions

**❌ Wrong:**
```markdown
## Step 1: Deploy

Deploy the application to production.

**Commands:**
```bash
# Deploy
./deploy.sh
```
```

**✅ Right:**
```markdown
## Step 1: Deploy to Production

Deploy application to AWS S3 bucket `prod-bucket` and invalidate CloudFront cache.

**Commands:**
```bash
# Sync to S3
aws s3 sync dist/ s3://prod-bucket/ --delete

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"
```

**Expected output:**
```
upload: dist/index.html to s3://prod-bucket/index.html
upload: dist/main.js to s3://prod-bucket/main.js
{
  "Invalidation": {
    "Id": "I1234567890ABC",
    "Status": "InProgress"
  }
}
```
```

---

### Mistake 2: Missing Error Handling

**❌ Wrong:**
```markdown
## Step 2: Run Tests

```bash
npm test
```
```

**✅ Right:**
```markdown
## Step 2: Run Tests

Run full test suite to verify code quality.

**Commands:**
```bash
npm test
```

**Expected output:**
```
Test Suites: 15 passed, 15 total
Tests:       120 passed, 120 total
```

**On error:**
- Test failures: Review test output, fix failing tests before proceeding
- Timeout errors: Increase Jest timeout in `jest.config.js`
- Out of memory: Run tests with `--maxWorkers=2` to reduce parallelism
```

---

### Mistake 3: General Knowledge in Skill (Should Be in CLAUDE.md)

**❌ Wrong (Skill File):**
```markdown
# Project Architecture

Our project uses React 18 with Next.js 14 App Router. The state management is handled by Zustand with persistence middleware. We have 5 main modules:
[300 lines of architecture explanation]
```

**✅ Right (CLAUDE.md):**
```markdown
## Architecture

### Core Concepts

**1. React 18 + Next.js 14**
App Router pattern for routing, Server Components for data fetching.

**2. State Management**
Zustand with persistence middleware.

[... rest of architecture in CLAUDE.md ...]
```

**✅ Right (Skill File):**
```markdown
---
name: analyze-architecture
description: Analyze project architecture and generate diagram
---

# Analyze Architecture

**Purpose:** Generate Mermaid diagram of project architecture from codebase.

**Prerequisites:** See `CLAUDE.md` Architecture section for context.

## Step 1: Scan Components
[... execution steps ...]
```

---

### Mistake 4: No Verification Steps

**❌ Wrong:**
```markdown
## Step 5: Deploy

```bash
./deploy.sh
```

Done!
```

**✅ Right:**
```markdown
## Step 5: Deploy

```bash
./deploy.sh
```

---

## Verification

**How to verify deployment succeeded:**
1. Visit https://production.example.com - should load homepage
2. Check health endpoint: `curl https://production.example.com/health`
   - Expected: `{"status": "healthy"}`
3. Check application logs:
   ```bash
   aws logs tail /aws/lambda/prod-app --follow
   ```
   - Expected: No error messages in last 5 minutes

**Rollback if verification fails:**
```bash
# Revert to previous deployment
aws s3 sync s3://prod-bucket-backup/ s3://prod-bucket/ --delete
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
```
```

---

## 9. Skill Directory Structure (Advanced)

For complex skills with scripts and references.

### Example: Deploy Production (Directory Structure)

```
.claude/skills/deploy-production/
├── skill.md                         # Main skill file
├── scripts/
│   ├── pre-deploy-checks.sh         # Pre-deployment validation
│   ├── deploy.sh                    # Main deployment script
│   ├── health-check.sh              # Post-deployment health check
│   └── rollback.sh                  # Emergency rollback script
├── references/
│   ├── aws-config.json              # AWS configuration reference
│   ├── deployment-checklist.md      # Manual checklist
│   └── runbook.md                   # Incident response runbook
└── assets/
    └── architecture-diagram.png     # Deployment architecture diagram
```

### Referencing Resources in skill.md

```markdown
## Step 1: Pre-Deployment Checks

Run validation script to check prerequisites.

**Commands:**
```bash
bash .claude/skills/deploy-production/scripts/pre-deploy-checks.sh
```

**Script does:**
- Checks AWS credentials
- Verifies git status
- Validates environment variables
- **See script:** `scripts/pre-deploy-checks.sh` for full logic

**Expected output:**
```
✅ AWS credentials valid
✅ Git working directory clean
✅ Environment variables set
All pre-deployment checks passed!
```
```

---

## 10. Model Selection Guidelines

Use `model` field in frontmatter to optimize for task complexity.

### Haiku (Fast, Inexpensive)

**Use for:**
- File operations (copy, move, delete)
- Simple text processing (find/replace)
- Running predefined scripts
- Data formatting (JSON to CSV, etc.)

**Example:**
```yaml
---
name: format-json
description: Format all JSON files in project with Prettier
model: haiku
---
```

### Sonnet (Balanced, Default)

**Use for:**
- Most workflows (deployment, testing, analysis)
- Multi-step tasks requiring coordination
- Tasks with decision points
- Code generation and refactoring

**Example:**
```yaml
---
name: deploy-staging
description: Deploy to staging with tests and health checks
model: sonnet
---
```

### Opus (Powerful, Expensive)

**Use for:**
- Complex architectural decisions
- Large-scale refactoring
- Code review and analysis
- Tasks requiring deep reasoning

**Example:**
```yaml
---
name: refactor-architecture
description: Refactor monolith to microservices with migration plan
model: opus
---
```

---

## 11. Related Standards

This document defines skill.md standards. See also:

- **CLAUDE-MD-STANDARDS.md** - Project-level CLAUDE.md standards
- **CHILD-CLAUDE-MD-GUIDE.md** - Sub-package CLAUDE.md standards
- **skills-vs-claude-decision-tree.md** - When to use skill vs CLAUDE.md
- **skill-frontmatter-schema.json** - JSON Schema for YAML frontmatter validation (Phase 4 deliverable)

---

## Version History

### v1.0.0 (2026-01-22)
- Initial release
- Defined 300-500 line budget
- Established YAML frontmatter requirements
- Provided skill template and examples
- Documented validation checklist

**Workorder:** WO-CLAUDE-MD-STANDARDS-001
**Session:** claude-md-standards
**Author:** CodeRef Assistant (Orchestrator Persona)

---

**Next Steps:**
1. Review and approve this skill template
2. Create skills-vs-claude-decision-tree.md (Phase 3)
3. Build skill-frontmatter-schema.json (Phase 4)
4. Build skill validator in Papertrail MCP (Phase 5)
5. Build skill generator in coderef-docs MCP (Phase 6)
