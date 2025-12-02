"""
Handler decorators for MCP tool handlers (ARCH-004, ARCH-005).

Provides standardized decorators for error handling and invocation logging
across all MCP tool handlers. These decorators eliminate repetitive boilerplate
and ensure consistent behavior.

Usage:
    from handler_decorators import mcp_error_handler, log_invocation

    @log_invocation  # Apply first (outermost)
    @mcp_error_handler  # Apply second
    async def handle_my_tool(arguments: dict) -> list[TextContent]:
        # Handler logic - can raise exceptions freely
        # Decorators handle error logging and response formatting
        pass
"""

from typing import Callable, ParamSpec, TypeVar
from functools import wraps
from mcp.types import TextContent
import json
import jsonschema

from error_responses import ErrorResponse
from logger_config import logger, log_error, log_security_event, log_tool_call

# Type parameters for generic decorator signatures
P = ParamSpec('P')
R = TypeVar('R', bound=list[TextContent])


# ARCH-004: Error Handler Decorator
def mcp_error_handler(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator for standardized error handling across MCP tool handlers (ARCH-004).

    Wraps async handler functions to catch common exceptions and map them to
    ErrorResponse factory methods. Automatically logs errors with handler context.

    Handles these exception types:
    - ValueError -> ErrorResponse.invalid_input
    - PermissionError -> ErrorResponse.permission_denied (logged as security event)
    - FileNotFoundError -> ErrorResponse.not_found
    - IOError -> ErrorResponse.io_error
    - UnicodeDecodeError -> ErrorResponse.encoding_error
    - json.JSONDecodeError -> ErrorResponse.malformed_json
    - jsonschema.ValidationError -> ErrorResponse.validation_failed
    - Exception (catch-all) -> ErrorResponse.generic_error

    Preserves error logging context including handler name and relevant arguments.
    Maintains async compatibility and function metadata.

    Usage:
        @log_invocation  # Apply logging decorator first
        @mcp_error_handler  # Then apply error handler
        async def handle_my_tool(arguments: dict) -> list[TextContent]:
            # Handler logic - can raise exceptions freely
            # Decorator handles error logging and response formatting
            pass

    Args:
        func: Async handler function to wrap

    Returns:
        Wrapped async function with error handling
    """
    @wraps(func)
    async def wrapper(arguments: dict) -> list[TextContent]:
        # Extract handler name from function name (remove 'handle_' prefix)
        handler_name = func.__name__.replace('handle_', '')

        # Extract context keys for logging (common argument names)
        context_keys = ['project_path', 'template_name', 'version', 'feature_name',
                       'plan_file_path', 'section']
        context = {k: arguments.get(k) for k in context_keys if k in arguments}

        try:
            # Execute the handler
            return await func(arguments)

        except json.JSONDecodeError as e:
            # Malformed JSON (check before ValueError since it's a subclass)
            log_error(f'{handler_name}_json_error', str(e), **context)
            return ErrorResponse.malformed_json(
                str(e),
                "Validate JSON syntax"
            )

        except jsonschema.ValidationError as e:
            # Schema validation failed (check before ValueError)
            log_error(f'{handler_name}_validation_failed', e.message, **context,
                     schema_path=str(e.path) if e.path else '(root)')
            return ErrorResponse.validation_failed(e)

        except ValueError as e:
            # Input validation errors
            log_error(f'{handler_name}_validation_error', str(e), **context)
            return ErrorResponse.invalid_input(
                str(e),
                "Check input parameters and try again"
            )

        except PermissionError as e:
            # Permission denied (security event)
            log_security_event('permission_denied', str(e), handler=handler_name, **context)
            return ErrorResponse.permission_denied(
                str(e),
                "Check file and directory permissions"
            )

        except FileNotFoundError as e:
            # Resource not found
            log_error(f'{handler_name}_not_found', str(e), **context)
            return ErrorResponse.not_found(
                str(e),
                "Verify the resource exists and path is correct"
            )

        except IOError as e:
            # I/O errors (disk full, etc.)
            log_error(f'{handler_name}_io_error', str(e), **context)
            return ErrorResponse.io_error(
                str(e),
                "Check disk space and file system permissions"
            )

        except UnicodeDecodeError as e:
            # Encoding errors
            log_error(f'{handler_name}_encoding_error', str(e), **context)
            return ErrorResponse.encoding_error(
                str(e),
                "File may be corrupted or not UTF-8 encoded"
            )

        except Exception as e:
            # Unexpected errors (catch-all)
            log_error(f'{handler_name}_error', str(e), **context)
            return ErrorResponse.generic_error(
                f"Failed to execute {handler_name}: {str(e)}"
            )

    return wrapper


# ARCH-005: Invocation Logging Decorator
def log_invocation(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator for standardized tool invocation logging (ARCH-005).

    Automatically logs tool invocations at entry using logger_config.log_tool_call().
    Extracts handler name and logs argument keys for audit trail and debugging.

    Maintains async compatibility and function metadata.

    Usage:
        @log_invocation  # Apply first (outermost decorator)
        @mcp_error_handler  # Apply second
        async def handle_my_tool(arguments: dict) -> list[TextContent]:
            # Handler logic
            pass

    Args:
        func: Async handler function to wrap

    Returns:
        Wrapped async function with invocation logging
    """
    @wraps(func)
    async def wrapper(arguments: dict) -> list[TextContent]:
        # Extract handler name from function name (remove 'handle_' prefix)
        handler_name = func.__name__.replace('handle_', '')

        # Log tool invocation with argument keys
        log_tool_call(handler_name, args_keys=list(arguments.keys()))

        # Execute the handler
        return await func(arguments)

    return wrapper
