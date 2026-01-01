# API Documentation

## Overview

- **Framework:** FastAPI, Flask
- **Authentication:** Unknown
- **Error Format:** RFC 7807
- **Total Endpoints:** 30

## Endpoints

### FastAPI

| Method | Path | File |
|--------|------|------|
| `GET` | `/users` | `coderef-docs\extractors.py` |
| `POST` | `/auth/login` | `coderef-docs\extractors.py` |
| `GET` | `/` | `coderef-docs\tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/users` | `coderef-docs\tests\integration\test_coderef_foundation_docs.py` |
| `POST` | `/users` | `coderef-docs\tests\integration\test_coderef_foundation_docs.py` |
| `GET` | `/` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/users/{user_id}` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `POST` | `/users` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `PUT` | `/users/{user_id}` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `DELETE` | `/users/{user_id}` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/data` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/endpoint{i}` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `GET` | `/api/v1` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |

### Flask

| Method | Path | File |
|--------|------|------|
| `"GET"` | `/users` | `coderef-docs\extractors.py` |
| `'GET'` | `/` | `coderef-docs\http_server.py` |
| `'GET'` | `/health` | `coderef-docs\http_server.py` |
| `'GET'` | `/debug` | `coderef-docs\http_server.py` |
| `'GET'` | `/tools` | `coderef-docs\http_server.py` |
| `'GET'` | `/openapi.json` | `coderef-docs\http_server.py` |
| `'GET'` | `/sse` | `coderef-docs\http_server.py` |
| `'GET', 'POST'` | `/api/hello` | `coderef-docs\http_server.py` |
| `'POST'` | `/api/<tool_name>` | `coderef-docs\http_server.py` |
| `'POST'` | `/mcp` | `coderef-docs\http_server.py` |
| `"GET", "POST"` | `/api/items` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `"GET", "PUT", "DELETE"` | `/api/items/<int:item_id>` | `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py` |
| `'GET'` | `/health` | `coderef-docs\coderef\archived\http_server_full.py` |
| `'GET'` | `/tools` | `coderef-docs\coderef\archived\http_server_full.py` |
| `'POST'` | `/mcp` | `coderef-docs\coderef\archived\http_server_full.py` |

### Endpoint Details

#### `GET` /users

- **File:** `coderef-docs\extractors.py`
- **Framework:** FastAPI

#### `POST` /auth/login

- **File:** `coderef-docs\extractors.py`
- **Framework:** FastAPI

#### `"GET"` /users

- **File:** `coderef-docs\extractors.py`
- **Framework:** Flask

#### `'GET'` /

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET'` /debug

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET'` /openapi.json

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET'` /sse

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'GET', 'POST'` /api/hello

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'POST'` /api/<tool_name>

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `coderef-docs\http_server.py`
- **Framework:** Flask

#### `GET` /

- **File:** `coderef-docs\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /users

- **File:** `coderef-docs\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `coderef-docs\tests\integration\test_coderef_foundation_docs.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /users/{user_id}

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `POST` /users

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `PUT` /users/{user_id}

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `DELETE` /users/{user_id}

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/data

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/endpoint{i}

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `GET` /api/v1

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** FastAPI

#### `"GET", "POST"` /api/items

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `"GET", "PUT", "DELETE"` /api/items/<int:item_id>

- **File:** `coderef-docs\tests\unit\generators\test_coderef_foundation_generator.py`
- **Framework:** Flask

#### `'GET'` /health

- **File:** `coderef-docs\coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'GET'` /tools

- **File:** `coderef-docs\coderef\archived\http_server_full.py`
- **Framework:** Flask

#### `'POST'` /mcp

- **File:** `coderef-docs\coderef\archived\http_server_full.py`
- **Framework:** Flask

## Authentication

*Authentication method not detected.*

## Error Handling

**Format:** RFC 7807

Example:

```json
{"type": "about:blank", "status": 400, "title": "Bad Request", "detail": "..."}
```

*Generated: 2025-12-31T02:19:16.649875*