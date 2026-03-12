# Tasks: Target Agent Auth Flow Configuration

**Input**: Design documents from `/specs/011-target-auth-flow/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/target-env-schema.md, quickstart.md

**Tests**: Not requested in spec — manual validation via notebook execution per quickstart.md

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure; no new folders needed (config extension only)

- [ ] T001 [P] Verify owasp/common.py and owasp/target.env.example exist at owasp/common.py and owasp/target.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend target.env.example with all new variables so adopters have the template before implementation

**⚠️ CRITICAL**: User story implementation depends on the schema being documented

- [ ] T002 Extend owasp/target.env.example with Auth section: TARGET_AUTH_URL, TARGET_AUTH_METHOD, TARGET_AUTH_BODY, TARGET_AUTH_HEADERS, TARGET_AUTH_RESPONSE_TOKEN_PATH plus comments per specs/011-target-auth-flow/contracts/target-env-schema.md
- [ ] T003 Extend owasp/target.env.example with TARGET_SESSION_START_METHOD, TARGET_SESSION_START_BODY, TARGET_SESSION_END_METHOD per research R3 and data-model.md

**Checkpoint**: target.env.example documents full schema; implementation can begin

---

## Phase 3: User Story 1 - Configure Auth Step for Protected Agents (Priority: P1) 🎯 MVP

**Goal**: OWASP evaluations can run against auth-protected agents by configuring Auth URL, method, body, and response token path in target.env

**Independent Test**: Set TARGET_AUTH_URL, TARGET_AUTH_METHOD, TARGET_AUTH_BODY, TARGET_AUTH_RESPONSE_TOKEN_PATH in owasp/target.env, run any OWASP category notebook against an auth-protected agent; simulation completes and evaluates the agent

### Implementation for User Story 1

- [ ] T004 [US1] Add _substitute_env_vars(text: str) -> str helper in owasp/common.py to replace $VAR and ${VAR} with os.environ.get(VAR, "")
- [ ] T005 [US1] In owasp/common.py build_target(), add branch: when config.get("TARGET_AUTH_URL") is set, build dict with type "custom_endpoint", auth_params (url, method, body with $VAR substituted, response_access_token_path), next_message_params, start_session_params, end_session_params, max_parallel_requests per research R1
- [ ] T006 [US1] In Auth path of build_target(): call Okareo(api_key) with os.environ.get("OKAREO_API_KEY"), raise ValueError if missing when Auth configured; call okareo.create_or_update_target(Target(target=dict, name=name)); return Target(target=name, name=name)
- [ ] T007 [US1] In Auth path: default TARGET_AUTH_RESPONSE_TOKEN_PATH to response.access_token when not set; apply _substitute_env_vars to TARGET_AUTH_BODY before passing to auth_params
- [ ] T008 [US1] In Auth path: build auth_params with url, method, body (substituted), headers (from TARGET_AUTH_HEADERS if set), response_access_token_path; use dot-path for response_access_token_path (e.g. response.access_token); ensure next_message_params, start_session_params, end_session_params headers include Authorization: Bearer {access_token} so the token is passed to downstream calls

**Checkpoint**: Auth-protected agents can complete OWASP evaluations; run notebook with Auth config to validate

---

## Phase 4: User Story 2 - Configure All Four Flow Steps Independently (Priority: P2)

**Goal**: Each step (Auth, Start, Next, End) has its own configurable method and body so adopters can connect to agents with varying API shapes

**Independent Test**: Configure agent with distinct body shapes for Auth (form-encoded), Start (optional body), Next (JSON), End (JSON with session_id); run evaluation successfully

### Implementation for User Story 2

- [ ] T009 [US2] In owasp/common.py build_target() non-Auth path: read TARGET_SESSION_START_METHOD, TARGET_SESSION_START_BODY; pass method and body to SessionConfig when session_start_url is set (body defaults to {} if empty)
- [ ] T010 [US2] In owasp/common.py build_target() non-Auth path: read TARGET_SESSION_END_METHOD; pass method to EndSessionConfig when session_end_url is set
- [ ] T011 [US2] In owasp/common.py build_target() Auth path: include start_session_params with method (TARGET_SESSION_START_METHOD) and body (TARGET_SESSION_START_BODY) when TARGET_SESSION_START_URL is set; include end_session_params with method (TARGET_SESSION_END_METHOD) when TARGET_SESSION_END_URL is set

**Checkpoint**: Per-step method and body configurable; Start/End can use GET or custom body

---

## Phase 5: User Story 3 - Omit Optional Steps for Simple Agents (Priority: P3)

**Goal**: Minimal config (Next only) continues to work; no Auth, Start, or End calls when not configured

**Independent Test**: Use target.env with only TARGET_NAME, TARGET_ENDPOINT_URL, TARGET_REQUEST_BODY, TARGET_RESPONSE_PATH; run OWASP notebook; evaluation completes with no Auth/Start/End calls

### Implementation for User Story 3

- [ ] T012 [US3] Verify build_target() with no TARGET_AUTH_URL, no TARGET_SESSION_START_URL, no TARGET_SESSION_END_URL uses CustomEndpointTarget path (no create_or_update_target call); existing behavior unchanged
- [ ] T013 [US3] Verify build_target() with TARGET_SESSION_START_URL and TARGET_SESSION_END_URL but no TARGET_AUTH_URL uses CustomEndpointTarget path; Start and End use new method/body vars when set

**Checkpoint**: Backward compatibility confirmed; existing configs work without changes

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and documentation

- [ ] T014 Run quickstart.md validation: copy owasp/target.env.example to owasp/target.env, set minimal Next-only config, run one OWASP category notebook (e.g. owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb), confirm target builds and evaluation starts
- [ ] T015 [P] If README.md documents target.env setup, add note about Auth/Start/End optional configuration per specs/011-target-auth-flow/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS user story implementation
- **User Story 1 (Phase 3)**: Depends on Foundational — MVP
- **User Story 2 (Phase 4)**: Depends on US1 (build_target has two paths; US2 extends both)
- **User Story 3 (Phase 5)**: Depends on US1 and US2 — verification of backward compat
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational — No dependencies on other stories; core Auth implementation
- **User Story 2 (P2)**: After US1 — Extends build_target with Start/End method and body; affects both Auth and non-Auth paths
- **User Story 3 (P3)**: After US1 and US2 — Verification only; ensures no regressions

### Within Each User Story

- US1: T004 (helper) before T005–T008; T005 establishes Auth branch before T006–T008 refine it
- US2: T009–T011 can be done in order; T011 depends on Auth path from US1
- US3: Verification tasks T012–T013 after implementation

### Parallel Opportunities

- T001 can run in parallel with any other task (verification only)
- T002 and T003 can run in parallel (both edit target.env.example)
- T015 (README) can run in parallel with T014 (different files)

---

## Parallel Example: User Story 1

```bash
# T004 must complete first (helper used by T005–T008)
# Then T005–T008 are sequential (same file, same function)
```

## Parallel Example: Foundational

```bash
# T002 and T003 both edit owasp/target.env.example — can be combined into one task or done sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (extend target.env.example)
3. Complete Phase 3: User Story 1 (Auth step)
4. **STOP and VALIDATE**: Run notebook with Auth config against auth-protected agent
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Template ready
2. Add User Story 1 → Auth-protected agents can be tested (MVP)
3. Add User Story 2 → Per-step method/body for Start/End
4. Add User Story 3 → Verify backward compat
5. Polish → Quickstart validation, README update

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 1: Setup | T001 | 1 |
| Phase 2: Foundational | T002, T003 | 2 |
| Phase 3: US1 | T004–T008 | 5 |
| Phase 4: US2 | T009–T011 | 3 |
| Phase 5: US3 | T012–T013 | 2 |
| Phase 6: Polish | T014–T015 | 2 |
| **Total** | | **15** |
