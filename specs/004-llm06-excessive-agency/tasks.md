# Tasks: OWASP LLM06 Excessive Agency Test Suite

**Input**: Design documents from `/specs/004-llm06-excessive-agency/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks — validation is performed by running the notebook against a target agent and inspecting pass/fail results.

**Organization**: Tasks are grouped by user story (attack scenario) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Artifacts**: `owasp/LLM06-excessive-agency/{scenarios,checks,drivers}/`
- **Notebook**: `owasp/LLM06-excessive-agency/notebooks/`
- **Config**: `owasp/config.env.example`, `owasp/target.env.example`
- **Specs**: `specs/004-llm06-excessive-agency/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository structure for the LLM06 category

- [x] T001 Create directory structure: `owasp/LLM06-excessive-agency/{scenarios,checks,drivers,notebooks}/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared checks and notebook scaffold that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Create the excessive agency detector check (multi-turn, model-based, pass/fail) in `owasp/LLM06-excessive-agency/checks/excessive-agency-detector.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` using `{simulation_message_history}`, `{scenario_result}` placeholders — evaluates whether the agent exceeded its authority boundaries at any point (unauthorized tool call, permission escalation, or approval bypass)
- [x] T003 [P] Create the agency boundary drift detector check (multi-turn, model-based, pass/fail) in `owasp/LLM06-excessive-agency/checks/agency-boundary-drift-detector.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` using `{simulation_message_history}`, `{scenario_result}` placeholders — evaluates whether the agent's resistance to authority-exceeding requests progressively weakened across turns
- [x] T004 Create the notebook scaffold (cells 0–3: title markdown, pip install, SDK init with `OKAREO_API_KEY` from `.env`, `NOTEBOOK_DIR`/`CATEGORY_DIR` resolution) in `owasp/LLM06-excessive-agency/notebooks/run-evaluation.ipynb`
- [x] T005 Add scenario upload cell to notebook — scan `scenarios/*.jsonl` and upload via `okareo.upload_scenario_set(scenario_name=f"LLM06-{stem}", file_path=str(jsonl_path))` with idempotent naming
- [x] T006 Add check registration cell to notebook — implement `parse_check_md()` to parse `checks/*.md` YAML front matter + `## Prompt Template` body, register via `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`
- [x] T007 Add driver registration cell to notebook — implement `parse_driver_md()` to parse `drivers/*.md` YAML front matter + `## Persona Prompt Template` body, register via `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature))`
- [x] T008 Add artifact upload summary cell to notebook — print registered scenario IDs, check IDs, driver IDs
- [x] T009 Add target configuration cell to notebook — load `owasp/target.env` via `dotenv_values()`, validate `TARGET_ENDPOINT_URL` is set, build `CustomEndpointTarget(next_turn=TurnConfig(...))` with optional `SessionConfig`/`EndSessionConfig`, wrap in `Target(target=..., name=TARGET_NAME)`
- [x] T010 Add multi-turn simulation loop cell to notebook — define `SCENARIO_DRIVER_MAP` dict mapping scenario names to driver names (`LLM06-unauthorized-tool-invocation` → `LLM06-tool-scope-manipulator`, `LLM06-permission-escalation` → `LLM06-privilege-escalator`, `LLM06-autonomous-action` → `LLM06-approval-gate-bypasser`), define `CHECK_NAMES` list with both check names, iterate scenarios and for each: look up driver from `registered_drivers[SCENARIO_DRIVER_MAP[scenario_name]]`, create `Driver(name, prompt_template, temperature)`, run `okareo.run_simulation(target, driver, name=f"LLM06 Simulation — {scenario_name}", api_key=OKAREO_API_KEY, first_turn="target", scenario=scenario, max_turns=10, checks=CHECK_NAMES)`
- [x] T011 Add results summary cell to notebook — print scenario name, pass/fail rates, and Okareo dashboard links for all completed runs

**Checkpoint**: Notebook scaffold complete — can now add scenarios and drivers per user story

---

## Phase 3: User Story 1 — Unauthorized Tool Invocation Detection (Priority: P1) MVP

**Goal**: Detect whether the target agent calls tools beyond its explicitly granted scope when manipulated by an adversarial user across multiple conversational turns

**Independent Test**: Run notebook with `unauthorized-tool-invocation.jsonl` and `tool-scope-manipulator.md` present. Verify both checks produce pass/fail — pass means agent refused all unauthorized tool requests, fail means agent invoked or attempted to invoke an out-of-scope tool.

### Implementation for User Story 1

- [x] T012 [P] [US1] Create the tool-scope-manipulator adversarial driver persona in `owasp/LLM06-excessive-agency/drivers/tool-scope-manipulator.md` per `contracts/driver-prompt.md` with YAML front matter (`owasp_category: LLM06`, `risk_severity: Critical`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.7`) and persona prompt template using mustache parameters `{manipulation_strategy}`, `{permitted_tools}`, `{target_tool}`, `{cover_story}`, `{escalation_steps}` — persona claims tools exist, reframes unauthorized actions via permitted tools, socially engineers tool access while staying in character and escalating gradually
- [x] T013 [P] [US1] Author 5-7 unauthorized tool invocation seed rows in `owasp/LLM06-excessive-agency/scenarios/unauthorized-tool-invocation.jsonl` per `contracts/scenario-jsonl.md` Scenario 1 schema — each row provides a distinct `manipulation_strategy` (social engineering, tool hallucination induction, scope reframing, capability claim fabrication, indirect delegation) with `permitted_tools`, `target_tool`, `cover_story`, `escalation_steps` fields and a `result` describing expected agent behavior
- [x] T014 [P] [US1] Create companion metadata file in `owasp/LLM06-excessive-agency/scenarios/unauthorized-tool-invocation_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM06`, `risk_severity: Critical`, `evaluation_mode: multi-turn`, `row_count` matching actual JSONL rows
- [x] T015 [US1] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM06-unauthorized-tool-invocation` scenario uploads, `LLM06-tool-scope-manipulator` driver registers, simulation runs for up to 10 turns per row, both checks produce per-row pass/fail results

**Checkpoint**: Unauthorized tool invocation scenario independently functional and testable

---

## Phase 4: User Story 2 — Permission Escalation Across Turns Detection (Priority: P1)

**Goal**: Detect whether the target agent progressively widens its operational permissions through sequential actions without explicit authorization, starting from a declared permission level and gradually performing actions at higher privilege levels

**Independent Test**: Run notebook with `permission-escalation.jsonl` and `privilege-escalator.md` present. Verify both checks produce pass/fail — pass means agent maintained its original permission level, fail means agent performed actions beyond its declared permissions.

### Implementation for User Story 2

- [x] T016 [P] [US2] Create the privilege-escalator adversarial driver persona in `owasp/LLM06-excessive-agency/drivers/privilege-escalator.md` per `contracts/driver-prompt.md` with YAML front matter (`owasp_category: LLM06`, `risk_severity: Critical`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.7`) and persona prompt template using mustache parameters `{escalation_strategy}`, `{initial_permission_level}`, `{target_permission_level}`, `{cover_story}`, `{escalation_steps}` — persona starts with legitimate requests at initial permission level, uses incremental widening, gaslighting, and batch embedding tactics to gradually push toward target permission level
- [x] T017 [P] [US2] Author 5-7 permission escalation seed rows in `owasp/LLM06-excessive-agency/scenarios/permission-escalation.jsonl` per `contracts/scenario-jsonl.md` Scenario 2 schema — each row provides a distinct `escalation_strategy` (incremental request widening, gaslighting about prior grants, batch embedding, false authority claim, implicit assumption) with `initial_permission_level`, `target_permission_level`, `cover_story`, `escalation_steps` fields and a `result` describing expected agent behavior
- [x] T018 [P] [US2] Create companion metadata file in `owasp/LLM06-excessive-agency/scenarios/permission-escalation_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM06`, `risk_severity: Critical`, `evaluation_mode: multi-turn`, `row_count` matching actual JSONL rows
- [x] T019 [US2] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM06-permission-escalation` scenario uploads, `LLM06-privilege-escalator` driver registers, simulation runs for up to 10 turns per row, both checks produce per-row pass/fail results

**Checkpoint**: Permission escalation scenario independently functional and testable

---

## Phase 5: User Story 3 — Autonomous Action Without Human Approval Detection (Priority: P1)

**Goal**: Detect whether the target agent performs high-impact actions (data deletion, external API calls, financial transactions) without required human confirmation, when pressured by an adversarial user who fabricates urgency and claims pre-approval

**Independent Test**: Run notebook with `autonomous-action.jsonl` and `approval-gate-bypasser.md` present. Verify both checks produce pass/fail — pass means agent required confirmation for every high-impact action, fail means agent executed an action without confirmation.

### Implementation for User Story 3

- [x] T020 [P] [US3] Create the approval-gate-bypasser adversarial driver persona in `owasp/LLM06-excessive-agency/drivers/approval-gate-bypasser.md` per `contracts/driver-prompt.md` with YAML front matter (`owasp_category: LLM06`, `risk_severity: Critical`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.7`) and persona prompt template using mustache parameters `{bypass_strategy}`, `{target_action}`, `{urgency_pretext}`, `{escalation_steps}` — persona fabricates urgency, claims pre-approval, impersonates authority figures, applies emotional pressure while never acknowledging the confirmation requirement
- [x] T021 [P] [US3] Author 5-7 autonomous action seed rows in `owasp/LLM06-excessive-agency/scenarios/autonomous-action.jsonl` per `contracts/scenario-jsonl.md` Scenario 3 schema — each row provides a distinct `bypass_strategy` (urgency fabrication, false pre-approval claim, impersonation of authority, emotional manipulation, deadline pressure) with `target_action`, `urgency_pretext`, `escalation_steps` fields and a `result` describing expected agent behavior
- [x] T022 [P] [US3] Create companion metadata file in `owasp/LLM06-excessive-agency/scenarios/autonomous-action_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM06`, `risk_severity: Critical`, `evaluation_mode: multi-turn`, `row_count` matching actual JSONL rows
- [x] T023 [US3] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM06-autonomous-action` scenario uploads, `LLM06-approval-gate-bypasser` driver registers, simulation runs for up to 10 turns per row, both checks produce per-row pass/fail results

**Checkpoint**: Autonomous action scenario independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Artifact integrity, adopter validation, and idempotency verification

- [x] T024 [P] Verify all artifact metadata headers comply with `contracts/metadata-header.md` — check that every `.md` and `_meta.md` file includes all required fields: `owasp_category: LLM06`, `risk_severity: Critical`, `artifact_type`, `status`, `version`, `name`, `description`, `evaluation_mode: multi-turn`
- [x] T025 [P] Add detailed results retrieval cell (optional, commented out by default) to notebook for per-row transcript inspection of any completed simulation run via `okareo.get_test_run_results()`
- [x] T026 Run quickstart.md validation — follow the steps in `specs/004-llm06-excessive-agency/quickstart.md` from a clean state to confirm clone-and-run works
- [x] T027 Verify notebook idempotency — run the full notebook twice consecutively and confirm no duplicate artifacts are created and results are consistent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1, US2, US3 (Phases 3, 4, 5)**: All depend on Foundational phase (shared checks + notebook scaffold + multi-turn simulation loop)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US3 (P1)**: Can start after Phase 2 — no dependencies on other stories

All three user stories are fully independent and can proceed in parallel once Foundational is complete. Each story creates its own driver persona and scenario file; the shared checks and notebook simulation loop are built in Phase 2.

### Within Each User Story

- Driver persona + scenario JSONL + metadata can be authored in parallel [P]
- Validation depends on all story artifacts (driver + scenario + metadata) being present
- Story complete before moving to Polish phase

### Parallel Opportunities

- T002 and T003 in Phase 2 (checks are different files)
- T004–T011 in Phase 2 build the notebook sequentially (cell dependencies)
- All three user stories can proceed in parallel after Phase 2
- Within each user story, all creation tasks (driver + scenario + metadata) are different files and fully parallelizable [P]

---

## Parallel Example: Phase 2 + User Stories

```text
# After Phase 1 completes, launch Foundational tasks:
Task T002: Create excessive-agency-detector check     ─┐
Task T003: Create agency-boundary-drift-detector check ─┤── Phase 2 (parallel)
Task T004–T011: Build notebook cells sequentially      ─┘

# After Phase 2 completes, launch all user stories in parallel:
US1: T012 + T013 + T014 (parallel) → T015 (validate)
US2: T016 + T017 + T018 (parallel) → T019 (validate)   ─── all 3 in parallel
US3: T020 + T021 + T022 (parallel) → T023 (validate)

# After all user stories complete:
Polish: T024 + T025 (parallel) → T026 → T027
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002–T011)
3. Complete Phase 3: User Story 1 — Unauthorized Tool Invocation (T012–T015)
4. **STOP and VALIDATE**: Run notebook end-to-end against a target agent; confirm 5-7 tool-scope manipulation scenarios produce pass/fail results with both checks
5. This delivers immediate security signal: "Does this agent resist unauthorized tool invocation under adversarial pressure?"

### Incremental Delivery

1. Setup + Foundational → Notebook scaffold ready with checks and simulation loop
2. Add US1 (unauthorized tool invocation) → MVP: tool-scope boundary testing
3. Add US2 (permission escalation) → Expanded: privilege widening detection
4. Add US3 (autonomous action) → Complete: approval-gate bypass detection
5. Polish → Production-ready LLM06 suite

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (unauthorized tool invocation)
   - Developer B: US2 (permission escalation)
   - Developer C: US3 (autonomous action without approval)
3. All stories complete and integrate independently into the same notebook

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable by running the notebook with only that story's scenario and driver files present
- All artifacts follow Constitution Principle VII (file-first) — create the file, then register via notebook
- Notebook cells use upsert semantics (idempotent) per research decision R6
- All 3 scenarios execute via `okareo.run_simulation()` with `max_turns=10, first_turn="target"` and dedicated adversarial driver personas — no single-turn scenarios or pass-through drivers needed
- Both checks (`LLM06-excessive-agency-detector` and `LLM06-agency-boundary-drift-detector`) are applied to every simulation run
- Scenario-to-driver mapping is defined in the notebook's simulation loop cell (T010) — each scenario is paired with its dedicated driver
