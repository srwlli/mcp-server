# DELIVERABLES: {{ feature_name }}

**Project**: {{ project_name }}
**Feature**: {{ feature_name }}
**Workorder**: {{ workorder_id }}
**Status**: {{ status }}
**Generated**: {{ generated_date }}

---

## Validation & Health Score

### Document Health
- **Overall Health Score**: {{ health.overall_score }}/100
  - Traceability (40%): {{ health.traceability }}/40
  - Completeness (30%): {{ health.completeness }}/30
  - Freshness (20%): {{ health.freshness }}/20
  - Validation (10%): {{ health.validation }}/10

### UDS Validation
- **Schema Validation**: {{ validation.status }}
- **Validation Score**: {{ validation.score }}/100
- **Issues Found**: {{ validation.issues|length }}
{% if validation.issues %}
{% for issue in validation.issues %}
  - [{{ issue.severity }}] {{ issue.message }}
{% endfor %}
{% endif %}

---

## Executive Summary

**Goal**: {{ goal }}

**Description**: {{ description }}

**Implementation Status**: {{ implementation_status }}

---

## Files Changed

### Summary
- **Total Files Modified**: {{ git.files_changed|length }}
- **Lines Added**: {{ git.total_additions }}
- **Lines Deleted**: {{ git.total_deletions }}
- **Net LOC**: {{ git.total_additions - git.total_deletions }}

### File Details
{% if git.files_changed %}
{% for file in git.files_changed %}
- {{ file.path|file_status_icon }} `{{ file.path }}` (+{{ file.additions }} -{{ file.deletions }})
{% endfor %}
{% else %}
*No file changes detected (may need git history analysis)*
{% endif %}

---

## Components Added

### New Code Elements
{% if coderef.components_added %}
{% for component in coderef.components_added %}
- **{{ component.name }}** ({{ component.type }})
  - File: `{{ component.file }}:{{ component.line }}`
{% endfor %}
{% else %}
*No new components detected (may need coderef scan)*
{% endif %}

### Functions Added
{% if coderef.functions_added %}
{% for func in coderef.functions_added %}
- **{{ func.name }}** ({{ func.type }})
  - File: `{{ func.file }}:{{ func.line }}`
{% endfor %}
{% else %}
*No new functions detected*
{% endif %}

### Complexity Delta
- **Average Complexity Change**: {{ coderef.complexity_delta|round(2) }}

---

## Implementation Phases

{% if plan.phases %}
{% for phase in plan.phases %}
### Phase {{ loop.index }}: {{ phase.name }}
- **Status**: {{ phase.status }}
- **Duration**: {{ phase.duration|format_duration }}
- **Deliverables**:
{% for deliverable in phase.deliverables %}
  - {{ deliverable }}
{% endfor %}
{% endfor %}
{% else %}
*No phase data available (plan.json may be missing)*
{% endif %}

---

## Priority Checklist

### Tasks by Priority
{% if plan.tasks %}
{% for task in plan.tasks|sort(attribute='priority', reverse=true) %}
- [{% if task.status == 'completed' %}x{% else %} {% endif %}] {{ task.priority|priority_color }} **{{ task.task_id }}**: {{ task.description }} ({{ task.status }})
{% endfor %}
{% else %}
*No task data available*
{% endif %}

---

## Git Commit History

### Commit Summary
- **Total Commits**: {{ git.commits|length }}
{% if git.commits %}
- **First Commit**: {{ git.commits[-1].date|humanize_date }}
- **Last Commit**: {{ git.commits[0].date|humanize_date }}
- **Contributors**: {{ git.commits|map(attribute='author')|unique|list|join(', ') }}
{% endif %}

### Recent Commits
{% if git.commits %}
{% for commit in git.commits[:10] %}
- **{{ commit.hash[:7] if commit.hash else 'N/A' }}** - {{ commit.message }} ({{ commit.author }}, {{ commit.date|humanize_date if commit.date else 'N/A' }})
{% endfor %}
{% if git.commits|length > 10 %}
*... and {{ git.commits|length - 10 }} more commits*
{% endif %}
{% else %}
*No commit history available (workorder may not be associated with git commits)*
{% endif %}

---

## Metrics Summary

### Code Metrics
| Metric | Value |
|--------|-------|
| Files Modified | {{ git.files_changed|length }} |
| Lines Added | {{ git.total_additions }} |
| Lines Deleted | {{ git.total_deletions }} |
| Net LOC | {{ git.total_additions - git.total_deletions }} |
| Components Added | {{ coderef.components_added|length }} |
| Functions Added | {{ coderef.functions_added|length }} |
| Complexity Delta | {{ coderef.complexity_delta|round(2) }} |

### Activity Metrics
| Metric | Value |
|--------|-------|
| Total Commits | {{ git.commits|length }} |
{% if git.commits %}
| Contributors | {{ git.commits|map(attribute='author')|unique|list|length }} |
{% endif %}

---

## Success Criteria

### Functional Requirements
{% if success_criteria.functional %}
{% for criterion in success_criteria.functional %}
- [{% if criterion.met %}x{% else %} {% endif %}] {{ criterion.requirement }} ({{ criterion.status }})
{% endfor %}
{% else %}
*Success criteria not defined in plan.json*
{% endif %}

### Quality Requirements
{% if success_criteria.quality %}
{% for criterion in success_criteria.quality %}
- [{% if criterion.met %}x{% else %} {% endif %}] {{ criterion.requirement }} ({{ criterion.status }})
{% endfor %}
{% endif %}

---

## Notes

*This enhanced deliverables report was automatically generated using Papertrail template engine.*
*Generated from: plan.json, git history, and .coderef/ analysis.*

**Data Sources**:
- Git analysis: {{ git.source|default('git log --grep=' + workorder_id) }}
- CodeRef baseline: {{ coderef.baseline|default('.coderef/index-baseline-' + feature_name + '.json') }}
- Plan data: {{ plan.source|default('coderef/workorder/' + feature_name + '/plan.json') }}

**Last Updated**: {{ generated_date }}
**Template Version**: 2.0.0 (Enhanced with Papertrail)
