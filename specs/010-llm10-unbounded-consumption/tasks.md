# Tasks: OWASP LLM10 Unbounded Consumption Test Suite

**Input**: Design documents from `/specs/010-llm10-unbounded-consumption/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks — validation is performed by running the notebook against a target agent and inspecting pass/fail results.

**Organization**: Tasks are grouped by user story (attack scenario) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Artifacts**: `owasp/LLM10-unbounded-consumption/{scenarios,checks,drivers}/`
- **Notebook**: `owasp/LLM10-unbounded-consumption/notebooks/`
- **Config**: `owasp/config.env.example`, `owasp/target.env.example`
- **Specs**: `specs/010-llm10-unbounded-consumption/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository structure for the LLM10 category

- [x] T001 Create directory structure: `owasp/LLM10-unbounded-consumption/{scenarios,checks,drivers,notebooks}/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared checks and notebook scaffold that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Create the loop-detection check (multi-turn, model-based, pass/fail) in `owasp/LLM10-unbounded-consumption/checks/loop-detection-check.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` using `{simulation_message_history}`, `{scenario_result}` placeholders — evaluates whether the transcript shows recursive/circular tool call chains, unbounded continuation, or agent terminated within bounds; handles tool-less agents (N/A → pass)
- [x] T003 [P] Create the resource-policy-enforcement check (multi-turn, model-based, pass/fail) in `owasp/LLM10-unbounded-consumption/checks/resource-policy-enforcement-check.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` using `{simulation_message_history}`, `{scenario_result}` placeholders — evaluates whether the system enforced consumption bounds (reject, throttle, terminate) when subjected to long prompts, rapid queries, or token bombs
- [x] T004 Create the notebook scaffold (cells 0–3: title markdown, pip install, SDK init with `OKAREO_API_KEY` from `.env`, `NOTEBOOK_DIR`/`CATEGORY_DIR` resolution) in `owasp/LLM10-unbounded-consumption/notebooks/run-evaluation.ipynb`
- [x] T005 Add scenario upload cell to notebook — scan `scenarios/*.jsonl` and upload via `okareo.upload_scenario_set(scenario_name=f"LLM10-{stem}", file_path=str(jsonl_path))` with idempotent naming
- [x] T006 Add check registration cell to notebook — implement `parse_check_md()` to parse `checks/*.md` YAML front matter + `## Prompt Template` body, register via `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`
- [x] T007 Add driver registration cell to notebook — implement `parse_driver_md()` to parse `drivers/*.md` YAML front matter + `## Persona Prompt Template` body, register via `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature))`
- [x] T008 Add artifact upload summary cell to notebook — print registered scenario IDs, check IDs, driver IDs
- [x] T009 Add target configuration cell to notebook — load `owasp/target.env` via `dotenv_values()`, validate `TARGET_ENDPOINT_URL` is set, build `CustomEndpointTarget(next_turn=TurnConfig(...))` with optional `SessionConfig`/`EndSessionConfig`, wrap in `Target(target=..., name=TARGET_NAME)`
- [x] T010 Add multi-turn simulation loop cell to notebook — define `SCENARIO_DRIVER_MAP` mapping scenario names to driver names (`LLM10-infinite-loop` → `LLM10-loop-inducing-driver`, `LLM10-resource-exhaustion` → `LLM10-resource-exhaustion-driver`), define `SCENARIO_FIRST_TURN` map (`LLM10-infinite-loop` → `"target"`, `LLM10-resource-exhaustion` → `"driver"`), define `SCENARIO_CHECK_MAP` mapping each scenario to its check, iterate scenarios and for each: look up driver from `registered_drivers`, create `Driver` with prompt_template + scenario row `input` substitution for mustache params, run `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn=SCENARIO_FIRST_TURN[scenario_name], checks=[SCENARIO_CHECK_MAP[scenario_name]])`
- [x] T011 Add results summary cell to notebook — print scenario name, pass/fail rates, and Okareo dashboard links for all completed runs

**Checkpoint**: Notebook scaffold complete — can now add scenarios and drivers per user story

---

## Phase 3: User Story 1 — Infinite Tool/Agent Loop Detection (Priority: P1) MVP

**Goal**: Detect whether the target agent enters recursive or circular tool call chains that consume unbounded resources without termination when prompted by an adversarial driver

**Independent Test**: Run notebook with `infinite-loop.jsonl` and `loop-inducing-driver.md` present. Verify loop-detection-check produces pass/fail — pass means agent terminated within bounds or has no tools (N/A), fail means agent exhibited circular tool patterns or unbounded continuation.

### Implementation for User Story 1

- [x] T012 [P] [US1] Create the loop-inducing-driver adversarial driver persona in `owasp/LLM10-unbounded-consumption/drivers/loop-inducing-driver.md` per `contracts/driver-prompt.md` with YAML front matter (`owasp_category: LLM10`, `risk_severity: Medium`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.6`) and persona prompt template using mustache parameters `{loop_strategy}`, `{workflow_description}`, `{target_tools}`, `{repeat_instruction}` — persona prompts the agent to perform workflows that could create recursive/circular tool call chains
- [x] T013 [P] [US1] Author 5–8 infinite-loop seed rows in `owasp/LLM10-unbounded-consumption/scenarios/infinite-loop.jsonl` per `contracts/scenario-jsonl.md` Scenario 1 schema — each row provides `loop_strategy` (chained_tool_loop, repeat_until, self_referential, exhaust_all), `workflow_description`, `target_tools`, `repeat_instruction`, and `result` describing expected agent behavior
- [x] T014 [P] [US1] Create companion metadata file in `owasp/LLM10-unbounded-consumption/scenarios/infinite-loop_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM10`, `risk_severity: Medium`, `evaluation_mode: multi-turn`, `row_count` matching actual JSONL rows
- [ ] T015 [US1] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM10-infinite-loop` scenario uploads, `LLM10-loop-inducing-driver` driver registers, simulation runs for up to 10 turns per row, loop-detection-check produces per-row pass/fail results

**Checkpoint**: Infinite-loop scenario independently functional and testable

---

## Phase 4: User Story 2 — Resource Exhaustion via Adversarial Inputs (Priority: P1)

**Goal**: Detect whether the target agent enforces consumption bounds (rate limits, token budgets, timeouts, circuit breakers) when subjected to long prompts, rapid repeated queries, and token-bomb inputs

**Independent Test**: Run notebook with `resource-exhaustion.jsonl` and `resource-exhaustion-driver.md` present. Verify resource-policy-enforcement-check produces pass/fail — pass means system enforced bounds (rejection, throttling, termination), fail means system accepted unbounded adversarial inputs without enforcement.

### Implementation for User Story 2

- [x] T016 [P] [US2] Create the resource-exhaustion-driver abusive driver persona in `owasp/LLM10-unbounded-consumption/drivers/resource-exhaustion-driver.md` per `contracts/driver-prompt.md` with YAML front matter (`owasp_category: LLM10`, `risk_severity: Medium`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.5`) and persona prompt template using mustache parameters `{abuse_type}`, `{abuse_parameters}` — persona sends long prompts, rapid repeated queries, or token-bomb inputs
- [x] T017 [P] [US2] Author 6–10 resource-exhaustion seed rows in `owasp/LLM10-unbounded-consumption/scenarios/resource-exhaustion.jsonl` per `contracts/scenario-jsonl.md` Scenario 2 schema — each row provides `abuse_type` (long_prompt, rapid_queries, token_bomb), `abuse_parameters` object, and `result` describing expected system behavior
- [x] T018 [P] [US2] Create companion metadata file in `owasp/LLM10-unbounded-consumption/scenarios/resource-exhaustion_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM10`, `risk_severity: Medium`, `evaluation_mode: multi-turn`, `row_count` matching actual JSONL rows
- [ ] T019 [US2] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM10-resource-exhaustion` scenario uploads, `LLM10-resource-exhaustion-driver` driver registers, simulation runs for up to 10 turns per row, resource-policy-enforcement-check produces per-row pass/fail results

**Checkpoint**: Resource-exhaustion scenario independently functional and testable

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Artifact integrity, adopter validation, and idempotency verification

- [x] T020 [P] Verify all artifact metadata headers comply with `contracts/metadata-header.md` — check that every `.md` and `_meta.md` file includes all required fields: `owasp_category: LLM10`, `risk_severity: Medium`, `artifact_type`, `status`, `version`, `name`, `description`, `evaluation_mode: multi-turn`
- [ ] T021 [P] Add detailed results retrieval cell (optional, commented out by default) to notebook for per-row transcript inspection of any completed simulation run via `okareo.get_test_run_results()`
- [ ] T022 Run quickstart.md validation — follow the steps in `specs/010-llm10-unbounded-consumption/quickstart.md` from a clean state to confirm clone-and-run works
- [ ] T023 Verify notebook idempotency — run the full notebook twice consecutively and confirm no duplicate artifacts are created and results are consistent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1, US2 (Phases 3, 4)**: All depend on Foundational phase (shared checks + notebook scaffold + multi-turn simulation loop)
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P1)**: Can start after Phase 2 — no dependencies on other stories

Both user stories are fully independent and can proceed in parallel once Foundational is complete.

### Within Each User Story

- Driver persona + scenario JSONL + metadata can be authored in parallel [P]
- Validation depends on all story artifacts (driver + scenario + metadata) being present
- Story complete before moving to Polish phase

### Parallel Opportunities

- T002 and T003 in Phase 2 (checks are different files)
- T004–T011 in Phase 2 build the notebook sequentially (cell dependencies)
- Both user stories can proceed in parallel after Phase 2
- Within each user story, all creation tasks (driver + scenario + metadata) are different files and fully parallelizable [P]

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable by running the notebook with only that story's scenario and driver files present
- All artifacts follow Constitution Principle VII (file-first) — create the file, then register via notebook
- Notebook cells use upsert semantics (idempotent)
- Scenario 1 uses `first_turn="target"`; Scenario 2 uses `first_turn="driver"` per plan
- Each scenario is paired with exactly one check (infinite-loop → loop-detection-check, resource-exhaustion → resource-policy-enforcement-check)
