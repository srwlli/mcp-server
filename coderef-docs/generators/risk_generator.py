"""
Risk assessment generator for assess_risk tool.

Analyzes proposed code changes across 5 risk dimensions (breaking changes, security,
performance, maintainability, reversibility) and generates structured risk assessments
with severity ratings, likelihood scores, and actionable recommendations.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from constants import Paths
from type_defs import (
    RiskDimensionDict, CompositeScoreDict, RecommendationDict,
    MitigationStrategyDict, OptionComparisonDict, ProjectContextDict,
    ProposedChangeDict, RiskAssessmentDict, RiskAssessmentResultDict
)
from logger_config import logger


class RiskGenerator:
    """
    Generator for assessing risk of proposed code changes.

    Evaluates changes across 5 dimensions (breaking, security, performance,
    maintainability, reversibility), calculates composite risk scores, and
    generates structured recommendations with mitigation strategies.
    """

    def __init__(self, project_path: Path):
        """
        Initialize risk assessment generator.

        Args:
            project_path: Absolute path to project directory
        """
        self.project_path = project_path.resolve()  # SEC-001: Canonicalize path
        self.assessment_dir = project_path / Paths.RISK_ASSESSMENTS_DIR

        # Severity to numeric mapping for scoring
        self.severity_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }

        # Compile regex patterns for security analysis
        self._secret_pattern = re.compile(r'(api[_\-\s]?key|password|secret|token|credential)', re.IGNORECASE)
        self._sql_pattern = re.compile(r'(SELECT|INSERT|UPDATE|DELETE)\s+.*\s+(FROM|INTO|SET)', re.IGNORECASE)
        self._exec_pattern = re.compile(r'(exec|eval|system|shell_exec)\s*\(', re.IGNORECASE)

        # Performance patterns
        self._loop_pattern = re.compile(r'for\s*\(|while\s*\(|forEach\(|map\(|filter\(')
        self._query_pattern = re.compile(r'\.(findAll|find|query|select)\(')

        logger.debug(f"Initialized RiskGenerator for {project_path}")

    def analyze_project_context(self) -> ProjectContextDict:
        """
        Analyze project context to gather information for risk evaluation.

        Discovers:
        - Number of files in project
        - Dependencies (if package files exist)
        - Test coverage indicators
        - Architecture patterns

        Returns:
            ProjectContextDict with analyzed context

        Performance: Optimized to complete in < 1 second for typical projects
        """
        logger.info("Analyzing project context for risk assessment")

        context: ProjectContextDict = {
            'files_analyzed': 0,
            'dependencies_found': 0,
            'test_coverage': 0.0,
            'architecture_patterns': [],
            'gaps': []
        }

        try:
            # Count source files (exclude common non-source directories)
            exclude_dirs = {'node_modules', '.git', 'dist', 'build', '__pycache__', '.venv', 'venv'}
            source_files = [
                f for f in self.project_path.rglob('*')
                if f.is_file() and not any(excl in f.parts for excl in exclude_dirs)
            ]
            context['files_analyzed'] = len(source_files)

            # Check for dependencies
            package_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'composer.json', 'go.mod']
            for pkg_file in package_files:
                pkg_path = self.project_path / pkg_file
                if pkg_path.exists():
                    context['dependencies_found'] += self._count_dependencies(pkg_path)

            # Detect test files
            test_files = [f for f in source_files if self._is_test_file(f)]
            if source_files:
                # Rough estimate: test coverage = test files / source files * 100
                context['test_coverage'] = min(100.0, (len(test_files) / len(source_files)) * 100)

            # Detect architecture patterns
            context['architecture_patterns'] = self._detect_architecture_patterns(source_files)

            # Identify gaps
            if context['dependencies_found'] == 0:
                context['gaps'].append("No dependency files found - unable to assess dependency risks")
            if context['test_coverage'] < 50:
                context['gaps'].append(f"Low test coverage ({context['test_coverage']:.1f}%) - risk assessment may be incomplete")

            logger.info(f"Project context analyzed: {context['files_analyzed']} files, {context['dependencies_found']} dependencies")

        except Exception as e:
            logger.warning(f"Error analyzing project context: {e}")
            context['gaps'].append(f"Context analysis incomplete: {str(e)}")

        return context

    def _count_dependencies(self, package_file: Path) -> int:
        """Count dependencies in a package file."""
        try:
            content = package_file.read_text(encoding='utf-8')
            if package_file.name == 'package.json':
                data = json.loads(content)
                return len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))
            elif package_file.name == 'requirements.txt':
                return len([line for line in content.splitlines() if line.strip() and not line.startswith('#')])
            # Add more package managers as needed
        except Exception as e:
            logger.debug(f"Error counting dependencies in {package_file}: {e}")
        return 0

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        name_lower = file_path.name.lower()
        return (
            'test' in name_lower or
            'spec' in name_lower or
            str(file_path).lower().find('/test/') != -1 or
            str(file_path).lower().find('\\test\\') != -1
        )

    def _detect_architecture_patterns(self, source_files: List[Path]) -> List[str]:
        """Detect common architecture patterns in the project."""
        patterns = []

        # Check for common directories/patterns
        dirs = {f.parent.name.lower() for f in source_files}

        if 'controllers' in dirs or 'routes' in dirs:
            patterns.append("MVC/REST API structure")
        if 'components' in dirs and 'pages' in dirs:
            patterns.append("Component-based frontend (React/Vue/etc)")
        if 'models' in dirs or 'entities' in dirs:
            patterns.append("ORM/Data modeling layer")
        if 'services' in dirs:
            patterns.append("Service layer architecture")
        if 'middleware' in dirs:
            patterns.append("Middleware pattern")

        return patterns

    def evaluate_breaking_changes(self, proposed_change: ProposedChangeDict, context: ProjectContextDict) -> RiskDimensionDict:
        """
        Evaluate risk of breaking changes.

        Analyzes:
        - File deletion (critical)
        - API/interface modifications (high)
        - Database schema changes (high)
        - Dependency version changes (medium)

        Args:
            proposed_change: Details of the proposed change
            context: Project context from analyze_project_context()

        Returns:
            RiskDimensionDict with breaking change assessment
        """
        findings = []
        evidence = []
        severity = 'low'
        likelihood = 10.0  # Base likelihood

        change_type = proposed_change['change_type']
        files_affected = proposed_change['files_affected']
        description = proposed_change['description'].lower()

        # Check for deletions
        if change_type == 'delete':
            severity = 'critical'
            likelihood = 90.0
            findings.append("File deletion detected - may break dependent code")
            evidence.append(f"Deleting {len(files_affected)} file(s)")

        # Check for API changes
        api_indicators = ['api', 'endpoint', 'route', 'interface', 'contract', 'schema']
        if any(indicator in description for indicator in api_indicators):
            severity = 'high'
            likelihood = max(likelihood, 70.0)
            findings.append("API or interface modification detected")
            evidence.append("Description mentions API/interface changes")

        # Check for database changes
        db_indicators = ['migration', 'schema', 'database', 'table', 'column']
        if any(indicator in description for indicator in db_indicators):
            severity = 'high'
            likelihood = max(likelihood, 75.0)
            findings.append("Database schema change detected")
            evidence.append("Description mentions database/schema changes")

        # Check affected files for critical patterns
        critical_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'docker-compose.yml']
        for file_path in files_affected:
            if any(critical in file_path.lower() for critical in critical_files):
                severity = max(severity, 'medium', key=lambda x: self.severity_map.get(x, 0))
                likelihood = max(likelihood, 50.0)
                findings.append(f"Critical configuration file affected: {file_path}")
                evidence.append(f"Modifying {file_path}")

        # Calculate score
        score = self._calculate_dimension_score(severity, likelihood)

        return {
            'severity': severity,
            'likelihood': likelihood,
            'score': score,
            'findings': findings if findings else ["No obvious breaking changes detected"],
            'evidence': evidence if evidence else ["Change type and description analyzed"],
            'mitigation_available': True
        }

    def evaluate_security_risks(self, proposed_change: ProposedChangeDict, context: ProjectContextDict) -> RiskDimensionDict:
        """
        Evaluate security risks.

        Analyzes:
        - Hardcoded secrets (critical)
        - SQL injection risks (high)
        - Command injection risks (high)
        - Authentication/authorization changes (medium-high)

        Args:
            proposed_change: Details of the proposed change
            context: Project context

        Returns:
            RiskDimensionDict with security risk assessment
        """
        findings = []
        evidence = []
        severity = 'low'
        likelihood = 5.0

        description = proposed_change['description'].lower()
        files_affected = proposed_change['files_affected']

        # Check for secret-related patterns
        if self._secret_pattern.search(description):
            severity = 'high'
            likelihood = max(likelihood, 60.0)
            findings.append("Potential secret/credential handling detected")
            evidence.append("Description mentions API keys, passwords, or secrets")

        # Check for SQL patterns
        if self._sql_pattern.search(description):
            severity = 'medium'
            likelihood = max(likelihood, 40.0)
            findings.append("SQL query modification detected - verify parameterization")
            evidence.append("Description contains SQL keywords")

        # Check for exec/eval patterns
        if self._exec_pattern.search(description):
            severity = 'critical'
            likelihood = max(likelihood, 80.0)
            findings.append("Code execution function detected - high injection risk")
            evidence.append("Description mentions exec/eval/system functions")

        # Check for auth-related changes
        auth_indicators = ['auth', 'login', 'permission', 'role', 'access', 'security']
        if any(indicator in description for indicator in auth_indicators):
            severity = max(severity, 'medium', key=lambda x: self.severity_map.get(x, 0))
            likelihood = max(likelihood, 50.0)
            findings.append("Authentication/authorization change detected")
            evidence.append("Description mentions auth/security components")

        # Check file paths for security-sensitive files
        sensitive_files = ['auth', 'security', 'permission', 'crypto', 'hash']
        for file_path in files_affected:
            if any(sensitive in file_path.lower() for sensitive in sensitive_files):
                severity = max(severity, 'medium', key=lambda x: self.severity_map.get(x, 0))
                likelihood = max(likelihood, 45.0)
                findings.append(f"Security-sensitive file affected: {file_path}")
                evidence.append(f"Modifying security-related file: {file_path}")

        score = self._calculate_dimension_score(severity, likelihood)

        return {
            'severity': severity,
            'likelihood': likelihood,
            'score': score,
            'findings': findings if findings else ["No obvious security risks detected"],
            'evidence': evidence if evidence else ["Change analyzed for security patterns"],
            'mitigation_available': True
        }

    def evaluate_performance_impact(self, proposed_change: ProposedChangeDict, context: ProjectContextDict) -> RiskDimensionDict:
        """
        Evaluate performance impact.

        Analyzes:
        - Algorithm complexity changes
        - Database query modifications
        - Loop/iteration changes
        - Caching additions/removals

        Args:
            proposed_change: Details of the proposed change
            context: Project context

        Returns:
            RiskDimensionDict with performance impact assessment
        """
        findings = []
        evidence = []
        severity = 'low'
        likelihood = 20.0

        description = proposed_change['description'].lower()

        # Check for performance-related keywords
        perf_negative = ['slow', 'inefficient', 'bottleneck', 'n+1', 'nested loop']
        perf_positive = ['optimize', 'cache', 'index', 'memoize', 'lazy load']

        if any(neg in description for neg in perf_negative):
            severity = 'medium'
            likelihood = max(likelihood, 55.0)
            findings.append("Potential performance degradation mentioned")
            evidence.append("Description mentions performance concerns")

        if any(pos in description for pos in perf_positive):
            severity = 'low'
            likelihood = max(likelihood, 15.0)
            findings.append("Performance optimization mentioned")
            evidence.append("Description mentions performance improvements")

        # Check for query/loop patterns
        if self._query_pattern.search(description):
            severity = max(severity, 'medium', key=lambda x: self.severity_map.get(x, 0))
            likelihood = max(likelihood, 40.0)
            findings.append("Database query modification detected")
            evidence.append("Description contains database query methods")

        if self._loop_pattern.search(description):
            severity = max(severity, 'low', key=lambda x: self.severity_map.get(x, 0))
            likelihood = max(likelihood, 30.0)
            findings.append("Loop or iteration detected")
            evidence.append("Description contains loop constructs")

        score = self._calculate_dimension_score(severity, likelihood)

        return {
            'severity': severity,
            'likelihood': likelihood,
            'score': score,
            'findings': findings if findings else ["No obvious performance impact detected"],
            'evidence': evidence if evidence else ["Change analyzed for performance patterns"],
            'mitigation_available': True
        }

    def evaluate_maintainability(self, proposed_change: ProposedChangeDict, context: ProjectContextDict) -> RiskDimensionDict:
        """
        Evaluate maintainability impact.

        Analyzes:
        - Code complexity
        - Documentation changes
        - Test coverage changes
        - Refactoring scope

        Args:
            proposed_change: Details of the proposed change
            context: Project context

        Returns:
            RiskDimensionDict with maintainability assessment
        """
        findings = []
        evidence = []
        severity = 'low'
        likelihood = 25.0

        description = proposed_change['description'].lower()
        files_affected = proposed_change['files_affected']
        change_type = proposed_change['change_type']

        # Check for large refactorings
        if change_type == 'refactor' and len(files_affected) > 10:
            severity = 'medium'
            likelihood = max(likelihood, 60.0)
            findings.append(f"Large refactoring affecting {len(files_affected)} files")
            evidence.append("Refactoring multiple files increases complexity")

        # Check for documentation
        doc_files = [f for f in files_affected if f.lower().endswith(('.md', '.txt', '.rst'))]
        if doc_files:
            severity = 'low'
            findings.append("Documentation files affected - good for maintainability")
            evidence.append(f"Updating {len(doc_files)} documentation file(s)")

        # Check for test files
        test_files = [f for f in files_affected if 'test' in f.lower() or 'spec' in f.lower()]
        if test_files:
            severity = 'low'
            findings.append("Test files affected - good for maintainability")
            evidence.append(f"Updating {len(test_files)} test file(s)")
        elif context.get('test_coverage', 0) < 50:
            severity = 'medium'
            likelihood = max(likelihood, 45.0)
            findings.append("No tests affected and project has low coverage")
            evidence.append(f"Test coverage: {context.get('test_coverage', 0):.1f}%")

        # Check for complexity indicators
        complex_indicators = ['complex', 'complicated', 'legacy', 'technical debt']
        if any(indicator in description for indicator in complex_indicators):
            severity = max(severity, 'medium', key=lambda x: self.severity_map.get(x, 0))
            likelihood = max(likelihood, 50.0)
            findings.append("Complexity mentioned in change description")
            evidence.append("Description mentions complexity/technical debt")

        score = self._calculate_dimension_score(severity, likelihood)

        return {
            'severity': severity,
            'likelihood': likelihood,
            'score': score,
            'findings': findings if findings else ["No obvious maintainability concerns"],
            'evidence': evidence if evidence else ["Change analyzed for maintainability patterns"],
            'mitigation_available': True
        }

    def evaluate_reversibility(self, proposed_change: ProposedChangeDict, context: ProjectContextDict) -> RiskDimensionDict:
        """
        Evaluate reversibility (rollback difficulty).

        Analyzes:
        - Database migrations (hard to reverse)
        - Data loss potential (irreversible)
        - Config changes (easy to reverse)
        - Deployment complexity

        Args:
            proposed_change: Details of the proposed change
            context: Project context

        Returns:
            RiskDimensionDict with reversibility assessment
        """
        findings = []
        evidence = []
        severity = 'low'
        likelihood = 15.0

        description = proposed_change['description'].lower()
        change_type = proposed_change['change_type']

        # Deletions are hard to reverse
        if change_type == 'delete':
            severity = 'critical'
            likelihood = 95.0
            findings.append("File deletion is difficult to reverse")
            evidence.append("Delete operations require backup/recovery")

        # Database migrations
        migration_indicators = ['migration', 'schema change', 'alter table', 'drop column']
        if any(indicator in description for indicator in migration_indicators):
            severity = 'high'
            likelihood = max(likelihood, 80.0)
            findings.append("Database migration detected - requires rollback script")
            evidence.append("Description mentions database migration")

        # Data modifications
        data_indicators = ['delete data', 'drop table', 'truncate', 'data loss']
        if any(indicator in description for indicator in data_indicators):
            severity = 'critical'
            likelihood = max(likelihood, 90.0)
            findings.append("Potential data loss detected - irreversible")
            evidence.append("Description mentions data deletion/loss")

        # Config changes (usually easy to reverse)
        config_indicators = ['config', 'setting', 'parameter', 'flag']
        if any(indicator in description for indicator in config_indicators):
            severity = 'low'
            likelihood = 10.0
            findings.append("Configuration change - easily reversible")
            evidence.append("Config changes can typically be rolled back")

        score = self._calculate_dimension_score(severity, likelihood)

        return {
            'severity': severity,
            'likelihood': likelihood,
            'score': score,
            'findings': findings if findings else ["No reversibility concerns detected"],
            'evidence': evidence if evidence else ["Change analyzed for rollback difficulty"],
            'mitigation_available': True
        }

    def _calculate_dimension_score(self, severity: str, likelihood: float) -> float:
        """
        Calculate dimension risk score from severity and likelihood.

        Formula: score = (severity_weight * likelihood) / 100 * 25
        Maps to 0-100 scale where:
        - low severity * low likelihood → ~2.5-25
        - critical severity * high likelihood → 80-100

        Args:
            severity: Severity level (low, medium, high, critical)
            likelihood: Likelihood percentage (0-100)

        Returns:
            Risk score (0-100)
        """
        severity_weight = self.severity_map.get(severity, 1)
        # Score = (severity * likelihood) normalized to 0-100
        # Max score: 4 * 100 = 400, so divide by 4 to get 0-100
        score = (severity_weight * likelihood) / 4.0
        return min(100.0, max(0.0, score))  # Clamp to 0-100

    def calculate_composite_score(self, dimensions: Dict[str, RiskDimensionDict]) -> CompositeScoreDict:
        """
        Calculate composite risk score from all 5 dimensions.

        Uses weighted average:
        - Breaking changes: 30%
        - Security: 25%
        - Performance: 15%
        - Maintainability: 15%
        - Reversibility: 15%

        Args:
            dimensions: Dict of all 5 risk dimension assessments

        Returns:
            CompositeScoreDict with overall risk score and level
        """
        weights = {
            'breaking_changes': 0.30,
            'security': 0.25,
            'performance': 0.15,
            'maintainability': 0.15,
            'reversibility': 0.15
        }

        # Calculate weighted score
        total_score = sum(
            dimensions[dim]['score'] * weights[dim]
            for dim in weights.keys()
        )

        # Determine risk level based on score
        if total_score >= 75:
            level = 'critical'
        elif total_score >= 50:
            level = 'high'
        elif total_score >= 25:
            level = 'medium'
        else:
            level = 'low'

        # Calculate confidence based on project context completeness
        # (This is simplified - actual confidence would consider more factors)
        confidence = 0.8  # Default high confidence

        explanation = (
            f"Composite score calculated as weighted average: "
            f"Breaking={dimensions['breaking_changes']['score']:.1f}×30%, "
            f"Security={dimensions['security']['score']:.1f}×25%, "
            f"Performance={dimensions['performance']['score']:.1f}×15%, "
            f"Maintainability={dimensions['maintainability']['score']:.1f}×15%, "
            f"Reversibility={dimensions['reversibility']['score']:.1f}×15% "
            f"= {total_score:.1f}"
        )

        return {
            'score': total_score,
            'level': level,
            'explanation': explanation,
            'confidence': confidence
        }

    def generate_recommendations(
        self,
        composite_score: CompositeScoreDict,
        dimensions: Dict[str, RiskDimensionDict],
        threshold: float = 50.0
    ) -> RecommendationDict:
        """
        Generate go/no-go recommendation based on risk score and threshold.

        Args:
            composite_score: Overall composite score
            dimensions: All dimension assessments
            threshold: Risk threshold for decision (default: 50.0)

        Returns:
            RecommendationDict with decision and rationale
        """
        score = composite_score['score']
        level = composite_score['level']

        # Determine decision
        if score < threshold * 0.5:
            decision = 'go'
        elif score < threshold:
            decision = 'proceed-with-caution'
        elif score < threshold * 1.5:
            decision = 'needs-review'
        else:
            decision = 'no-go'

        # Build rationale
        high_risk_dims = [
            dim_name for dim_name, dim_data in dimensions.items()
            if dim_data['score'] >= 50
        ]

        if decision == 'go':
            rationale = f"Risk score ({score:.1f}) is well below threshold ({threshold}). No significant risks identified across all dimensions."
        elif decision == 'proceed-with-caution':
            rationale = f"Risk score ({score:.1f}) is moderate. {len(high_risk_dims)} dimension(s) show elevated risk: {', '.join(high_risk_dims)}. Review mitigation strategies before proceeding."
        elif decision == 'needs-review':
            rationale = f"Risk score ({score:.1f}) exceeds threshold ({threshold}). High-risk dimensions: {', '.join(high_risk_dims)}. Manual review required."
        else:
            rationale = f"Risk score ({score:.1f}) is critically high. Major risks in: {', '.join(high_risk_dims)}. Not recommended without substantial risk mitigation."

        # Add conditions for safer proceeding
        conditions = []
        if 'breaking_changes' in high_risk_dims:
            conditions.append("Ensure comprehensive test coverage before deployment")
        if 'security' in high_risk_dims:
            conditions.append("Security review and penetration testing required")
        if 'reversibility' in high_risk_dims:
            conditions.append("Create rollback plan and backup data")

        return {
            'decision': decision,
            'rationale': rationale,
            'conditions': conditions if conditions else []
        }

    def generate_mitigation_strategies(self, dimensions: Dict[str, RiskDimensionDict]) -> List[MitigationStrategyDict]:
        """
        Generate actionable mitigation strategies for identified risks.

        Args:
            dimensions: All dimension assessments

        Returns:
            List of MitigationStrategyDict with prioritized strategies
        """
        strategies: List[MitigationStrategyDict] = []

        # Breaking changes mitigations
        if dimensions['breaking_changes']['score'] >= 30:
            strategies.append({
                'risk_dimension': 'breaking_changes',
                'strategy': 'Implement feature flags to enable gradual rollout and quick rollback',
                'priority': 'high' if dimensions['breaking_changes']['score'] >= 50 else 'medium',
                'estimated_effort': 'medium'
            })
            strategies.append({
                'risk_dimension': 'breaking_changes',
                'strategy': 'Add integration tests covering all affected APIs and interfaces',
                'priority': 'high',
                'estimated_effort': 'high'
            })

        # Security mitigations
        if dimensions['security']['score'] >= 30:
            strategies.append({
                'risk_dimension': 'security',
                'strategy': 'Conduct security code review with focus on injection and auth vulnerabilities',
                'priority': 'critical' if dimensions['security']['score'] >= 70 else 'high',
                'estimated_effort': 'medium'
            })
            strategies.append({
                'risk_dimension': 'security',
                'strategy': 'Run static analysis security testing (SAST) tools',
                'priority': 'high',
                'estimated_effort': 'low'
            })

        # Performance mitigations
        if dimensions['performance']['score'] >= 30:
            strategies.append({
                'risk_dimension': 'performance',
                'strategy': 'Benchmark performance before and after changes to measure impact',
                'priority': 'medium',
                'estimated_effort': 'medium'
            })
            strategies.append({
                'risk_dimension': 'performance',
                'strategy': 'Add database query indexes if modifying data access patterns',
                'priority': 'medium',
                'estimated_effort': 'low'
            })

        # Maintainability mitigations
        if dimensions['maintainability']['score'] >= 30:
            strategies.append({
                'risk_dimension': 'maintainability',
                'strategy': 'Add comprehensive code documentation and update architecture docs',
                'priority': 'medium',
                'estimated_effort': 'medium'
            })

        # Reversibility mitigations
        if dimensions['reversibility']['score'] >= 30:
            strategies.append({
                'risk_dimension': 'reversibility',
                'strategy': 'Create database migration rollback scripts',
                'priority': 'critical' if dimensions['reversibility']['score'] >= 70 else 'high',
                'estimated_effort': 'medium'
            })
            strategies.append({
                'risk_dimension': 'reversibility',
                'strategy': 'Document rollback procedure in deployment plan',
                'priority': 'high',
                'estimated_effort': 'low'
            })

        return strategies

    def compare_options(
        self,
        options: List[dict],
        context: ProjectContextDict
    ) -> Dict[str, Any]:
        """
        Compare multiple alternative approaches and rank by risk.

        Args:
            options: List of alternative options (each with description, files_affected, etc.)
            context: Project context

        Returns:
            Dict with comparison results, rankings, and recommended option
        """
        logger.info(f"Comparing {len(options)} alternative options")

        option_assessments = []

        for i, option in enumerate(options):
            option_id = f"option_{i+1}"

            # Treat each option as a proposed change
            proposed_change: ProposedChangeDict = {
                'description': option.get('description', f'Option {i+1}'),
                'change_type': option.get('change_type', 'modify'),
                'files_affected': option.get('files_affected', []),
                'context': option.get('context', {})
            }

            # Evaluate all dimensions
            dimensions = {
                'breaking_changes': self.evaluate_breaking_changes(proposed_change, context),
                'security': self.evaluate_security_risks(proposed_change, context),
                'performance': self.evaluate_performance_impact(proposed_change, context),
                'maintainability': self.evaluate_maintainability(proposed_change, context),
                'reversibility': self.evaluate_reversibility(proposed_change, context)
            }

            # Calculate composite score
            composite = self.calculate_composite_score(dimensions)

            # Extract pros/cons from findings
            pros = []
            cons = []
            for dim_name, dim_data in dimensions.items():
                for finding in dim_data['findings']:
                    if 'good' in finding.lower() or 'easy' in finding.lower() or 'optimization' in finding.lower():
                        pros.append(f"{dim_name.replace('_', ' ').title()}: {finding}")
                    elif dim_data['score'] >= 30:
                        cons.append(f"{dim_name.replace('_', ' ').title()}: {finding}")

            option_assessments.append({
                'option_id': option_id,
                'description': proposed_change['description'],
                'composite_score': composite['score'],
                'rank': 0,  # Will be set after sorting
                'pros': pros if pros else ["No specific advantages identified"],
                'cons': cons if cons else ["No specific disadvantages identified"]
            })

        # Sort by score (lowest risk = best rank)
        option_assessments.sort(key=lambda x: x['composite_score'])

        # Assign ranks
        for rank, assessment in enumerate(option_assessments, start=1):
            assessment['rank'] = rank

        # Recommended option is the one with lowest risk score
        recommended_option = option_assessments[0]['option_id']

        return {
            'options': option_assessments,
            'recommended_option': recommended_option
        }

    def save_assessment(self, assessment: RiskAssessmentDict, feature_name: str = None) -> Path:
        """
        Save risk assessment to JSON file.

        Args:
            assessment: Complete risk assessment data
            feature_name: Optional feature name for filename

        Returns:
            Path to saved assessment file
        """
        # Create assessments directory if it doesn't exist
        self.assessment_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if feature_name:
            filename = f"{feature_name}-{timestamp}.json"
        else:
            filename = f"assessment-{timestamp}.json"

        filepath = self.assessment_dir / filename

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(assessment, f, indent=2)

        logger.info(f"Risk assessment saved to {filepath}")

        return filepath
