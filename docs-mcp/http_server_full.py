"""
HTTP wrapper for docs-mcp MCP server enabling ChatGPT integration via MCP protocol.

Exposes all 23 docs-mcp tools through HTTP endpoints using JSON-RPC 2.0 protocol.
Designed for Railway.app deployment with native PORT environment variable binding.
"""

print("[INIT] Starting http_server.py imports...")

import json
import logging
import os
import signal
import sys
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple

print("[INIT] Standard library imports complete")

from flask import Flask, Request, jsonify, request
from pydantic import BaseModel, ValidationError

print("[INIT] Flask and Pydantic imports complete")

# Import dependencies - handle import errors gracefully for production
print("[INIT] Attempting to import TOOL_HANDLERS...")
try:
    from tool_handlers import TOOL_HANDLERS
    print(f"[INIT] SUCCESS: TOOL_HANDLERS imported ({len(TOOL_HANDLERS)} tools)")
except ImportError as e:
    print(f"[INIT] ERROR: Could not import TOOL_HANDLERS: {e}")
    TOOL_HANDLERS = {}

print("[INIT] Attempting to import ErrorResponse...")
try:
    from error_responses import ErrorResponse
    print("[INIT] SUCCESS: ErrorResponse imported")
except ImportError as e:
    print(f"[INIT] ERROR: Could not import ErrorResponse: {e}")
    ErrorResponse = None

print("[INIT] Attempting to import logger...")
try:
    from logger_config import logger
    print("[INIT] SUCCESS: logger imported")
except ImportError as e:
    print(f"[INIT] ERROR: Could not import logger: {e}")
    # Fallback logger
    import logging
    logger = logging.getLogger('http_server')

print("[INIT] All imports complete, defining functions...")

# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app() -> Flask:
    """
    Create and configure Flask application with error handlers and logging.

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Global state for tool discovery caching
    app.tools_cache = None

    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================

    @app.errorhandler(404)
    def not_found(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle 404 errors."""
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32604,
                'message': 'Endpoint not found',
                'data': {'path': request.path}
            }
        }), 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> Tuple[Dict[str, Any], int]:
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': 'Internal server error'
            }
        }), 500

    # ========================================================================
    # ROUTES
    # ========================================================================

    @app.route('/health', methods=['GET'])
    def health() -> Tuple[Dict[str, Any], int]:
        """
        Health check endpoint for Railway deployment monitoring.

        Returns:
            Tuple[Dict, int]: JSON response with status and 200 OK
        """
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0'
        }), 200

    @app.route('/tools', methods=['GET'])
    def tools() -> Tuple[Dict[str, Any], int]:
        """
        Tool discovery endpoint listing all available MCP tools.

        Returns:
            Tuple[Dict, int]: JSON array of tools with schemas and 200 OK
        """
        # Cache tool list at startup to avoid repeated imports
        if app.tools_cache is None:
            app.tools_cache = _build_tools_list()

        return jsonify({
            'tools': app.tools_cache,
            'count': len(app.tools_cache),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    @app.route('/mcp', methods=['POST'])
    def mcp_endpoint() -> Tuple[Dict[str, Any], int]:
        """
        Main MCP endpoint accepting JSON-RPC 2.0 requests.

        Expected request format:
            {
                "jsonrpc": "2.0",
                "id": <string|number>,
                "method": "<tool_name>",
                "params": {<tool_parameters>}
            }

        Returns:
            Tuple[Dict, int]: JSON-RPC 2.0 response (result or error) and status code
        """
        try:
            # Parse and validate JSON
            if not request.is_json:
                return jsonify(_json_rpc_error(
                    id=None,
                    code=-32700,
                    message='Parse error: Content-Type must be application/json'
                )), 400

            try:
                data = request.get_json(force=True, silent=False)
            except Exception as e:
                logger.error(f"JSON parse error: {str(e)}")
                return jsonify(_json_rpc_error(
                    id=None,
                    code=-32700,
                    message='Parse error: Invalid JSON'
                )), 400

            # Validate JSON-RPC 2.0 structure
            validation_result = _validate_json_rpc_request(data)
            if validation_result:
                return validation_result

            # Extract fields
            request_id = data.get('id')
            method = data['method']
            params = data.get('params', {})

            # Log the request
            logger.info(
                'MCP request received',
                extra={
                    'method': method,
                    'request_id': request_id,
                    'param_keys': list(params.keys()) if isinstance(params, dict) else 'invalid'
                }
            )

            # Validate method exists
            if method not in TOOL_HANDLERS:
                logger.warning(f"Unknown method requested: {method}")
                return _json_rpc_error(
                    id=request_id,
                    code=-32601,
                    message=f'Method not found: {method}'
                ), 200  # JSON-RPC spec: errors still return 200

            # Validate params is dict
            if not isinstance(params, dict):
                return _json_rpc_error(
                    id=request_id,
                    code=-32602,
                    message='Invalid params: must be object',
                    data={'received_type': type(params).__name__}
                ), 200

            # Execute tool
            try:
                import asyncio
                import time
                start_time = time.time()

                # Call the tool handler
                handler = TOOL_HANDLERS[method]

                # Check if handler is async
                if asyncio.iscoroutinefunction(handler):
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(handler(params))
                else:
                    result = handler(params)

                execution_time = time.time() - start_time

                # Log successful execution
                logger.info(
                    'MCP request completed',
                    extra={
                        'method': method,
                        'request_id': request_id,
                        'execution_time': execution_time,
                        'status': 'success'
                    }
                )

                # Format response
                response_data = _format_tool_response(result)

                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': response_data
                }), 200

            except TimeoutError as e:
                logger.error(
                    'MCP request timeout',
                    extra={'method': method, 'request_id': request_id, 'error': str(e)}
                )
                return _json_rpc_error(
                    id=request_id,
                    code=-32000,
                    message='Tool execution timeout',
                    data={'details': str(e)}
                ), 200

            except PermissionError as e:
                logger.warning(
                    'MCP permission denied',
                    extra={'method': method, 'request_id': request_id, 'error': str(e)}
                )
                return _json_rpc_error(
                    id=request_id,
                    code=-32000,
                    message='Tool execution error',
                    data={'type': 'PermissionError', 'details': str(e)}
                ), 200

            except Exception as e:
                logger.error(
                    'MCP tool execution error',
                    extra={
                        'method': method,
                        'request_id': request_id,
                        'error': str(e),
                        'error_type': type(e).__name__
                    }
                )
                return _json_rpc_error(
                    id=request_id,
                    code=-32000,
                    message='Tool execution error',
                    data={'type': type(e).__name__, 'details': str(e)}
                ), 200

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON parse error: {str(e)}")
            return jsonify(_json_rpc_error(
                id=None,
                code=-32700,
                message='Parse error: Invalid JSON'
            )), 400

        except Exception as e:
            logger.error(f"Unexpected error in /mcp endpoint: {str(e)}")
            return _json_rpc_error(
                id=None,
                code=-32603,
                message='Internal server error'
            ), 500

    # ========================================================================
    # GRACEFUL SHUTDOWN
    # ========================================================================

    def _signal_handler(signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    # ========================================================================
    # CORS HEADERS (Development)
    # ========================================================================

    @app.after_request
    def add_cors_headers(response):
        """Add CORS headers for development. v2 will restrict to ChatGPT domain."""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    return app


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_json_rpc_request(data: Any) -> Optional[Tuple[Dict[str, Any], int]]:
    """
    Validate JSON-RPC 2.0 request structure.

    Args:
        data: Parsed JSON request data

    Returns:
        Error response tuple if invalid, None if valid
    """
    # Check if data is dict
    if not isinstance(data, dict):
        return _json_rpc_error(
            id=None,
            code=-32600,
            message='Invalid Request: must be object'
        ), 200

    # Check required fields
    if 'jsonrpc' not in data or data['jsonrpc'] != '2.0':
        return _json_rpc_error(
            id=data.get('id'),
            code=-32600,
            message='Invalid Request: jsonrpc must be "2.0"'
        ), 200

    if 'id' not in data or data['id'] is None:
        return _json_rpc_error(
            id=None,
            code=-32600,
            message='Invalid Request: id required and cannot be null'
        ), 200

    if 'method' not in data:
        return _json_rpc_error(
            id=data.get('id'),
            code=-32600,
            message='Invalid Request: method required'
        ), 200

    return None


def _json_rpc_error(
    id: Optional[Any],
    code: int,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create JSON-RPC 2.0 error response.

    Args:
        id: Request ID from client
        code: JSON-RPC error code
        message: Error message
        data: Optional additional error details

    Returns:
        Dict: JSON-RPC error response
    """
    error_dict = {
        'code': code,
        'message': message
    }
    if data:
        error_dict['data'] = data

    return {
        'jsonrpc': '2.0',
        'id': id,
        'error': error_dict
    }


def _build_tools_list() -> List[Dict[str, Any]]:
    """
    Build list of all available tools with schemas for discovery.

    Returns:
        List[Dict]: Array of tool definitions
    """
    import asyncio
    from server import list_tools

    # list_tools() is async, so we need to run it in an event loop
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # No event loop in current thread, create new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        tools_obj = loop.run_until_complete(list_tools())
    except Exception as e:
        logger.error(f"Failed to list tools: {str(e)}")
        # Return empty list as fallback
        return []

    tools_data = []

    for tool in tools_obj:
        tools_data.append({
            'name': tool.name,
            'description': tool.description,
            'inputSchema': tool.inputSchema
        })

    return tools_data


def _format_tool_response(result: Any) -> Any:
    """
    Format tool response for JSON serialization.

    Handles TextContent responses from MCP tools and converts to JSON-safe format.

    Args:
        result: Tool response (could be TextContent list or other)

    Returns:
        JSON-serializable response
    """
    if isinstance(result, list):
        # Handle TextContent list responses from MCP tools
        formatted = []
        for item in result:
            if hasattr(item, 'type') and hasattr(item, 'text'):
                # TextContent from mcp.types
                formatted.append({
                    'type': item.type,
                    'text': item.text
                })
            elif isinstance(item, dict):
                formatted.append(item)
            else:
                formatted.append(str(item))
        return formatted

    return result


# ============================================================================
# CREATE APP INSTANCE FOR GUNICORN
# ============================================================================

# Create app at module level so gunicorn can find it: `gunicorn http_server:app`
# Must be at module level and NOT inside if __name__ == '__main__'

# Add extensive error handling and logging for Railway debugging
print("=" * 80)
print("STARTING HTTP_SERVER MODULE INITIALIZATION")
print("=" * 80)

try:
    print("Step 1: About to call create_app()...")
    app = create_app()
    print("Step 2: create_app() succeeded!")
    print(f"Step 3: app object created: {app}")
    print(f"Step 4: app type: {type(app)}")
    print("=" * 80)
    print("HTTP_SERVER MODULE INITIALIZATION COMPLETE")
    print("=" * 80)
except Exception as e:
    print("!" * 80)
    print(f"CRITICAL ERROR: create_app() failed!")
    print(f"Exception type: {type(e).__name__}")
    print(f"Exception message: {str(e)}")
    print("!" * 80)
    import traceback
    traceback.print_exc()
    print("!" * 80)
    # Create a minimal fallback app so gunicorn can at least find 'app'
    print("Creating minimal fallback Flask app...")
    app = Flask(__name__)

    @app.route('/health')
    def health():
        return jsonify({'status': 'degraded', 'error': str(e)}), 503

    print(f"Fallback app created: {app}")
    print("!" * 80)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    # Log startup
    logger.info(f"Starting MCP HTTP server on port {port}")

    # Run app (gunicorn in production, Flask dev in development)
    if debug:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=False)
