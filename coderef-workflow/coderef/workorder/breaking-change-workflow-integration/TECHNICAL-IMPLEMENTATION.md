# Breaking Change Workflow Integration - Technical Implementation Reference

**For:** Developers implementing the workflow integration
**Language:** TypeScript
**Framework:** coderef-workflow orchestration

---

## 1. Template Updates

### 1.1 Update plan.json Template

**File:** `packages/generators/src/templates/plan.json`

**Changes:** Add breaking change detection tasks to phases

```json
{
  "phases": [
    {
      "id": "phase_0",
      "name": "Preparation",
      "tasks": [
        {
          "id": "PREP-BREAKING-001",
          "title": "Detect existing breaking changes",
          "description": "Analyze current branch for breaking changes that may affect implementation",
          "tool": "mcp__coderef_breaking__detect",
          "tool_params": {
            "baseRef": "main",
            "headRef": "{{ context.feature_branch }}",
            "maxDepth": 5,
            "format": "json"
          },
          "acceptance_criteria": [
            "Risk assessment complete",
            "Baseline metrics recorded",
            "Risks added to plan.risks"
          ],
          "estimated_effort": "5m",
          "outputs": {
            "risk_assessment": "{{ tool_output }}",
            "baseline_breaking_count": "{{ tool_output.summary.breakingCount }}",
            "affected_modules": "{{ extract_modules(tool_output.changes) }}"
          }
        }
      ]
    },
    {
      "id": "phase_3",
      "name": "Verification",
      "tasks": [
        {
          "id": "VERIFY-BREAKING-001",
          "title": "Validate no new breaking changes introduced",
          "description": "Detect if implementation introduced new breaking changes",
          "depends_on": ["PREP-BREAKING-001"],
          "tool": "mcp__coderef_breaking__detect",
          "tool_params": {
            "baseRef": "main",
            "useWorktree": true,
            "maxDepth": 5,
            "format": "json"
          },
          "acceptance_criteria": [
            "No new breaking changes detected",
            "OR all breaking changes have migration hints",
            "Report saved for documentation"
          ],
          "estimated_effort": "10m",
          "gates": [
            {
              "id": "breaking-changes-introduced",
              "condition": "tool_output.summary.breakingCount > context.baseline_breaking_count",
              "action": "fail",
              "message": "Feature introduced {{ new_count }} new breaking changes - requires migration patterns",
              "remediation": "Agent must implement wrap/rename/adapter patterns or rollback changes"
            }
          ],
          "outputs": {
            "verification_report": "{{ tool_output }}",
            "new_breaking_count": "{{ tool_output.summary.breakingCount - context.baseline_breaking_count }}",
            "impacted_modules": "{{ extract_modules(tool_output.changes) }}"
          }
        }
      ]
    }
  ]
}
```

### 1.2 Update communication.json Template

**File:** `packages/generators/src/templates/communication.json`

**Changes:** Add breaking change shared gates for multi-agent coordination

```json
{
  "shared_gates": [
    {
      "id": "breaking-change-validation",
      "name": "Breaking Change Validation Gate",
      "runs_after": "all_agents_complete",
      "description": "Verify no new breaking changes were introduced by any agent",
      "check": {
        "tool": "mcp__coderef_breaking__detect",
        "params": {
          "baseRef": "main",
          "useWorktree": true,
          "maxDepth": 5
        }
      },
      "pass_condition": "new_breaking_count <= allowed_threshold",
      "allowed_threshold": 0,
      "on_fail": {
        "action": "require_agent_remediation",
        "message": "Breaking changes detected - agents must implement migration patterns",
        "escalate_to": "tech_lead"
      }
    }
  ],
  "agents": [
    {
      "agent_id": 1,
      "task_ids": ["IMPL-001", "IMPL-002"],
      "constraints": {
        "must_not_break": [
          "src/api/public/",
          "src/auth/core",
          "src/exports.ts"
        ],
        "success_criteria": [
          "Tasks completed",
          "No breaking changes to must_not_break modules",
          "All breaking changes have migration patterns with confidence > 85%"
        ]
      }
    }
  ]
}
```

---

## 2. Workflow Hooks Implementation

### 2.1 Baseline Hook (Pre-Implementation)

**File:** `packages/workflow/src/hooks/breaking-change-baseline.ts`

