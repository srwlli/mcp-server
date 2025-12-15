"""
CodeRef Foundation Generator - Unified foundation docs powered by coderef analysis.

Generates comprehensive project context for planning workflows:
- ARCHITECTURE.md (patterns, decisions, constraints)
- SCHEMA.md (entities, relationships)
- COMPONENTS.md (component hierarchy - UI projects only)
- project-context.json (structured context for planning)

Replaces: api_inventory, database_inventory, dependency_inventory,
          config_inventory, test_inventory, inventory_manifest, documentation_inventory
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re
import subprocess
from datetime import datetime

from logger_config import logger
from constants import EXCLUDE_DIRS, ALLOWED_FILE_EXTENSIONS

__all__ = ['CoderefFoundationGenerator']


class CoderefFoundationGenerator:
    """
    Unified foundation docs generator powered by coderef analysis.

    Generates:
    - ARCHITECTURE.md (patterns, decisions, constraints)
    - SCHEMA.md (entities, relationships)
    - COMPONENTS.md (component hierarchy - UI projects only)
    - project-context.json (structured context for planning)
    """

    def __init__(
        self,
        project_path: Path,
        include_components: Optional[bool] = None,
        deep_extraction: bool = True,
        use_coderef: bool = True
    ):
        """
        Initialize generator.

        Args:
            project_path: Path to project directory
            include_components: Generate COMPONENTS.md (None = auto-detect UI project)
            deep_extraction: Deep extraction from existing docs (vs shallow preview)
            use_coderef: Use coderef-mcp for pattern detection
        """
        self.project_path = project_path
        self.include_components = include_components
        self.deep_extraction = deep_extraction
        self.use_coderef = use_coderef

        # Output directories
        self.foundation_docs_dir = project_path / 'coderef' / 'foundation-docs'
        self.foundation_docs_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Initialized CoderefFoundationGenerator for: {project_path}")

    def generate(self) -> Dict[str, Any]:
        """
        Main generation method - orchestrates all operations.

        Returns:
            Dict with generated files, project context, and metadata
        """
        import time
        start_time = time.time()

        logger.info("Starting coderef foundation docs generation", extra={'project_path': str(self.project_path)})

        # Detect if UI project (for COMPONENTS.md)
        is_ui_project = self._detect_ui_project() if self.include_components is None else self.include_components

        # Phase 1: Deep extraction from existing foundation docs
        logger.info("Phase 1: Extracting from existing foundation docs...")
        existing_docs = self._extract_existing_docs()

        # Phase 2: Auto-detect from code
        logger.info("Phase 2: Auto-detecting from code...")
        api_context = self._detect_api_endpoints()
        database_context = self._detect_database_schema()
        dependencies_context = self._detect_dependencies()

        # Phase 3: Git activity analysis
        logger.info("Phase 3: Analyzing git activity...")
        git_activity = self._analyze_git_activity()

        # Phase 4: Code pattern detection (coderef-mcp integration)
        logger.info("Phase 4: Detecting code patterns...")
        patterns = self._detect_code_patterns() if self.use_coderef else {}

        # Phase 5: Similar features discovery
        logger.info("Phase 5: Discovering similar features...")
        similar_features = self._discover_similar_features()

        # Build project context JSON
        project_context = {
            'api_context': api_context,
            'dependencies': dependencies_context,
            'database': database_context,
            'activity': git_activity,
            'patterns': patterns,
            'similar_features': similar_features,
            'existing_docs': existing_docs,
            '_metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'coderef_foundation_generator',
                'version': '1.0.0'
            }
        }

        # Generate output files
        files_generated = []

        # Generate ARCHITECTURE.md
        arch_content = self._generate_architecture_md(project_context, existing_docs)
        arch_path = self.foundation_docs_dir / 'ARCHITECTURE.md'
        arch_path.write_text(arch_content, encoding='utf-8')
        files_generated.append('ARCHITECTURE.md')

        # Generate SCHEMA.md
        schema_content = self._generate_schema_md(project_context, existing_docs)
        schema_path = self.foundation_docs_dir / 'SCHEMA.md'
        schema_path.write_text(schema_content, encoding='utf-8')
        files_generated.append('SCHEMA.md')

        # Generate COMPONENTS.md (conditional)
        if is_ui_project:
            components_content = self._generate_components_md(project_context, existing_docs)
            components_path = self.foundation_docs_dir / 'COMPONENTS.md'
            components_path.write_text(components_content, encoding='utf-8')
            files_generated.append('COMPONENTS.md')

        # Save project-context.json
        context_path = self.foundation_docs_dir / 'project-context.json'
        context_path.write_text(json.dumps(project_context, indent=2), encoding='utf-8')
        files_generated.append('project-context.json')

        duration = time.time() - start_time

        result = {
            'files_generated': files_generated,
            'output_dir': str(self.foundation_docs_dir),
            'project_context': project_context,
            'is_ui_project': is_ui_project,
            'duration_seconds': round(duration, 2),
            'success': True
        }

        logger.info(
            f"Coderef foundation docs generation complete in {duration:.2f}s",
            extra={'files_generated': files_generated, 'duration_seconds': duration}
        )

        return result

    def _detect_ui_project(self) -> bool:
        """Auto-detect if project is UI/frontend based on common patterns."""
        ui_indicators = [
            'package.json',  # Node.js
            'src/components',
            'src/pages',
            'src/views',
            'components/',
            'pages/',
            'app/',  # Next.js
            'styles/',
            '.tsx',
            '.jsx',
            'tailwind.config.js',
            'next.config.js',
            'vite.config.js',
        ]

        for indicator in ui_indicators:
            if (self.project_path / indicator).exists():
                return True
            # Check for file extensions
            if indicator.startswith('.'):
                for f in self.project_path.rglob(f'*{indicator}'):
                    if not any(excl in str(f) for excl in EXCLUDE_DIRS):
                        return True

        return False

    def _extract_existing_docs(self) -> Dict[str, Any]:
        """Extract deep content from existing foundation docs."""
        docs = {
            'architecture': None,
            'schema': None,
            'api': None,
            'components': None,
            'readme': None
        }

        # Look in both project root and coderef/foundation-docs
        search_paths = [
            self.project_path,
            self.foundation_docs_dir
        ]

        doc_patterns = {
            'architecture': ['ARCHITECTURE.md', 'architecture.md'],
            'schema': ['SCHEMA.md', 'schema.md', 'DATABASE.md', 'database.md'],
            'api': ['API.md', 'api.md'],
            'components': ['COMPONENTS.md', 'components.md'],
            'readme': ['README.md', 'readme.md']
        }

        for doc_type, filenames in doc_patterns.items():
            for search_path in search_paths:
                for filename in filenames:
                    doc_path = search_path / filename
                    if doc_path.exists():
                        if self.deep_extraction:
                            # Full content extraction with structure parsing
                            content = doc_path.read_text(encoding='utf-8')
                            docs[doc_type] = self._parse_markdown_structure(content)
                        else:
                            # Shallow preview (500 chars)
                            content = doc_path.read_text(encoding='utf-8')[:500]
                            docs[doc_type] = {'preview': content}
                        break
                if docs[doc_type]:
                    break

        return docs

    def _parse_markdown_structure(self, content: str) -> Dict[str, Any]:
        """Parse markdown into structured sections."""
        sections = {}
        current_section = 'intro'
        current_content = []

        for line in content.split('\n'):
            if line.startswith('# '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[2:].strip().lower().replace(' ', '_')
                current_content = []
            elif line.startswith('## '):
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[3:].strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return {
            'sections': sections,
            'full_content': content,
            'word_count': len(content.split())
        }

    def _detect_api_endpoints(self) -> Dict[str, Any]:
        """Auto-detect API endpoints from code."""
        endpoints = []
        frameworks_detected = []

        # FastAPI patterns
        fastapi_patterns = [
            r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        ]

        # Flask patterns
        flask_patterns = [
            r'@app\.route\(["\']([^"\']+)["\'].*methods=\[([^\]]+)\]',
            r'@blueprint\.route\(["\']([^"\']+)["\']',
        ]

        # Express patterns
        express_patterns = [
            r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
        ]

        # Scan Python files
        for py_file in self.project_path.rglob('*.py'):
            if any(excl in str(py_file) for excl in EXCLUDE_DIRS):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')

                # FastAPI detection
                for pattern in fastapi_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        if 'FastAPI' not in frameworks_detected:
                            frameworks_detected.append('FastAPI')
                        for match in matches:
                            method, path = match
                            endpoints.append({
                                'method': method.upper(),
                                'path': path,
                                'file': str(py_file.relative_to(self.project_path)),
                                'framework': 'FastAPI'
                            })

                # Flask detection
                for pattern in flask_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        if 'Flask' not in frameworks_detected:
                            frameworks_detected.append('Flask')
                        for match in matches:
                            if len(match) == 2:
                                path, methods = match
                            else:
                                path = match[0]
                                methods = 'GET'
                            endpoints.append({
                                'method': methods,
                                'path': path,
                                'file': str(py_file.relative_to(self.project_path)),
                                'framework': 'Flask'
                            })
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")

        # Scan JS/TS files
        for ext in ['*.js', '*.ts']:
            for js_file in self.project_path.rglob(ext):
                if any(excl in str(js_file) for excl in EXCLUDE_DIRS):
                    continue
                try:
                    content = js_file.read_text(encoding='utf-8')

                    for pattern in express_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            if 'Express' not in frameworks_detected:
                                frameworks_detected.append('Express')
                            for match in matches:
                                method, path = match
                                endpoints.append({
                                    'method': method.upper(),
                                    'path': path,
                                    'file': str(js_file.relative_to(self.project_path)),
                                    'framework': 'Express'
                                })
                except Exception as e:
                    logger.debug(f"Error reading {js_file}: {e}")

        return {
            'endpoints': endpoints,
            'count': len(endpoints),
            'frameworks_detected': frameworks_detected,
            'auth_method': self._detect_auth_method(),
            'error_format': self._detect_error_format()
        }

    def _detect_auth_method(self) -> str:
        """Detect authentication method used."""
        auth_indicators = {
            'JWT': ['jwt', 'jsonwebtoken', 'pyjwt', 'jose'],
            'OAuth': ['oauth', 'passport', 'authlib'],
            'Session': ['session', 'cookie-session'],
            'API Key': ['api_key', 'apikey', 'x-api-key'],
            'Basic': ['basic-auth', 'basicauth']
        }

        for auth_type, indicators in auth_indicators.items():
            for indicator in indicators:
                # Check package.json
                pkg_json = self.project_path / 'package.json'
                if pkg_json.exists():
                    content = pkg_json.read_text(encoding='utf-8').lower()
                    if indicator in content:
                        return auth_type

                # Check requirements.txt / pyproject.toml
                for req_file in ['requirements.txt', 'pyproject.toml']:
                    req_path = self.project_path / req_file
                    if req_path.exists():
                        content = req_path.read_text(encoding='utf-8').lower()
                        if indicator in content:
                            return auth_type

        return 'Unknown'

    def _detect_error_format(self) -> str:
        """Detect error response format."""
        # Look for common error handler patterns
        error_patterns = {
            'JSON API': r'{"errors":\s*\[',
            'RFC 7807': r'{"type":|"status":|"title":|"detail":',
            'Custom': r'{"error":|{"message":'
        }

        for py_file in self.project_path.rglob('*.py'):
            if any(excl in str(py_file) for excl in EXCLUDE_DIRS):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                for format_name, pattern in error_patterns.items():
                    if re.search(pattern, content):
                        return format_name
            except:
                pass

        return 'Unknown'

    def _detect_database_schema(self) -> Dict[str, Any]:
        """Auto-detect database schema from models/migrations."""
        tables = []
        relationships = []
        migrations = []

        # SQLAlchemy models
        sqlalchemy_pattern = r'class\s+(\w+)\s*\([^)]*(?:Base|Model)[^)]*\):'
        column_pattern = r'(\w+)\s*=\s*Column\(([^)]+)\)'
        fk_pattern = r'ForeignKey\(["\']([^"\']+)["\']\)'

        for py_file in self.project_path.rglob('*.py'):
            if any(excl in str(py_file) for excl in EXCLUDE_DIRS):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')

                # Find model classes
                model_matches = re.findall(sqlalchemy_pattern, content)
                for model_name in model_matches:
                    columns = re.findall(column_pattern, content)
                    table = {
                        'name': model_name,
                        'columns': [],
                        'file': str(py_file.relative_to(self.project_path))
                    }
                    for col_name, col_def in columns:
                        table['columns'].append({
                            'name': col_name,
                            'definition': col_def.strip()
                        })
                        # Check for foreign keys
                        fk_match = re.search(fk_pattern, col_def)
                        if fk_match:
                            relationships.append({
                                'from': model_name,
                                'to': fk_match.group(1).split('.')[0],
                                'type': 'foreign_key'
                            })
                    tables.append(table)
            except Exception as e:
                logger.debug(f"Error parsing {py_file}: {e}")

        # Find migrations
        migration_dirs = ['migrations', 'alembic', 'db/migrate']
        for mig_dir in migration_dirs:
            mig_path = self.project_path / mig_dir
            if mig_path.exists():
                for mig_file in mig_path.rglob('*.py'):
                    migrations.append({
                        'file': str(mig_file.relative_to(self.project_path)),
                        'name': mig_file.stem
                    })

        return {
            'tables': tables,
            'relationships': relationships,
            'migrations': migrations,
            'table_count': len(tables),
            'has_migrations': len(migrations) > 0
        }

    def _detect_dependencies(self) -> Dict[str, Any]:
        """Auto-detect dependencies with basic analysis."""
        dependencies = {
            'count': 0,
            'production': [],
            'development': [],
            'outdated': [],
            'vulns': []
        }

        # Check package.json (Node.js)
        pkg_json = self.project_path / 'package.json'
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding='utf-8'))
                deps = data.get('dependencies', {})
                dev_deps = data.get('devDependencies', {})

                for name, version in deps.items():
                    dependencies['production'].append({
                        'name': name,
                        'version': version,
                        'ecosystem': 'npm'
                    })

                for name, version in dev_deps.items():
                    dependencies['development'].append({
                        'name': name,
                        'version': version,
                        'ecosystem': 'npm'
                    })

                dependencies['count'] = len(deps) + len(dev_deps)
            except Exception as e:
                logger.debug(f"Error parsing package.json: {e}")

        # Check requirements.txt (Python)
        req_txt = self.project_path / 'requirements.txt'
        if req_txt.exists():
            try:
                content = req_txt.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse name==version or name>=version
                        match = re.match(r'^([a-zA-Z0-9_-]+)([=<>!]+)?(.+)?', line)
                        if match:
                            dependencies['production'].append({
                                'name': match.group(1),
                                'version': match.group(3) or '*',
                                'ecosystem': 'pip'
                            })
                            dependencies['count'] += 1
            except Exception as e:
                logger.debug(f"Error parsing requirements.txt: {e}")

        # Check pyproject.toml (Python)
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding='utf-8')
                # Simple TOML parsing for dependencies
                in_deps = False
                for line in content.split('\n'):
                    if '[project.dependencies]' in line or '[tool.poetry.dependencies]' in line:
                        in_deps = True
                        continue
                    if in_deps:
                        if line.startswith('['):
                            in_deps = False
                            continue
                        if '=' in line or '"' in line:
                            # Parse dependency line
                            match = re.match(r'^"?([a-zA-Z0-9_-]+)"?\s*[=,]', line.strip())
                            if match:
                                dependencies['production'].append({
                                    'name': match.group(1),
                                    'version': '*',
                                    'ecosystem': 'pip'
                                })
                                dependencies['count'] += 1
            except Exception as e:
                logger.debug(f"Error parsing pyproject.toml: {e}")

        return dependencies

    def _analyze_git_activity(self) -> Dict[str, Any]:
        """Parse git log for recent activity."""
        activity = {
            'recent_commits': [],
            'active_files': [],
            'contributors': [],
            'has_git': False
        }

        git_dir = self.project_path / '.git'
        if not git_dir.exists():
            return activity

        activity['has_git'] = True

        try:
            # Get recent commits (last 10)
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10', '--format=%h|%s|%an|%ar'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            activity['recent_commits'].append({
                                'hash': parts[0],
                                'message': parts[1],
                                'author': parts[2],
                                'when': parts[3]
                            })

            # Get most active files (last 30 days)
            result = subprocess.run(
                ['git', 'log', '--since=30.days', '--name-only', '--format='],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                file_counts = {}
                for line in result.stdout.strip().split('\n'):
                    if line:
                        file_counts[line] = file_counts.get(line, 0) + 1
                # Top 10 most changed files
                sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                activity['active_files'] = [{'file': f, 'changes': c} for f, c in sorted_files]

            # Get contributors
            result = subprocess.run(
                ['git', 'log', '--format=%an', '--since=90.days'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                contributors = set(result.stdout.strip().split('\n'))
                activity['contributors'] = list(contributors - {''})

        except Exception as e:
            logger.debug(f"Error analyzing git activity: {e}")

        return activity

    def _detect_code_patterns(self) -> Dict[str, Any]:
        """Detect code patterns (handlers, decorators, error handling)."""
        patterns = {
            'handlers': [],
            'decorators': [],
            'error_handling': []
        }

        # Handler patterns (async def handle_*, def on_*)
        handler_pattern = r'(?:async\s+)?def\s+(handle_\w+|on_\w+)\s*\('

        # Decorator patterns
        decorator_pattern = r'@(\w+(?:\.\w+)*)\s*(?:\([^)]*\))?'

        # Error handling patterns
        error_patterns = [
            r'except\s+(\w+(?:Error|Exception))',
            r'raise\s+(\w+(?:Error|Exception))\s*\(',
        ]

        decorator_counts = {}
        error_types = set()
        handlers = []

        for py_file in self.project_path.rglob('*.py'):
            if any(excl in str(py_file) for excl in EXCLUDE_DIRS):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')

                # Find handlers
                for match in re.finditer(handler_pattern, content):
                    handlers.append({
                        'name': match.group(1),
                        'file': str(py_file.relative_to(self.project_path))
                    })

                # Count decorators
                for match in re.finditer(decorator_pattern, content):
                    dec_name = match.group(1)
                    decorator_counts[dec_name] = decorator_counts.get(dec_name, 0) + 1

                # Find error types
                for pattern in error_patterns:
                    for match in re.finditer(pattern, content):
                        error_types.add(match.group(1))

            except Exception as e:
                logger.debug(f"Error analyzing {py_file}: {e}")

        patterns['handlers'] = handlers[:20]  # Limit to 20
        patterns['decorators'] = [
            {'name': k, 'count': v}
            for k, v in sorted(decorator_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        ]
        patterns['error_handling'] = list(error_types)[:20]

        return patterns

    def _discover_similar_features(self) -> List[Dict[str, Any]]:
        """Discover similar features from coderef/archived/."""
        similar = []

        archived_dir = self.project_path / 'coderef' / 'archived'
        if not archived_dir.exists():
            return similar

        for feature_dir in archived_dir.iterdir():
            if feature_dir.is_dir():
                plan_file = feature_dir / 'plan.json'
                if plan_file.exists():
                    try:
                        data = json.loads(plan_file.read_text(encoding='utf-8'))
                        similar.append({
                            'name': feature_dir.name,
                            'workorder_id': data.get('META_DOCUMENTATION', {}).get('workorder_id', ''),
                            'goal': data.get('goal', '')[:200]
                        })
                    except:
                        pass

        return similar[:10]  # Limit to 10 recent features

    def _generate_architecture_md(self, context: Dict, existing: Dict) -> str:
        """Generate ARCHITECTURE.md content."""
        lines = ['# Architecture Documentation', '']

        # If existing architecture doc, extract and enhance
        if existing.get('architecture') and existing['architecture'].get('full_content'):
            lines.append('## Overview')
            lines.append('')
            # Extract intro section or first 500 chars
            sections = existing['architecture'].get('sections', {})
            if 'intro' in sections:
                lines.append(sections['intro'][:1000])
            elif 'overview' in sections:
                lines.append(sections['overview'][:1000])
            else:
                lines.append(existing['architecture']['full_content'][:1000])
            lines.append('')

        # Add detected patterns
        patterns = context.get('patterns', {})
        if patterns:
            lines.append('## Code Patterns')
            lines.append('')

            if patterns.get('handlers'):
                lines.append('### Handler Functions')
                lines.append('')
                for h in patterns['handlers'][:10]:
                    lines.append(f"- `{h['name']}` in `{h['file']}`")
                lines.append('')

            if patterns.get('decorators'):
                lines.append('### Common Decorators')
                lines.append('')
                for d in patterns['decorators'][:10]:
                    lines.append(f"- `@{d['name']}` ({d['count']} uses)")
                lines.append('')

            if patterns.get('error_handling'):
                lines.append('### Error Types')
                lines.append('')
                for e in patterns['error_handling'][:10]:
                    lines.append(f"- `{e}`")
                lines.append('')

        # Add API summary
        api = context.get('api_context', {})
        if api.get('endpoints'):
            lines.append('## API Architecture')
            lines.append('')
            lines.append(f"**Frameworks:** {', '.join(api.get('frameworks_detected', ['Unknown']))}")
            lines.append(f"**Authentication:** {api.get('auth_method', 'Unknown')}")
            lines.append(f"**Error Format:** {api.get('error_format', 'Unknown')}")
            lines.append(f"**Endpoint Count:** {api.get('count', 0)}")
            lines.append('')

        # Add activity summary
        activity = context.get('activity', {})
        if activity.get('has_git'):
            lines.append('## Recent Activity')
            lines.append('')
            if activity.get('active_files'):
                lines.append('### Most Active Files')
                lines.append('')
                for f in activity['active_files'][:5]:
                    lines.append(f"- `{f['file']}` ({f['changes']} changes)")
                lines.append('')

            if activity.get('contributors'):
                lines.append(f"**Active Contributors:** {', '.join(activity['contributors'][:5])}")
                lines.append('')

        lines.append('')
        lines.append(f"*Generated: {datetime.now().isoformat()}*")

        return '\n'.join(lines)

    def _generate_schema_md(self, context: Dict, existing: Dict) -> str:
        """Generate SCHEMA.md content."""
        lines = ['# Schema Documentation', '']

        # Database schema
        db = context.get('database', {})
        if db.get('tables'):
            lines.append('## Database Tables')
            lines.append('')
            for table in db['tables'][:20]:
                lines.append(f"### {table['name']}")
                lines.append('')
                lines.append(f"*File: `{table['file']}`*")
                lines.append('')
                if table.get('columns'):
                    lines.append('| Column | Definition |')
                    lines.append('|--------|------------|')
                    for col in table['columns'][:15]:
                        lines.append(f"| {col['name']} | {col['definition'][:50]} |")
                lines.append('')

        # Relationships
        if db.get('relationships'):
            lines.append('## Relationships')
            lines.append('')
            for rel in db['relationships'][:20]:
                lines.append(f"- `{rel['from']}` → `{rel['to']}` ({rel['type']})")
            lines.append('')

        # Migrations
        if db.get('migrations'):
            lines.append('## Migrations')
            lines.append('')
            lines.append(f"**Migration Count:** {len(db['migrations'])}")
            lines.append('')
            for mig in db['migrations'][:10]:
                lines.append(f"- `{mig['file']}`")
            lines.append('')

        # If no database found
        if not db.get('tables'):
            lines.append('*No database models detected.*')
            lines.append('')

        lines.append('')
        lines.append(f"*Generated: {datetime.now().isoformat()}*")

        return '\n'.join(lines)

    def _generate_components_md(self, context: Dict, existing: Dict) -> str:
        """Generate COMPONENTS.md content (for UI projects)."""
        lines = ['# Component Documentation', '']

        # If existing components doc, include it
        if existing.get('components') and existing['components'].get('full_content'):
            lines.append(existing['components']['full_content'])
            lines.append('')
        else:
            # Auto-detect components
            lines.append('## Detected Components')
            lines.append('')

            component_dirs = ['components', 'src/components', 'app/components', 'pages', 'src/pages']
            found_components = []

            for comp_dir in component_dirs:
                comp_path = self.project_path / comp_dir
                if comp_path.exists():
                    for ext in ['*.tsx', '*.jsx', '*.vue', '*.svelte']:
                        for comp_file in comp_path.rglob(ext):
                            if any(excl in str(comp_file) for excl in EXCLUDE_DIRS):
                                continue
                            found_components.append({
                                'name': comp_file.stem,
                                'path': str(comp_file.relative_to(self.project_path)),
                                'type': ext[2:]  # tsx, jsx, etc.
                            })

            if found_components:
                lines.append('| Component | Path | Type |')
                lines.append('|-----------|------|------|')
                for comp in found_components[:30]:
                    lines.append(f"| {comp['name']} | `{comp['path']}` | {comp['type']} |")
                lines.append('')
                lines.append(f"**Total Components:** {len(found_components)}")
            else:
                lines.append('*No UI components detected.*')

        lines.append('')
        lines.append(f"*Generated: {datetime.now().isoformat()}*")

        return '\n'.join(lines)
