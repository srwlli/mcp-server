"""
HTTP wrapper for docs-mcp MCP server enabling ChatGPT integration via MCP protocol.

Simplified version that works without importing server.py (MCP server).
Provides /health and /mcp endpoints. /tools endpoint disabled until we solve the server.py import issue.
"""

print("=" * 80)
print("HTTP_SERVER STARTING (Simplified Version)")
print("=" * 80)

import asyncio
import json
import logging
import os
import sys
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

print("Standard library imports complete")

# ============================================================================
# MULTI-SERVER CONFIGURATION
# ============================================================================

# List of MCP server directories to load (sibling directories)
# In standalone mode (Railway or STANDALONE_MODE=true), only load docs-mcp
# In multi-server mode (local), load all servers
# Auto-detect Railway environment or explicit STANDALONE_MODE flag
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None
STANDALONE_MODE = os.environ.get('STANDALONE_MODE', 'false').lower() == 'true' or IS_RAILWAY
SERVER_DIRS = ['docs-mcp'] if STANDALONE_MODE else ['docs-mcp', 'coderef-mcp', 'hello-world-mcp', 'personas-mcp']

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================
# API Key authentication (required for production)
MCP_API_KEY = os.environ.get('MCP_API_KEY')
# CORS allowed origins (comma-separated, or '*' for all)
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = ['/', '/health', '/openapi.json']

print(f"Environment: {'Railway' if IS_RAILWAY else 'Local'}")
print(f"Standalone mode: {STANDALONE_MODE}")
print(f"Will load servers: {SERVER_DIRS}")
print(f"API Key configured: {'YES' if MCP_API_KEY else 'NO'}")
print(f"Allowed origins: {ALLOWED_ORIGINS}")

# Storage for loaded servers
LOADED_SERVERS = {}  # {server_name: module}
TOOL_REGISTRY = {}   # {tool_name: server_name}
ALL_TOOL_HANDLERS = {}  # {tool_name: handler_function}

print(f"Will attempt to load {len(SERVER_DIRS)} MCP servers")

# Import MCP server for tool discovery (LEGACY - will be replaced by multi-server)
print("Attempting to import server module...")
try:
    import server
    print("SUCCESS: server module imported")
    SERVER_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Could not import server: {e}")
    SERVER_AVAILABLE = False
    server = None

from flask import Flask, jsonify, request

print("Flask imported successfully")

# Import dependencies with graceful fallbacks
print("Attempting to import TOOL_HANDLERS...")
try:
    from tool_handlers import TOOL_HANDLERS
    print(f"SUCCESS: TOOL_HANDLERS imported ({len(TOOL_HANDLERS)} tools)")
except ImportError as e:
    print(f"ERROR: Could not import TOOL_HANDLERS: {e}")
    TOOL_HANDLERS = {}

print("Attempting to import logger...")
try:
    from logger_config import logger
    print("SUCCESS: logger imported")
except ImportError as e:
    print(f"ERROR: Could not import logger: {e}")
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('http_server')

print("All imports complete")

# ============================================================================
# MULTI-SERVER LOADING
# ============================================================================

def _load_mcp_servers() -> Dict[str, Any]:
    """
    Dynamically import all MCP servers from sibling directories.
    In standalone mode, directly inject current module's TOOL_HANDLERS.

    Returns:
        Dict mapping server_name to imported module
    """
    loaded = {}

    # In standalone mode on Railway, we're already in docs-mcp directory
    # Import the server module directly instead of loading from sibling directory
    if STANDALONE_MODE and SERVER_DIRS == ['docs-mcp']:
        logger.info("Standalone mode: Importing server module directly")
        try:
            import server as docs_server
            loaded['docs-mcp'] = docs_server
            logger.info("✓ Loaded docs-mcp server module directly")
        except Exception as e:
            logger.error(f"✗ Failed to import server module: {e}")
        return loaded

    parent_dir = Path(__file__).parent.parent  # Go up to .mcp-servers/
    logger.info(f"Loading MCP servers from: {parent_dir}")

    for server_dir in SERVER_DIRS:
        server_path = parent_dir / server_dir
        server_file = server_path / 'server.py'

        if not server_path.exists():
            logger.warning(f"Server directory not found: {server_dir}")
            continue

        if not server_file.exists():
            logger.warning(f"server.py not found in: {server_dir}")
            continue

        try:
            # Add server directory to sys.path for imports
            server_path_str = str(server_path)
            if server_path_str not in sys.path:
                sys.path.insert(0, server_path_str)

            # Import using importlib
            spec = importlib.util.spec_from_file_location(
                f"{server_dir}.server",
                server_file
            )
            server_module = importlib.util.module_from_spec(spec)
            sys.modules[f"{server_dir}.server"] = server_module
            spec.loader.exec_module(server_module)

            loaded[server_dir] = server_module
            logger.info(f"✓ Loaded server: {server_dir}")

        except Exception as e:
            logger.error(f"✗ Failed to import {server_dir}: {e}")
            continue

    logger.info(f"Successfully loaded {len(loaded)}/{len(SERVER_DIRS)} servers")
    return loaded