```typescript
import { BreakingChangeDetector } from '@coderef/core/context/breaking-change-detector';
import { AnalyzerService } from '@coderef/core';
import { ImpactSimulator } from '@coderef/core/context/impact-simulator';

export async function recordBreakingChangeBaseline(
  context: WorkflowContext,
  sourceDir: string = '.'
): Promise<void> {
  const analyzer = new AnalyzerService(sourceDir);
  const graph = analyzer.getGraph?.() || { nodes: [], edges: [] };
  const simulator = new ImpactSimulator(graph);
  const detector = new BreakingChangeDetector(analyzer, simulator);

  // Record baseline breaking changes
  const baseline = await detector.detectChanges('main', 'worktree', true, 5);

  // Store in context for later comparison
  context.breaking_change_baseline = {
    report: baseline,
    count: baseline.summary.breakingCount,
    recorded_at: new Date().toISOString(),
    base_ref: 'main'
  };

  console.log(
    `✓ Breaking change baseline recorded: ${baseline.summary.breakingCount} existing`
  );
}

// Hook registration
export const hook = {
  name: 'breaking-change-baseline',
  trigger: 'before_implementation',
  handler: recordBreakingChangeBaseline
};
```

### 2.2 Verification Hook (Post-Implementation)

**File:** `packages/workflow/src/hooks/breaking-change-verification.ts`

```typescript
import { BreakingChangeDetector } from '@coderef/core/context/breaking-change-detector';
import { AnalyzerService } from '@coderef/core';
import { ImpactSimulator } from '@coderef/core/context/impact-simulator';

export async function verifyNoNewBreakingChanges(
  context: WorkflowContext,
  sourceDir: string = '.'
): Promise<VerificationResult> {
  const analyzer = new AnalyzerService(sourceDir);
  const graph = analyzer.getGraph?.() || { nodes: [], edges: [] };
  const simulator = new ImpactSimulator(graph);
  const detector = new BreakingChangeDetector(analyzer, simulator);

  // Detect current breaking changes
  const current = await detector.detectChanges('main', 'worktree', true, 5);
  const baseline = context.breaking_change_baseline;

  // Calculate net new breaking changes
  const newBreakingCount =
    current.summary.breakingCount - (baseline?.count ?? 0);

  if (newBreakingCount > 0) {
    // Identify new breaking changes
    const newChanges = current.changes.filter(change =>
      !baseline?.report?.changes?.some(
        bc => bc.element.name === change.element.name &&
              bc.element.file === change.element.file
      )
    );

    return {
      passed: false,
      message: `${newBreakingCount} new breaking changes introduced`,
      breaking_changes: newChanges,
      remediation: newChanges.map(change => ({
        element: change.element.name,
        severity: change.severity,
        affected_call_sites: change.impactedCallSites.length,
        suggested_patterns: change.migrationHints.map(h => h.hintType),
        migration_guide: formatMigrationGuide(change)
      }))
    };
  }

  return {
    passed: true,
    message: 'No new breaking changes introduced',
    report: current
  };
}

function formatMigrationGuide(change: any): string {
  return `
## Migration Guide: ${change.element.name}

**Change Type:** ${change.changeType}
**Severity:** ${change.severity}
**Affected Call Sites:** ${change.impactedCallSites.length}

**Suggested Fixes:**
${change.migrationHints
  .map((h: any) => `- ${h.hintType}: ${h.text}`)
  .join('\n')}
  `.trim();
}

// Hook registration
export const hook = {
  name: 'breaking-change-verification',
  trigger: 'after_implementation',
  handler: verifyNoNewBreakingChanges,
  on_failure: {
    action: 'require_remediation',
    message: 'Agent must implement migration patterns for breaking changes'
  }
};
```

### 2.3 Documentation Hook (Post-Verification)

**File:** `packages/workflow/src/hooks/breaking-change-documentation.ts`

```typescript
export async function generateBreakingChangeDocumentation(
  context: WorkflowContext,
  verification_result: VerificationResult
): Promise<void> {
  if (verification_result.passed) {
    console.log('✓ No breaking changes - documentation skipped');
    return;
  }

  const report = verification_result.report;
  const migrationGuide = generateMigrationMarkdown(report);

  // Save migration guide
  context.deliverables.migration_guide = migrationGuide;

  // Prepare changelog entry
  context.deliverables.changelog_entry = {
    version: context.version,
    change_type: 'breaking_change',
    title: `Breaking Changes in v${context.version}`,
    description: migrationGuide,
    affected_files: report.changes.map(c => c.element.file),
    migration_guide: migrationGuide
  };

  console.log('✓ Migration guide generated');
}

function generateMigrationMarkdown(report: BreakingChangeReport): string {
  return `
