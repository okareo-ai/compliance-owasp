# Contract: target.env Schema

**Branch**: `011-target-auth-flow` | **Date**: 2026-03-12

## Purpose

Defines the variable schema for `owasp/target.env` (and its template `owasp/target.env.example`). This file is the single source of configuration for the agent under test across all OWASP categories. Adopters copy the example, fill in values, and all notebooks load from it via `build_target()`.

## File Format

- **Format**: dotenv (key=value, one per line)
- **Encoding**: UTF-8
- **Comments**: Lines starting with `#` are ignored
- **Variable substitution**: Values may reference environment variables via `$VAR` or `${VAR}`; substituted at load time for Auth body and other fields that may contain secrets

## Variable Schema

### Required

| Variable | Type | Description |
|----------|------|-------------|
| TARGET_NAME | string | Human-readable name for the Okareo target (e.g., "FinanceBot") |
| TARGET_ENDPOINT_URL | string | HTTP URL for the Next turn endpoint (required step) |

### Next Turn (Required)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TARGET_METHOD | string | POST | HTTP method for Next turn |
| TARGET_REQUEST_BODY | JSON string | `{"message": "{latest_message}"}` | Body template; placeholders: `{latest_message}`, `{session_id}`, `{access_token}` |
| TARGET_RESPONSE_PATH | string | response | JSONPath to assistant response in API response |
| TARGET_MAX_PARALLEL_REQUESTS | int | 1 | Max concurrent conversations |

### Static Authentication (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TARGET_API_KEY | string | (empty) | Static API key; sent as `Authorization: Bearer <key>` and `api-key` header. Use when no Auth step is needed. |

### Auth Step (Optional)

When set, a token is acquired before Start/Next/End. The token is injected as `{access_token}` in downstream requests.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TARGET_AUTH_URL | string | (empty) | Token endpoint URL (e.g., OAuth2 token URL) |
| TARGET_AUTH_METHOD | string | POST | HTTP method for Auth request |
| TARGET_AUTH_BODY | string | (empty) | Request body. Use `$TARGET_AUTH_CLIENT_ID`, `$TARGET_AUTH_CLIENT_SECRET` for secrets from env. |
| TARGET_AUTH_HEADERS | string | (empty) | Optional headers (e.g., `Content-Type: application/x-www-form-urlencoded`) |
| TARGET_AUTH_RESPONSE_TOKEN_PATH | string | response.access_token | JSONPath to token in Auth response |

### Start Session (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TARGET_SESSION_START_URL | string | (empty) | URL to create a session |
| TARGET_SESSION_START_METHOD | string | POST | HTTP method for Start |
| TARGET_SESSION_START_BODY | string | (empty) | Request body; supports `{access_token}` |
| TARGET_SESSION_ID_PATH | string | session_id | JSONPath to session ID in Start response |

### End Session (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TARGET_SESSION_END_URL | string | (empty) | URL to end a session |
| TARGET_SESSION_END_METHOD | string | POST | HTTP method for End |
| TARGET_SESSION_END_BODY | string | (empty) | Request body; supports `{session_id}`, `{access_token}` |

## Validation Rules

1. `TARGET_ENDPOINT_URL` MUST be set; otherwise `build_target()` raises `ValueError`
2. When `TARGET_AUTH_URL` is set, `TARGET_AUTH_RESPONSE_TOKEN_PATH` defaults to `response.access_token` if not specified
3. When `TARGET_AUTH_BODY` references `$VAR`, the variable MUST be set in the environment (e.g., in `.env`) before config load; otherwise substitution yields empty string
4. `TARGET_REQUEST_BODY` MUST be valid JSON when parsed

## Example (Minimal — Next Only)

```env
TARGET_NAME=my-agent
TARGET_ENDPOINT_URL=https://my-agent.example.com/chat
TARGET_REQUEST_BODY={"message": "{latest_message}"}
TARGET_RESPONSE_PATH=response
```

## Example (Auth + Next)

```env
TARGET_NAME=my-agent
TARGET_ENDPOINT_URL=https://my-agent.example.com/chat
TARGET_REQUEST_BODY={"message": "{latest_message}", "Authorization": "Bearer {access_token}"}

TARGET_AUTH_URL=https://auth.example.com/oauth2/token
TARGET_AUTH_METHOD=POST
TARGET_AUTH_HEADERS=Content-Type: application/x-www-form-urlencoded
TARGET_AUTH_BODY=grant_type=client_credentials&client_id=$TARGET_AUTH_CLIENT_ID&client_secret=$TARGET_AUTH_CLIENT_SECRET
TARGET_AUTH_RESPONSE_TOKEN_PATH=response.access_token
```

Set `TARGET_AUTH_CLIENT_ID` and `TARGET_AUTH_CLIENT_SECRET` in `.env` (gitignored).

## Backward Compatibility

Configs that omit `TARGET_AUTH_*`, `TARGET_SESSION_START_*`, and `TARGET_SESSION_END_*` continue to work as before. Only `TARGET_ENDPOINT_URL` and `TARGET_NAME` are required.
