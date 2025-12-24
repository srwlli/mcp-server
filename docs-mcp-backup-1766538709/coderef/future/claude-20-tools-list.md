# 20 Potential New Tools for docs-mcp

**Generated:** 2025-10-18
**Context:** After implementing update_all_documentation tool, reviewing workflow gaps and expansion opportunities

---

## Workflow Analysis

**Current Workflow Coverage:**
```
1. Gather Context (/gather-context) 
2. Analyze Project (/analyze-for-planning) 
3. Create Plan (/create-plan) 
4. Validate Plan (/validate-plan) 
5. Implementation (manual)
6. Update Deliverables (/update-deliverables) 
7. Update Documentation (/update-docs)  NEW!
8. Archive Feature (/archive-feature) 
```

**Gaps Identified:**
- No implementation tracking during development
- No code review automation
- No testing workflow integration
- No deployment/release automation
- No retrospective/learning capture
- No cross-project knowledge sharing

---

## 20 New Tool Ideas

### Category: Implementation Tracking & Quality

#### 1. `track_implementation_progress`
**Purpose:** Real-time tracking of implementation progress against plan.json tasks
**Inputs:**
- `project_path`
- `feature_name`
- `task_id` (from plan.json)
- `status` (not_started, in_progress, blocked, complete)
- `notes` (optional blockers/comments)

**Output:** Updates progress.json, calculates completion percentage, identifies blockers

**Why:** Currently no visibility into implementation progress until /update-deliverables. This would enable real-time tracking.

**Workflow Integration:** During implementation phase, agent updates progress as tasks complete

---

#### 2. `validate_implementation_against_plan`
**Purpose:** Compare implemented code against plan.json to ensure all tasks were completed
**Inputs:**
- `project_path`
- `feature_name`
- `git_commit_range` (optional, defaults to feature branch)

**Output:** Validation report showing:
- Tasks completed vs. planned
- Files modified vs. expected files in plan
- Missing test coverage
- Unapproved scope creep (files modified not in plan)

**Why:** Ensures implementation stayed true to plan, catches scope creep

**Workflow Integration:** Run BEFORE /update-deliverables to verify completeness

---

#### 3. `generate_code_review_checklist`
**Purpose:** Generate customized code review checklist from plan.json and project standards
**Inputs:**
- `project_path`
- `feature_name`
- `include_standards` (boolean, default true)

**Output:** Markdown checklist combining:
- Plan.json success criteria
- Project coding standards
- Language-specific best practices
- Security checklist items

**Why:** Standardizes code review process, ensures consistency

**Workflow Integration:** Run AFTER implementation, BEFORE merge

---

#### 4. `auto_code_review`
**Purpose:** Automated code review using static analysis + standards compliance
**Inputs:**
- `project_path`
- `feature_name`
- `severity_threshold` (critical, major, minor)

**Output:** Review report with:
- Standards violations (from /check-consistency)
- Static analysis issues (pylint, eslint, etc.)
- Security vulnerabilities
- Complexity metrics
- Test coverage gaps

**Why:** First-pass automated review before human review

**Workflow Integration:** Run AFTER implementation, automated pre-commit gate

---

### Category: Testing & Quality Assurance

#### 5. `generate_test_plan`
**Purpose:** Generate test plan from plan.json implementation tasks
**Inputs:**
- `project_path`
- `feature_name`

**Output:** test-plan.md with:
- Unit test scenarios (from each task)
- Integration test scenarios
- Edge cases to test
- Expected test coverage targets

**Why:** Currently no structured test planning, tests often incomplete

**Workflow Integration:** Run AFTER /create-plan, BEFORE implementation

---

#### 6. `validate_test_coverage`
**Purpose:** Validate test coverage meets plan.json success criteria
**Inputs:**
- `project_path`
- `feature_name`
- `coverage_threshold` (default from plan.json)

**Output:** Coverage report comparing:
- Actual coverage vs. plan target
- Untested critical paths
- Missing test categories (unit/integration/e2e)

**Why:** Enforces test coverage requirements from plan

**Workflow Integration:** Run AFTER tests written, BEFORE /update-deliverables

