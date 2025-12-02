"""API inventory generator for discovering REST/GraphQL endpoints across multiple frameworks."""

import json
import ast
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import jsonschema
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths
from logger_config import logger, log_error, log_security_event


class ApiGenerator:
    """Helper class for generating comprehensive API endpoint inventories."""

    def __init__(self, project_path: Path):
        """
        Initialize API inventory generator.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "api-schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized ApiGenerator for {project_path}")

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load JSON schema for API manifest validation (SEC-002).

        Returns:
            Schema dictionary or None if schema file doesn't exist

        Raises:
            json.JSONDecodeError: If schema JSON is malformed
        """
        if not self.schema_path.exists():
            logger.warning(f"No schema found at {self.schema_path}")
            return None

        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            logger.debug(f"Loaded schema from {self.schema_path}")
            return schema
        except json.JSONDecodeError as e:
            log_error('schema_load_error', f"Malformed schema file: {self.schema_path}", error=str(e))
            raise json.JSONDecodeError(
                f"Malformed schema file: {self.schema_path}",
                e.doc,
                e.pos
            )

    def validate_manifest(self, data: Dict[str, Any]) -> None:
        """
        Validate manifest data against JSON schema (SEC-002).

        Args:
            data: Manifest dictionary to validate

        Raises:
            jsonschema.ValidationError: If data doesn't match schema
            jsonschema.SchemaError: If schema itself is invalid
        """
        if self.schema is None:
            logger.warning("No schema available, skipping validation")
            return

        try:
            jsonschema.validate(data, self.schema)
            logger.debug("API manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('manifest_validation_error', f"API manifest validation failed: {str(e)}", error=str(e))
            raise

    def detect_frameworks(self, frameworks: Optional[List[str]] = None) -> List[str]:
        """
        Detect API frameworks used in the project.

        Supports: FastAPI, Flask, Express

        Args:
            frameworks: Optional list of frameworks to check. If ['all'], check all supported frameworks.

        Returns:
            List of detected framework names

        Raises:
            PermissionError: If project directory cannot be accessed
        """
        if frameworks is None or frameworks == ['all']:
            # Check all supported frameworks
            frameworks_to_check = ['fastapi', 'flask', 'express']
        else:
            frameworks_to_check = [fw.lower() for fw in frameworks]

        detected = set()

        logger.info(f"Detecting API frameworks in {self.project_path}")

        try:
            # Scan Python files for FastAPI/Flask
            if 'fastapi' in frameworks_to_check or 'flask' in frameworks_to_check:
                for py_file in self.project_path.rglob('*.py'):
                    # Skip common exclude directories
                    if any(exclude in py_file.parts for exclude in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                        continue

                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Check for FastAPI
                        if 'fastapi' in frameworks_to_check:
                            if re.search(r'from\s+fastapi\s+import|import\s+fastapi', content, re.IGNORECASE):
                                detected.add('fastapi')
                                logger.debug(f"FastAPI detected in {py_file}")

                        # Check for Flask
                        if 'flask' in frameworks_to_check:
                            if re.search(r'from\s+flask\s+import|import\s+flask', content, re.IGNORECASE):
                                detected.add('flask')
                                logger.debug(f"Flask detected in {py_file}")

                    except Exception as e:
                        logger.debug(f"Error reading {py_file}: {str(e)}")
                        continue

            # Scan JavaScript/TypeScript files for Express
            if 'express' in frameworks_to_check:
                for js_file in list(self.project_path.rglob('*.js')) + list(self.project_path.rglob('*.ts')):
                    # Skip common exclude directories
                    if any(exclude in js_file.parts for exclude in ['.git', 'node_modules', 'dist', 'build']):
                        continue

                    try:
                        with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Check for Express
                        if re.search(r'require\([\'"]express[\'"]\)|import\s+.*\s+from\s+[\'"]express[\'"]', content):
                            detected.add('express')
                            logger.debug(f"Express detected in {js_file}")

                    except Exception as e:
                        logger.debug(f"Error reading {js_file}: {str(e)}")
                        continue

            logger.info(f"Detected frameworks: {list(detected)}")
            return sorted(list(detected))

        except PermissionError as e:
            log_security_event('permission_denied', f"Cannot access project directory: {self.project_path}", path=str(self.project_path))
            raise PermissionError(f"Cannot access project directory: {self.project_path}")

    def extract_endpoints(
        self,
        frameworks: List[str],
        include_graphql: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Extract API endpoints from source code.

        Args:
            frameworks: List of detected frameworks
            include_graphql: Whether to parse GraphQL schemas

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []

        logger.info(f"Extracting endpoints for frameworks: {frameworks}")

        # Extract from each detected framework
        if 'fastapi' in frameworks:
            endpoints.extend(self._extract_fastapi_endpoints())
        if 'flask' in frameworks:
            endpoints.extend(self._extract_flask_endpoints())
        if 'express' in frameworks:
            endpoints.extend(self._extract_express_endpoints())

        # Extract GraphQL endpoints if requested
        if include_graphql:
            endpoints.extend(self._extract_graphql_endpoints())

        logger.info(f"Extracted {len(endpoints)} total endpoints")
        return endpoints

    def _extract_fastapi_endpoints(self) -> List[Dict[str, Any]]:
        """
        Extract endpoints from FastAPI applications using AST parsing.

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        logger.info("Extracting FastAPI endpoints")

        for py_file in self.project_path.rglob('*.py'):
            # Skip common exclude directories
            if any(exclude in py_file.parts for exclude in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Parse Python AST
                tree = ast.parse(content, filename=str(py_file))

                # Find FastAPI route decorators
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            endpoint = self._parse_fastapi_decorator(decorator, node, py_file)
                            if endpoint:
                                endpoints.append(endpoint)

            except SyntaxError:
                logger.debug(f"Syntax error parsing {py_file}, skipping")
                continue
            except Exception as e:
                logger.debug(f"Error extracting FastAPI endpoints from {py_file}: {str(e)}")
                continue

        logger.info(f"Found {len(endpoints)} FastAPI endpoints")
        return endpoints

    def _parse_fastapi_decorator(
        self,
        decorator: ast.expr,
        func_node: ast.FunctionDef,
        file_path: Path
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a FastAPI decorator to extract endpoint information.

        Args:
            decorator: AST decorator node
            func_node: Function definition node
            file_path: Path to source file

        Returns:
            Endpoint dictionary or None if not a route decorator
        """
        # Check if decorator is a route method (app.get, app.post, etc.)
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                method = decorator.func.attr
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    # Extract path from first argument
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        path = decorator.args[0].value

                        # Get function parameters
                        params = [arg.arg for arg in func_node.args.args if arg.arg != 'self']

                        # Check if function has docstring
                        docstring = ast.get_docstring(func_node)

                        relative_path = file_path.relative_to(self.project_path)

                        return {
                            "path": path,
                            "method": method.upper(),
                            "framework": "fastapi",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": func_node.lineno,
                            "function": func_node.name,
                            "parameters": params,
                            "documented": bool(docstring),
                            "doc_coverage": 100 if docstring else 0
                        }

        return None

    def _extract_flask_endpoints(self) -> List[Dict[str, Any]]:
        """
        Extract endpoints from Flask applications using AST parsing.

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        logger.info("Extracting Flask endpoints")

        for py_file in self.project_path.rglob('*.py'):
            # Skip common exclude directories
            if any(exclude in py_file.parts for exclude in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Parse Python AST
                tree = ast.parse(content, filename=str(py_file))

                # Find Flask route decorators
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            endpoint = self._parse_flask_decorator(decorator, node, py_file)
                            if endpoint:
                                endpoints.append(endpoint)

            except SyntaxError:
                logger.debug(f"Syntax error parsing {py_file}, skipping")
                continue
            except Exception as e:
                logger.debug(f"Error extracting Flask endpoints from {py_file}: {str(e)}")
                continue

        logger.info(f"Found {len(endpoints)} Flask endpoints")
        return endpoints

    def _parse_flask_decorator(
        self,
        decorator: ast.expr,
        func_node: ast.FunctionDef,
        file_path: Path
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a Flask decorator to extract endpoint information.

        Args:
            decorator: AST decorator node
            func_node: Function definition node
            file_path: Path to source file

        Returns:
            Endpoint dictionary or None if not a route decorator
        """
        # Check if decorator is @app.route or @blueprint.route
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'route':
                # Extract path from first argument
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value

                    # Extract methods from keyword arguments
                    methods = ['GET']  # Flask default
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods':
                            if isinstance(keyword.value, ast.List):
                                methods = [
                                    elt.value for elt in keyword.value.elts
                                    if isinstance(elt, ast.Constant)
                                ]

                    # Get function parameters
                    params = [arg.arg for arg in func_node.args.args if arg.arg != 'self']

                    # Check if function has docstring
                    docstring = ast.get_docstring(func_node)

                    relative_path = file_path.relative_to(self.project_path)

                    # Create endpoint entry for each HTTP method
                    results = []
                    for method in methods:
                        results.append({
                            "path": path,
                            "method": method.upper(),
                            "framework": "flask",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": func_node.lineno,
                            "function": func_node.name,
                            "parameters": params,
                            "documented": bool(docstring),
                            "doc_coverage": 100 if docstring else 0
                        })

                    # Return first endpoint (will be called multiple times if multiple methods)
                    return results[0] if results else None

        return None

    def _extract_express_endpoints(self) -> List[Dict[str, Any]]:
        """
        Extract endpoints from Express applications using regex patterns.

        Note: JavaScript AST parsing deferred to Phase 3.5. Using regex for now.

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        logger.info("Extracting Express endpoints")

        for js_file in list(self.project_path.rglob('*.js')) + list(self.project_path.rglob('*.ts')):
            # Skip common exclude directories
            if any(exclude in js_file.parts for exclude in ['.git', 'node_modules', 'dist', 'build']):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                # Regex pattern for Express routes: app.get('/path', ...
                pattern = r'(app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]'

                for i, line in enumerate(lines, 1):
                    for match in re.finditer(pattern, line):
                        method = match.group(2).upper()
                        path = match.group(3)

                        relative_path = js_file.relative_to(self.project_path)

                        endpoints.append({
                            "path": path,
                            "method": method,
                            "framework": "express",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": i,
                            "function": "unknown",  # Hard to extract from regex
                            "parameters": [],
                            "documented": False,  # Would need deeper analysis
                            "doc_coverage": 0
                        })

            except Exception as e:
                logger.debug(f"Error extracting Express endpoints from {js_file}: {str(e)}")
                continue

        logger.info(f"Found {len(endpoints)} Express endpoints")
        return endpoints

    def _extract_graphql_endpoints(self) -> List[Dict[str, Any]]:
        """
        Extract GraphQL schemas (optional feature).

        Returns:
            List of GraphQL endpoint dictionaries
        """
        endpoints = []
        logger.info("Extracting GraphQL endpoints")

        for graphql_file in self.project_path.rglob('*.graphql'):
            try:
                with open(graphql_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple regex to find Query and Mutation types
                query_pattern = r'type\s+Query\s*\{([^}]+)\}'
                mutation_pattern = r'type\s+Mutation\s*\{([^}]+)\}'

                relative_path = graphql_file.relative_to(self.project_path)

                # Extract queries
                for match in re.finditer(query_pattern, content, re.DOTALL):
                    fields = match.group(1)
                    for field_match in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*(\w+)', fields):
                        endpoints.append({
                            "path": f"/graphql (query: {field_match.group(1)})",
                            "method": "POST",
                            "framework": "graphql",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": 0,
                            "function": field_match.group(1),
                            "parameters": [],
                            "documented": False,
                            "doc_coverage": 0
                        })

                # Extract mutations
                for match in re.finditer(mutation_pattern, content, re.DOTALL):
                    fields = match.group(1)
                    for field_match in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*(\w+)', fields):
                        endpoints.append({
                            "path": f"/graphql (mutation: {field_match.group(1)})",
                            "method": "POST",
                            "framework": "graphql",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": 0,
                            "function": field_match.group(1),
                            "parameters": [],
                            "documented": False,
                            "doc_coverage": 0
                        })

            except Exception as e:
                logger.debug(f"Error extracting GraphQL from {graphql_file}: {str(e)}")
                continue

        logger.info(f"Found {len(endpoints)} GraphQL endpoints")
        return endpoints

    def parse_openapi_docs(self) -> Dict[str, Dict[str, Any]]:
        """
        Parse OpenAPI/Swagger documentation files using pyyaml.

        Returns:
            Dictionary mapping endpoint paths to documentation metadata
        """
        docs = {}
        logger.info("Parsing OpenAPI/Swagger documentation")

        # Search for OpenAPI/Swagger files in project root and docs directories
        search_patterns = ['openapi.yaml', 'openapi.yml', 'openapi.json', 'swagger.yaml', 'swagger.yml', 'swagger.json']
        openapi_files = []

        for pattern in search_patterns:
            openapi_files.extend(self.project_path.rglob(pattern))

        if not openapi_files:
            logger.info("No OpenAPI/Swagger files found")
            return docs

        # Try to import pyyaml
        try:
            import yaml
        except ImportError:
            logger.warning("pyyaml not installed, skipping OpenAPI parsing. Install with: pip install pyyaml>=6.0")
            return docs

        for doc_file in openapi_files:
            try:
                logger.info(f"Parsing OpenAPI/Swagger file: {doc_file}")

                # Read and parse the file
                with open(doc_file, 'r', encoding='utf-8') as f:
                    if doc_file.suffix == '.json':
                        spec = json.load(f)
                    else:
                        spec = yaml.safe_load(f)

                # Extract paths from OpenAPI spec
                paths = spec.get('paths', {})

                for path, path_item in paths.items():
                    # Iterate through HTTP methods
                    for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                        if method in path_item:
                            operation = path_item[method]

                            # Build endpoint key (path + method)
                            endpoint_key = f"{method.upper()}:{path}"

                            # Extract documentation metadata
                            docs[endpoint_key] = {
                                "summary": operation.get('summary', ''),
                                "description": operation.get('description', ''),
                                "tags": operation.get('tags', []),
                                "deprecated": operation.get('deprecated', False),
                                "parameters": [
                                    p.get('name', '') for p in operation.get('parameters', [])
                                ],
                                "operationId": operation.get('operationId', ''),
                                "source_file": str(doc_file.relative_to(self.project_path))
                            }

                logger.info(f"Extracted {len(docs)} documented endpoints from {doc_file.name}")

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {doc_file}: {str(e)}")
                continue
            except yaml.YAMLError as e:
                logger.warning(f"Invalid YAML in {doc_file}: {str(e)}")
                continue
            except Exception as e:
                logger.debug(f"Error parsing OpenAPI file {doc_file}: {str(e)}")
                continue

        logger.info(f"Total OpenAPI/Swagger documented endpoints: {len(docs)}")
        return docs

    def calculate_documentation_coverage(
        self,
        endpoints: List[Dict[str, Any]],
        openapi_docs: Dict[str, Dict[str, Any]]
    ) -> int:
        """
        Calculate percentage of endpoints with documentation.

        Enriches endpoints with OpenAPI documentation where available.

        Args:
            endpoints: List of discovered endpoints
            openapi_docs: Dictionary of OpenAPI documentation

        Returns:
            Documentation coverage percentage (0-100)
        """
        if not endpoints:
            return 0

        documented_count = 0

        # Match OpenAPI docs with source endpoints
        for endpoint in endpoints:
            # Build endpoint key (method:path)
            endpoint_key = f"{endpoint.get('method', 'GET')}:{endpoint.get('path', '')}"

            # Check if endpoint has OpenAPI documentation
            if endpoint_key in openapi_docs:
                doc = openapi_docs[endpoint_key]

                # Enrich endpoint with OpenAPI data
                endpoint['summary'] = doc.get('summary', '')
                endpoint['description'] = doc.get('description', '')
                endpoint['tags'] = doc.get('tags', [])
                endpoint['deprecated'] = doc.get('deprecated', False)

                # Mark as documented
                if doc.get('summary') or doc.get('description'):
                    endpoint['documented'] = True
                    endpoint['doc_coverage'] = 100
                    documented_count += 1
            elif endpoint.get('documented', False):
                # Already marked as documented (has docstring)
                documented_count += 1

        coverage = int((documented_count / len(endpoints)) * 100)

        logger.info(f"Documentation coverage: {coverage}% ({documented_count}/{len(endpoints)} endpoints)")
        return coverage

    def generate_manifest(
        self,
        frameworks: Optional[List[str]] = None,
        include_graphql: bool = False,
        scan_documentation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive API inventory manifest.

        Args:
            frameworks: List of frameworks to check (None = all)
            include_graphql: Whether to include GraphQL endpoints
            scan_documentation: Whether to scan for OpenAPI/Swagger docs

        Returns:
            Complete API manifest dictionary

        Raises:
            IOError: If manifest cannot be generated
        """
        logger.info(f"Generating API inventory manifest")

        try:
            # Detect frameworks
            detected_frameworks = self.detect_frameworks(frameworks)

            # Extract endpoints
            endpoints = self.extract_endpoints(detected_frameworks, include_graphql)

            # Parse documentation if requested
            openapi_docs = {}
            if scan_documentation:
                openapi_docs = self.parse_openapi_docs()

            # Calculate metrics
            doc_coverage = self.calculate_documentation_coverage(endpoints, openapi_docs)

            # Count endpoints by framework and method
            framework_counts = {}
            method_counts = {}
            for endpoint in endpoints:
                fw = endpoint.get('framework', 'unknown')
                framework_counts[fw] = framework_counts.get(fw, 0) + 1

                method = endpoint.get('method', 'UNKNOWN')
                method_counts[method] = method_counts.get(method, 0) + 1

            # Build manifest structure
            manifest = {
                "project_name": self.project_path.name,
                "project_path": str(self.project_path),
                "generated_at": datetime.now().isoformat(),
                "frameworks": detected_frameworks,
                "endpoints": endpoints,
                "metrics": {
                    "total_endpoints": len(endpoints),
                    "documented_endpoints": sum(1 for ep in endpoints if ep.get('documented', False)),
                    "documentation_coverage": doc_coverage,
                    "frameworks_detected": detected_frameworks,
                    "framework_breakdown": framework_counts,
                    "method_breakdown": method_counts,
                    "rest_endpoints": len([ep for ep in endpoints if ep.get('framework') != 'graphql']),
                    "graphql_endpoints": len([ep for ep in endpoints if ep.get('framework') == 'graphql'])
                }
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"API manifest generation complete: {len(endpoints)} endpoints")
            return manifest

        except Exception as e:
            log_error('manifest_generation_error', f"Failed to generate API manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate API inventory manifest: {str(e)}")

    def save(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save API manifest to JSON file.

        Args:
            manifest: Manifest dictionary to save
            output_file: Optional custom output file path (defaults to coderef/inventory/api.json)

        Returns:
            Path to saved manifest file

        Raises:
            IOError: If file cannot be written
        """
        if output_file is None:
            self.inventory_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.inventory_dir / "api.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"API manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('manifest_save_error', f"Failed to save API manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save API manifest to {output_file}: {str(e)}")