def _build_unified_tool_registry() -> Tuple[Dict[str, str], Dict[str, Any]]:
    """
    Build unified tool registry from all loaded servers.

    Returns:
        Tuple of (tool_registry, all_tool_handlers)
        - tool_registry: {tool_name: server_name}
        - all_tool_handlers: {tool_name: handler_function}
    """
    tool_registry = {}
    all_handlers = {}

    for server_name, server_module in LOADED_SERVERS.items():
        try:
            # Handle servers with TOOL_HANDLERS pattern (docs-mcp, coderef-mcp)
            if hasattr(server_module, 'TOOL_HANDLERS'):
                handlers = server_module.TOOL_HANDLERS
                logger.info(f"  {server_name}: {len(handlers)} tools (TOOL_HANDLERS pattern)")

                for tool_name, handler in handlers.items():
                    if tool_name in tool_registry:
                        logger.warning(f"  ⚠ Duplicate tool '{tool_name}' in {server_name} (already in {tool_registry[tool_name]})")
                    else:
                        tool_registry[tool_name] = server_name
                        all_handlers[tool_name] = handler

            # Handle servers with MCP Server pattern (hello-world-mcp, personas-mcp)
            elif hasattr(server_module, 'app'):
                # These use @app.list_tools() and @app.call_tool() decorators
                # Access the ListToolsRequest handler from request_handlers
                try:
                    from mcp.types import ListToolsRequest

                    app = server_module.app

                    # Check if app has request_handlers with ListToolsRequest
                    if hasattr(app, 'request_handlers') and ListToolsRequest in app.request_handlers:
                        # Get the handler and call it
                        handler = app.request_handlers[ListToolsRequest]
                        request = ListToolsRequest()
                        result = asyncio.run(handler(request))

                        # Extract tools from result.root.tools
                        tools = result.root.tools if hasattr(result.root, 'tools') else []
                        tool_count = len(tools)
                        logger.info(f"  {server_name}: {tool_count} tools (MCP Server pattern)")

                        # Register each tool
                        for tool in tools:
                            tool_name = tool.name
                            if tool_name in tool_registry:
                                logger.warning(f"  ⚠ Duplicate tool '{tool_name}' in {server_name} (already in {tool_registry[tool_name]})")
                            else:
                                tool_registry[tool_name] = server_name
                                # Store reference to MCP app for routing
                                all_handlers[tool_name] = app
                    else:
                        logger.warning(f"  {server_name}: MCP Server pattern but no ListToolsRequest handler found")

                except Exception as e:
                    logger.error(f"  ✗ Failed to discover tools from {server_name}: {e}")
                    import traceback
                    traceback.print_exc()

        except Exception as e:
            logger.error(f"  ✗ Failed to extract tools from {server_name}: {e}")
            continue

    logger.info(f"Unified registry: {len([k for k in tool_registry.keys() if not k.startswith('_server_')])} tools from {len(LOADED_SERVERS)} servers")
    return tool_registry, all_handlers