---

#### 7. `generate_test_fixtures`
**Purpose:** Generate test fixtures/mocks from API/database schemas
**Inputs:**
- `project_path`
- `fixture_type` (api_response, database_record, mock_object)
- `schema_file` (optional, auto-detect from inventory)

**Output:** Language-specific test fixtures based on schemas

**Why:** Reduces boilerplate test setup, ensures realistic test data

**Workflow Integration:** During test writing phase

---

### Category: Documentation & Knowledge

#### 8. `generate_migration_guide`
**Purpose:** Auto-generate migration guide for breaking changes
**Inputs:**
- `project_path`
- `version_from`
- `version_to`
- `breaking_changes` (array from changelog)

**Output:** MIGRATION.md with:
- Breaking changes summary
- Before/after code examples
- Step-by-step migration steps
- Deprecation timeline

**Why:** Breaking changes need clear migration docs, currently manual

**Workflow Integration:** Run when change_type=breaking_change

---

#### 9. `generate_release_notes`
**Purpose:** Compile changelog entries into user-friendly release notes
**Inputs:**
- `project_path`
- `version` (or version range)
- `audience` (technical, end_user, both)

**Output:** RELEASE_NOTES.md formatted for specific audience

**Why:** CHANGELOG.json is structured data, needs human-readable format

**Workflow Integration:** Run BEFORE release/deployment

---

#### 10. `sync_docs_with_code`
**Purpose:** Validate documentation matches current code (API signatures, configs, etc.)
**Inputs:**
- `project_path`
- `doc_types` (api, architecture, user_guide)

**Output:** Sync report showing:
- Outdated API documentation
- Missing new features in docs
- Removed features still documented
- Configuration drift

**Why:** Docs often drift from code, need automated sync check

**Workflow Integration:** Run periodically or on docs changes

---

#### 11. `generate_architectural_decision_record`
**Purpose:** Create ADR (Architectural Decision Record) from plan.json decisions
**Inputs:**
- `project_path`
- `feature_name`
- `decision_type` (technology, pattern, approach)
- `decision_details` (from agent context)

**Output:** ADR in docs/adr/ following standard template

**Why:** Captures "why" decisions were made, valuable for future

**Workflow Integration:** Run during planning or when major decisions made

---

### Category: Deployment & Release

#### 12. `validate_release_readiness`
**Purpose:** Pre-release checklist validation
**Inputs:**
- `project_path`
- `version`
- `release_type` (major, minor, patch)

**Output:** Release readiness report checking:
- All tests passing
- Documentation updated
- CHANGELOG complete
- Breaking changes documented
- Migration guide exists (if needed)
- Security scan passed

**Why:** Prevents incomplete releases, standardizes release process

**Workflow Integration:** Run BEFORE tagging release

---

#### 13. `generate_deployment_checklist`
**Purpose:** Generate environment-specific deployment checklist
**Inputs:**
- `project_path`
- `environment` (dev, staging, production)
- `deployment_type` (first_deploy, update, rollback)

**Output:** Deployment checklist with:
- Pre-deployment steps
- Deployment commands
- Smoke tests
- Rollback procedure

**Why:** Standardizes deployments, reduces errors

**Workflow Integration:** Before any deployment

---

#### 14. `track_deployment_metrics`
**Purpose:** Log deployment metrics and outcomes
**Inputs:**
- `project_path`
- `version`
- `environment`
- `deployment_status` (success, failed, rolled_back)
- `metrics` (deploy_time, downtime, errors)

**Output:** Updates deployment-history.json with metrics

**Why:** Track deployment success rate, identify patterns

**Workflow Integration:** After each deployment

---

### Category: Learning & Improvement

#### 15. `generate_retrospective_template`
**Purpose:** Create feature retrospective template from DELIVERABLES.md
**Inputs:**
- `project_path`
- `feature_name`

**Output:** retrospective.md with prompts:
- What went well (from deliverables metrics)
- What could improve
- Blockers encountered
- Lessons learned
- Action items for next feature

**Why:** Captures learning, improves future planning

**Workflow Integration:** Run AFTER /archive-feature

---