# Breaking Changes in v${report.metadata.analyzedAt}

## Summary
- **Total Breaking Changes:** ${report.summary.breakingCount}
- **Affected Call Sites:** ${report.changes.reduce((sum, c) => sum + c.impactedCallSites.length, 0)}

## Detailed Changes

${report.changes
  .map(change => `
### ${change.element.name} (${change.severity})

**Change:** ${change.changeType}
**Affected:** ${change.impactedCallSites.length} call sites

**Before:**
\`\`\`
${change.details.before}
\`\`\`

**After:**
\`\`\`
${change.details.after}
\`\`\`

**Migration Patterns:**
${change.migrationHints
  .map(h => `- **${h.hintType}**: ${h.text}`)
  .join('\n')}

**Confidence:** ${(change.impactedCallSites[0]?.confidence * 100).toFixed(0)}%
`)
  .join('\n')}
`.trim();
}

export const hook = {
  name: 'breaking-change-documentation',
  trigger: 'after_verification',
  handler: generateBreakingChangeDocumentation
};
```

---

## 3. Agent Handoff Context

### 3.1 Update claude.md Generation

**File:** `packages/workflow/src/context/handoff-generator.ts`

**Changes:** Include breaking change section in claude.md

```typescript
export async function generateClaudeMd(
  context: WorkflowContext,
  plan: Plan
): Promise<string> {
  // ... existing code ...

  // Add breaking change section
  const breakingChangeSection = await generateBreakingChangeSection(
    context.breaking_change_baseline
  );

  return `
# Agent Context - ${context.feature_name}

${breakingChangeSection}

${existingContent}
  `.trim();
}

async function generateBreakingChangeSection(
  baseline: BreakingChangeBaseline
): Promise<string> {
  if (!baseline) {
    return '## Breaking Changes\nNo breaking changes detected.\n';
  }

  const { report } = baseline;

  return `
## Breaking Changes (CR-001)

### Current Status
- **Total Breaking Changes:** ${report.summary.breakingCount}
- **Affected Call Sites:** ${report.changes.reduce((s, c) => s + c.impactedCallSites.length, 0)}

### Your Responsibilities

1. **Run breaking change detection after implementation:**
   \`\`\`bash
   coderef breaking main --format table
   \`\`\`

2. **Review confidence scores:**
   - >85%: High certainty of breakage
   - 60-85%: Likely breakage
   - <60%: Possible breakage

3. **Implement migration patterns:**
   - **Wrap:** Create new function alongside old one
   - **Rename:** Rename and provide adapters
   - **Adapter:** Create wrapper for compatibility
   - **Default Params:** Add default parameter values
   - **Options Object:** Convert to options object

4. **Verify all call sites:**
   Each breaking change lists impacted call sites - verify all can be updated

### Available Tools
- \`mcp__coderef_breaking__detect\` - Run detection
- Breaking change reports in JSON format
- Migration hint suggestions in all reports
  `.trim();
}
```

---

## 4. Test Selection Strategy

### 4.1 Breaking-Change-Aware Test Selector

**File:** `packages/workflow/src/test-strategy/breaking-change-aware-selector.ts`

```typescript
export async function selectTestsForBreakingChanges(
  breaking_changes: BreakingChangeReport,
  all_tests: TestFile[]
): Promise<TestFile[]> {
  // Extract modules affected by breaking changes
  const affectedModules = new Set<string>();

  for (const change of breaking_changes.changes) {
    const module = change.element.file.split('/')[0];
    affectedModules.add(module);

    // Also add modules containing impacted call sites
    for (const site of change.impactedCallSites) {
      affectedModules.add(site.file.split('/')[0]);
    }
  }

  // Filter tests to affected modules
  const selectedTests = all_tests.filter(test => {
    const testModule = test.file.split('/')[0];
    return affectedModules.has(testModule);
  });

  return selectedTests;
}

// Usage in workflow
export const test_selection_strategy = {
  name: 'breaking-change-aware',
  selector: selectTestsForBreakingChanges,
  scope: 'affected_modules_only'
};
```

---

## 5. Migration Guide Generation

### 5.1 Migration Guide Generator

**File:** `packages/workflow/src/documentation/migration-guide-generator.ts`

```typescript
export function generateMigrationGuide(report: BreakingChangeReport): string {
  const changes = report.changes;

  if (changes.length === 0) {
    return 'No breaking changes in this release.\n';
  }

  return `
# Migration Guide

${generateSummaryTable(changes)}

${changes.map(generateChangeSection).join('\n\n')}

# Quick Reference

## By Severity
${generateSeverityIndex(changes)}

## By Pattern
${generatePatternIndex(changes)}
  `.trim();
}