def _route_tool_call(tool_name: str, arguments: dict) -> Any:
    """
    Route tool call to the appropriate server.

    Args:
        tool_name: Name of tool to call
        arguments: Tool arguments

    Returns:
        Tool execution result
    """
    # Check if tool exists in unified handlers
    if tool_name in ALL_TOOL_HANDLERS:
        handler = ALL_TOOL_HANDLERS[tool_name]

        # Check if handler is an MCP Server app (from MCP Server pattern)
        if hasattr(handler, 'call_tool'):
            # This is an MCP Server app - use request_handlers[CallToolRequest]
            from mcp.types import CallToolRequest

            if not (hasattr(handler, 'request_handlers') and CallToolRequest in handler.request_handlers):
                raise ValueError(f"MCP Server app missing CallToolRequest handler for tool: {tool_name}")

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Create CallToolRequest and call the handler directly
            call_handler = handler.request_handlers[CallToolRequest]
            request = CallToolRequest(name=tool_name, arguments=arguments)
            result = loop.run_until_complete(call_handler(request))
            return result

        # Regular handler function (TOOL_HANDLERS pattern)
        if callable(handler):
            # Execute async or sync
            if asyncio.iscoroutinefunction(handler):
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                return loop.run_until_complete(handler(arguments))
            else:
                return handler(arguments)

    raise ValueError(f"Unknown tool: {tool_name}")


# Load all MCP servers at startup
try:
    logger.info("=" * 80)
    logger.info("LOADING MCP SERVERS")
    logger.info("=" * 80)
    logger.info(f"API Key configured: {'YES' if MCP_API_KEY else 'NO (auth disabled)'}")
    logger.info(f"Allowed origins: {ALLOWED_ORIGINS}")

    LOADED_SERVERS = _load_mcp_servers()

    # Add already-imported docs-mcp components if not loaded via _load_mcp_servers
    if 'docs-mcp' in LOADED_SERVERS and TOOL_HANDLERS:
        # Inject the already-imported TOOL_HANDLERS into the docs-mcp server module
        LOADED_SERVERS['docs-mcp'].TOOL_HANDLERS = TOOL_HANDLERS
        logger.info("✓ Injected existing TOOL_HANDLERS into docs-mcp")

    TOOL_REGISTRY, ALL_TOOL_HANDLERS = _build_unified_tool_registry()

    logger.info("=" * 80)
    logger.info(f"SERVERS READY: {len(LOADED_SERVERS)} servers, {len(ALL_TOOL_HANDLERS)} tools")
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"Failed to load MCP servers: {e}")
    import traceback
    traceback.print_exc()
    # Fallback to just docs-mcp
    LOADED_SERVERS = {}
    TOOL_REGISTRY = {}
    ALL_TOOL_HANDLERS = TOOL_HANDLERS if TOOL_HANDLERS else {}

# ============================================================================
# MCP PROTOCOL HELPER FUNCTIONS
# ============================================================================

def _build_mcp_tools_list() -> list:
    """Build MCP-format tools list from TOOL_HANDLERS."""
    tools = []

    # Tool metadata (manually defined for now)
    tool_descriptions = {
        'list_templates': 'List all available POWER framework documentation templates',
        'get_template': 'Retrieve the content of a specific documentation template',
        'generate_foundation_docs': 'Generate all foundation documentation for a project',
        'generate_individual_doc': 'Generate a single documentation file',
        'get_changelog': 'Query project changelog with optional filters',
        'add_changelog_entry': 'Add a new entry to the project changelog',
        'update_changelog': 'Agentic workflow to update changelog based on recent changes',
        'generate_quickref_interactive': 'Generate universal quickref guide via interactive interview',
        'establish_standards': 'Extract UI/UX/behavior standards from codebase',
        'audit_codebase': 'Audit codebase for standards compliance',
        'check_consistency': 'Quick consistency check on modified files',
        'get_planning_template': 'Get implementation planning template',
        'analyze_project_for_planning': 'Analyze project for implementation planning',
        'create_plan': 'Create implementation plan',
        'validate_implementation_plan': 'Validate implementation plan quality',
        'generate_plan_review_report': 'Generate markdown review report',
        'inventory_manifest': 'Generate comprehensive file inventory',
        'dependency_inventory': 'Analyze project dependencies',
        'api_inventory': 'Discover API endpoints',
        'database_inventory': 'Discover database schemas',
        'config_inventory': 'Discover configuration files',
        'test_inventory': 'Discover test files and coverage',
        'documentation_inventory': 'Discover documentation files'
    }

    for tool_name in TOOL_HANDLERS.keys():
        tools.append({
            'name': tool_name,
            'description': tool_descriptions.get(tool_name, f'{tool_name} tool'),
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'project_path': {
                        'type': 'string',
                        'description': 'Absolute path to project directory'
                    }
                },
                'required': ['project_path']
            }
        })

    return tools