#### 16. `analyze_estimation_accuracy`
**Purpose:** Compare planned vs. actual metrics across features
**Inputs:**
- `project_path`
- `time_range` (optional, default all features)

**Output:** Analysis showing:
- Planned LOC vs. actual LOC (per feature)
- Planned time vs. actual time
- Common estimation errors
- Improvement trends over time

**Why:** Improves future estimation accuracy

**Workflow Integration:** Run periodically for process improvement

---

#### 17. `extract_reusable_patterns`
**Purpose:** Identify code patterns that could be abstracted/reused
**Inputs:**
- `project_path`
- `similarity_threshold` (0-100, default 80)

**Output:** patterns-report.md with:
- Duplicated code sections
- Similar patterns across features
- Refactoring opportunities
- Potential library extractions

**Why:** Reduces code duplication, identifies abstraction opportunities

**Workflow Integration:** Run periodically or during refactoring planning

---

### Category: Cross-Project & Collaboration

#### 18. `share_feature_template`
**Purpose:** Export feature (plan + code) as reusable template for other projects
**Inputs:**
- `project_path`
- `feature_name`
- `template_name`
- `generalization_level` (specific, generic, abstract)

**Output:** Template package with:
- Generalized plan.json
- Code templates with placeholders
- Documentation templates
- Setup instructions

**Why:** Enables cross-project knowledge sharing

**Workflow Integration:** Run AFTER successful feature implementation

---

#### 19. `import_feature_template`
**Purpose:** Import and adapt feature template from another project
**Inputs:**
- `project_path`
- `template_path`
- `customization_params` (project-specific values)

**Output:** Adapted feature structure ready for implementation

**Why:** Accelerates common features, ensures consistency

**Workflow Integration:** Alternative to /gather-context for common features

---

#### 20. `generate_knowledge_graph`
**Purpose:** Build knowledge graph of features, dependencies, and decisions
**Inputs:**
- `project_path`
- `include_archived` (boolean, default true)

**Output:** knowledge-graph.json with:
- Features and their relationships
- Shared components
- Decision lineage (ADRs)
- Technology evolution
- Contributor expertise map

**Why:** Visualizes project knowledge, aids onboarding and planning

**Workflow Integration:** Run periodically to update project knowledge base

---

## Priority Ranking

### High Priority (Immediate Workflow Gaps)
1. **validate_implementation_against_plan** - Ensures plan compliance
2. **generate_test_plan** - Currently no test planning
3. **validate_release_readiness** - Prevents incomplete releases
4. **generate_migration_guide** - Breaking changes need docs

### Medium Priority (Quality & Automation)
5. **auto_code_review** - Automates first-pass review
6. **validate_test_coverage** - Enforces coverage requirements
7. **sync_docs_with_code** - Prevents doc drift
8. **track_implementation_progress** - Real-time visibility

### Lower Priority (Nice to Have)
9. **generate_retrospective_template** - Captures learning
10. **analyze_estimation_accuracy** - Long-term improvement
11. **generate_knowledge_graph** - Advanced knowledge management
12. **share_feature_template** - Cross-project collaboration

---

## Implementation Notes

**Common Patterns Across Tools:**
- All use workorder tracking for traceability
- All integrate with existing workflow (context ’ plan ’ implement ’ validate ’ archive)
- All follow agentic design (agent provides context, not file parsing)
- All use feature-specific working directories (coderef/working/{feature_name}/)
- All generate structured outputs (JSON + Markdown reports)

**Technical Considerations:**
- Some tools require language-specific implementations (static analysis)
- Some tools need external integrations (CI/CD, test frameworks)
- Some tools are meta-tools (instruction-based like update_changelog)
- Some tools require git integration (deployment tracking, metrics)

**Next Steps:**
1. Review with user for feedback
2. Prioritize based on immediate workflow pain points
3. Create implementation plans for top 5 tools
4. Implement incrementally with dogfooding

---

**Total Tools Proposed:** 20
**Categories:** 5 (Implementation Tracking, Testing, Documentation, Deployment, Learning)
**Immediate Workflow Impact:** High (fills critical gaps in current workflow)
