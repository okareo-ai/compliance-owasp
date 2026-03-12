# Data Model: Target Agent Auth Flow Configuration

**Branch**: `011-target-auth-flow` | **Date**: 2026-03-12

## Entity Definitions

### SharedTargetConfiguration

The single environment file at `owasp/target.env` that defines the agent under test for all OWASP categories. Extended to support Auth, Start, Next, and End steps, each with its own URL, method, body, and response mapping.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| TARGET_NAME | string | Yes | Human-readable name used as the Okareo target registration name |
| TARGET_ENDPOINT_URL | string | Yes | HTTP endpoint for the Next turn (required step) |
| TARGET_METHOD | string | No (default: POST) | HTTP method for Next turn |
| TARGET_REQUEST_BODY | JSON string | No | Request body template for Next; supports `{latest_message}`, `{session_id}`, `{access_token}` |
| TARGET_RESPONSE_PATH | string | No (default: response) | JSONPath to the assistant's response in the Next turn response |
| TARGET_MAX_PARALLEL_REQUESTS | int | No (default: 1) | Concurrent conversation limit |
| TARGET_API_KEY | string | No | Static API key sent as Authorization header (alternative to Auth step) |
| **Auth (optional)** | | | |
| TARGET_AUTH_URL | string | No | URL for token acquisition; when set, Auth step runs before Start/Next |
| TARGET_AUTH_METHOD | string | No (default: POST) | HTTP method for Auth request |
| TARGET_AUTH_BODY | string | No | Request body for Auth; supports `$VAR` / `${VAR}` for env substitution |
| TARGET_AUTH_HEADERS | string | No | Optional headers for Auth (e.g., Content-Type: application/x-www-form-urlencoded) |
| TARGET_AUTH_RESPONSE_TOKEN_PATH | string | No (default: response.access_token) | JSONPath to token in Auth response |
| **Start (optional)** | | | |
| TARGET_SESSION_START_URL | string | No | URL to create a session before the first turn |
| TARGET_SESSION_START_METHOD | string | No (default: POST) | HTTP method for Start |
| TARGET_SESSION_START_BODY | string | No | Request body for Start; supports `{access_token}` when Auth configured |
| TARGET_SESSION_ID_PATH | string | No | JSONPath to session ID in Start response |
| **End (optional)** | | | |
| TARGET_SESSION_END_URL | string | No | URL to end a session after the last turn |
| TARGET_SESSION_END_METHOD | string | No (default: POST) | HTTP method for End |
| TARGET_SESSION_END_BODY | string | No | Request body for End; supports `{session_id}`, `{access_token}` |

**Validation rules**:
- `TARGET_ENDPOINT_URL` is required; fail fast if missing
- When `TARGET_AUTH_URL` is set, `TARGET_AUTH_RESPONSE_TOKEN_PATH` defaults to `response.access_token`
- When Auth is configured, `build_target()` registers the target via `create_or_update_target` and returns `Target(target=name, name=name)`
- When Auth is not configured, `build_target()` builds `CustomEndpointTarget` client-side and returns `Target(target=endpoint, name=name)` as today

**Relationships**:
- Loaded by `owasp/common.build_target()` from `owasp/target.env`
- Consumed by all OWASP category notebooks (LLM01–LLM10) via `target = build_target(CATEGORY_DIR)`
- When Auth configured: `build_target` → `create_or_update_target` → `Target(target=name)` → `run_simulation`
- When Auth not configured: `build_target` → `Target(target=CustomEndpointTarget)` → `run_simulation`

---

### Auth Step (Logical)

| Field | Type | Description |
|-------|------|-------------|
| url | string | Token endpoint URL |
| method | string | HTTP method (default POST) |
| body | string | Request body; `$VAR` substituted from env |
| headers | string | Optional headers |
| response_access_token_path | string | JSONPath to token (default response.access_token) |

**Relationships**: Mapped to `auth_params` in Okareo API when `TARGET_AUTH_URL` is set.

---

### Start Step (Logical)

| Field | Type | Description |
|-------|------|-------------|
| url | string | Session creation endpoint |
| method | string | HTTP method (default POST) |
| body | string | Request body; supports `{access_token}` |
| response_session_id_path | string | JSONPath to session ID |

**Relationships**: Mapped to `start_session_params` in Okareo API. Already supported; extended with optional method/body override.

---

### Next Step (Logical)

| Field | Type | Description |
|-------|------|-------------|
| url | string | Turn endpoint (required) |
| method | string | HTTP method (default POST) |
| body | object | JSON body template; supports `{latest_message}`, `{session_id}`, `{access_token}` |
| response_message_path | string | JSONPath to assistant response |

**Relationships**: Mapped to `next_message_params` in Okareo API. Required.

---

### End Step (Logical)

| Field | Type | Description |
|-------|------|-------------|
| url | string | Session end endpoint |
| method | string | HTTP method (default POST) |
| body | object | Request body; supports `{session_id}`, `{access_token}` |

**Relationships**: Mapped to `end_session_params` in Okareo API. Already supported; extended with optional method override.

## Entity Relationship Diagram

```text
SharedTargetConfiguration (target.env)
    │
    ├── Auth Step (optional) ──→ auth_params
    ├── Start Step (optional) ──→ start_session_params
    ├── Next Step (required) ──→ next_message_params
    └── End Step (optional) ──→ end_session_params
            │
            ▼
    build_target() ──→ Target ──→ run_simulation()
```
