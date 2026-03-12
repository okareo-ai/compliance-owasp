# Research: Target Agent Auth Flow Configuration

**Branch**: `011-target-auth-flow` | **Date**: 2026-03-12

## R1: Okareo Python SDK Auth Support for Custom Endpoint Targets

**Decision**: When Auth is configured, build a dict with `auth_params`, `next_message_params`, `start_session_params`, `end_session_params` and pass `Target(target=dict, name=name)` to `create_or_update_target`, then return `Target(target=name, name=name)` so `run_simulation` uses the registered target. When Auth is not configured, continue using `CustomEndpointTarget` built client-side as today.

**Rationale**: The Okareo Python SDK v0.0.124 `CustomEndpointTarget` does not expose auth — its `params()` returns only `start_session_params`, `next_message_params`, `end_session_params`. However, `create_or_update_target` accepts `Target(target=dict, name=name)`; when `target` is a dict, it is used directly as the model payload (no `params()` call). The Okareo API accepts `auth_params` as a sibling of `next_message_params`. Therefore: when Auth is configured, we build a full dict `{type: "custom_endpoint", auth_params: {...}, next_message_params: {...}, ...}`, call `create_or_update_target(Target(target=dict, name=name))` to register it, and return `Target(target=name, name=name)` for `run_simulation`. When Auth is not configured, we build `CustomEndpointTarget` and return `Target(target=endpoint, name=name)` as today.

**Alternatives considered**:
- **Upgrade SDK**: Wait for Okareo to add auth to `CustomEndpointTarget`. Rejected because it blocks adopters with auth-protected agents indefinitely.
- **Fork SDK**: Add auth support locally. Rejected — violates Principle IV (forkability); adopters would need a custom SDK.
- **Static API key only**: Rely on `TARGET_API_KEY` for all auth. Rejected — spec requires OAuth2-style token acquisition for agents that need it.

---

## R2: Environment Variable Substitution for Sensitive Auth Credentials

**Decision**: Support `$VAR` or `${VAR}` syntax in `target.env` for Auth body fields. At config load time, substitute values from `os.environ`. Document that adopters set `TARGET_AUTH_CLIENT_ID`, `TARGET_AUTH_CLIENT_SECRET` (or similar) in `.env` and reference them in the Auth body template as `$TARGET_AUTH_CLIENT_ID`, `$TARGET_AUTH_CLIENT_SECRET`.

**Rationale**: FR-008 requires sensitive credentials to be configurable without storing them in plain text in the config file. The project already uses `python-dotenv` to load `.env`; adopters keep secrets there. The `target.env` file can reference env vars by name. Standard patterns: `$VAR` (shell-style) or `${VAR}` (bash-style). We use `os.path.expandvars` or a simple regex to substitute `$VAR` / `${VAR}` with `os.environ.get(VAR, '')` when parsing the Auth body. The `.env` file is gitignored; `target.env` is gitignored; only `target.env.example` is committed (with placeholders like `$TARGET_AUTH_CLIENT_SECRET` and a comment explaining to set the var in `.env`).

**Alternatives considered**:
- **Separate secrets file**: A `target.secrets.env` that is loaded but never committed. Rejected — adds another file; `.env` already serves this purpose.
- **No substitution**: Require adopters to manually inject credentials. Rejected — error-prone and doesn't satisfy FR-008.

---

## R3: Per-Step Body and Method for Start and End

**Decision**: Extend `target.env` with `TARGET_SESSION_START_METHOD`, `TARGET_SESSION_START_BODY`, `TARGET_SESSION_END_METHOD` (and keep existing `TARGET_SESSION_END_BODY`). Default Start/End to POST and empty body `{}` when not specified, matching current behavior.

**Rationale**: The spec (FR-002, FR-004) requires Start and End to have their own method and body. Currently `SessionConfig` and `EndSessionConfig` in `owasp/common.py` hardcode `method="POST"` and use `session_end_body` from config. `SessionConfig` does not pass a body (defaults to empty). We add optional vars so adopters can override when their agent requires GET or a non-empty body. Defaults preserve backward compatibility.

---

## R4: Auth Body Format (JSON vs Form-Encoded)

**Decision**: Support Auth body as a JSON string in `TARGET_AUTH_BODY`. For form-encoded auth (common in OAuth2 token endpoints), adopters can set `TARGET_AUTH_HEADERS=Content-Type: application/x-www-form-urlencoded` and `TARGET_AUTH_BODY` as form-encoded key=value pairs. The Okareo API `auth_params.body` accepts a string; we pass it through. Document both JSON and form-encoded examples in `target.env.example`.

**Rationale**: OAuth2 `client_credentials` typically uses `application/x-www-form-urlencoded` with `grant_type=client_credentials&client_id=...&client_secret=...`. Some providers use JSON. Supporting a string body with configurable Content-Type covers both. We do not implement automatic form-encoding — adopters provide the body string; we substitute `$VAR` for secrets.