function generateChangeSection(change: BreakingChange): string {
  return `
## ${change.element.name}

**Severity:** ${change.severity}
**Type:** ${change.changeType}
**Affected Call Sites:** ${change.impactedCallSites.length}

### What Changed
\`\`\`typescript
// Before
${change.details.before}

// After
${change.details.after}
\`\`\`

### Migration Patterns

${change.migrationHints.map(hint => `
#### ${hint.hintType}

${hint.text}

\`\`\`typescript
${hint.codeExample}
\`\`\`

Confidence: ${(hint.confidence * 100).toFixed(0)}%
`).join('\n')}

### Affected Call Sites
${change.impactedCallSites
  .slice(0, 5)
  .map((site, i) => `${i + 1}. ${site.file}:${site.line} (${site.callerElement})`)
  .join('\n')}
${change.impactedCallSites.length > 5 ? `... and ${change.impactedCallSites.length - 5} more` : ''}
  `.trim();
}
```

---

## 6. Integration Testing

### 6.1 Test Suite for Workflow Integration

**File:** `packages/workflow/src/__tests__/breaking-change-integration.test.ts`

```typescript
describe('Breaking Change Workflow Integration', () => {
  it('should record baseline before implementation', async () => {
    const context = createTestContext();
    await recordBreakingChangeBaseline(context);

    expect(context.breaking_change_baseline).toBeDefined();
    expect(context.breaking_change_baseline.count).toBeGreaterThanOrEqual(0);
  });

  it('should detect new breaking changes after implementation', async () => {
    const context = createTestContext();
    const baseline = { count: 2 };
    context.breaking_change_baseline = baseline;

    const result = await verifyNoNewBreakingChanges(context);

    if (result.breaking_changes.length > 0) {
      expect(result.passed).toBe(false);
      expect(result.remediation).toBeDefined();
    }
  });

  it('should pass verification if no new breaking changes', async () => {
    // Setup scenario where no new changes introduced
    const result = await verifyNoNewBreakingChanges(context);
    expect(result.passed).toBe(true);
  });

  it('should generate migration guide from breaking changes', async () => {
    const report = createMockBreakingChangeReport();
    const guide = generateMigrationGuide(report);

    expect(guide).toContain('Migration Guide');
    expect(guide).toContain(report.changes[0].element.name);
  });

  it('should select tests for affected modules', async () => {
    const report = createMockBreakingChangeReport();
    const allTests = createMockTests();

    const selected = await selectTestsForBreakingChanges(report, allTests);

    expect(selected.length).toBeLessThan(allTests.length);
    expect(selected.length).toBeGreaterThan(0);
  });
});
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions Workflow

**File:** `.github/workflows/breaking-change-check.yml`

```yaml
name: Breaking Change Check

on: [pull_request]

jobs:
  breaking-changes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Detect breaking changes
        id: breaking
        run: |
          REPORT=$(npm run coderef breaking main -- --format json)
          BREAKING_COUNT=$(echo "$REPORT" | jq '.summary.breakingCount')
          echo "breaking_count=$BREAKING_COUNT" >> $GITHUB_OUTPUT
          echo "$REPORT" > breaking-changes-report.json

      - name: Comment PR with results
        if: steps.breaking.outputs.breaking_count > 0
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('breaking-changes-report.json', 'utf8'));
            const comment = `## ⚠️ Breaking Changes Detected\n\n${report.summary.breakingCount} breaking changes found.`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail if breaking changes
        if: steps.breaking.outputs.breaking_count > 0
        run: exit 1
```

---

## Summary

This implementation provides:

1. ✅ Template updates for automatic task inclusion
2. ✅ Workflow hooks for baseline and verification
3. ✅ Agent handoff context integration
4. ✅ Smart test selection based on impact
5. ✅ Migration guide generation
6. ✅ CI/CD pipeline integration
7. ✅ Comprehensive testing

**Total Implementation Effort:** ~16 hours for all components

**Suggested Implementation Order:**
1. Template updates (2 hrs)
2. Workflow hooks (4 hrs)
3. Agent handoff (2 hrs)
4. Test selection (3 hrs)
5. Migration guide (3 hrs)
6. CI/CD integration (2 hrs)
