"""Database inventory generator for discovering schemas across multiple database systems."""

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


class DatabaseGenerator:
    """Helper class for generating comprehensive database schema inventories."""

    def __init__(self, project_path: Path):
        """
        Initialize database inventory generator.

        Args:
            project_path: Path to project directory to analyze
        """
        self.project_path = project_path
        self.inventory_dir = project_path / Paths.INVENTORY_DIR
        self.schema_path = self.inventory_dir / "database-schema.json"
        self.schema = self._load_schema()
        logger.info(f"Initialized DatabaseGenerator for {project_path}")

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load JSON schema for database manifest validation (SEC-002).

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
            logger.debug("Database manifest validation passed")
        except jsonschema.ValidationError as e:
            log_error('manifest_validation_error', f"Database manifest validation failed: {str(e)}", error=str(e))
            raise

    def detect_database_systems(self, systems: Optional[List[str]] = None) -> List[str]:
        """
        Detect database systems used in the project.

        Supports: PostgreSQL, MySQL, MongoDB, SQLite

        Args:
            systems: Optional list of database systems to check. If ['all'], check all supported systems.

        Returns:
            List of detected database system names

        Raises:
            PermissionError: If project directory cannot be accessed
        """
        if systems is None or systems == ['all']:
            # Check all supported database systems
            systems_to_check = ['postgresql', 'mysql', 'mongodb', 'sqlite']
        else:
            systems_to_check = [sys.lower() for sys in systems]

        detected = set()

        logger.info(f"Detecting database systems in {self.project_path}")

        try:
            # Scan Python files for database imports
            for py_file in self.project_path.rglob('*.py'):
                # Skip common exclude directories
                if any(exclude in py_file.parts for exclude in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                    continue

                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for PostgreSQL (psycopg2, asyncpg, SQLAlchemy with postgres)
                    if 'postgresql' in systems_to_check:
                        if re.search(r'import\s+(psycopg2|asyncpg)|from\s+(psycopg2|asyncpg)\s+import|postgresql://|postgres://', content, re.IGNORECASE):
                            detected.add('postgresql')
                            logger.debug(f"PostgreSQL detected in {py_file}")

                    # Check for MySQL (pymysql, mysql-connector, MySQLdb)
                    if 'mysql' in systems_to_check:
                        if re.search(r'import\s+(pymysql|mysql\.connector|MySQLdb)|from\s+(pymysql|mysql\.connector|MySQLdb)\s+import|mysql://', content, re.IGNORECASE):
                            detected.add('mysql')
                            logger.debug(f"MySQL detected in {py_file}")

                    # Check for MongoDB (pymongo, motor)
                    if 'mongodb' in systems_to_check:
                        if re.search(r'import\s+(pymongo|motor)|from\s+(pymongo|motor)\s+import|mongodb://', content, re.IGNORECASE):
                            detected.add('mongodb')
                            logger.debug(f"MongoDB detected in {py_file}")

                    # Check for SQLite
                    if 'sqlite' in systems_to_check:
                        if re.search(r'import\s+sqlite3|from\s+sqlite3\s+import|sqlite://', content, re.IGNORECASE):
                            detected.add('sqlite')
                            logger.debug(f"SQLite detected in {py_file}")

                except Exception as e:
                    logger.debug(f"Error reading {py_file}: {str(e)}")
                    continue

            # Scan JavaScript/TypeScript files for database imports
            for js_file in list(self.project_path.rglob('*.js')) + list(self.project_path.rglob('*.ts')):
                # Skip common exclude directories
                if any(exclude in js_file.parts for exclude in ['.git', 'node_modules', 'dist', 'build']):
                    continue

                try:
                    with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for PostgreSQL (pg, node-postgres)
                    if 'postgresql' in systems_to_check:
                        if re.search(r'require\([\'"]pg[\'"]\)|import\s+.*\s+from\s+[\'"]pg[\'"]|postgresql://', content):
                            detected.add('postgresql')
                            logger.debug(f"PostgreSQL detected in {js_file}")

                    # Check for MySQL (mysql, mysql2)
                    if 'mysql' in systems_to_check:
                        if re.search(r'require\([\'"]mysql2?[\'"]\)|import\s+.*\s+from\s+[\'"]mysql2?[\'"]|mysql://', content):
                            detected.add('mysql')
                            logger.debug(f"MySQL detected in {js_file}")

                    # Check for MongoDB (mongodb, mongoose)
                    if 'mongodb' in systems_to_check:
                        if re.search(r'require\([\'"]mongodb[\'"]\)|require\([\'"]mongoose[\'"]\)|import\s+.*\s+from\s+[\'"]mongo(db|ose)[\'"]|mongodb://', content):
                            detected.add('mongodb')
                            logger.debug(f"MongoDB detected in {js_file}")

                    # Check for SQLite (sqlite3, better-sqlite3)
                    if 'sqlite' in systems_to_check:
                        if re.search(r'require\([\'"](?:better-)?sqlite3[\'"]\)|import\s+.*\s+from\s+[\'"](?:better-)?sqlite3[\'"]', content):
                            detected.add('sqlite')
                            logger.debug(f"SQLite detected in {js_file}")

                except Exception as e:
                    logger.debug(f"Error reading {js_file}: {str(e)}")
                    continue

            logger.info(f"Detected database systems: {list(detected)}")
            return sorted(list(detected))

        except PermissionError as e:
            log_security_event('permission_denied', f"Cannot access project directory: {self.project_path}", path=str(self.project_path))
            raise PermissionError(f"Cannot access project directory: {self.project_path}")

    def extract_schemas(
        self,
        database_systems: List[str],
        include_migrations: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract database schemas from source code.

        Args:
            database_systems: List of detected database systems
            include_migrations: Whether to parse migration files

        Returns:
            List of table/collection dictionaries
        """
        tables = []

        logger.info(f"Extracting schemas for database systems: {database_systems}")

        # Extract from ORM models
        if 'postgresql' in database_systems or 'mysql' in database_systems or 'sqlite' in database_systems:
            tables.extend(self._extract_sqlalchemy_models())
            tables.extend(self._extract_sequelize_models())

        if 'mongodb' in database_systems:
            tables.extend(self._extract_mongoose_schemas())

        # Extract from migration files if requested
        if include_migrations:
            if 'postgresql' in database_systems or 'mysql' in database_systems or 'sqlite' in database_systems:
                tables.extend(self._extract_alembic_migrations())
                tables.extend(self._extract_knex_migrations())

        logger.info(f"Extracted {len(tables)} total tables/collections")
        return tables

    def _extract_sqlalchemy_models(self) -> List[Dict[str, Any]]:
        """
        Extract table definitions from SQLAlchemy ORM models using AST parsing.

        Returns:
            List of table dictionaries
        """
        tables = []
        logger.info("Extracting SQLAlchemy models")

        for py_file in self.project_path.rglob('*.py'):
            # Skip common exclude directories
            if any(exclude in py_file.parts for exclude in ['.git', 'node_modules', '__pycache__', 'venv', '.venv']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check if file contains SQLAlchemy models
                if 'sqlalchemy' not in content.lower():
                    continue

                # Parse Python AST
                tree = ast.parse(content, filename=str(py_file))

                # Find SQLAlchemy model classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        table = self._parse_sqlalchemy_model(node, py_file, content)
                        if table:
                            tables.append(table)

            except SyntaxError:
                logger.debug(f"Syntax error parsing {py_file}, skipping")
                continue
            except Exception as e:
                logger.debug(f"Error extracting SQLAlchemy models from {py_file}: {str(e)}")
                continue

        logger.info(f"Found {len(tables)} SQLAlchemy tables")
        return tables

    def _parse_sqlalchemy_model(
        self,
        class_node: ast.ClassDef,
        file_path: Path,
        content: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a SQLAlchemy model class to extract table information.

        Args:
            class_node: Class definition AST node
            file_path: Path to source file
            content: File content for additional parsing

        Returns:
            Table dictionary or None if not a model class
        """
        # Check if class has __tablename__ attribute
        tablename = None
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__tablename__':
                        if isinstance(node.value, ast.Constant):
                            tablename = node.value.value

        if not tablename:
            return None

        # Extract columns
        columns = []
        relationships = []

        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        column_name = target.id

                        # Check if assignment is a Column() call
                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'Column':
                                # Extract column type (first argument)
                                column_type = 'unknown'
                                if node.value.args:
                                    if isinstance(node.value.args[0], ast.Name):
                                        column_type = node.value.args[0].id
                                    elif isinstance(node.value.args[0], ast.Call) and isinstance(node.value.args[0].func, ast.Name):
                                        column_type = node.value.args[0].func.id

                                # Check for constraints in keywords
                                nullable = True
                                primary_key = False
                                unique = False

                                for keyword in node.value.keywords:
                                    if keyword.arg == 'nullable' and isinstance(keyword.value, ast.Constant):
                                        nullable = keyword.value.value
                                    elif keyword.arg == 'primary_key' and isinstance(keyword.value, ast.Constant):
                                        primary_key = keyword.value.value
                                    elif keyword.arg == 'unique' and isinstance(keyword.value, ast.Constant):
                                        unique = keyword.value.value

                                columns.append({
                                    "name": column_name,
                                    "type": column_type,
                                    "nullable": nullable,
                                    "primary_key": primary_key,
                                    "unique": unique
                                })

                            # Check if assignment is a relationship() call
                            elif isinstance(node.value.func, ast.Name) and node.value.func.id == 'relationship':
                                # Extract related model name (first argument)
                                if node.value.args and isinstance(node.value.args[0], ast.Constant):
                                    related_model = node.value.args[0].value
                                    relationships.append({
                                        "name": column_name,
                                        "related_table": related_model,
                                        "type": "relationship"
                                    })

        relative_path = file_path.relative_to(self.project_path)

        return {
            "name": tablename,
            "type": "table",
            "database_type": "sql",
            "orm": "sqlalchemy",
            "file": str(relative_path).replace('\\', '/'),
            "line": class_node.lineno,
            "class_name": class_node.name,
            "columns": columns,
            "relationships": relationships,
            "indexes": [],  # Would require deeper analysis
            "constraints": []  # Would require deeper analysis
        }

    def _extract_sequelize_models(self) -> List[Dict[str, Any]]:
        """
        Extract table definitions from Sequelize ORM models (Node.js).

        Returns:
            List of table dictionaries
        """
        tables = []
        logger.info("Extracting Sequelize models")

        for js_file in list(self.project_path.rglob('*.js')) + list(self.project_path.rglob('*.ts')):
            # Skip common exclude directories
            if any(exclude in js_file.parts for exclude in ['.git', 'node_modules', 'dist', 'build']):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                # Check if file contains Sequelize
                if 'sequelize' not in content.lower():
                    continue

                # Regex pattern for Sequelize.define or sequelize.define
                define_pattern = r'(\w+)\s*=\s*(?:sequelize|Sequelize)\.define\s*\(\s*[\'"](\w+)[\'"]'

                for i, line in enumerate(lines, 1):
                    match = re.search(define_pattern, line)
                    if match:
                        model_name = match.group(1)
                        table_name = match.group(2)

                        relative_path = js_file.relative_to(self.project_path)

                        tables.append({
                            "name": table_name,
                            "type": "table",
                            "database_type": "sql",
                            "orm": "sequelize",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": i,
                            "class_name": model_name,
                            "columns": [],  # Would need deeper parsing
                            "relationships": [],
                            "indexes": [],
                            "constraints": []
                        })

            except Exception as e:
                logger.debug(f"Error extracting Sequelize models from {js_file}: {str(e)}")
                continue

        logger.info(f"Found {len(tables)} Sequelize tables")
        return tables

    def _extract_mongoose_schemas(self) -> List[Dict[str, Any]]:
        """
        Extract collection definitions from Mongoose schemas (MongoDB).

        Returns:
            List of collection dictionaries
        """
        collections = []
        logger.info("Extracting Mongoose schemas")

        for js_file in list(self.project_path.rglob('*.js')) + list(self.project_path.rglob('*.ts')):
            # Skip common exclude directories
            if any(exclude in js_file.parts for exclude in ['.git', 'node_modules', 'dist', 'build']):
                continue

            try:
                with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                # Check if file contains Mongoose
                if 'mongoose' not in content.lower():
                    continue

                # Regex pattern for mongoose.model or Schema definition
                model_pattern = r'mongoose\.model\s*\(\s*[\'"](\w+)[\'"]'

                for i, line in enumerate(lines, 1):
                    match = re.search(model_pattern, line)
                    if match:
                        collection_name = match.group(1)

                        relative_path = js_file.relative_to(self.project_path)

                        collections.append({
                            "name": collection_name,
                            "type": "collection",
                            "database_type": "nosql",
                            "orm": "mongoose",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": i,
                            "class_name": collection_name,
                            "fields": [],  # Would need deeper parsing
                            "indexes": [],
                            "validators": []
                        })

            except Exception as e:
                logger.debug(f"Error extracting Mongoose schemas from {js_file}: {str(e)}")
                continue

        logger.info(f"Found {len(collections)} Mongoose collections")
        return collections

    def _extract_alembic_migrations(self) -> List[Dict[str, Any]]:
        """
        Extract table definitions from Alembic migration files (SQLAlchemy).

        Returns:
            List of table dictionaries from migrations
        """
        tables = []
        logger.info("Extracting Alembic migrations")

        # Look for alembic/versions directory
        alembic_dirs = list(self.project_path.rglob('alembic/versions'))

        for versions_dir in alembic_dirs:
            for migration_file in versions_dir.glob('*.py'):
                try:
                    with open(migration_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Look for create_table() calls
                    create_table_pattern = r'op\.create_table\s*\(\s*[\'"](\w+)[\'"]'
                    matches = re.finditer(create_table_pattern, content)

                    for match in matches:
                        table_name = match.group(1)

                        relative_path = migration_file.relative_to(self.project_path)

                        tables.append({
                            "name": table_name,
                            "type": "table",
                            "database_type": "sql",
                            "source": "alembic_migration",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": 0,
                            "columns": [],  # Would need deeper parsing
                            "relationships": [],
                            "indexes": [],
                            "constraints": []
                        })

                except Exception as e:
                    logger.debug(f"Error extracting from Alembic migration {migration_file}: {str(e)}")
                    continue

        logger.info(f"Found {len(tables)} tables in Alembic migrations")
        return tables

    def _extract_knex_migrations(self) -> List[Dict[str, Any]]:
        """
        Extract table definitions from Knex.js migration files.

        Returns:
            List of table dictionaries from migrations
        """
        tables = []
        logger.info("Extracting Knex migrations")

        # Look for migrations directory
        migration_dirs = list(self.project_path.rglob('migrations'))

        for migrations_dir in migration_dirs:
            for migration_file in list(migrations_dir.glob('*.js')) + list(migrations_dir.glob('*.ts')):
                try:
                    with open(migration_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Look for knex.schema.createTable() calls
                    create_table_pattern = r'knex\.schema\.createTable\s*\(\s*[\'"](\w+)[\'"]'
                    matches = re.finditer(create_table_pattern, content)

                    for match in matches:
                        table_name = match.group(1)

                        relative_path = migration_file.relative_to(self.project_path)

                        tables.append({
                            "name": table_name,
                            "type": "table",
                            "database_type": "sql",
                            "source": "knex_migration",
                            "file": str(relative_path).replace('\\', '/'),
                            "line": 0,
                            "columns": [],  # Would need deeper parsing
                            "relationships": [],
                            "indexes": [],
                            "constraints": []
                        })

                except Exception as e:
                    logger.debug(f"Error extracting from Knex migration {migration_file}: {str(e)}")
                    continue

        logger.info(f"Found {len(tables)} tables in Knex migrations")
        return tables

    def generate_manifest(
        self,
        database_systems: Optional[List[str]] = None,
        include_migrations: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive database inventory manifest.

        Args:
            database_systems: List of database systems to check (None = all)
            include_migrations: Whether to scan migration files

        Returns:
            Complete database manifest dictionary

        Raises:
            IOError: If manifest cannot be generated
        """
        logger.info(f"Generating database inventory manifest")

        try:
            # Detect database systems
            detected_systems = self.detect_database_systems(database_systems)

            # Extract schemas
            schemas = self.extract_schemas(detected_systems, include_migrations)

            # Calculate metrics
            sql_tables = [s for s in schemas if s.get('database_type') == 'sql']
            nosql_collections = [s for s in schemas if s.get('database_type') == 'nosql']

            # Count by database type
            system_counts = {}
            orm_counts = {}
            for schema in schemas:
                db_type = schema.get('database_type', 'unknown')
                system_counts[db_type] = system_counts.get(db_type, 0) + 1

                orm = schema.get('orm') or schema.get('source', 'unknown')
                orm_counts[orm] = orm_counts.get(orm, 0) + 1

            # Build manifest structure
            manifest = {
                "project_name": self.project_path.name,
                "project_path": str(self.project_path),
                "generated_at": datetime.now().isoformat(),
                "database_systems": detected_systems,
                "schemas": schemas,
                "metrics": {
                    "total_schemas": len(schemas),
                    "sql_tables": len(sql_tables),
                    "nosql_collections": len(nosql_collections),
                    "database_systems_detected": detected_systems,
                    "system_breakdown": system_counts,
                    "orm_breakdown": orm_counts,
                    "total_columns": sum(len(s.get('columns', [])) for s in schemas),
                    "total_relationships": sum(len(s.get('relationships', [])) for s in schemas)
                }
            }

            # Validate manifest
            self.validate_manifest(manifest)

            logger.info(f"Database manifest generation complete: {len(schemas)} schemas")
            return manifest

        except Exception as e:
            log_error('manifest_generation_error', f"Failed to generate database manifest: {str(e)}", error=str(e))
            raise IOError(f"Failed to generate database inventory manifest: {str(e)}")

    def save(self, manifest: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """
        Save database manifest to JSON file.

        Args:
            manifest: Manifest dictionary to save
            output_file: Optional custom output file path (defaults to coderef/inventory/database.json)

        Returns:
            Path to saved manifest file

        Raises:
            IOError: If file cannot be written
        """
        if output_file is None:
            self.inventory_dir.mkdir(parents=True, exist_ok=True)
            output_file = self.inventory_dir / "database.json"

        try:
            # Validate before saving
            self.validate_manifest(manifest)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Add trailing newline

            logger.info(f"Database manifest saved to {output_file}")
            return output_file

        except Exception as e:
            log_error('manifest_save_error', f"Failed to save database manifest: {str(e)}", path=str(output_file))
            raise IOError(f"Failed to save database manifest to {output_file}: {str(e)}")
