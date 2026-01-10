"""
CodeRef Foundation Generator - Unified foundation docs powered by coderef analysis.

Generates comprehensive project context for planning workflows:
- ARCHITECTURE.md (patterns, decisions, constraints)
- SCHEMA.md (entities, relationships)
- COMPONENTS.md (component hierarchy - UI projects only)
- API.md (endpoints, auth, error handling)
- project-context.json (structured context for planning)

Replaces: api_inventory, database_inventory, dependency_inventory,
          config_inventory, test_inventory, inventory_manifest, documentation_inventory
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import re
import subprocess
import os
import sys
from datetime import datetime

# Add coderef/ utilities to path for wrapper functions
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from coderef.utils import generate_foundation_docs as coderef_generate_docs, check_coderef_available

from logger_config import logger
from constants import EXCLUDE_DIRS, ALLOWED_FILE_EXTENSIONS

# Default coderef CLI path (can be overridden by environment variable)
DEFAULT_CODEREF_CLI_PATH = r"C:\Users\willh\Desktop\projects\coderef-system\packages\cli"
from generators.mermaid_formatter import (
    generate_module_diagram,
    compute_graph_metrics,
    get_high_impact_elements
)

__all__ = ['CoderefFoundationGenerator']

# Document generation order for sequential processing with progress feedback
# Each entry: (doc_name, output_path_relative, generator_method_name, requires_coderef_or_ui)
DOC_GENERATION_ORDER = [
    ('README.md', '', '_generate_readme_md', False),
    ('ARCHITECTURE.md', 'coderef/foundation-docs', '_generate_architecture_md', False),
    ('SCHEMA.md', 'coderef/foundation-docs', '_generate_schema_md', False),
    ('COMPONENTS.md', 'coderef/foundation-docs', '_generate_components_md', True),  # Conditional
    ('API.md', 'coderef/foundation-docs', '_generate_api_md', False),
    ('project-context.json', 'coderef/foundation-docs', None, False),  # Special handling
]


class CoderefFoundationGenerator:
    """
    Unified foundation docs generator powered by coderef analysis.

    Generates:
    - ARCHITECTURE.md (patterns, decisions, constraints)
    - SCHEMA.md (entities, relationships)
    - COMPONENTS.md (component hierarchy - UI projects only)
    - API.md (endpoints, auth, error handling)
    - project-context.json (structured context for planning)
    """

    def __init__(
        self,
        project_path: Path,
        include_components: Optional[bool] = None,
        deep_extraction: bool = True,
        use_coderef: bool = True,
        force_regenerate: bool = False
    ):
        """
        Initialize generator.

        Args:
            project_path: Path to project directory
            include_components: Generate COMPONENTS.md (None = auto-detect UI project)
            deep_extraction: Deep extraction from existing docs (vs shallow preview)
            use_coderef: Use coderef-mcp for pattern detection
            force_regenerate: Regenerate all docs even if they already exist (default: False)
        """
        self.project_path = project_path
        self.include_components = include_components
        self.deep_extraction = deep_extraction
        self.use_coderef = use_coderef
        self.force_regenerate = force_regenerate

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

        # Detect if UI project (for COMPONENTS.md fallback)
        is_ui_project = self._detect_ui_project() if self.include_components is None else self.include_components

        # Phase 0: Ensure coderef index exists (auto-scan if needed)
        auto_scan_performed = False
        auto_scan_success = False
        if self.use_coderef:
            logger.info("Phase 0: Ensuring coderef index exists...")
            index_existed = (self.project_path / '.coderef' / 'index.json').exists()
            scan_success = self._ensure_coderef_index()
            auto_scan_performed = not index_existed and scan_success
            auto_scan_success = scan_success
            if scan_success:
                logger.info("Coderef index ready" + (" (auto-scanned)" if auto_scan_performed else " (pre-existing)"))
            else:
                logger.info("Coderef index unavailable, will use regex fallback")

        # Phase 0.5: Load coderef data (99% accurate AST data)
        logger.info("Phase 0.5: Loading coderef data...")
        coderef_data = self._load_coderef_data()
        has_coderef = coderef_data is not None

        if has_coderef:
            logger.info(f"Coderef data loaded: {len(coderef_data.get('elements', []))} elements")

            # FAST PATH: Try external script generation (scripts/parse_coderef_data.py)
            # This is MUCH faster than internal generation for large codebases
            if not self.force_regenerate:  # Only use fast path if not forcing regeneration
                try:
                    logger.info("Attempting fast-path generation via scripts/parse_coderef_data.py...")
                    external_docs = coderef_generate_docs(str(self.project_path))

                    if external_docs:
                        duration = time.time() - start_time
                        logger.info(f"Fast-path generation successful in {duration:.2f}s ({len(external_docs)} docs)")

                        # Return early with external generation results
                        return {
                            'files_generated': list(external_docs.values()),
                            'files_skipped': [],
                            'generated_count': len(external_docs),
                            'skipped_count': 0,
                            'doc_timings': {doc: {'skipped': False, 'duration': duration / len(external_docs)} for doc in external_docs.keys()},
                            'output_dir': str(self.foundation_docs_dir),
                            'project_context': {'source': 'external_script'},
                            'is_ui_project': is_ui_project,
                            'has_coderef_data': True,
                            'auto_scan_performed': auto_scan_performed,
                            'auto_scan_success': auto_scan_success,
                            'force_regenerate': False,
                            'generation_method': 'external_script',
                            'duration_seconds': round(duration, 2),
                            'success': True,
                            'utilization': 'scripts/parse_coderef_data.py (external)'
                        }
                except Exception as e:
                    logger.debug(f"Fast-path generation failed: {str(e)}, falling back to internal generation")
        else:
            logger.info("No coderef data found, falling back to regex detection")

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
            'coderef': {
                'available': has_coderef,
                'element_count': len(coderef_data.get('elements', [])) if has_coderef else 0,
                'has_graph': bool(coderef_data.get('graph')) if has_coderef else False,
                'auto_scan_attempted': self.use_coderef,
                'auto_scan_performed': auto_scan_performed,
                'auto_scan_success': auto_scan_success
            },
            '_metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'coderef_foundation_generator',
                'version': '2.0.0'  # Updated version for coderef integration
            }
        }

        # Generate output files with progress feedback and resume capability
        files_generated = []
        files_skipped = []
        doc_timings = {}

        # Determine which docs to generate
        docs_to_process = [
            ('README.md', '', '_generate_readme_md', False),
            ('ARCHITECTURE.md', 'coderef/foundation-docs', '_generate_architecture_md', False),
            ('SCHEMA.md', 'coderef/foundation-docs', '_generate_schema_md', False),
            ('COMPONENTS.md', 'coderef/foundation-docs', '_generate_components_md', True),
            ('API.md', 'coderef/foundation-docs', '_generate_api_md', False),
            ('project-context.json', 'coderef/foundation-docs', None, False),
        ]

        total_docs = len(docs_to_process)

        for idx, (doc_name, subdir, generator_method, requires_coderef_or_ui) in enumerate(docs_to_process, 1):
            doc_start = time.time()

            # Determine output path
            if subdir:
                output_path = self.foundation_docs_dir / doc_name
                relative_path = f"{subdir}/{doc_name}"
            else:
                output_path = self.project_path / doc_name
                relative_path = doc_name

            # Skip conditional docs (COMPONENTS.md) if conditions not met
            if requires_coderef_or_ui and not (has_coderef or is_ui_project):
                logger.info(f"Skipping {doc_name} ({idx}/{total_docs}) - not a UI project and no coderef data")
                continue

            # Check if file exists and skip unless force_regenerate
            if output_path.exists() and not self.force_regenerate:
                logger.info(f"Skipping {doc_name} ({idx}/{total_docs}) - already exists (use force_regenerate=True to overwrite)")
                files_skipped.append(relative_path)
                doc_timings[doc_name] = {'skipped': True, 'duration': 0}
                continue

            # Log progress
            logger.info(f"Generating {doc_name} ({idx}/{total_docs})...")

            # Generate content
            if doc_name == 'project-context.json':
                # Special handling for JSON
                content = json.dumps(project_context, indent=2)
            elif doc_name == 'README.md':
                content = self._generate_readme_md(project_context, coderef_data)
            elif doc_name == 'ARCHITECTURE.md':
                content = self._generate_architecture_md(project_context, existing_docs, coderef_data)
            elif doc_name == 'SCHEMA.md':
                content = self._generate_schema_md(project_context, existing_docs)
            elif doc_name == 'COMPONENTS.md':
                content = self._generate_components_md(project_context, existing_docs, coderef_data)
            elif doc_name == 'API.md':
                content = self._generate_api_md(project_context, existing_docs)
            else:
                continue

            # Write file
            output_path.write_text(content, encoding='utf-8')
            files_generated.append(relative_path)

            # GAP-009: Validate foundation docs (UDS compliance)
            if doc_name.endswith('.md'):
                try:
                    from papertrail.validators.foundation import FoundationDocValidator
                    validator = FoundationDocValidator()
                    result = validator.validate_file(str(output_path))

                    if not result['valid']:
                        logger.warning(f"{doc_name} validation failed (score: {result.get('score', 0)})")
                        for error in result.get('errors', []):
                            logger.warning(f"  - {error}")
                    else:
                        logger.info(f"{doc_name} validated successfully (score: {result.get('score', 100)})")
                except ImportError:
                    logger.warning("FoundationDocValidator not available - skipping validation")
                except Exception as e:
                    logger.warning(f"{doc_name} validation error: {e} - continuing")

            doc_duration = time.time() - doc_start
            doc_timings[doc_name] = {'skipped': False, 'duration': round(doc_duration, 2)}
            logger.info(f"Generated {doc_name} ({idx}/{total_docs}) in {doc_duration:.2f}s")

        duration = time.time() - start_time

        result = {
            'files_generated': files_generated,
            'files_skipped': files_skipped,
            'generated_count': len(files_generated),
            'skipped_count': len(files_skipped),
            'doc_timings': doc_timings,
            'output_dir': str(self.foundation_docs_dir),
            'project_context': project_context,
            'is_ui_project': is_ui_project,
            'has_coderef_data': has_coderef,
            'auto_scan_performed': auto_scan_performed,
            'auto_scan_success': auto_scan_success,
            'force_regenerate': self.force_regenerate,
            'duration_seconds': round(duration, 2),
            'success': True
        }

        logger.info(
            f"Coderef foundation docs generation complete in {duration:.2f}s "
            f"(generated: {len(files_generated)}, skipped: {len(files_skipped)})",
            extra={
                'files_generated': files_generated,
                'files_skipped': files_skipped,
                'duration_seconds': duration,
                'has_coderef_data': has_coderef
            }
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

    def _load_coderef_data(self) -> Optional[Dict[str, Any]]:
        """
        Load .coderef/index.json and graph.json if available.

        Returns:
            Dict with 'elements' and 'graph' if .coderef/ exists, None otherwise.
            Falls back to regex detection when None is returned.
        """
        index_path = self.project_path / '.coderef' / 'index.json'
        graph_path = self.project_path / '.coderef' / 'graph.json'

        if not index_path.exists():
            logger.debug(f"No .coderef/index.json found at {self.project_path}, falling back to regex")
            return None

        try:
            elements = json.loads(index_path.read_text(encoding='utf-8'))
            graph = None

            if graph_path.exists():
                graph = json.loads(graph_path.read_text(encoding='utf-8'))

            logger.info(
                f"Loaded coderef data: {len(elements)} elements, graph={'present' if graph else 'missing'}",
                extra={'element_count': len(elements), 'has_graph': graph is not None}
            )

            return {
                'elements': elements,
                'graph': graph
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse coderef JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error loading coderef data: {e}")
            return None

    def _ensure_coderef_index(self) -> bool:
        """
        Ensure .coderef/index.json exists by running coderef CLI scan if needed.

        Returns:
            True if index exists (or was created), False if scan failed
        """
        index_path = self.project_path / '.coderef' / 'index.json'

        # If index already exists, we're good
        if index_path.exists():
            logger.debug(f"Coderef index already exists at {index_path}")
            return True

        logger.info(f"No coderef index found, running auto-scan for: {self.project_path}")

        # Get CLI path from environment or use default
        cli_path = os.environ.get("CODEREF_CLI_PATH", DEFAULT_CODEREF_CLI_PATH)
        cli_bin = os.path.join(cli_path, "dist", "cli.js")

        # Verify CLI exists
        if not os.path.exists(cli_bin):
            logger.warning(f"Coderef CLI not found at {cli_bin}, falling back to regex detection")
            return False

        try:
            # Create .coderef directory if it doesn't exist
            coderef_dir = self.project_path / '.coderef'
            coderef_dir.mkdir(parents=True, exist_ok=True)

            # Determine languages to scan based on project files
            languages = self._detect_project_languages()
            lang_arg = ','.join(languages) if languages else 'py,ts,tsx,js,jsx'

            # Build the command
            cmd = [
                'node',
                cli_bin,
                'scan',
                str(self.project_path),
                '--lang', lang_arg,
                '--analyzer', 'ast',
                '--json'
            ]

            logger.info(f"Running coderef scan: {' '.join(cmd[:4])}...")

            # Execute the scan
            result = subprocess.run(
                cmd,
                cwd=cli_path,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for large projects
            )

            if result.returncode != 0:
                logger.warning(f"Coderef scan failed with code {result.returncode}: {result.stderr[:500]}")
                return False

            # Parse the JSON output
            try:
                scan_result = json.loads(result.stdout)
                elements = scan_result.get('elements', [])

                # Save to index.json
                index_path.write_text(json.dumps(elements, indent=2), encoding='utf-8')
                logger.info(f"Coderef scan complete: {len(elements)} elements indexed to {index_path}")

                # If graph data is available, save it too
                if scan_result.get('graph'):
                    graph_path = self.project_path / '.coderef' / 'graph.json'
                    graph_path.write_text(json.dumps(scan_result['graph'], indent=2), encoding='utf-8')
                    logger.info(f"Graph data saved to {graph_path}")

                return True

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse coderef scan output: {e}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning("Coderef scan timed out after 120 seconds")
            return False
        except FileNotFoundError:
            logger.warning("Node.js not found - coderef CLI requires Node.js")
            return False
        except Exception as e:
            logger.warning(f"Coderef scan failed: {e}")
            return False

    def _detect_project_languages(self) -> List[str]:
        """Detect programming languages used in the project."""
        languages = set()

        # Check for common files/extensions
        lang_indicators = {
            'py': ['*.py', 'requirements.txt', 'pyproject.toml', 'setup.py'],
            'ts': ['*.ts', 'tsconfig.json'],
            'tsx': ['*.tsx'],
            'js': ['*.js', 'package.json'],
            'jsx': ['*.jsx'],
        }

        for lang, patterns in lang_indicators.items():
            for pattern in patterns:
                if pattern.startswith('*.'):
                    # File extension check (limit search to avoid slowdown)
                    for f in list(self.project_path.rglob(pattern))[:5]:
                        if not any(excl in str(f) for excl in EXCLUDE_DIRS):
                            languages.add(lang)
                            break
                else:
                    # Specific file check
                    if (self.project_path / pattern).exists():
                        languages.add(lang)

        return list(languages) if languages else ['py', 'ts', 'js']

    def _categorize_elements(self, elements: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize elements by type and naming patterns.

        Args:
            elements: List of element dicts from index.json

        Returns:
            Dict with categorized elements:
            - handlers: functions matching handle_*
            - generators: classes matching *Generator
            - services: classes matching *Service
            - middleware: classes/functions matching *Middleware
            - components: type=component or React-style names
            - utilities: remaining functions
            - classes: remaining classes
        """
        categories = {
            'handlers': [],
            'generators': [],
            'services': [],
            'middleware': [],
            'components': [],
            'utilities': [],
            'classes': [],
            'functions': [],
            'all': elements
        }

        for elem in elements:
            name = elem.get('name', '')
            elem_type = elem.get('type', '')

            # Handler pattern: handle_*, on_*
            if name.startswith('handle_') or name.startswith('on_'):
                categories['handlers'].append(elem)
            # Generator pattern: *Generator
            elif name.endswith('Generator'):
                categories['generators'].append(elem)
            # Service pattern: *Service
            elif name.endswith('Service'):
                categories['services'].append(elem)
            # Middleware pattern: *Middleware, *middleware
            elif 'middleware' in name.lower():
                categories['middleware'].append(elem)
            # Component pattern: explicit type or PascalCase with props
            elif elem_type == 'component' or (elem_type == 'function' and name[0].isupper() and '_' not in name):
                categories['components'].append(elem)
            # Remaining by type
            elif elem_type == 'function':
                categories['utilities'].append(elem)
            elif elem_type == 'class':
                categories['classes'].append(elem)
            else:
                categories['functions'].append(elem)

        return categories

    def _get_element_relationships(self, element_id: str, graph: Optional[Dict]) -> Dict[str, List[str]]:
        """
        Get callers and callees for an element from graph.json.

        Args:
            element_id: The element's ID/reference
            graph: Graph data from graph.json

        Returns:
            Dict with 'callers' and 'callees' lists
        """
        relationships = {'callers': [], 'callees': []}

        if not graph:
            return relationships

        edges = graph.get('edges', [])

        for edge_entry in edges:
            # Handle both array format [edgeId, edgeData] and dict format
            if isinstance(edge_entry, list) and len(edge_entry) >= 2:
                edge_data = edge_entry[1]
            elif isinstance(edge_entry, dict):
                edge_data = edge_entry
            else:
                continue

            source = edge_data.get('source', '')
            target = edge_data.get('target', '')
            edge_type = edge_data.get('type', '')

            # Only consider call relationships
            if edge_type not in ['calls', 'imports', 'uses']:
                continue

            if source == element_id:
                relationships['callees'].append(target)
            elif target == element_id:
                relationships['callers'].append(source)

        return relationships

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

    def _generate_architecture_md(self, context: Dict, existing: Dict, coderef_data: Optional[Dict] = None) -> str:
        """
        Generate ARCHITECTURE.md content with diagrams and metrics.

        Includes: Module dependency graph, graph metrics, high-impact elements.
        """
        lines = ['# Architecture Documentation', '']

        # If existing architecture doc, extract and enhance
        if existing.get('architecture') and existing['architecture'].get('full_content'):
            lines.append('## Overview')
            lines.append('')
            sections = existing['architecture'].get('sections', {})
            if 'intro' in sections:
                lines.append(sections['intro'][:1000])
            elif 'overview' in sections:
                lines.append(sections['overview'][:1000])
            else:
                lines.append(existing['architecture']['full_content'][:1000])
            lines.append('')

        # Module Dependency Graph (from coderef data)
        if coderef_data and coderef_data.get('graph'):
            graph = coderef_data['graph']

            lines.append('## Module Dependency Graph')
            lines.append('')
            diagram = generate_module_diagram(graph)
            lines.append(diagram)
            lines.append('')

            # Graph Metrics
            metrics = compute_graph_metrics(graph)
            lines.append('## Metrics')
            lines.append('')
            lines.append(f"- **Total Files:** {metrics.get('node_count', 0)}")
            lines.append(f"- **Total Elements:** {len(coderef_data.get('elements', []))}")
            lines.append(f"- **Graph Density:** {metrics.get('density', 0)} (lower = better modularity)")

            circular = metrics.get('circular_dependencies', [])
            if circular:
                lines.append(f"- **Circular Dependencies:** {len(circular)} ⚠️")
                for cycle in circular[:3]:
                    lines.append(f"  - {cycle}")
            else:
                lines.append('- **Circular Dependencies:** 0 ✅')

            isolated = metrics.get('isolated_nodes', [])
            lines.append(f"- **Isolated Nodes:** {len(isolated)} (constants, types)")
            lines.append('')

            # High-Impact Elements
            high_impact = get_high_impact_elements(graph, limit=10)
            if high_impact:
                lines.append('## High-Impact Elements')
                lines.append('')
                lines.append('Elements with most dependents (change these carefully):')
                lines.append('')
                lines.append('| Element | File | Dependents | Risk |')
                lines.append('|---------|------|------------|------|')
                for elem in high_impact:
                    name = elem.get('name', '')
                    file = elem.get('file', '').split('/')[-1] if elem.get('file') else ''
                    deps = elem.get('dependents', 0)
                    risk = elem.get('risk', 'LOW')
                    risk_emoji = '🔴' if risk == 'HIGH' else ('🟡' if risk == 'MEDIUM' else '🟢')
                    lines.append(f"| {name} | `{file}` | {deps} | {risk_emoji} {risk} |")
                lines.append('')
        else:
            lines.append('## Module Dependency Graph')
            lines.append('')
            # Show helpful message based on what happened
            coderef_info = context.get('coderef', {})
            if coderef_info.get('auto_scan_attempted') and not coderef_info.get('auto_scan_success'):
                lines.append('*Auto-scan attempted but failed. Check that:*')
                lines.append('- *Node.js is installed*')
                lines.append('- *CODEREF_CLI_PATH environment variable is set correctly*')
                lines.append('- *The coderef CLI is built (`pnpm build` in cli directory)*')
            else:
                lines.append('*No coderef data available. Using regex-based pattern detection.*')
            lines.append('')

        # Add detected patterns (from regex fallback)
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

    def _generate_components_md(self, context: Dict, existing: Dict, coderef_data: Optional[Dict] = None) -> str:
        """
        Generate COMPONENTS.md content with ALL modules (not just UI).

        Includes: Handlers, Generators, Services, Middleware, UI Components, Utilities
        With relationship data (callers/callees) when coderef data is available.
        """
        lines = ['# Project Components', '']

        # Check for coderef data
        if coderef_data and coderef_data.get('elements'):
            elements = coderef_data['elements']
            graph = coderef_data.get('graph')
            categories = self._categorize_elements(elements)

            # Summary section
            lines.append('## Summary')
            lines.append('')
            lines.append(f"- **Total Elements:** {len(elements)} (from coderef scan)")

            # Count by type
            type_counts = {}
            for elem in elements:
                elem_type = elem.get('type', 'unknown')
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

            type_summary = ' | '.join([f"**{t.title()}s:** {c}" for t, c in sorted(type_counts.items())])
            lines.append(f"- {type_summary}")
            lines.append('')

            # Dependency diagram placeholder
            lines.append('## Dependency Diagram')
            lines.append('')
            lines.append('<!-- AGENT: Generate Mermaid diagram from relationships -->')
            lines.append('')

            # Handlers section
            if categories['handlers']:
                lines.append(f"## Handlers ({len(categories['handlers'])} detected)")
                lines.append('')
                for handler in categories['handlers'][:15]:
                    name = handler.get('name', 'unknown')
                    file = handler.get('file', '')
                    line = handler.get('line', '')
                    elem_type = handler.get('type', 'function')

                    lines.append(f"### {name}")
                    lines.append('')
                    lines.append(f"- **File:** `{file}:{line}`" if line else f"- **File:** `{file}`")
                    lines.append(f"- **Type:** {elem_type}")

                    # Add relationships if graph available
                    elem_id = handler.get('id', name)
                    rels = self._get_element_relationships(elem_id, graph)
                    if rels['callees']:
                        lines.append(f"- **Calls:** `{'`, `'.join(rels['callees'][:5])}`")
                    if rels['callers']:
                        lines.append(f"- **Called by:** `{'`, `'.join(rels['callers'][:5])}`")

                    lines.append('- **Purpose:** <!-- AGENT: Describe purpose -->')
                    lines.append('')

            # Generators section
            if categories['generators']:
                lines.append(f"## Generators ({len(categories['generators'])} detected)")
                lines.append('')
                for gen in categories['generators'][:10]:
                    name = gen.get('name', 'unknown')
                    file = gen.get('file', '')
                    line = gen.get('line', '')

                    lines.append(f"### {name}")
                    lines.append('')
                    lines.append(f"- **File:** `{file}:{line}`" if line else f"- **File:** `{file}`")

                    elem_id = gen.get('id', name)
                    rels = self._get_element_relationships(elem_id, graph)
                    if rels['callers']:
                        lines.append(f"- **Used by:** `{'`, `'.join(rels['callers'][:5])}`")

                    lines.append('- **Purpose:** <!-- AGENT: Describe purpose -->')
                    lines.append('')

            # Services section
            if categories['services']:
                lines.append(f"## Services ({len(categories['services'])} detected)")
                lines.append('')
                for svc in categories['services'][:10]:
                    name = svc.get('name', 'unknown')
                    file = svc.get('file', '')
                    lines.append(f"### {name}")
                    lines.append('')
                    lines.append(f"- **File:** `{file}`")
                    lines.append('- **Purpose:** <!-- AGENT: Describe purpose -->')
                    lines.append('')
            else:
                lines.append('## Services (0 detected)')
                lines.append('')
                lines.append('*No *Service classes found*')
                lines.append('')

            # Middleware section
            if categories['middleware']:
                lines.append(f"## Middleware ({len(categories['middleware'])} detected)")
                lines.append('')
                for mw in categories['middleware'][:10]:
                    name = mw.get('name', 'unknown')
                    file = mw.get('file', '')
                    lines.append(f"- `{name}` in `{file}`")
                lines.append('')

            # UI Components section
            if categories['components']:
                lines.append(f"## UI Components ({len(categories['components'])} detected)")
                lines.append('')
                lines.append('| Component | File | Type |')
                lines.append('|-----------|------|------|')
                for comp in categories['components'][:20]:
                    name = comp.get('name', '')
                    file = comp.get('file', '')
                    comp_type = comp.get('type', 'component')
                    lines.append(f"| {name} | `{file}` | {comp_type} |")
                lines.append('')

            # Utilities section
            if categories['utilities']:
                lines.append(f"## Utilities ({len(categories['utilities'])} detected)")
                lines.append('')
                lines.append('| Utility | File | Purpose |')
                lines.append('|---------|------|---------|')
                for util in categories['utilities'][:20]:
                    name = util.get('name', '')
                    file = util.get('file', '')
                    lines.append(f"| {name} | `{file}` | <!-- AGENT: Purpose --> |")
                lines.append('')

            # Classes section
            if categories['classes']:
                lines.append(f"## Other Classes ({len(categories['classes'])} detected)")
                lines.append('')
                for cls in categories['classes'][:10]:
                    name = cls.get('name', '')
                    file = cls.get('file', '')
                    lines.append(f"- `{name}` in `{file}`")
                lines.append('')

        else:
            # Fall back to regex-based UI component detection (backward compatible)
            lines.append('## Detected Components')
            lines.append('')
            lines.append('*Note: Run `coderef index` for comprehensive module analysis with relationships.*')
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
                                'type': ext[2:]
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

    def _generate_api_md(self, context: Dict, existing: Dict) -> str:
        """Generate API.md content with all detected endpoints."""
        lines = ['# API Documentation', '']

        api = context.get('api_context', {})

        # Overview section
        lines.append('## Overview')
        lines.append('')
        frameworks = api.get('frameworks_detected', [])
        lines.append(f"- **Framework:** {', '.join(frameworks) if frameworks else 'Unknown'}")
        lines.append(f"- **Authentication:** {api.get('auth_method', 'Unknown')}")
        lines.append(f"- **Error Format:** {api.get('error_format', 'Unknown')}")
        lines.append(f"- **Total Endpoints:** {api.get('count', 0)}")
        lines.append('')

        # Endpoints section
        endpoints = api.get('endpoints', [])
        if endpoints:
            lines.append('## Endpoints')
            lines.append('')

            # Group by framework
            by_framework = {}
            for ep in endpoints:
                fw = ep.get('framework', 'Unknown')
                if fw not in by_framework:
                    by_framework[fw] = []
                by_framework[fw].append(ep)

            for framework, fw_endpoints in by_framework.items():
                if len(by_framework) > 1:
                    lines.append(f"### {framework}")
                    lines.append('')

                # Endpoints table
                lines.append('| Method | Path | File |')
                lines.append('|--------|------|------|')
                for ep in fw_endpoints:
                    method = ep.get('method', 'GET')
                    path = ep.get('path', '/')
                    file = ep.get('file', '')
                    lines.append(f"| `{method}` | `{path}` | `{file}` |")
                lines.append('')

            # Detailed endpoint list
            lines.append('### Endpoint Details')
            lines.append('')
            for ep in endpoints[:50]:  # Limit to 50 for readability
                method = ep.get('method', 'GET')
                path = ep.get('path', '/')
                file = ep.get('file', '')
                framework = ep.get('framework', 'Unknown')
                lines.append(f"#### `{method}` {path}")
                lines.append('')
                lines.append(f"- **File:** `{file}`")
                lines.append(f"- **Framework:** {framework}")
                lines.append('')
        else:
            lines.append('## Endpoints')
            lines.append('')
            lines.append('*No API endpoints detected.*')
            lines.append('')

        # Authentication section
        auth_method = api.get('auth_method', 'Unknown')
        lines.append('## Authentication')
        lines.append('')
        if auth_method != 'Unknown':
            lines.append(f"**Method:** {auth_method}")
            lines.append('')
            auth_notes = {
                'JWT': 'JSON Web Tokens for stateless authentication. Pass in `Authorization: Bearer <token>` header.',
                'OAuth': 'OAuth 2.0 authentication. See provider documentation for token endpoints.',
                'Session': 'Session-based authentication with cookies. Ensure CSRF protection is enabled.',
                'API Key': 'API key authentication. Pass in `X-API-Key` header or as query parameter.',
                'Basic': 'HTTP Basic authentication. Credentials in `Authorization` header.'
            }
            if auth_method in auth_notes:
                lines.append(auth_notes[auth_method])
        else:
            lines.append('*Authentication method not detected.*')
        lines.append('')

        # Error handling section
        error_format = api.get('error_format', 'Unknown')
        lines.append('## Error Handling')
        lines.append('')
        if error_format != 'Unknown':
            lines.append(f"**Format:** {error_format}")
            lines.append('')
            error_examples = {
                'JSON API': '```json\n{"errors": [{"status": "400", "title": "Bad Request", "detail": "..."}]}\n```',
                'RFC 7807': '```json\n{"type": "about:blank", "status": 400, "title": "Bad Request", "detail": "..."}\n```',
                'Custom': '```json\n{"error": "error_code", "message": "Human readable message"}\n```'
            }
            if error_format in error_examples:
                lines.append('Example:')
                lines.append('')
                lines.append(error_examples[error_format])
        else:
            lines.append('*Error format not detected.*')
        lines.append('')

        lines.append(f"*Generated: {datetime.now().isoformat()}*")

        return '\n'.join(lines)

    def _generate_readme_md(self, context: Dict, coderef_data: Optional[Dict] = None) -> str:
        """
        Generate README.md with project overview, stats, and architecture diagram.

        Saved to project root (not coderef/foundation-docs/).
        """
        project_name = self.project_path.name
        lines = [f'# {project_name}', '']

        # Overview section with AGENT marker
        lines.append('## Overview')
        lines.append('')
        lines.append('<!-- AGENT: Describe what this project does -->')
        lines.append('')

        # Quick Stats section
        lines.append('## Quick Stats')
        lines.append('')
        lines.append('| Metric | Value |')
        lines.append('|--------|-------|')

        # Gather stats from context and coderef
        if coderef_data and coderef_data.get('elements'):
            elements = coderef_data['elements']

            # Count by type
            type_counts = {}
            for elem in elements:
                elem_type = elem.get('type', 'unknown')
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1

            for elem_type, count in sorted(type_counts.items()):
                lines.append(f"| {elem_type.title()}s | {count} |")

        # API endpoint count
        api = context.get('api_context', {})
        if api.get('count', 0) > 0:
            lines.append(f"| API Endpoints | {api['count']} |")

        # Database tables
        db = context.get('database', {})
        if db.get('table_count', 0) > 0:
            lines.append(f"| Database Tables | {db['table_count']} |")

        # Dependencies
        deps = context.get('dependencies', {})
        if deps.get('count', 0) > 0:
            lines.append(f"| Dependencies | {deps['count']} |")

        lines.append('')

        # Architecture Overview diagram
        if coderef_data and coderef_data.get('graph'):
            lines.append('## Architecture Overview')
            lines.append('')
            diagram = generate_module_diagram(coderef_data['graph'], max_nodes=10)
            lines.append(diagram)
            lines.append('')

        # Quick Start section with AGENT marker
        lines.append('## Quick Start')
        lines.append('')
        lines.append('<!-- AGENT: Installation and usage instructions -->')
        lines.append('')

        # Documentation links
        lines.append('## Documentation')
        lines.append('')
        lines.append('- [API Reference](coderef/foundation-docs/API.md)')
        lines.append('- [Architecture](coderef/foundation-docs/ARCHITECTURE.md)')
        lines.append('- [Components](coderef/foundation-docs/COMPONENTS.md)')
        lines.append('- [Schema](coderef/foundation-docs/SCHEMA.md)')
        lines.append('')

        # Footer
        lines.append('---')
        lines.append('')
        lines.append(f"*Generated: {datetime.now().isoformat()}*")

        return '\n'.join(lines)
