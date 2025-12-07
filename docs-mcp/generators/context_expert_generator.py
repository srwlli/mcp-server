"""Context Expert Generator for creating and managing domain-specific context experts.

This generator handles:
- Code structure analysis (AST for Python, regex for JS/TS)
- Git history extraction
- Relationship detection (imports/exports)
- Staleness calculation
- Expert candidate discovery

Part of the Context Experts feature (v3.0.0).
"""

import ast
import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import (
    ContextExpertPaths,
    ContextExpertStatus,
    ContextExpertCapability,
    ResourceType,
    ExpertDomain,
    EXPERT_ID_PATTERN
)
from context_expert_models import (
    GitHistoryEntry,
    CodeStructure,
    RelationshipContext,
    UsagePattern,
    ContextExpertDefinition,
    ContextExpertIndex,
    ExpertSuggestion,
    ExpertOnboarding
)
from logger_config import logger, log_error


class ContextExpertGenerator:
    """Generator class for creating and managing context experts."""

    def __init__(self, project_path: Path):
        """
        Initialize context expert generator.

        Args:
            project_path: Absolute path to project directory
        """
        self.project_path = Path(project_path).resolve()
        self.experts_dir = self.project_path / ContextExpertPaths.EXPERTS
        self.cache_dir = self.project_path / ContextExpertPaths.CACHE
        self.index_path = self.project_path / ContextExpertPaths.INDEX

    def _ensure_directories(self) -> None:
        """Create expert storage directories if they don't exist."""
        self.experts_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_expert_id(self, resource_path: str) -> str:
        """
        Generate unique expert ID from resource path.

        Format: CE-{resource-slug}-NNN
        """
        # Create slug from path
        slug = resource_path.replace('/', '-').replace('\\', '-').replace('.', '_')
        slug = re.sub(r'[^a-zA-Z0-9_-]', '', slug)
        slug = slug[:30]  # Limit length

        # Get next number for this slug
        existing = list(self.experts_dir.glob(f"{slug}*.json"))
        next_num = len(existing) + 1

        return f"CE-{slug}-{next_num:03d}"

    def _compute_content_hash(self, resource_path: str) -> str:
        """Compute SHA256 hash of resource content for change detection."""
        full_path = self.project_path / resource_path
        if full_path.is_file():
            content = full_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        elif full_path.is_dir():
            # Hash directory listing + file hashes
            files = sorted(full_path.rglob('*'))
            content = ''.join(str(f) for f in files[:100])  # Limit for performance
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return 'unknown'

    def analyze_code_structure(self, resource_path: str) -> CodeStructure:
        """
        Analyze code structure using AST for Python or regex for JS/TS.

        Args:
            resource_path: Relative path to file or directory

        Returns:
            CodeStructure with functions, classes, imports, exports, etc.
        """
        full_path = self.project_path / resource_path

        functions: List[str] = []
        classes: List[str] = []
        imports: List[str] = []
        exports: List[str] = []
        line_count = 0
        complexity_score = 0.0

        if full_path.is_file():
            files = [full_path]
        elif full_path.is_dir():
            files = list(full_path.rglob('*.py')) + list(full_path.rglob('*.ts')) + \
                    list(full_path.rglob('*.tsx')) + list(full_path.rglob('*.js')) + \
                    list(full_path.rglob('*.jsx'))
        else:
            return CodeStructure(
                functions=[], classes=[], imports=[], exports=[],
                line_count=0, complexity_score=0.0
            )

        for file_path in files[:50]:  # Limit for performance
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                line_count += len(lines)

                if file_path.suffix == '.py':
                    # Use AST for Python
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                functions.append(node.name)
                            elif isinstance(node, ast.AsyncFunctionDef):
                                functions.append(f"async {node.name}")
                            elif isinstance(node, ast.ClassDef):
                                classes.append(node.name)
                            elif isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports.append(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports.append(node.module)
                    except SyntaxError:
                        # Fall back to regex for invalid Python
                        self._extract_with_regex(content, functions, classes, imports, exports)
                else:
                    # Use regex for JS/TS
                    self._extract_with_regex(content, functions, classes, imports, exports)

            except Exception as e:
                log_error('code_structure_analysis', str(e), file_path=str(file_path))
                continue

        # Calculate complexity score (simplified)
        complexity_score = min(100.0, (
            len(functions) * 2 +
            len(classes) * 5 +
            len(imports) * 0.5 +
            line_count / 100
        ))

        return CodeStructure(
            functions=functions[:100],  # Limit results
            classes=classes[:50],
            imports=list(set(imports))[:100],
            exports=list(set(exports))[:50],
            line_count=line_count,
            complexity_score=round(complexity_score, 2)
        )

    def _extract_with_regex(
        self,
        content: str,
        functions: List[str],
        classes: List[str],
        imports: List[str],
        exports: List[str]
    ) -> None:
        """Extract code structure using regex (for JS/TS or fallback)."""
        # Functions: function name(), const name = () =>, async function name()
        fn_patterns = [
            r'function\s+(\w+)\s*\(',
            r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>',
            r'(\w+)\s*:\s*(?:async\s*)?\([^)]*\)\s*=>',  # Object method
            r'async\s+function\s+(\w+)\s*\(',
        ]
        for pattern in fn_patterns:
            functions.extend(re.findall(pattern, content))

        # Classes: class Name
        class_matches = re.findall(r'class\s+(\w+)', content)
        classes.extend(class_matches)

        # Imports
        import_patterns = [
            r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]',
        ]
        for pattern in import_patterns:
            imports.extend(re.findall(pattern, content))

        # Exports
        export_patterns = [
            r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
            r'export\s*\{\s*([^}]+)\s*\}',
            r'module\.exports\s*=\s*(\w+)',
        ]
        for pattern in export_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if ',' in match:
                    exports.extend([e.strip() for e in match.split(',')])
                else:
                    exports.append(match)

    def extract_git_history(self, resource_path: str, limit: int = 20) -> List[GitHistoryEntry]:
        """
        Extract git history for a resource.

        Args:
            resource_path: Relative path to file or directory
            limit: Maximum number of commits to retrieve

        Returns:
            List of GitHistoryEntry objects
        """
        history: List[GitHistoryEntry] = []
        full_path = self.project_path / resource_path

        try:
            # Git log with file changes
            result = subprocess.run(
                [
                    'git', 'log', f'-{limit}',
                    '--pretty=format:%H|%an|%aI|%s',
                    '--numstat',
                    '--', str(full_path)
                ],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return history

            current_entry: Optional[Dict[str, Any]] = None

            for line in result.stdout.splitlines():
                if '|' in line and len(line.split('|')) >= 4:
                    # New commit line
                    if current_entry:
                        history.append(GitHistoryEntry(**current_entry))

                    parts = line.split('|')
                    current_entry = {
                        'commit_hash': parts[0][:8],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3],
                        'files_changed': [],
                        'lines_added': 0,
                        'lines_deleted': 0
                    }
                elif line.strip() and current_entry:
                    # File change line (added\tdeleted\tfilename)
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            current_entry['lines_added'] += added
                            current_entry['lines_deleted'] += deleted
                            current_entry['files_changed'].append(parts[2])
                        except ValueError:
                            pass

            if current_entry:
                history.append(GitHistoryEntry(**current_entry))

        except subprocess.TimeoutExpired:
            log_error('git_history_timeout', 'Git log timed out', resource_path=resource_path)
        except Exception as e:
            log_error('git_history_error', str(e), resource_path=resource_path)

        return history

    def detect_relationships(self, resource_path: str) -> RelationshipContext:
        """
        Detect file relationships: dependencies, dependents, tests, docs.

        Args:
            resource_path: Relative path to file or directory

        Returns:
            RelationshipContext with relationship data
        """
        full_path = self.project_path / resource_path

        dependencies: List[str] = []
        dependents: List[str] = []
        test_files: List[str] = []
        doc_files: List[str] = []
        config_files: List[str] = []

        # Get resource name for searching
        resource_name = Path(resource_path).stem

        # Find dependencies (files this resource imports)
        if full_path.is_file():
            try:
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                # Extract import paths
                import_patterns = [
                    r'from\s+([.\w]+)\s+import',
                    r'import\s+([.\w]+)',
                    r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                    r'require\s*\(\s*[\'"]([^\'"]+)[\'"]',
                ]
                for pattern in import_patterns:
                    for match in re.findall(pattern, content):
                        if not match.startswith('.'):
                            dependencies.append(match)
            except Exception:
                pass

        # Find dependents (files that import this resource)
        try:
            result = subprocess.run(
                ['git', 'grep', '-l', resource_name],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines()[:20]:
                    if line != resource_path and not line.startswith('.git'):
                        dependents.append(line)
        except Exception:
            pass

        # Find associated test files
        test_patterns = [
            f'test_{resource_name}.py',
            f'{resource_name}_test.py',
            f'{resource_name}.test.ts',
            f'{resource_name}.test.js',
            f'{resource_name}.spec.ts',
            f'{resource_name}.spec.js',
        ]
        for test_dir in ['tests', 'test', '__tests__', 'spec']:
            test_path = self.project_path / test_dir
            if test_path.exists():
                for pattern in test_patterns:
                    for match in test_path.rglob(pattern):
                        test_files.append(str(match.relative_to(self.project_path)))

        # Find related documentation
        doc_patterns = [
            f'{resource_name}.md',
            f'{resource_name.upper()}.md',
            f'{resource_name}-docs.md',
        ]
        for doc_dir in ['docs', 'doc', 'documentation', '.']:
            doc_path = self.project_path / doc_dir
            if doc_path.exists():
                for pattern in doc_patterns:
                    for match in doc_path.glob(pattern):
                        doc_files.append(str(match.relative_to(self.project_path)))

        # Find related config files
        config_patterns = [
            f'{resource_name}.config.*',
            f'{resource_name}.json',
            f'{resource_name}.yaml',
            f'{resource_name}.yml',
        ]
        for pattern in config_patterns:
            for match in self.project_path.glob(pattern):
                config_files.append(str(match.relative_to(self.project_path)))

        return RelationshipContext(
            dependencies=list(set(dependencies))[:50],
            dependents=list(set(dependents))[:50],
            test_files=list(set(test_files))[:20],
            doc_files=list(set(doc_files))[:10],
            config_files=list(set(config_files))[:10]
        )

    def analyze_usage_patterns(self, resource_path: str) -> UsagePattern:
        """
        Analyze how/where a resource is used.

        Args:
            resource_path: Relative path to file or directory

        Returns:
            UsagePattern with call sites, usage count, etc.
        """
        full_path = self.project_path / resource_path
        resource_name = Path(resource_path).stem

        call_sites: List[str] = []
        usage_count = 0
        hot_paths: List[str] = []

        # Search for usages of exported symbols
        try:
            result = subprocess.run(
                ['git', 'grep', '-n', resource_name],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 2 and parts[0] != resource_path:
                            call_sites.append(f"{parts[0]}:{parts[1]}")
                            usage_count += 1
        except Exception:
            pass

        # Identify hot paths (frequently referenced files)
        file_counts: Dict[str, int] = {}
        for site in call_sites:
            file_path = site.split(':')[0]
            file_counts[file_path] = file_counts.get(file_path, 0) + 1

        hot_paths = sorted(file_counts.keys(), key=lambda x: file_counts[x], reverse=True)[:5]

        # Get last modified time
        last_modified = datetime.now(timezone.utc).isoformat()
        if full_path.exists():
            stat = full_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()

        return UsagePattern(
            call_sites=call_sites[:50],
            usage_count=usage_count,
            hot_paths=hot_paths,
            last_modified=last_modified
        )

    def calculate_staleness(self, expert: ContextExpertDefinition) -> float:
        """
        Calculate staleness score (0-100) for an expert.

        0 = completely up-to-date
        100 = completely stale

        Args:
            expert: The expert definition to check

        Returns:
            Staleness score 0-100
        """
        # Compare current content hash with stored hash
        current_hash = self._compute_content_hash(expert['resource_path'])
        stored_hash = expert.get('resource_hash', '')

        if current_hash != stored_hash:
            # Content has changed
            return 75.0

        # Check time since last refresh
        try:
            last_refreshed = datetime.fromisoformat(expert['last_refreshed'].replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_old = (now - last_refreshed).days

            if days_old > 30:
                return 50.0
            elif days_old > 7:
                return 25.0
            else:
                return max(0.0, days_old * 2.0)
        except Exception:
            return 50.0

    def suggest_candidates(
        self,
        criteria: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[ExpertSuggestion]:
        """
        Auto-discover expert candidates based on codebase analysis.

        Args:
            criteria: Optional filter criteria
            limit: Maximum number of suggestions

        Returns:
            List of ExpertSuggestion objects
        """
        suggestions: List[ExpertSuggestion] = []
        criteria = criteria or {}

        # Default search patterns for important files
        important_patterns = [
            # Core files
            ('**/server.py', 'Core server entry point', ['high_impact', 'core']),
            ('**/main.py', 'Main application entry', ['high_impact', 'core']),
            ('**/app.py', 'Application module', ['high_impact', 'core']),
            # API handlers
            ('**/handlers/**/*.py', 'API handler', ['api', 'high_change']),
            ('**/routes/**/*.ts', 'API routes', ['api']),
            ('**/controllers/**/*.ts', 'Controllers', ['api']),
            # Data layer
            ('**/models/**/*.py', 'Data models', ['db', 'schema']),
            ('**/schemas/**/*.py', 'Schemas', ['db', 'validation']),
            ('**/migrations/**/*.py', 'Database migrations', ['db', 'high_risk']),
            # UI components
            ('**/components/**/*.tsx', 'UI components', ['ui', 'high_change']),
            ('**/components/**/*.vue', 'Vue components', ['ui']),
            # Tests
            ('**/tests/**/*.py', 'Test suite', ['test']),
            ('**/__tests__/**/*.ts', 'Test files', ['test']),
            # Config
            ('**/config/**/*', 'Configuration', ['config', 'infra']),
        ]

        for pattern, reason, matched_criteria in important_patterns:
            for match in self.project_path.glob(pattern):
                if match.is_file() and len(suggestions) < limit:
                    rel_path = str(match.relative_to(self.project_path))

                    # Skip already-created experts
                    expert_file = self.experts_dir / f"{Path(rel_path).stem}.json"
                    if expert_file.exists():
                        continue

                    # Calculate confidence based on criteria match
                    confidence = 0.5 + (len(matched_criteria) * 0.1)

                    # Boost for frequently changed files
                    git_history = self.extract_git_history(rel_path, limit=5)
                    if len(git_history) >= 5:
                        confidence += 0.2
                        matched_criteria.append('high_change_frequency')

                    suggestions.append(ExpertSuggestion(
                        resource_path=rel_path,
                        resource_type='file',
                        suggestion_reason=reason,
                        criteria_matched=matched_criteria,
                        confidence_score=min(1.0, confidence),
                        metrics={
                            'recent_commits': len(git_history),
                            'file_size': match.stat().st_size
                        }
                    ))

        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence_score'], reverse=True)
        return suggestions[:limit]

    def create_expert(
        self,
        resource_path: str,
        resource_type: str,
        capabilities: List[str],
        domain: str,
        workorder_id: Optional[str] = None,
        assigned_by: Optional[str] = None
    ) -> ContextExpertDefinition:
        """
        Create a new context expert for a resource.

        Args:
            resource_path: Relative path to file or directory
            resource_type: 'file' or 'directory'
            capabilities: List of capabilities (answer_questions, review_changes, generate_docs)
            domain: Domain specialization (ui, db, api, core, test, etc.)
            workorder_id: Optional associated workorder
            assigned_by: Optional agent ID that assigned this expert

        Returns:
            Complete ContextExpertDefinition
        """
        self._ensure_directories()

        now = datetime.now(timezone.utc).isoformat()
        expert_id = self._generate_expert_id(resource_path)

        # Analyze the resource
        code_structure = self.analyze_code_structure(resource_path)
        git_history = self.extract_git_history(resource_path)
        relationships = self.detect_relationships(resource_path)
        usage_patterns = self.analyze_usage_patterns(resource_path)

        # Generate expertise areas from code analysis
        expertise_areas = []
        if code_structure['classes']:
            expertise_areas.append('object-oriented')
        if code_structure['functions']:
            expertise_areas.append('functional')
        if any('async' in f for f in code_structure['functions']):
            expertise_areas.append('async-patterns')
        if relationships['test_files']:
            expertise_areas.append('tested')
        if relationships['dependencies']:
            expertise_areas.append('integrated')

        # Extract inline documentation
        full_path = self.project_path / resource_path
        inline_docs = None
        if full_path.is_file():
            try:
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                # Extract docstrings and major comments
                docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)[:5]
                if docstrings:
                    inline_docs = '\n---\n'.join(d.strip()[:500] for d in docstrings)
            except Exception:
                pass

        # Create expert name from path
        name = Path(resource_path).stem.replace('_', ' ').replace('-', ' ').title()
        name = f"{domain.upper()} Expert: {name}"

        expert = ContextExpertDefinition(
            expert_id=expert_id,
            name=name,
            version='1.0.0',
            created_at=now,
            updated_at=now,
            resource_type=resource_type,
            resource_path=resource_path,
            resource_hash=self._compute_content_hash(resource_path),
            code_structure=code_structure,
            git_history=git_history,
            relationships=relationships,
            usage_patterns=usage_patterns,
            inline_docs=inline_docs,
            related_docs=relationships['doc_files'],
            capabilities=capabilities,
            expertise_areas=expertise_areas,
            domain=domain,
            onboarding=None,  # Lloyd will fill this in
            assignment_type='manual' if assigned_by else 'auto_suggested',
            assigned_by=assigned_by,
            workorder_id=workorder_id,
            status=ContextExpertStatus.ACTIVE.value,
            last_refreshed=now,
            staleness_score=0.0
        )

        # Save expert to file
        import json
        expert_file = self.experts_dir / f"{expert_id}.json"
        with open(expert_file, 'w', encoding='utf-8') as f:
            json.dump(expert, f, indent=2)

        # Update index
        self._update_index(expert)

        logger.info(f"Created context expert: {expert_id}", extra={
            'expert_id': expert_id,
            'resource_path': resource_path,
            'domain': domain
        })

        return expert

    def _update_index(self, expert: ContextExpertDefinition) -> None:
        """Update the expert index with new/updated expert."""
        import json

        # Load or create index
        index: ContextExpertIndex = {
            'version': '1.0.0',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_experts': 0,
            'experts': [],
            'auto_suggestions': []
        }

        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except Exception:
                pass

        # Update or add expert entry
        expert_summary = {
            'expert_id': expert['expert_id'],
            'name': expert['name'],
            'resource_path': expert['resource_path'],
            'domain': expert['domain'],
            'status': expert['status'],
            'staleness_score': expert['staleness_score']
        }

        # Remove existing entry if present
        index['experts'] = [e for e in index['experts'] if e.get('expert_id') != expert['expert_id']]
        index['experts'].append(expert_summary)
        index['total_experts'] = len(index['experts'])
        index['generated_at'] = datetime.now(timezone.utc).isoformat()

        # Save index
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    def get_expert(self, expert_id: str) -> Optional[ContextExpertDefinition]:
        """
        Retrieve an expert by ID.

        Args:
            expert_id: The expert ID (CE-xxx-NNN format)

        Returns:
            ContextExpertDefinition or None if not found
        """
        import json
        expert_file = self.experts_dir / f"{expert_id}.json"

        if not expert_file.exists():
            return None

        try:
            with open(expert_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_error('get_expert_error', str(e), expert_id=expert_id)
            return None

    def list_experts(
        self,
        domain: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all experts with optional filtering.

        Args:
            domain: Filter by domain (ui, db, api, etc.)
            status: Filter by status (active, stale, archived)

        Returns:
            List of expert summaries
        """
        import json

        if not self.index_path.exists():
            return []

        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        except Exception:
            return []

        experts = index.get('experts', [])

        if domain:
            experts = [e for e in experts if e.get('domain') == domain]
        if status:
            experts = [e for e in experts if e.get('status') == status]

        return experts

    def update_expert(self, expert_id: str) -> Optional[ContextExpertDefinition]:
        """
        Refresh an expert's context data.

        Args:
            expert_id: The expert ID to update

        Returns:
            Updated ContextExpertDefinition or None if not found
        """
        import json

        expert = self.get_expert(expert_id)
        if not expert:
            return None

        # Re-analyze the resource
        resource_path = expert['resource_path']

        expert['code_structure'] = self.analyze_code_structure(resource_path)
        expert['git_history'] = self.extract_git_history(resource_path)
        expert['relationships'] = self.detect_relationships(resource_path)
        expert['usage_patterns'] = self.analyze_usage_patterns(resource_path)
        expert['resource_hash'] = self._compute_content_hash(resource_path)
        expert['updated_at'] = datetime.now(timezone.utc).isoformat()
        expert['last_refreshed'] = datetime.now(timezone.utc).isoformat()
        expert['staleness_score'] = 0.0

        # Save updated expert
        expert_file = self.experts_dir / f"{expert_id}.json"
        with open(expert_file, 'w', encoding='utf-8') as f:
            json.dump(expert, f, indent=2)

        # Update index
        self._update_index(expert)

        logger.info(f"Updated context expert: {expert_id}")
        return expert

    def add_onboarding(
        self,
        expert_id: str,
        assigned_docs: List[str],
        domain_scope: str,
        briefing_notes: str,
        onboarded_by: str = 'Lloyd'
    ) -> Optional[ContextExpertDefinition]:
        """
        Add Lloyd's onboarding data to an expert.

        Args:
            expert_id: The expert ID
            assigned_docs: List of docs the expert should read
            domain_scope: Domain specialization description
            briefing_notes: Custom briefing from Lloyd
            onboarded_by: Agent ID (default: Lloyd)

        Returns:
            Updated ContextExpertDefinition or None if not found
        """
        import json

        expert = self.get_expert(expert_id)
        if not expert:
            return None

        expert['onboarding'] = ExpertOnboarding(
            assigned_docs=assigned_docs,
            domain_scope=domain_scope,
            briefing_notes=briefing_notes,
            onboarded_at=datetime.now(timezone.utc).isoformat(),
            onboarded_by=onboarded_by
        )
        expert['updated_at'] = datetime.now(timezone.utc).isoformat()

        # Save updated expert
        expert_file = self.experts_dir / f"{expert_id}.json"
        with open(expert_file, 'w', encoding='utf-8') as f:
            json.dump(expert, f, indent=2)

        logger.info(f"Added onboarding to expert: {expert_id}", extra={
            'onboarded_by': onboarded_by
        })
        return expert
