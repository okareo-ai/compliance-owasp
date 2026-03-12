# Feature Specification: Target Agent Auth Flow Configuration

**Feature Branch**: `011-target-auth-flow`  
**Created**: 2026-03-12  
**Status**: Draft  
**Input**: User description: "Some Okareo customers require use of authentication before their agent interacts. The Target configuration in Okareo allows for this. The flow is Auth -> Start -> Next -> End. Only Next is required. The others are optional. Each one has a unique body and response mapping. Let's modify the common Target agent registry to allow any of these to be configured as part of OWASP testing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Auth Step for Protected Agents (Priority: P1)

As an OWASP tester whose agent requires authentication before accepting requests, I need to configure an Auth step in the shared target configuration so that OWASP evaluations acquire a token before interacting with my agent.

**Why this priority**: Customers with protected agents cannot run OWASP tests today without this capability. Auth is the first step in the flow and blocks all downstream steps.

**Independent Test**: Can be fully tested by setting Auth URL, method, body, and response token path in target config, then running any OWASP category notebook against an agent that requires auth. The simulation completes successfully and evaluates the agent.

**Acceptance Scenarios**:

1. **Given** a target configuration with Auth URL, method, body template, and response token path set, **When** an OWASP evaluation runs, **Then** the system acquires a token from the Auth endpoint before the first conversation turn and uses it for subsequent requests.
2. **Given** a target configuration with Auth configured, **When** the Auth endpoint returns a valid token, **Then** the evaluation proceeds through Start (if configured), Next, and End (if configured) without manual intervention.
3. **Given** a target configuration with Auth configured, **When** the Auth endpoint returns 401 or fails, **Then** the evaluation fails fast with a clear error indicating authentication could not be completed.

---

### User Story 2 - Configure All Four Flow Steps Independently (Priority: P2)

As an OWASP tester, I need each flow step (Auth, Start, Next, End) to have its own configurable request body and response mapping so I can connect to agents with varying API shapes.

**Why this priority**: Different agents use different request/response formats. Without per-step configuration, customers cannot test agents that deviate from a single assumed format.

**Independent Test**: Can be tested by configuring an agent that uses distinct body shapes for Auth (e.g., form-encoded), Start (e.g., empty POST), Next (JSON with message), and End (JSON with session_id), then verifying the evaluation completes successfully.

**Acceptance Scenarios**:

1. **Given** a target configuration, **When** Auth is configured, **Then** Auth has its own URL, method, body template, and response token path independent of other steps.
2. **Given** a target configuration, **When** Start is configured, **Then** Start has its own URL, method, body template, and response session ID path independent of other steps.
3. **Given** a target configuration, **When** End is configured, **Then** End has its own URL, method, and body template independent of other steps.
4. **Given** a target configuration, **When** Next is configured (required), **Then** Next has its own URL, method, body template, and response message path.

---

### User Story 3 - Omit Optional Steps for Simple Agents (Priority: P3)

As an OWASP tester with a stateless agent that requires no auth or session management, I need to configure only the Next step so that evaluations run without unnecessary calls.

**Why this priority**: Many agents are stateless and do not require Auth, Start, or End. The configuration must remain simple for these cases.

**Independent Test**: Can be tested by using a minimal target config with only Next endpoint set (no Auth, Start, End), then running an OWASP evaluation. The evaluation completes successfully with no Auth, Start, or End calls.

**Acceptance Scenarios**:

1. **Given** a target configuration with only Next endpoint set, **When** an OWASP evaluation runs, **Then** no Auth, Start, or End calls are made; only Next turn requests are sent.
2. **Given** a target configuration with Auth and Next set (no Start, no End), **When** an OWASP evaluation runs, **Then** Auth runs first, then Next turn requests; no Start or End calls are made.
3. **Given** a target configuration with Start, Next, and End set (no Auth), **When** an OWASP evaluation runs, **Then** Start runs before first turn, Next for each turn, End after last turn; no Auth call is made.

---

### Edge Cases

- What happens when Auth is configured but the Auth endpoint returns an unexpected response shape (e.g., token at a different JSON path)? The system should fail with a clear error indicating the token could not be extracted.
- What happens when Auth succeeds but Start fails (e.g., 401 on Start because token is not passed)? The system should surface the downstream failure; if the platform supports retry on 401, it may re-authenticate once.
- How does the system handle sensitive credentials in Auth body (e.g., client_secret)? Credentials should be configurable via environment variables or secure storage, not hardcoded in config files.
- What happens when only Auth is configured without Next? The configuration is invalid; Next is required. The system should fail fast at config load time with a clear error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The shared target configuration MUST support an optional Auth step with its own URL, HTTP method, request body template, and response token path.
- **FR-002**: The shared target configuration MUST support an optional Start step with its own URL, HTTP method, request body template, and response session ID path.
- **FR-003**: The shared target configuration MUST support the required Next step with its own URL, HTTP method, request body template, and response message path.
- **FR-004**: The shared target configuration MUST support an optional End step with its own URL, HTTP method, and request body template.
- **FR-005**: When Auth is configured, the system MUST execute Auth before Start (if Start is configured) or before the first Next turn (if Start is not configured).
- **FR-006**: When Auth is configured, the acquired token MUST be available for use in Start, Next, and End requests (e.g., via a template variable such as `{access_token}`).
- **FR-007**: The system MUST validate that Next is configured at config load time and fail with a clear error if it is missing.
- **FR-008**: The system MUST allow sensitive Auth credentials (e.g., client_id, client_secret) to be configured without storing them in plain text in the config file.
- **FR-009**: All OWASP category notebooks MUST continue to load the target from the shared configuration file without code changes; the extended configuration MUST be backward compatible with existing configs that omit Auth, Start, or End.

### Key Entities

- **Target Configuration**: The single file that defines the agent under test for all OWASP categories. Contains settings for Auth (optional), Start (optional), Next (required), End (optional). Each step has URL, method, body, and response path(s) as applicable.
- **Auth Step**: Optional pre-conversation step that acquires a token. Has URL, method, body template, response token path. Token is used in downstream steps.
- **Start Step**: Optional step to create a session before the first turn. Has URL, method, body template, response session ID path.
- **Next Step**: Required step for each conversation turn. Has URL, method, body template, response message path.
- **End Step**: Optional step to close the session after the last turn. Has URL, method, body template.

## Assumptions

- The Okareo platform supports Auth (credential authentication) as a first-class step before Start/Next/End; the OWASP suite will align with this capability.
- Auth typically uses OAuth2 client_credentials or similar token-acquisition flows; the configuration will support configurable body and response path to accommodate different providers.
- Existing target configs that use only Next (and optionally Start/End) will continue to work without modification.
- Sensitive Auth credentials will be provided via environment variables or a separate secrets mechanism; the config file will reference them by variable name, not by value.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with auth-protected agents can complete OWASP evaluations end-to-end without manual token injection or code changes to notebooks.
- **SC-002**: Users can configure Auth, Start, Next, and End with distinct body and response mappings; at least one real agent using all four steps completes an evaluation successfully.
- **SC-003**: Existing OWASP evaluations that use only Next (or Next + Start + End) continue to pass without config or code changes.
- **SC-004**: Configuration errors (e.g., missing Next, invalid Auth response path) surface within 30 seconds of evaluation start with an actionable error message.
