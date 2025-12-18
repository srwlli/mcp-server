# API Documentation

## Overview

- **Framework:** Flask, FastAPI
- **Authentication:** Unknown
- **Error Format:** RFC 7807
- **Total Endpoints:** 27

## Endpoints

### Flask

| Method | Path | File |
|--------|------|------|
| `'GET'` | `/` | `docs-mcp\http_server.py` |
| `'GET'` | `/health` | `docs-mcp\http_server.py` |
| `'GET'` | `/debug` | `docs-mcp\http_server.py` |
| `'GET'` | `/tools` | `docs-mcp\http_server.py` |
| `'GET'` | `/openapi.json` | `docs-mcp\http_server.py` |
| `'GET'` | `/sse` | `docs-mcp\http_server.py` |
| `'GET', 'POST'` | `/api/hello` | `docs-mcp\http_server.py` |
| `'POST'` | `/api/<tool_name>` | `docs-mcp\http_server.py` |
| `'POST'` | `/mcp` | `docs-mcp\http_server.py` |
| `"GET", "POST"` | `/api/items` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `"GET", "PUT", "DELETE"` | `/api/items/<int:item_id>` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `'GET'` | `/health` | `docs-mcp\coderef\archived\http_server_full.py` |
| `'GET'` | `/tools` | `docs-mcp\coderef\archived\http_server_full.py` |
| `'POST'` | `/mcp` | `docs-mcp\coderef\archived\http_server_full.py` |

### FastAPI

| Method | Path | File |
|--------|------|------|
| `GET` | `/` | `docs-mcp\tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/users` | `docs-mcp\tests\integration\test_coderef_foundation_docs.py` |
| `POST` | `/users` | `docs-mcp\tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/users/{user_id}` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `POST` | `/users` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `PUT` | `/users/{user_id}` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `DELETE` | `/users/{user_id}` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/data` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/endpoint{i}` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/v1` | `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py` |

### Endpoint Details

#### `'GET'` /

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET'` /debug

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET'` /openapi.json

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET'` /sse

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'GET', 'POST'` /api/hello

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'POST'` /api/<tool_name>

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `docs-mcp\http_server.py`
- **Framework:** Flask

#### `GET` /

- **File:** `docs-mcp\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /users

- **File:** `docs-mcp\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `docs-mcp\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /users/{user_id}

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `PUT` /users/{user_id}

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `DELETE` /users/{user_id}

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/data

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/endpoint{i}

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/v1

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `"GET", "POST"` /api/items

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `"GET", "PUT", "DELETE"` /api/items/<int:item_id>

- **File:** `docs-mcp\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `docs-mcp\coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `docs-mcp\coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `docs-mcp\coderef\archived\http_server_full.py`
- **Framework:** Flask

## Authentication

*Authentication method not detected.*

## Error Handling

**Format:** RFC 7807

Example:

```json
{"type": "about:blank", "status": 400, "title": "Bad Request", "detail": "..."}
```

*Generated: 2025-12-18T00:34:05.557384*