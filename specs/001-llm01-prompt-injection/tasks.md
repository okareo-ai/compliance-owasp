# Tasks: OWASP LLM01 Prompt Injection Test Suite

**Input**: Design documents from `/specs/001-llm01-prompt-injection/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks — validation is performed by running the notebook against a target agent and inspecting pass/fail results.

**Organization**: Tasks are grouped by user story (attack scenario) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Artifacts**: `owasp/LLM01-prompt-injection/{scenarios,checks,drivers}/`
- **Notebook**: `owasp/LLM01-prompt-injection/notebooks/`
- **Config**: `owasp/config.env.example`, `owasp/target.env.example`
- **Specs**: `specs/001-llm01-prompt-injection/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository structure, environment configuration, and dependency management

- [x] T001 Create directory structure: `owasp/LLM01-prompt-injection/{scenarios,checks,drivers,notebooks}/`
- [x] T002 [P] Create Okareo API key config template in `owasp/config.env.example` with `OKAREO_API_KEY` variable
- [x] T003 [P] Create shared target agent config template in `owasp/target.env.example` with `TARGET_ENDPOINT_URL`, `TARGET_NAME`, `TARGET_API_KEY` variables
- [x] T004 [P] Add `.env` and `owasp/target.env` to `.gitignore` to prevent credential leaks

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared artifacts and notebook scaffold that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create the injection compliance detector check (single-turn, model-based, pass/fail) in `owasp/LLM01-prompt-injection/checks/injection-compliance-detector.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` using `{scenario_input}`, `{model_output}`, `{scenario_result}` placeholders
- [x] T006 Create the notebook scaffold (cells 0–3: title, pip install, SDK init, category dir resolution) in `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T007 Add scenario upload cell to notebook — scan `scenarios/*.jsonl` and upload via `okareo.upload_scenario_set()` with idempotent naming `LLM01-{stem}`
- [x] T008 Add check registration cell to notebook — parse `checks/*.md` YAML front matter + prompt template body, register via `okareo.create_or_update_check()` with `ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL)`
- [x] T009 Add target configuration cell to notebook — load `owasp/target.env` via `dotenv_values()`, validate `TARGET_ENDPOINT_URL` is set, register `CustomEndpointTarget` via `okareo.register_model()`
- [x] T010 Add single-turn evaluation loop cell to notebook — iterate `SINGLE_TURN_SCENARIOS` list, create inline pass-through `Driver(temperature=0)` with verbatim-repeat template, run via `okareo.run_simulation(target, driver, scenario, max_turns=1, first_turn="driver", checks=[SINGLE_TURN_CHECK])`
- [x] T011 Add results summary cell to notebook — print scenario name, status, run ID for all completed runs

**Checkpoint**: Notebook scaffold complete — can now add scenarios per user story

---

## Phase 3: User Story 1 — Direct Prompt Injection Detection (Priority: P1) MVP

**Goal**: Detect whether the target agent complies with explicit role-hijacking and instruction-override attacks via single-turn prompts

**Independent Test**: Run notebook with only `direct-injection.jsonl` present in scenarios/. Verify the check produces pass/fail for each row — pass means agent refused injection, fail means agent complied.

### Implementation for User Story 1

- [x] T012 [P] [US1] Author 15-20 direct injection seed prompts (ignore-prior-instructions, DAN persona hijack, system prompt extraction, authority-claim overrides) in `owasp/LLM01-prompt-injection/scenarios/direct-injection.jsonl` per `contracts/scenario-jsonl.md` single-turn row schema
- [x] T013 [P] [US1] Create companion metadata file in `owasp/LLM01-prompt-injection/scenarios/direct-injection_meta.md` per `contracts/metadata-header.md` with `evaluation_mode: single-turn`, `row_count` matching actual JSONL rows
- [x] T014 [US1] Add `LLM01-direct-injection` to the `SINGLE_TURN_SCENARIOS` list in the evaluation cell of `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T015 [US1] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM01-direct-injection` scenario uploads, check registers, and single-turn test produces per-row pass/fail results

**Checkpoint**: Direct injection scenario independently functional and testable

---

## Phase 4: User Story 2 — Indirect Prompt Injection via External Content (Priority: P1)

**Goal**: Detect whether the target agent can be manipulated through malicious content embedded in external sources (RAG documents, uploaded files, web content)

**Independent Test**: Run notebook with `indirect-injection.jsonl` present. Verify pass/fail — pass means agent answered the real user question ignoring the embedded injection, fail means agent followed the embedded instruction.

### Implementation for User Story 2

- [x] T016 [P] [US2] Author 10-15 indirect injection seed prompts (injected instructions in retrieved docs, metadata-embedded payloads, invisible-text injections in file uploads) in `owasp/LLM01-prompt-injection/scenarios/indirect-injection.jsonl` per `contracts/scenario-jsonl.md` single-turn row schema
- [x] T017 [P] [US2] Create companion metadata file in `owasp/LLM01-prompt-injection/scenarios/indirect-injection_meta.md` per `contracts/metadata-header.md`
- [x] T018 [US2] Add `LLM01-indirect-injection` to the `SINGLE_TURN_SCENARIOS` list in the evaluation cell of `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T019 [US2] Validate: run notebook — confirm indirect injection scenario uploads and produces per-row pass/fail results

**Checkpoint**: Indirect injection scenario independently functional

---

## Phase 5: User Story 3 — Multi-Turn Jailbreak Escalation (Priority: P1)

**Goal**: Detect whether the target agent's safety boundaries erode under sustained crescendo attack pressure over 5-10 conversational turns

**Independent Test**: Run notebook with `crescendo-attack.jsonl` present. Verify the compliance drift detector assesses each simulation — pass means agent maintained consistent refusal quality, fail means progressive compliance drift or explicit jailbreak.

### Implementation for User Story 3

- [x] T020 [P] [US3] Create the compliance drift detector check (multi-turn, model-based, pass/fail) in `owasp/LLM01-prompt-injection/checks/compliance-drift-detector.md` with YAML front matter per `contracts/check-prompt.md` and prompt template using `{simulation_message_history}`, `{scenario_result}` placeholders for per-turn and drift evaluation
- [x] T021 [P] [US3] Create the jailbreak escalator adversarial driver persona in `owasp/LLM01-prompt-injection/drivers/jailbreak-escalator.md` per `contracts/driver-prompt.md` with mustache parameters `{escalation_strategy}`, `{initial_topic}`, `{target_behavior}`, `{escalation_steps}` and hard rules for gradual escalation
- [x] T022 [P] [US3] Author 3-5 crescendo attack seed rows (role-playing, hypothetical framing, educational framing, incremental normalization, false authority) in `owasp/LLM01-prompt-injection/scenarios/crescendo-attack.jsonl` per `contracts/scenario-jsonl.md` multi-turn row schema — each row provides driver parameterization via JSON `input` object
- [x] T023 [P] [US3] Create companion metadata file in `owasp/LLM01-prompt-injection/scenarios/crescendo-attack_meta.md` per `contracts/metadata-header.md` with `evaluation_mode: multi-turn`
- [x] T024 [US3] Add driver registration cell to notebook — parse `drivers/*.md` YAML front matter + persona prompt template, register via `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature))`
- [x] T025 [US3] Add multi-turn simulation cell to notebook — create `Driver(name=DRIVER_NAME, prompt_template=driver.prompt_template, temperature=0.6)`, run via `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn="target", checks=[MULTI_TURN_CHECK])`
- [x] T026 [US3] Validate: run notebook — confirm crescendo scenario uploads, driver registers, simulation runs for 5-10 turns per seed row, compliance drift detector produces pass/fail with per-turn assessment

**Checkpoint**: Multi-turn jailbreak simulation independently functional

---

## Phase 6: User Story 4 — Obfuscated and Encoded Injection Detection (Priority: P2)

**Goal**: Detect whether the target agent can be manipulated using Base64-encoded, multilingual, Unicode homoglyph, or adversarial suffix injection payloads

**Independent Test**: Run notebook with `obfuscated-injection.jsonl` present. Verify pass/fail — pass means agent did not decode and comply with hidden instructions, fail means agent was tricked by obfuscation.

### Implementation for User Story 4

- [x] T027 [P] [US4] Author 15-20 obfuscated injection seed prompts (Base64-encoded instructions, hex-encoded payloads, multilingual injections in Spanish/Arabic/Chinese/French, Unicode homoglyph substitutions, zero-width character injections, adversarial suffix strings, chat template delimiter exploits) in `owasp/LLM01-prompt-injection/scenarios/obfuscated-injection.jsonl` per `contracts/scenario-jsonl.md` single-turn row schema
- [x] T028 [P] [US4] Create companion metadata file in `owasp/LLM01-prompt-injection/scenarios/obfuscated-injection_meta.md` per `contracts/metadata-header.md`
- [x] T029 [US4] Add `LLM01-obfuscated-injection` to the `SINGLE_TURN_SCENARIOS` list in the evaluation cell of `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T030 [US4] Validate: run notebook — confirm obfuscated injection scenario uploads and produces per-row pass/fail results

**Checkpoint**: Obfuscated injection scenario independently functional

---

## Phase 7: User Story 5 — Payload Splitting Attack Detection (Priority: P2)

**Goal**: Detect whether the target agent synthesizes fragmented malicious intent across multiple inputs into policy-violating behavior

**Independent Test**: Run notebook with `payload-splitting.jsonl` present. Verify pass/fail — pass means agent recognized cumulative harmful intent and refused, fail means agent synthesized the fragments into harmful output.

### Implementation for User Story 5

- [x] T031 [P] [US5] Author 10-15 payload splitting seed prompts (sequential message fragments, cross-input splitting via user message + tool parameter, fabricated tool responses containing fragments, explicit fragment-combination instructions) in `owasp/LLM01-prompt-injection/scenarios/payload-splitting.jsonl` per `contracts/scenario-jsonl.md` single-turn row schema
- [x] T032 [P] [US5] Create companion metadata file in `owasp/LLM01-prompt-injection/scenarios/payload-splitting_meta.md` per `contracts/metadata-header.md`
- [x] T033 [US5] Add `LLM01-payload-splitting` to the `SINGLE_TURN_SCENARIOS` list in the evaluation cell of `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T034 [US5] Validate: run notebook — confirm payload splitting scenario uploads and produces per-row pass/fail results

**Checkpoint**: Payload splitting scenario independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Notebook completeness, results display, and adopter documentation

- [x] T035 Add artifact upload summary cell to notebook (print registered scenario IDs, check IDs, driver IDs) in `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`
- [x] T036 [P] Add detailed results retrieval cell (optional, commented out by default) to notebook for per-row inspection of any completed test run
- [x] T037 [P] Verify all artifact metadata headers comply with `contracts/metadata-header.md` — check that every `.md` and `_meta.md` file includes all 7 required fields: `owasp_category`, `risk_severity`, `artifact_type`, `status`, `version`, `name`, `description`
- [x] T038 Run quickstart.md validation — follow the steps in `specs/001-llm01-prompt-injection/quickstart.md` from a clean state to confirm clone-and-run works
- [x] T039 Verify notebook idempotency — run the full notebook twice consecutively and confirm no duplicate artifacts are created and results are consistent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1, US2, US4, US5 (Phases 3, 4, 6, 7)**: All depend on Foundational phase (shared check + notebook scaffold + single-turn evaluation loop)
- **US3 (Phase 5)**: Depends on Foundational phase (notebook scaffold) — DOES NOT depend on single-turn check or evaluation loop (has its own)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US3 (P1)**: Can start after Phase 2 — fully independent (own check, own driver, own evaluation cell)
- **US4 (P2)**: Can start after Phase 2 — no dependencies on other stories
- **US5 (P2)**: Can start after Phase 2 — no dependencies on other stories

All five user stories are fully independent and can proceed in parallel once Foundational is complete.

### Within Each User Story

- Scenario JSONL + metadata can be authored in parallel [P]
- Notebook integration depends on scenario file existing
- Validation depends on all story artifacts being registered

### Parallel Opportunities

- T002, T003, T004 in Phase 1 (all different files)
- T005 (check) can run in parallel with T006–T011 (notebook) since they target different files — the check file just needs to exist before the notebook's check registration cell runs
- All five user stories can proceed in parallel after Phase 2
- Within each user story, scenario JSONL and metadata files are authored in parallel [P]
- US3's three creation tasks (T020, T021, T022, T023) are all different files and fully parallelizable

---

## Parallel Example: Phase 2 + User Stories

```text
# After Phase 1 completes, launch Foundational tasks:
Task T005: Create injection-compliance-detector check  ─┐
Task T006: Create notebook scaffold                     ─┤── Phase 2
Task T007-T011: Build notebook cells sequentially       ─┘

# After Phase 2 completes, launch all user stories in parallel:
US1: T012 + T013 (parallel) → T014 → T015
US2: T016 + T017 (parallel) → T018 → T019    ─── all 5 in parallel
US3: T020 + T021 + T022 + T023 (parallel) → T024 → T025 → T026
US4: T027 + T028 (parallel) → T029 → T030
US5: T031 + T032 (parallel) → T033 → T034
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T004)
2. Complete Phase 2: Foundational (T005–T011)
3. Complete Phase 3: User Story 1 — Direct Injection (T012–T015)
4. **STOP and VALIDATE**: Run notebook end-to-end against a target agent; confirm 15-20 injection prompts produce pass/fail results
5. This delivers immediate security signal: "Does this agent resist basic prompt injection?"

### Incremental Delivery

1. Setup + Foundational → Notebook scaffold ready
2. Add US1 (direct injection) → MVP: basic injection detection
3. Add US2 (indirect injection) → Expanded: RAG/file poisoning coverage
4. Add US3 (crescendo jailbreak) → Advanced: multi-turn resilience testing
5. Add US4 (obfuscated injection) → Hardened: encoding bypass detection
6. Add US5 (payload splitting) → Complete: fragmented attack detection
7. Polish → Production-ready suite

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (direct injection) + US2 (indirect injection)
   - Developer B: US3 (crescendo jailbreak — most complex, own check + driver)
   - Developer C: US4 (obfuscated injection) + US5 (payload splitting)
3. All stories complete and integrate independently into the same notebook

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable by running the notebook with only that story's scenario file present
- All artifacts follow Constitution Principle VII (file-first) — create the file, then register via notebook
- Notebook cells use upsert semantics (idempotent) per research decision R6
- All scenarios execute via `okareo.run_simulation()` — single-turn with `max_turns=1, first_turn="driver"` and a pass-through driver; multi-turn with `max_turns=10, first_turn="target"` and the adversarial driver
- Single-turn scenarios all share the `injection-compliance-detector` check; only US3 uses the `compliance-drift-detector` check