def _handle_search(query: str) -> dict:
    """Handle search requests from ChatGPT."""
    # Simple search implementation - returns available tools matching query
    results = []

    query_lower = query.lower()
    tool_descriptions = {
        'list_templates': 'List all available POWER framework documentation templates',
        'generate_foundation_docs': 'Generate all foundation documentation',
        'establish_standards': 'Extract coding standards from codebase',
        'audit_codebase': 'Audit codebase for compliance',
        'analyze_project_for_planning': 'Analyze project for planning',
        'inventory_manifest': 'Generate file inventory'
    }

    for tool_name, description in tool_descriptions.items():
        if query_lower in tool_name.lower() or query_lower in description.lower():
            results.append({
                'title': tool_name,
                'description': description,
                'uri': f'tool://{tool_name}'
            })

    return {'results': results}


def _handle_fetch(uri: str) -> dict:
    """Handle fetch requests from ChatGPT."""
    # Extract tool name from URI (e.g., "tool://list_templates")
    if uri.startswith('tool://'):
        tool_name = uri[7:]  # Remove "tool://" prefix

        if tool_name == 'list_templates':
            # Return list of available templates
            return {
                'content': 'Available templates: readme, architecture, api, components, schema, user-guide',
                'mimeType': 'text/plain'
            }
        elif tool_name in TOOL_HANDLERS:
            return {
                'content': f'Tool {tool_name} is available. Use tools/call to execute it.',
                'mimeType': 'text/plain'
            }

    return {
        'content': f'Resource not found: {uri}',
        'mimeType': 'text/plain'
    }


# ============================================================================
# OPENRPC TRANSFORMATION HELPERS
# ============================================================================

def _transform_tool_to_openrpc_method(tool: Any) -> Dict[str, Any]:
    """
    Transform a single MCP Tool object to OpenRPC method format.

    Args:
        tool: MCP Tool object with name, description, inputSchema

    Returns:
        OpenRPC method specification dict
    """
    # Extract input schema properties
    input_schema = tool.inputSchema if hasattr(tool, 'inputSchema') else {}
    properties = input_schema.get('properties', {})
    required = input_schema.get('required', [])

    # Build params array from properties
    params = []
    for param_name, param_schema in properties.items():
        param_spec = {
            'name': param_name,
            'schema': param_schema,
            'required': param_name in required
        }
        if 'description' in param_schema:
            param_spec['description'] = param_schema['description']
        params.append(param_spec)

    # Build OpenRPC method spec
    method = {
        'name': tool.name,
        'description': tool.description,
        'params': params,
        'result': {
            'name': 'result',
            'schema': {
                'type': 'object',
                'description': f'Result from {tool.name} tool execution'
            }
        }
    }

    return method


def _build_openrpc_spec(tools: list) -> Dict[str, Any]:
    """
    Build OpenRPC 1.3.2 specification from MCP tool list.

    Args:
        tools: List of MCP Tool objects

    Returns:
        OpenRPC specification dict
    """
    methods = []

    # Transform each tool to OpenRPC method
    for tool in tools:
        try:
            method = _transform_tool_to_openrpc_method(tool)
            methods.append(method)
        except Exception as e:
            logger.warning(f"Failed to transform tool {getattr(tool, 'name', 'unknown')}: {e}")
            continue

    # Build OpenRPC spec
    spec = {
        'openrpc': '1.3.2',
        'info': {
            'title': 'docs-mcp Tools API',
            'version': '2.0.0',
            'description': 'MCP server providing 33 tools for documentation generation, changelog management, planning workflows, and project inventory'
        },
        'methods': methods
    }

    return spec


# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # ========================================================================
    # API KEY AUTHENTICATION MIDDLEWARE
    # ========================================================================
    @app.before_request
    def check_api_key():
        """
        Validate API key for protected endpoints.

        - Skips auth for PUBLIC_ENDPOINTS (/, /health, /openapi.json)
        - Skips auth if MCP_API_KEY not configured (dev mode)
        - Returns 401 for invalid/missing API key

        NOTE: We read os.environ.get('MCP_API_KEY') at REQUEST TIME, not module
        load time, because Gunicorn workers may not have env vars available
        when the module is first imported. This is critical for Railway deployment.
        """
        # Skip auth for public endpoints
        if request.path in PUBLIC_ENDPOINTS:
            return None

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None

        # Read API key at request time (not module load time)
        # This is critical for Railway/Gunicorn where env vars may not be
        # available when the module is first imported
        api_key = os.environ.get('MCP_API_KEY')

        # DEBUG: Log what we're seeing at request time
        logger.info(f"[AUTH DEBUG] Path={request.path} API_KEY_SET={bool(api_key)} KEY_LEN={len(api_key) if api_key else 0}")

        # Skip auth if no API key configured (dev mode)
        if not api_key:
            logger.info(f"[AUTH DEBUG] Skipping auth - no API key configured at request time")
            return None

        # Validate API key from X-API-Key header
        provided_key = request.headers.get('X-API-Key')
        if not provided_key or provided_key != api_key:
            # Log failed authentication attempt
            logger.warning(
                f"Auth failed: IP={request.remote_addr} Path={request.path} "
                f"Method={request.method} Key={'[provided]' if provided_key else '[missing]'}"
            )
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key. Include X-API-Key header.'
            }), 401

        return None

    @app.route('/', methods=['GET'])
    def root() -> Tuple[Dict[str, Any], int]:
        """Root endpoint - Unified MCP HTTP server information."""
        # Build server breakdown
        server_breakdown = {}
        for server_name in SERVER_DIRS:
            if server_name in LOADED_SERVERS:
                tool_count = sum(1 for tool, srv in TOOL_REGISTRY.items() if srv == server_name and not tool.startswith('_'))
                server_breakdown[server_name] = {
                    'status': 'loaded',
                    'tools': tool_count
                }
            else:
                server_breakdown[server_name] = {
                    'status': 'failed',
                    'tools': 0
                }

        return jsonify({
            'name': 'Unified MCP HTTP Server',
            'version': '2.0.0',
            'description': f'Multi-server MCP gateway exposing tools from {len(LOADED_SERVERS)}/{len(SERVER_DIRS)} servers',
            'openapi': '/openapi.json',
            'endpoints': {
                'health': '/health',
                'openapi': '/openapi.json (OpenAPI 3.0 - ChatGPT compatible)',
                'tools': '/tools (OpenRPC 1.3.2 - MCP compatible)',
                'sse': '/sse (Server-Sent Events)',
                'mcp': '/mcp (JSON-RPC 2.0 invocation)',
                'api': '/api/{tool_name} (REST - ChatGPT compatible)'
            },
            'total_tools': len(ALL_TOOL_HANDLERS),
            'servers_loaded': len(LOADED_SERVERS),
            'servers_total': len(SERVER_DIRS),
            'server_breakdown': server_breakdown
        }), 200

    @app.route('/health', methods=['GET'])
    def health() -> Tuple[Dict[str, Any], int]:
        """Health check endpoint with multi-server status."""
        # Build server status details
        servers_status = {}
        for server_name in SERVER_DIRS:
            if server_name in LOADED_SERVERS:
                tool_count = sum(1 for tool, srv in TOOL_REGISTRY.items() if srv == server_name and not tool.startswith('_'))
                servers_status[server_name] = {
                    'status': 'operational',
                    'tools': tool_count
                }
            else:
                servers_status[server_name] = {
                    'status': 'failed',
                    'tools': 0,
                    'reason': 'Import error or dependency conflict'
                }

        return jsonify({
            'status': 'operational' if len(LOADED_SERVERS) > 0 else 'degraded',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '2.0.0',
            'tools_available': len(ALL_TOOL_HANDLERS),
            'servers_loaded': len(LOADED_SERVERS),
            'servers_total': len(SERVER_DIRS),
            'servers': servers_status
        }), 200

    @app.route('/tools', methods=['GET'])
    def tools() -> Tuple[Dict[str, Any], int]:
        """
        OpenRPC tool discovery endpoint for ChatGPT integration.

        Returns OpenRPC 1.3.2 specification with all available MCP tools
        from all loaded servers (docs-mcp, hello-world-mcp, personas-mcp, etc.).
        """
        try:
            all_tools = []

            # Gather tools from all loaded MCP Server pattern servers
            from mcp.types import ListToolsRequest

            for server_name, server_module in LOADED_SERVERS.items():
                try:
                    # Check if this is an MCP Server pattern server
                    if hasattr(server_module, 'app'):
                        app_obj = server_module.app

                        # Get tools via request_handlers
                        if hasattr(app_obj, 'request_handlers') and ListToolsRequest in app_obj.request_handlers:
                            handler = app_obj.request_handlers[ListToolsRequest]
                            request_obj = ListToolsRequest()
                            result = asyncio.run(handler(request_obj))

                            # Extract tools from result
                            tools = result.root.tools if hasattr(result.root, 'tools') else []
                            all_tools.extend(tools)
                            logger.info(f"Retrieved {len(tools)} tools from {server_name}")

                    # For docs-mcp with server.list_tools() (legacy)
                    elif server_name == 'docs-mcp' and hasattr(server_module, 'list_tools'):
                        tools_list = asyncio.run(server_module.list_tools())
                        all_tools.extend(tools_list)
                        logger.info(f"Retrieved {len(tools_list)} tools from {server_name} (legacy)")

                except Exception as e:
                    logger.warning(f"Failed to get tools from {server_name}: {e}")
                    continue

            logger.info(f"Total tools retrieved from all servers: {len(all_tools)}")

            # Transform to OpenRPC spec
            try:
                openrpc_spec = _build_openrpc_spec(all_tools)
                logger.info(f"Generated OpenRPC spec with {len(openrpc_spec.get('methods', []))} methods")
            except Exception as e:
                logger.error(f"Failed to build OpenRPC spec: {e}")
                return jsonify({
                    'error': 'Internal server error',
                    'message': f'Failed to generate OpenRPC spec: {str(e)}',
                    'status': 500
                }), 500

            # Return OpenRPC spec
            return jsonify(openrpc_spec), 200

        except Exception as e:
            logger.error(f"Unexpected error in /tools endpoint: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e),
                'status': 500
            }), 500

    @app.route('/openapi.json', methods=['GET'])
    def openapi_schema() -> Tuple[Dict[str, Any], int]:
        """
        OpenAPI 3.0 schema endpoint for ChatGPT Connectors.

        Translates MCP tools to OpenAPI format since ChatGPT expects
        OpenAPI 3.0 instead of OpenRPC 1.3.2.
        """
        try:
            # Get all tools from MCP servers
            all_tools = []
            from mcp.types import ListToolsRequest

            for server_name, server_module in LOADED_SERVERS.items():
                try:
                    if hasattr(server_module, 'app'):
                        app_obj = server_module.app
                        if hasattr(app_obj, 'request_handlers') and ListToolsRequest in app_obj.request_handlers:
                            handler = app_obj.request_handlers[ListToolsRequest]
                            request_obj = ListToolsRequest()
                            result = asyncio.run(handler(request_obj))
                            tools = result.root.tools if hasattr(result.root, 'tools') else []
                            all_tools.extend(tools)
                    elif server_name == 'docs-mcp' and hasattr(server_module, 'list_tools'):
                        tools_list = asyncio.run(server_module.list_tools())
                        all_tools.extend(tools_list)
                except Exception as e:
                    logger.warning(f"Failed to get tools from {server_name} for OpenAPI: {e}")
                    continue

            # Build OpenAPI paths from MCP tools
            paths = {}

            # Add hello world test endpoint
            paths["/api/hello"] = {
                "get": {
                    "summary": "Simple hello world test endpoint",
                    "operationId": "hello",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {"type": "string"},
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "tools_available": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            for tool in all_tools:
                tool_name = getattr(tool, 'name', 'unknown')
                description = getattr(tool, 'description', '')
                input_schema = getattr(tool, 'inputSchema', {})

                # Create REST endpoint path for this tool
                path = f"/api/{tool_name}"
                paths[path] = {
                    "post": {
                        "summary": description,
                        "operationId": tool_name,
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": input_schema if input_schema else {
                                        "type": "object",
                                        "properties": {
                                            "project_path": {
                                                "type": "string",
                                                "description": "Absolute path to project directory"
                                            }
                                        },
                                        "required": ["project_path"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

            # Build OpenAPI 3.0 specification
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": "docs-mcp Tools API",
                    "version": "2.0.0",
                    "description": "MCP server providing 36 tools for documentation generation, changelog management, planning workflows, and project inventory"
                },
                "servers": [
                    {
                        "url": "https://docs-mcp-production.up.railway.app",
                        "description": "Production server"
                    }
                ],
                "paths": paths
            }

            logger.info(f"Generated OpenAPI spec with {len(paths)} paths")
            return jsonify(openapi_spec), 200

        except Exception as e:
            logger.error(f"Failed to generate OpenAPI schema: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': f'Failed to generate OpenAPI schema: {str(e)}'
            }), 500

    @app.route('/sse', methods=['GET'])
    def sse_endpoint():
        """
        Server-Sent Events (SSE) endpoint for ChatGPT MCP connector.

        ChatGPT expects a text/event-stream response for SSE transport.
        Returns streaming response with proper SSE headers.
        """
        logger.info("SSE endpoint accessed by ChatGPT connector")

        def generate():
            # Send initial connection event
            yield 'event: connected\n'
            yield 'data: {"status":"ok","transport":"sse"}\n\n'

        from flask import Response
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

    @app.route('/api/hello', methods=['GET', 'POST'])
    def hello_world():
        """Simple hello world test endpoint for ChatGPT."""
        return jsonify({
            'message': 'Hello from docs-mcp!',
            'status': 'working',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'tools_available': len(ALL_TOOL_HANDLERS)
        }), 200

    @app.route('/api/<tool_name>', methods=['POST'])
    def api_tool_endpoint(tool_name: str) -> Tuple[Dict[str, Any], int]:
        """
        REST API endpoint for individual tools (OpenAPI/ChatGPT compatibility).

        Handles POST requests to /api/{tool_name} and routes them to MCP tools.
        """
        try:
            # Get JSON body
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            arguments = request.get_json(force=True)

            # Check if tool exists
            if tool_name not in ALL_TOOL_HANDLERS:
                return jsonify({
                    'error': 'Tool not found',
                    'tool': tool_name,
                    'available_tools': list(ALL_TOOL_HANDLERS.keys())
                }), 404

            # Route tool call
            logger.info(f"REST API call: {tool_name} (from {TOOL_REGISTRY.get(tool_name, 'unknown')})")
            result = _route_tool_call(tool_name, arguments)

            # Format response for ChatGPT (simple JSON, not MCP format)
            if isinstance(result, list):
                # Extract text from MCP response format
                if len(result) > 0 and hasattr(result[0], 'text'):
                    return jsonify({'result': result[0].text}), 200
                elif len(result) > 0 and isinstance(result[0], dict) and 'text' in result[0]:
                    return jsonify({'result': result[0]['text']}), 200

            # Return as-is if already simple format
            response_data = _format_tool_response(result)
            return jsonify({'result': response_data}), 200

        except Exception as e:
            logger.error(f"REST API error for {tool_name}: {e}")
            return jsonify({
                'error': 'Tool execution failed',
                'tool': tool_name,
                'message': str(e)
            }), 500

    @app.route('/mcp', methods=['POST'])
    def mcp_endpoint() -> Tuple[Dict[str, Any], int]:
        """Main MCP endpoint accepting JSON-RPC 2.0 requests."""
        try:
            # Parse JSON
            if not request.is_json:
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32700,
                        'message': 'Parse error: Content-Type must be application/json'
                    }
                }), 400

            data = request.get_json(force=True)

            # Validate JSON-RPC structure
            if not isinstance(data, dict):
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {'code': -32600, 'message': 'Invalid Request'}
                }), 200

            request_id = data.get('id')
            method = data.get('method')
            params = data.get('params', {})

            if not method:
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {'code': -32600, 'message': 'Missing method'}
                }), 200

            # ================================================================
            # MCP PROTOCOL METHODS (Required by ChatGPT)
            # ================================================================

            # Handle initialize method
            if method == 'initialize':
                logger.info("MCP initialize request received")
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'protocolVersion': '2025-03-26',
                        'capabilities': {
                            'tools': {'listChanged': True},
                            'resources': {}
                        },
                        'serverInfo': {
                            'name': 'docs-mcp',
                            'version': '2.0.0'
                        },
                        'instructions': 'docs-mcp provides 23 tools for documentation generation, changelog management, standards auditing, implementation planning, and project inventory analysis.'
                    }
                }), 200

            # Handle notifications/initialized (client ready signal)
            if method == 'notifications/initialized':
                logger.info("Client initialized notification received")
                return '', 204  # No content response for notifications

            # Handle tools/list method
            if method == 'tools/list':
                logger.info("MCP tools/list request received")
                tools_list = _build_mcp_tools_list()
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {'tools': tools_list}
                }), 200

            # Handle search method (required by ChatGPT connector)
            if method == 'search':
                logger.info(f"MCP search request: {params}")
                query = params.get('query', '')
                search_results = _handle_search(query)
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': search_results
                }), 200

            # Handle fetch method (required by ChatGPT connector)
            if method == 'fetch':
                logger.info(f"MCP fetch request: {params}")
                uri = params.get('uri', '')
                fetch_result = _handle_fetch(uri)
                return jsonify({
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': fetch_result
                }), 200

            # ================================================================
            # TOOL EXECUTION
            # ================================================================

            # Handle tools/call method (MCP protocol standard)
            if method == 'tools/call':
                tool_name = params.get('name')
                arguments = params.get('arguments', {})

                if not tool_name:
                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {'code': -32602, 'message': 'Missing tool name'}
                    }), 200

                # Check if tool exists in unified registry
                if tool_name not in ALL_TOOL_HANDLERS:
                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32601,
                            'message': f'Tool not found: {tool_name}'
                        }
                    }), 200

                # Route tool call to appropriate server
                try:
                    logger.info(f"Routing tool call: {tool_name} (from {TOOL_REGISTRY.get(tool_name, 'unknown')})")
                    result = _route_tool_call(tool_name, arguments)
                    response_data = _format_tool_response(result)

                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'result': {'content': response_data} if not isinstance(response_data, dict) or 'content' not in response_data else response_data
                    }), 200
                except Exception as e:
                    logger.error(f"Tool execution error for {tool_name}: {e}")
                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32603,
                            'message': f'Tool execution failed: {str(e)}'
                        }
                    }), 200

            # Legacy support: Direct method name as tool (backward compatibility)
            # Check if method exists in unified tool handlers
            if method in ALL_TOOL_HANDLERS:
                try:
                    logger.info(f"Legacy tool call: {method} (from {TOOL_REGISTRY.get(method, 'unknown')})")
                    result = _route_tool_call(method, params)
                    response_data = _format_tool_response(result)

                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'result': response_data
                    }), 200
                except Exception as e:
                    logger.error(f"Tool execution error for {method}: {e}")
                    return jsonify({
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32603,
                            'message': f'Tool execution failed: {str(e)}'
                        }
                    }), 200

            # Method not found
            return jsonify({
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                }
            }), 200

        except Exception as e:
            logger.error(f"MCP endpoint error: {str(e)}")
            return jsonify({
                'jsonrpc': '2.0',
                'id': data.get('id') if 'data' in locals() else None,
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': {'details': str(e)}
                }
            }), 500

    @app.after_request
    def add_cors_headers(response):
        """
        Add CORS headers for cross-origin requests.

        Uses ALLOWED_ORIGINS env var to restrict origins in production.
        Set to '*' for development or comma-separated list for production.
        Example: ALLOWED_ORIGINS=https://chat.openai.com,https://myapp.com
        """
        response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key'
        return response

    return app


def _format_tool_response(result: Any) -> Any:
    """Format tool response for JSON serialization."""
    if isinstance(result, list):
        formatted = []
        for item in result:
            if hasattr(item, 'type') and hasattr(item, 'text'):
                formatted.append({'type': item.type, 'text': item.text})
            elif isinstance(item, dict):
                formatted.append(item)
            else:
                formatted.append(str(item))
        return formatted
    return result


# ============================================================================
# CREATE APP INSTANCE FOR GUNICORN
# ============================================================================

print("=" * 80)
print("Creating Flask app...")
try:
    app = create_app()
    print(f"SUCCESS: Flask app created: {app}")
    print(f"Tools available: {len(TOOL_HANDLERS)}")
    print("=" * 80)
    print("HTTP_SERVER READY")
    print("=" * 80)
except Exception as e:
    print("!" * 80)
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("!" * 80)
    # Fallback
    app = Flask(__name__)
    @app.route('/health')
    def health():
        return jsonify({'status': 'error', 'message': str(e)}), 503


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting HTTP server on port {port}")
    app.run(host='0.0.0.0', port=port)
