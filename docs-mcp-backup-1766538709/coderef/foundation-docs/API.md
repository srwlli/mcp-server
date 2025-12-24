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
| `'GET'` | `/` | `http_server.py` |
| `'GET'` | `/health` | `http_server.py` |
| `'GET'` | `/debug` | `http_server.py` |
| `'GET'` | `/tools` | `http_server.py` |
| `'GET'` | `/openapi.json` | `http_server.py` |
| `'GET'` | `/sse` | `http_server.py` |
| `'GET', 'POST'` | `/api/hello` | `http_server.py` |
| `'POST'` | `/api/<tool_name>` | `http_server.py` |
| `'POST'` | `/mcp` | `http_server.py` |
| `"GET", "POST"` | `/api/items` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `"GET", "PUT", "DELETE"` | `/api/items/<int:item_id>` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `'GET'` | `/health` | `coderef\archived\http_server_full.py` |
| `'GET'` | `/tools` | `coderef\archived\http_server_full.py` |
| `'POST'` | `/mcp` | `coderef\archived\http_server_full.py` |

### FastAPI

| Method | Path | File |
|--------|------|------|
| `GET` | `/` | `tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/users` | `tests\integration\test_coderef_foundation_docs.py` |
| `POST` | `/users` | `tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/users/{user_id}` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `POST` | `/users` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `PUT` | `/users/{user_id}` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `DELETE` | `/users/{user_id}` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/data` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/endpoint{i}` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/v1` | `tests\unit\generators\test_coderef_foundation_generator.py` |

### Endpoint Details

#### `'GET'` /

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET'` /debug

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET'` /openapi.json

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET'` /sse

- **File:** `http_server.py`
- **Framework:** Flask

#### `'GET', 'POST'` /api/hello

- **File:** `http_server.py`
- **Framework:** Flask

#### `'POST'` /api/<tool_name>

- **File:** `http_server.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `http_server.py`
- **Framework:** Flask

#### `GET` /

- **File:** `tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /users

- **File:** `tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /users/{user_id}

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `PUT` /users/{user_id}

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `DELETE` /users/{user_id}

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/data

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/endpoint{i}

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/v1

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `"GET", "POST"` /api/items

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `"GET", "PUT", "DELETE"` /api/items/<int:item_id>

- **File:** `tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `coderef\archived\http_server_full.py`
- **Framework:** Flask

## Authentication

*Authentication method not detected.*

## Error Handling

**Format:** RFC 7807

Example:

```json
{"type": "about:blank", "status": 400, "title": "Bad Request", "detail": "..."}
```

*Generated: 2025-12-15T15:05:23.286534*