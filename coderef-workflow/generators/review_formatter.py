"""
Review report formatter for implementation plans.

Formats validation results into structured markdown review reports.
"""

from datetime import datetime
from typing import Dict, List
from type_defs import PlanReviewDict, ValidationResultDict, ValidationIssueDict


class ReviewFormatter:
    """Formats validation results into markdown review reports."""

    def __init__(self, validation_result: ValidationResultDict, plan_name: str):
        """Initialize formatter with validation result and plan name.

        Args:
            validation_result: ValidationResultDict from validate_implementation_plan
            plan_name: Name of the plan being reviewed
        """
        self.validation_result = validation_result
        self.plan_name = plan_name
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.score = validation_result['score']
        self.result = validation_result['validation_result']
        self.issues = validation_result['issues']
        self.approved = validation_result['approved']

    def format_report(self) -> str:
        """Generate complete markdown review report.

        Returns:
            Complete markdown report string
        """
        sections = [
            self._format_header(),
            self._format_summary(),
            self._format_issues_by_severity('critical'),
            self._format_issues_by_severity('major'),
            self._format_issues_by_severity('minor'),
            self._generate_recommendations(),
            self._format_approval_status()
        ]

        # Join sections with horizontal rule separators
        # Filter out empty sections (e.g., no critical issues)
        return '\n\n---\n\n'.join(filter(None, sections))

    def _format_header(self) -> str:
        """Format report header with title, plan name, date, score."""
        # Map score to grade
        if self.score >= 90:
            grade = 'A'
        elif self.score >= 85:
            grade = 'B'
        elif self.score >= 70:
            grade = 'C'
        elif self.score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        # Map result to emoji
        result_emoji = {
            'PASS': '✅',
            'PASS_WITH_WARNINGS': '⚠️',
            'NEEDS_REVISION': '🔄',
            'FAIL': '❌'
        }.get(self.result, '❓')

        return f'''# Implementation Plan Review Report

**Plan:** {self.plan_name}
**Validation Date:** {self.timestamp}
**Score:** {self.score}/100 ({grade})
**Result:** {self.result} {result_emoji}
**Approved:** {'Yes ✅' if self.approved else 'No ❌'}'''

    def _format_summary(self) -> str:
        """Format summary section with issue counts and brief assessment."""
        # Count issues by severity
        critical_count = len([i for i in self.issues if i['severity'] == 'critical'])
        major_count = len([i for i in self.issues if i['severity'] == 'major'])
        minor_count = len([i for i in self.issues if i['severity'] == 'minor'])
        total_count = len(self.issues)

        # Generate assessment based on result
        if self.result == 'PASS':
            assessment = 'Plan meets all quality requirements and is ready for implementation.'
        elif self.result == 'PASS_WITH_WARNINGS':
            assessment = 'Plan meets minimum quality requirements but has minor improvements recommended.'
        elif self.result == 'NEEDS_REVISION':
            assessment = 'Plan requires revisions to meet quality standards. Address issues below and re-validate.'
        else:  # FAIL
            assessment = 'Plan has significant quality issues and is not ready for implementation. Major revisions required.'

        return f'''## Summary

- **Critical Issues:** {critical_count} 🔴
- **Major Issues:** {major_count} 🟡
- **Minor Issues:** {minor_count} 🟢
- **Total Issues:** {total_count}

{assessment}'''

    def _format_issue_item(self, issue: ValidationIssueDict) -> str:
        """Format single issue with emoji, section, description, suggestion."""
        # Map severity to emoji
        emoji_map = {
            'critical': '🔴',
            'major': '🟡',
            'minor': '🟢'
        }
        emoji = emoji_map.get(issue['severity'], '⚪')

        return f'''### {emoji} [{issue['section']}]
**Issue:** {issue['issue']}
**Suggestion:** {issue['suggestion']}
'''

    def _format_issues_by_severity(self, severity: str) -> str:
        """Format all issues of given severity into markdown section."""
        # Filter issues by severity
        severity_issues = [i for i in self.issues if i['severity'] == severity]

        if not severity_issues:
            return None  # No section if no issues

        # Section heading with emoji
        headings = {
            'critical': '## Critical Issues 🔴',
            'major': '## Major Issues 🟡',
            'minor': '## Minor Issues 🟢'
        }
        heading = headings.get(severity, f'## {severity.title()} Issues')

        # Format each issue
        formatted_issues = [self._format_issue_item(issue) for issue in severity_issues]

        # Combine with heading
        return heading + '\n\n' + '\n'.join(formatted_issues)

    def _generate_recommendations(self) -> str:
        """Generate actionable recommendations based on issue patterns."""
        if not self.issues:
            return None  # No recommendations if no issues

        recommendations = []

        # Analyze issue patterns
        missing_sections = [i for i in self.issues if 'missing' in i['issue'].lower() and 'section' in i['issue'].lower()]
        placeholders = [i for i in self.issues if 'placeholder' in i['issue'].lower() or 'tbd' in i['issue'].lower()]
        circular_deps = [i for i in self.issues if 'circular' in i['issue'].lower()]
        short_descriptions = [i for i in self.issues if 'description' in i['issue'].lower() and 'short' in i['issue'].lower()]
        vague_criteria = [i for i in self.issues if 'success criteria' in i['issue'].lower() and 'lack' in i['issue'].lower()]
        ambiguous = [i for i in self.issues if 'ambiguous' in i['issue'].lower() or 'question' in i['issue'].lower()]

        # Generate specific recommendations
        if missing_sections:
            recommendations.append(f'Complete all required sections - {len(missing_sections)} sections are missing or incomplete')

        if placeholders:
            recommendations.append(f'Replace all placeholder text - {len(placeholders)} instances of TBD/TODO/[placeholder] found')

        if circular_deps:
            recommendations.append('Resolve circular dependencies by reordering tasks or splitting into independent phases')

        if short_descriptions:
            recommendations.append(f'Expand task descriptions - {len(short_descriptions)} tasks have descriptions < 20 words')

        if vague_criteria:
            recommendations.append('Make success criteria measurable with specific metrics (response time < 2s, test coverage > 90%)')

        if ambiguous:
            recommendations.append(f'Remove ambiguous language - {len(ambiguous)} instances of questions or uncertain phrases found')

        # Add priority guidance
        critical_count = len([i for i in self.issues if i['severity'] == 'critical'])
        if critical_count > 0:
            recommendations.insert(0, f'PRIORITY: Fix all {critical_count} critical issues first - these are blockers')

        # Limit to top 5 recommendations
        recommendations = recommendations[:5]

        # Format as numbered list
        formatted_recs = '\n'.join(f'{i+1}. {rec}' for i, rec in enumerate(recommendations))

        return f'''## Recommendations

Based on the validation results, here are actionable next steps:

{formatted_recs}'''

    def _format_approval_status(self) -> str:
        """Format approval status with emoji and requirements."""
        if self.approved:
            return f'''## Approval Status ✅

**APPROVED FOR IMPLEMENTATION**

This plan has been approved with a score of {self.score}/100.

**Next Steps:**
1. Begin implementation following the task breakdown
2. Maintain documentation as you progress
3. Track completion of acceptance criteria
4. Update this plan if significant deviations occur'''

        # Calculate gap to approval threshold (90)
        gap = 90 - self.score

        # Count issues by severity
        critical_count = len([i for i in self.issues if i['severity'] == 'critical'])
        major_count = len([i for i in self.issues if i['severity'] == 'major'])
        minor_count = len([i for i in self.issues if i['severity'] == 'minor'])

        # Generate priority guidance
        priority_msg = ''
        if critical_count > 0:
            priority_msg = f'\n\n**⚠️ CRITICAL:** Address all {critical_count} critical issues first - these are approval blockers.'
        elif major_count > 0:
            priority_msg = f'\n\n**Priority:** Focus on resolving {major_count} major issues to reach approval threshold.'

        return f'''## Approval Status ❌

**NOT APPROVED - REVISIONS REQUIRED**

This plan requires additional work to meet approval standards.

**Current Score:** {self.score}/100
**Approval Threshold:** 90/100
**Gap:** {gap} points

**Issue Summary:**
- Critical issues: {critical_count} 🔴
- Major issues: {major_count} 🟡
- Minor issues: {minor_count} 🟢{priority_msg}

**Next Steps:**
1. Review the recommendations section above
2. Address issues starting with highest severity
3. Re-validate the plan after revisions
4. Resubmit when score >= 90/100'''
