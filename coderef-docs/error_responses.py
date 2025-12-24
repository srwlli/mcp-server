"""
Centralized error response factory for consistent error formatting (ARCH-001).

Provides static methods for creating standardized error responses across all MCP tools.
"""

from mcp.types import TextContent
import jsonschema

__all__ = ['ErrorResponse']


class ErrorResponse:
    """Factory class for creating consistent error responses."""

    @staticmethod
    def invalid_input(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for invalid input (ValueError).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ Invalid input: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def not_found(resource: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for resource not found (FileNotFoundError).

        Args:
            resource: Description of what was not found
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ {resource} not found"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def permission_denied(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for permission denied (PermissionError).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ Permission denied: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def validation_failed(error: jsonschema.ValidationError) -> list[TextContent]:
        """
        Create error response for schema validation failure.

        Args:
            error: jsonschema ValidationError object

        Returns:
            List containing TextContent with formatted error message including path
        """
        text = f"❌ Changelog validation failed\n\nError: {error.message}"
        if error.path:
            path_str = " → ".join(str(p) for p in error.path)
            text += f"\nPath: {path_str}"
        else:
            text += "\nPath: (root)"
        text += "\n\n💡 Check CHANGELOG.json against schema at coderef/changelog/schema.json"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def malformed_json(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for malformed JSON (json.JSONDecodeError).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ Malformed JSON: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        else:
            text += "\n\n💡 Validate JSON syntax"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def encoding_error(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for encoding errors (UnicodeDecodeError).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ Encoding error: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        else:
            text += "\n\n💡 File may be corrupted or not UTF-8 encoded"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def io_error(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create error response for I/O errors (IOError).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ File operation failed: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]

    @staticmethod
    def generic_error(detail: str, hint: str = None) -> list[TextContent]:
        """
        Create generic error response (Exception).

        Args:
            detail: Error detail message
            hint: Optional hint for fixing the error

        Returns:
            List containing TextContent with formatted error message
        """
        text = f"❌ Error: {detail}"
        if hint:
            text += f"\n\n💡 {hint}"
        return [TextContent(type="text", text=text)]
