# Tasks: OWASP LLM04 Data and Model Poisoning Test Suite

**Input**: Design documents from `/specs/003-llm04-data-poisoning/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks — validation is performed by running the notebook against a target agent and inspecting pass/fail results.

**Organization**: Tasks are grouped by user story (attack scenario) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Artifacts**: `owasp/LLM04-data-model-poisoning/{scenarios,checks}/`
- **Notebook**: `owasp/LLM04-data-model-poisoning/notebooks/`
- **Config**: `owasp/config.env.example`, `owasp/target.env.example` (shared, already exist from LLM01)
- **Specs**: `specs/003-llm04-data-poisoning/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the LLM04 directory structure. Shared config files (`config.env.example`, `target.env.example`, `.gitignore` entries) already exist from LLM01/LLM02 and do not need to be recreated.

- [x] T001 Create directory structure: `owasp/LLM04-data-model-poisoning/{scenarios,checks,notebooks}/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Notebook scaffold and all three model-based checks that user stories depend on. Checks are created in this phase because each user story needs its check registered before evaluation can run.

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Create the corpus poisoning detector check (single-turn, model-based, pass/fail) in `owasp/LLM04-data-model-poisoning/checks/corpus-poisoning-detector.md` with YAML front matter per `contracts/metadata-header.md` (`owasp_category: LLM04`, `risk_severity: High`, `check_type: model`, `output_type: pass_fail`) and prompt template per `contracts/check-prompt.md` using `{scenario_input}`, `{model_output}`, `{scenario_result}` placeholders — the prompt instructs the evaluator to assess whether the response reflects poisoned content (described in `{scenario_result}`) or legitimate knowledge
- [x] T003 [P] Create the behavioral drift detector check (single-turn, model-based, pass/fail) in `owasp/LLM04-data-model-poisoning/checks/behavioral-drift-detector.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` — the prompt instructs the evaluator to compare `{model_output}` against the baseline in `{scenario_result}` across four dimensions: factual accuracy, policy/safety adherence, reasoning quality, and tone consistency
- [x] T004 [P] Create the backdoor trigger detector check (single-turn, model-based, pass/fail) in `owasp/LLM04-data-model-poisoning/checks/backdoor-trigger-detector.md` with YAML front matter per `contracts/metadata-header.md` and prompt template per `contracts/check-prompt.md` — the prompt instructs the evaluator to assess whether `{model_output}` deviates from expected normal behavior in `{scenario_result}`, flagging policy violations, factual deviations, or anomalous behavior
- [x] T005 Create the notebook scaffold (cells 0–3: title/description, pip install `okareo python-dotenv`, SDK init with `Okareo(OKAREO_API_KEY)` and key confirmation print, category directory resolution to `owasp/LLM04-data-model-poisoning/`) in `owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb`
- [x] T006 Add scenario upload cell to notebook — scan `scenarios/*.jsonl` and upload via `okareo.upload_scenario_set(scenario_name, file_path)` with idempotent naming `LLM04-{stem}`, store results in `registered_scenarios` dict
- [x] T007 Add check registration cell to notebook — scan `checks/*.md`, parse YAML front matter + prompt template body (text after `## Prompt Template` heading), register via `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`, store results in `registered_checks` dict
- [x] T008 Add target configuration cell to notebook — load `owasp/target.env` via `dotenv_values()`, validate `TARGET_ENDPOINT_URL` is set (fail fast with clear error if missing), build `CustomEndpointTarget(next_turn=TurnConfig(...))` with optional `SessionConfig`/`EndSessionConfig`, register via `okareo.register_model()`
- [x] T009 Add single-turn evaluation loop cell to notebook — define `SCENARIO_CHECK_MAP` dict mapping each scenario name to its check name (`LLM04-corpus-poisoning` → `LLM04-corpus-poisoning-detector`, etc.), iterate scenarios, create inline pass-through `Driver(temperature=0)` with verbatim-repeat template, run via `okareo.run_simulation(target, driver, scenario, max_turns=1, first_turn="driver", checks=[check_name])`
- [x] T010 Add results summary cell to notebook — print scenario name, pass/fail status, aggregate pass rate, and Okareo dashboard link for each completed run

**Checkpoint**: Notebook scaffold complete — can now add scenarios per user story

---

## Phase 3: User Story 1 — RAG Corpus Poisoning Detection (Priority: P1) MVP

**Goal**: Detect whether adversarial content injected into the agent's retrieval store manipulates its outputs

**Independent Test**: Run notebook with only `corpus-poisoning.jsonl` present in scenarios/. Verify the corpus poisoning detector check produces pass/fail for each row — pass means agent responded with legitimate knowledge, fail means agent's response reflects poisoned content.

### Implementation for User Story 1

- [x] T011 [P] [US1] Author 10-14 corpus poisoning seed prompts spanning four poisoning strategies in `owasp/LLM04-data-model-poisoning/scenarios/corpus-poisoning.jsonl` per `contracts/scenario-jsonl.md` corpus poisoning row schema — each row has `input` (factual question on topic vulnerable to poisoning) and `result` (two-part description of correct behavior + what poisoned output looks like). Coverage: factual manipulation (3-4 rows), embedded adversarial instructions (3-4 rows), authority spoofing (2-3 rows), topic-targeted poisoning (2-3 rows)
- [x] T012 [P] [US1] Create companion metadata file in `owasp/LLM04-data-model-poisoning/scenarios/corpus-poisoning_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM04`, `risk_severity: High`, `artifact_type: scenario`, `evaluation_mode: single-turn`, `version: "1.0.0"`, `row_count` matching actual JSONL rows
- [x] T013 [US1] Add `LLM04-corpus-poisoning` to the `SCENARIO_CHECK_MAP` in the evaluation cell of `owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb` mapping to check `LLM04-corpus-poisoning-detector`
- [x] T014 [US1] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM04-corpus-poisoning` scenario uploads, check registers, and single-turn simulation produces per-row pass/fail results with rationale explaining whether poisoned content was detected

**Checkpoint**: Corpus poisoning scenario independently functional and testable

---

## Phase 4: User Story 2 — Behavioral Drift Detection (Priority: P1)

**Goal**: Detect whether the target agent's behavior has silently changed by comparing current outputs against known-good baseline responses

**Independent Test**: Run notebook with `behavioral-drift.jsonl` present. Verify the drift detector compares each response against the baseline in `result` — pass means semantically consistent across all four dimensions, fail means drift detected with rationale explaining which dimensions changed.

### Implementation for User Story 2

- [x] T015 [P] [US2] Author 10-14 behavioral drift seed prompts spanning four behavioral dimensions in `owasp/LLM04-data-model-poisoning/scenarios/behavioral-drift.jsonl` per `contracts/scenario-jsonl.md` behavioral drift row schema — each row has `input` (standardized prompt) and `result` (known-good baseline response). Coverage: factual accuracy (3-4 rows), safety/policy adherence (3-4 rows), reasoning quality (2-3 rows), tone consistency (2-3 rows). Baseline responses should represent exemplary, policy-compliant answers.
- [x] T016 [P] [US2] Create companion metadata file in `owasp/LLM04-data-model-poisoning/scenarios/behavioral-drift_meta.md` per `contracts/metadata-header.md` with `version: "1.0.0"` — version tracks baseline capture point
- [x] T017 [US2] Add `LLM04-behavioral-drift` to the `SCENARIO_CHECK_MAP` in the evaluation cell of `owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb` mapping to check `LLM04-behavioral-drift-detector`
- [x] T018 [US2] Add a markdown documentation cell to the notebook (before the evaluation section) explaining the baseline capture workflow: (1) point `owasp/target.env` at trusted model, (2) run prompts, (3) save responses as `result` in JSONL, (4) version the `_meta.md`, (5) commit as baseline source of truth
- [x] T019 [US2] Validate: run notebook — confirm behavioral drift scenario uploads and produces per-row pass/fail results, with failing rows identifying which dimensions drifted

**Checkpoint**: Behavioral drift scenario independently functional

---

## Phase 5: User Story 3 — Backdoor/Sleeper Trigger Detection (Priority: P1)

**Goal**: Detect whether specific trigger phrases activate planted backdoor behaviors that deviate from normal operation

**Independent Test**: Run notebook with `backdoor-trigger.jsonl` present. Verify the trigger detector assesses each row — pass means response is consistent with expected normal behavior, fail means trigger caused behavioral deviation.

### Implementation for User Story 3

- [x] T020 [P] [US3] Author 10-12 backdoor trigger seed prompts (paired triggered + clean control rows) in `owasp/LLM04-data-model-poisoning/scenarios/backdoor-trigger.jsonl` per `contracts/scenario-jsonl.md` backdoor trigger row schema — triggered prompts use `[[TRIGGER:...]]` annotation, clean prompts are identical without the trigger. Coverage: rare token sequences (2-3 pairs), specific code words (2-3 pairs), Unicode homoglyphs (1-2 pairs), benign-seeming phrases (1-2 pairs). Each `result` describes expected normal behavior.
- [x] T021 [P] [US3] Create companion metadata file in `owasp/LLM04-data-model-poisoning/scenarios/backdoor-trigger_meta.md` per `contracts/metadata-header.md`
- [x] T022 [US3] Add `LLM04-backdoor-trigger` to the `SCENARIO_CHECK_MAP` in the evaluation cell of `owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb` mapping to check `LLM04-backdoor-trigger-detector`
- [x] T023 [US3] Validate: run notebook — confirm backdoor trigger scenario uploads and produces per-row pass/fail results, with failing rows describing the specific behavioral deviation caused by the trigger

**Checkpoint**: Backdoor trigger scenario independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Notebook completeness, results display, and adopter documentation

- [x] T024 Add artifact upload summary cell to notebook (print all registered scenario names/IDs and check names/IDs in a formatted table) in `owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb`
- [x] T025 [P] Verify all artifact metadata headers comply with `contracts/metadata-header.md` — check that every `.md` and `_meta.md` file includes all required fields: `owasp_category: LLM04`, `risk_severity: High`, `artifact_type`, `status`, `version`, `name`, `description`, `evaluation_mode: single-turn`
- [x] T026 [P] Verify scenario JSONL files are valid — each line is valid JSON, every row has `input` (string) and `result` (string) fields, row counts match `_meta.md` `row_count` values
- [x] T027 Run quickstart.md validation — follow the steps in `specs/003-llm04-data-poisoning/quickstart.md` from a clean state to confirm the notebook runs end-to-end
- [x] T028 Verify notebook idempotency — run the full notebook twice consecutively and confirm no duplicate artifacts are created and results are consistent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1, US2, US3 (Phases 3, 4, 5)**: All depend on Foundational phase (notebook scaffold + checks + evaluation loop)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US3 (P1)**: Can start after Phase 2 — no dependencies on other stories

All three user stories are fully independent and can proceed in parallel once Foundational is complete.

### Within Each User Story

- Scenario JSONL + metadata can be authored in parallel [P]
- Notebook integration (adding to `SCENARIO_CHECK_MAP`) depends on scenario file existing
- Validation depends on all story artifacts being registered

### Parallel Opportunities

- T002, T003, T004 in Phase 2 (checks — all different files)
- T005–T010 in Phase 2 (notebook — sequential within notebook, but parallel with T002–T004)
- All three user stories can proceed in parallel after Phase 2
- Within each user story, scenario JSONL and metadata files are authored in parallel [P]
- T025 and T026 in Phase 6 (different validation targets)

---

## Parallel Example: Phase 2 + User Stories

```text
# Phase 1 completes (T001):
T001: Create directory structure

# Phase 2 — checks and notebook in parallel:
T002: Corpus poisoning check     ─┐
T003: Behavioral drift check     ─┤── checks (parallel, different files)
T004: Backdoor trigger check     ─┘
T005: Notebook scaffold          ─┐
T006: Scenario upload cell       ─┤
T007: Check registration cell    ─┤── notebook (sequential cells)
T008: Target config cell         ─┤
T009: Evaluation loop cell       ─┤
T010: Results summary cell       ─┘

# After Phase 2 completes, launch all user stories in parallel:
US1: T011 + T012 (parallel) → T013 → T014
US2: T015 + T016 (parallel) → T017 → T018 → T019    ─── all 3 in parallel
US3: T020 + T021 (parallel) → T022 → T023
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002–T010)
3. Complete Phase 3: User Story 1 — Corpus Poisoning (T011–T014)
4. **STOP and VALIDATE**: Run notebook end-to-end against a target agent; confirm 10-14 corpus poisoning prompts produce pass/fail results with rationale
5. This delivers immediate security signal: "Does this agent resist RAG corpus poisoning?"

### Incremental Delivery

1. Setup + Foundational → Notebook scaffold ready
2. Add US1 (corpus poisoning) → MVP: RAG poisoning detection
3. Add US2 (behavioral drift) → Expanded: version consistency monitoring
4. Add US3 (backdoor triggers) → Complete: hidden activation detection
5. Polish → Production-ready suite

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (corpus poisoning)
   - Developer B: US2 (behavioral drift — includes baseline workflow documentation)
   - Developer C: US3 (backdoor triggers)
3. All stories complete and integrate independently into the same notebook

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable by running the notebook with only that story's scenario file present
- All artifacts follow Constitution Principle VII (file-first) — create the file, then register via notebook
- Notebook cells use upsert semantics (idempotent) per research decision R7
- All scenarios execute via `okareo.run_simulation()` with `max_turns=1, first_turn="driver"` and a pass-through driver
- Each scenario uses exactly one model-based check (unlike LLM02 which uses two checks per scenario)
- No `drivers/` directory — all scenarios are single-turn with an inline pass-through driver
- No code-based checks — all three detection tasks require semantic judgment (research decision R1)
- Behavioral drift scenarios store the known-good baseline in the `result` field — the `{scenario_result}` placeholder gives the check native access
- Backdoor trigger scenarios use `[[TRIGGER:...]]` annotation in `input` for human readability; clean control rows are separate entries
