"""Base generator with shared logic for all documentation generators."""

from pathlib import Path
from typing import Optional, Dict
import sys

# Add parent directory to path for constants import
sys.path.insert(0, str(Path(__file__).parent.parent))
from constants import Paths, Files
from type_defs import PathsDict, TemplateInfoDict

# Import logging (ARCH-003)
from logger_config import logger, log_security_event, log_error


class BaseGenerator:
    """Base class providing common functionality for documentation generators."""

    def __init__(self, templates_dir: Path):
        """
        Initialize base generator.

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir

    def _sanitize_template_name(self, template_name: str) -> str:
        """
        Sanitize template name to prevent path traversal (SEC-005).

        Args:
            template_name: Template name to validate

        Returns:
            Sanitized template name

        Raises:
            ValueError: If template name contains invalid characters
        """
        import re
        if not template_name or not re.match(r'^[a-zA-Z0-9_-]+$', template_name):
            log_security_event('path_traversal_blocked', f"Invalid template name: {template_name}", template_name=template_name)
            raise ValueError(f"Invalid template name: {template_name}")
        return template_name

    def read_template(self, template_name: str) -> str:
        """
        Read a template file from templates/power/ directory.

        Args:
            template_name: Name of template (e.g., 'readme', 'architecture')

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
            IOError: If template file cannot be read
            ValueError: If template name contains invalid characters (SEC-005)
        """
        # Sanitize template name to prevent path traversal (SEC-005)
        template_name = self._sanitize_template_name(template_name)

        template_file = self.templates_dir / f"{template_name}.txt"

        if not template_file.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found at {template_file}"
            )

        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading template '{template_name}': {str(e)}")

    def validate_project_path(self, project_path: str) -> Path:
        """
        Validate that project path exists and is a directory.
        Resolves symlinks and relative paths for security.

        Args:
            project_path: Path to project directory

        Returns:
            Validated and resolved Path object

        Raises:
            ValueError: If path doesn't exist or isn't a directory
        """
        # Resolve to absolute path and follow symlinks (SEC-001)
        logger.debug(f"Validating project path: {project_path}")
        path = Path(project_path).resolve()

        if not path.exists():
            log_error('path_validation_failed', f"Project path does not exist: {project_path}", path=project_path)
            raise ValueError(f"Project path does not exist: {project_path}")

        if not path.is_dir():
            log_error('path_validation_failed', f"Project path is not a directory: {project_path}", path=project_path)
            raise ValueError(f"Project path is not a directory: {project_path}")

        logger.info(f"Project path validated: {path}")
        return path

    def create_output_directory(self, project_path: Path, subdir: Optional[str] = None) -> Path:
        """
        Create output directory for generated documentation.

        Args:
            project_path: Project root directory
            subdir: Subdirectory name for docs (default: from Paths.FOUNDATION_DOCS)

        Returns:
            Path to created/existing output directory
        """
        if subdir is None:
            subdir = Paths.FOUNDATION_DOCS
        output_dir = project_path / subdir
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_template_info(self, template_name: str) -> TemplateInfoDict:
        """
        Parse template to extract metadata.

        Args:
            template_name: Name of template

        Returns:
            Dictionary with template metadata (framework, purpose, save_as, etc.)
        """
        content = self.read_template(template_name)
        metadata = {}

        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if key in ['framework', 'purpose', 'save_as', 'store_as']:
                    metadata[key] = value

        return metadata

    # Template name constants for special handling
    TEMPLATE_README = 'readme'
    TEMPLATE_MY_GUIDE = 'my-guide'

    def get_doc_output_path(self, project_path: Path, template_name: str) -> Path:
        """
        Get the correct output path for a documentation file (SEC-003).

        README.md and my-guide.md are special and go to project root.
        All other docs go to coderef/foundation-docs/.

        Args:
            project_path: Root project directory
            template_name: Name of template (e.g., 'readme', 'architecture', 'my-guide')

        Returns:
            Full path where the document should be saved
        """
        template_info = self.get_template_info(template_name)
        filename = template_info.get('save_as', f'{template_name.upper()}.md')

        # README.md and my-guide.md go to project root (SEC-003)
        if template_name.lower() in [self.TEMPLATE_README, self.TEMPLATE_MY_GUIDE]:
            return project_path / filename

        # All other docs go to foundation-docs/ (using constant)
        # Only create directory when needed (not for root docs)
        docs_dir = project_path / Paths.FOUNDATION_DOCS
        docs_dir.mkdir(parents=True, exist_ok=True)
        return docs_dir / filename

    def save_document(self, content: str, output_dir: Path, filename: str) -> str:
        """
        Save generated document to output directory.

        Args:
            content: Document content to save
            output_dir: Directory to save document in
            filename: Name of file to save

        Returns:
            Absolute path to saved file as string

        Raises:
            IOError: If file cannot be written
        """
        file_path = output_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(file_path)
        except Exception as e:
            raise IOError(f"Error saving document to {file_path}: {str(e)}")

    def prepare_generation(self, project_path: str) -> PathsDict:
        """
        Prepare project for documentation generation.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary with 'project_path' and 'output_dir' Path objects

        Raises:
            ValueError: If project path is invalid
        """
        # Validate project path
        validated_path = self.validate_project_path(project_path)

        # Create output directory
        output_dir = self.create_output_directory(validated_path)

        return {
            'project_path': validated_path,
            'output_dir': output_dir
        }
