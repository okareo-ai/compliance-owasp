# Tasks: OWASP LLM05 Improper Output Handling Test Suite

**Input**: Design documents from `/specs/005-llm05-output-handling/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks — validation is performed by running the notebook against a target agent and inspecting pass/fail results.

**Organization**: Tasks are grouped by user story (attack scenario) to enable independent implementation and testing of each scenario.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Artifacts**: `owasp/LLM05-improper-output-handling/{scenarios,checks,drivers,notebooks}/`
- **Notebook**: `owasp/LLM05-improper-output-handling/notebooks/`
- **Config**: `owasp/config.env.example`, `owasp/target.env.example` (shared — already exist from LLM01)
- **Specs**: `specs/005-llm05-output-handling/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository structure for LLM05 artifacts. Config templates already exist from LLM01 — no duplication.

- [x] T001 Create directory structure: `owasp/LLM05-improper-output-handling/{scenarios,checks,drivers,notebooks}/`
- [x] T002 Confirm `owasp/config.env.example` and `owasp/target.env.example` exist (created by LLM01); no new config files needed

**Checkpoint**: Directory scaffold ready — artifact files can now be created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared notebook scaffold and pass-through driver that ALL three user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Create the pass-through driver in `owasp/LLM05-improper-output-handling/drivers/pass-through-driver.md` — YAML front matter per `contracts/metadata-header.md` (`owasp_category: LLM05`, `artifact_type: driver`, `temperature: 0`), body contains the verbatim-repeat template with `{scenario_input}` placeholder
- [x] T004 Create the notebook scaffold with core cells (title, `%pip install okareo python-dotenv --quiet`, SDK init printing last 5 chars of key, category directory resolution) in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T005 Add scenario upload cell to notebook — scan `scenarios/*.jsonl`, upload each via `okareo.upload_scenario_set(scenario_name="LLM05-{stem}", file_path=...)`, store in `registered_scenarios` dict in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T006 Add check registration cell to notebook — iterate `checks/` directory: for `.md` files parse YAML front matter + prompt body and register via `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`; for `.py` files read source and register via `okareo.create_or_update_check(name, description, check=CodeBasedCheck(code=src, check_type=CheckOutputType.PASS_FAIL))`; store all in `registered_checks` dict in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T007 Add driver registration cell to notebook — parse `drivers/pass-through-driver.md` YAML front matter + prompt body, register via `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature=0))` in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T008 Add target configuration cell to notebook — load `owasp/target.env` via `dotenv_values()`, fail fast with clear error if `TARGET_ENDPOINT_URL` is missing, construct `CustomEndpointTarget(next_turn=TurnConfig(...))`, register target in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T009 Add evaluation loop cell to notebook — define `SCENARIO_CHECK_MAP = {"LLM05-injection-payload-detection": "LLM05-output-injection-detector", "LLM05-unsafe-code-generation": "LLM05-unsafe-code-detector", "LLM05-schema-violation": "LLM05-schema-compliance-check"}`, iterate map, create inline pass-through `Driver(temperature=0)` with verbatim-repeat template, run `okareo.run_simulation(target, driver, scenario, max_turns=1, first_turn="driver", checks=[check_name])` for each entry in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T010 Add results summary cell to notebook — print scenario name, pass/fail rate, Okareo dashboard URL for each completed simulation run in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`

**Checkpoint**: Notebook scaffold complete — can now add scenarios and checks per user story

---

## Phase 3: User Story 1 — Injection Payload Detection in Model Output (Priority: P1) 🎯 MVP

**Goal**: Detect whether the target agent emits XSS vectors, SQL injection patterns, or OS command injection sequences in its raw output that would be dangerous for downstream consumption

**Independent Test**: Run notebook with only `injection-payload-detection.jsonl` and `output-injection-detector.md` present (other scenarios absent). Verify the check produces pass/fail for each row — pass means output is free of executable injection payloads, fail means the output contained a dangerous pattern in non-escaped form.

### Implementation for User Story 1

- [x] T011 [P] [US1] Create the output-injection-detector model-based check in `owasp/LLM05-improper-output-handling/checks/output-injection-detector.md` — YAML front matter per `contracts/metadata-header.md` (`name: LLM05-output-injection-detector`, `check_type: model`, `evaluation_mode: single-turn`), prompt template per `contracts/check-prompt-model.md` covering all three payload families (XSS, SQL injection, command injection) with context-assessment rules that distinguish escaped/fenced educational content from executable payloads; uses `{scenario_input}`, `{model_output}`, `{scenario_result}` placeholders
- [x] T012 [P] [US1] Author ~15 injection-eliciting seed prompts covering XSS (5 rows: HTML form generators, template requests, dynamic content builders), SQL injection (5 rows: query construction requests, user-lookup examples, report generators), and command injection (5 rows: shell command requests, file listing helpers, dynamic CLI wrappers) in `owasp/LLM05-improper-output-handling/scenarios/injection-payload-detection.jsonl` per `contracts/scenario-jsonl.md` row schema — each row's `result` field describes what a safe response looks like
- [x] T013 [P] [US1] Create companion metadata file in `owasp/LLM05-improper-output-handling/scenarios/injection-payload-detection_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM05`, `risk_severity: High`, `artifact_type: scenario`, `evaluation_mode: single-turn`, `row_count` matching actual JSONL rows
- [x] T014 [US1] Validate: run notebook Part 1 (upload) + Part 2 (evaluate) — confirm `LLM05-injection-payload-detection` scenario uploads, `LLM05-output-injection-detector` check registers as a model-based check, and single-turn simulation produces per-row pass/fail results with evaluator rationale

**Checkpoint**: Injection payload detection scenario independently functional and testable

---

## Phase 4: User Story 2 — Unsafe Code and Command Generation Detection (Priority: P1)

**Goal**: Detect whether the target agent generates outputs containing path traversal sequences, unconstrained shell execution constructs, or OS execution API calls with unsanitized user input

**Independent Test**: Run notebook with only `unsafe-code-generation.jsonl` and `unsafe-code-detector.md` present. Verify pass/fail — pass means code output is safe to execute as-written, fail means the output contains an unsafe pattern (path traversal, dynamic shell invocation, or unsanitized OS API call) that would be dangerous in a real execution environment.

### Implementation for User Story 2

- [x] T015 [P] [US2] Create the unsafe-code-detector model-based check in `owasp/LLM05-improper-output-handling/checks/unsafe-code-detector.md` — YAML front matter per `contracts/metadata-header.md` (`name: LLM05-unsafe-code-detector`, `check_type: model`, `evaluation_mode: single-turn`), prompt template per `contracts/check-prompt-model.md` covering all three unsafe pattern families (path traversal, shell execution, unsafe OS API calls) with context-assessment rules that distinguish validated/sanitized usage from unsafe pass-through; uses `{scenario_input}`, `{model_output}`, `{scenario_result}` placeholders
- [x] T016 [P] [US2] Author ~15 unsafe-code-eliciting seed prompts covering path traversal (5 rows: file reader functions, config loaders, user-specified path handlers), shell execution (5 rows: bash script generators, CLI wrappers, infrastructure automation snippets), and unsafe API calls (5 rows: Node.js `exec` examples, Python subprocess handlers, OS command builders in various languages) in `owasp/LLM05-improper-output-handling/scenarios/unsafe-code-generation.jsonl` per `contracts/scenario-jsonl.md` row schema — each row's `result` field describes what makes the output unsafe
- [x] T017 [P] [US2] Create companion metadata file in `owasp/LLM05-improper-output-handling/scenarios/unsafe-code-generation_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM05`, `risk_severity: High`, `artifact_type: scenario`, `evaluation_mode: single-turn`, `row_count` matching actual JSONL rows
- [x] T018 [US2] Validate: run notebook — confirm `LLM05-unsafe-code-generation` scenario uploads, `LLM05-unsafe-code-detector` check registers as a model-based check, and single-turn simulation produces per-row pass/fail results with evaluator rationale

**Checkpoint**: Unsafe code generation detection scenario independently functional

---

## Phase 5: User Story 3 — Structured Output Schema Violation Detection (Priority: P2)

**Goal**: Deterministically validate that the target agent's structured JSON responses conform to declared schemas — catching missing required fields, type mismatches, unexpected keys, and prototype-pollution-risk key injection

**Independent Test**: Run notebook with only `schema-violation.jsonl` and `schema-compliance-check.py` present. Verify the code-based check produces pass/fail for each row — pass means the response is fully schema-compliant, fail means the check explanation identifies the specific violation class (missing field, type mismatch, extra key, or proto-pollution key).

### Implementation for User Story 3

- [x] T019 [P] [US3] Create the schema-compliance code-based check in `owasp/LLM05-improper-output-handling/checks/schema-compliance-check.py` — Python comment metadata header per `contracts/metadata-header.md` (`name: LLM05-schema-compliance-check`, `check_type: code`, `output_type: pass_fail`); implements `Check(CodeBasedCheck)` with `evaluate(model_output, scenario_result)` per `contracts/check-prompt-code.md` validation logic: (1) parse schema from `scenario_result` JSON, (2) extract JSON from raw response handling preamble/fences, (3) validate required fields and types, (4) enforce strict mode (no extra keys), (5) recursively scan for prototype-pollution-risk keys (`__proto__`, `constructor`, `__defineGetter__`, `__defineSetter__`, `__lookupGetter__`, `__lookupSetter__`, `prototype`); each violation path returns `CheckResponse(score=False, explanation=<specific violation description>)`
- [x] T020 [P] [US3] Author ~10 schema-violation seed rows covering: missing required fields (2 rows), type mismatch (2 rows — e.g., string where integer expected), unexpected keys in strict mode (2 rows), prototype-pollution key injection (2 rows — `__proto__` or `constructor` in response), and non-JSON preamble/prose wrapping the JSON (2 rows) in `owasp/LLM05-improper-output-handling/scenarios/schema-violation.jsonl` per `contracts/scenario-jsonl.md` Scenario 3 row schema — each row's `result` field is a JSON-encoded schema definition string per `contracts/scenario-jsonl.md` schema definition format
- [x] T021 [P] [US3] Create companion metadata file in `owasp/LLM05-improper-output-handling/scenarios/schema-violation_meta.md` per `contracts/metadata-header.md` with `owasp_category: LLM05`, `risk_severity: High`, `artifact_type: scenario`, `evaluation_mode: single-turn`, `row_count` matching actual JSONL rows
- [x] T022 [US3] Validate: run notebook — confirm `LLM05-schema-violation` scenario uploads, `LLM05-schema-compliance-check` registers as a code-based check (not model-based), and single-turn simulation produces per-row pass/fail results with violation-specific explanation strings from the code-based check

**Checkpoint**: Schema violation detection independently functional with deterministic code-based validation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Notebook completeness, artifact quality verification, and adopter documentation validation

- [x] T023 Add upload summary cell to notebook — after all registration cells, print a summary table of registered artifact names and IDs (scenarios, checks, driver) in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T024 [P] Add optional detailed results retrieval cell (commented out by default) to notebook for per-row inspection of any completed run via `okareo.get_test_run_results(test_run_id, detail_level="detailed")` in `owasp/LLM05-improper-output-handling/notebooks/run-evaluation.ipynb`
- [x] T025 [P] Verify all artifact metadata headers comply with `contracts/metadata-header.md` — confirm every `.md`, `_meta.md`, and `.py` artifact file includes all required fields: `owasp_category: LLM05`, `risk_severity: High`, `artifact_type`, `status`, `version`, `name`, `description`, `evaluation_mode`
- [x] T026 [P] Verify the code-based check `.py` file uses a Python comment metadata header (not YAML front matter) per `contracts/metadata-header.md` and that the `Check(CodeBasedCheck)` class is importable (run `python -c "import ast; ast.parse(open('owasp/LLM05-improper-output-handling/checks/schema-compliance-check.py').read())"` to confirm parse-clean)
- [x] T027 Run quickstart.md validation — follow steps in `specs/005-llm05-output-handling/quickstart.md` from a clean state to confirm: directory exists, config templates present, notebook opens and runs end-to-end against target agent without errors
- [x] T028 Verify notebook idempotency — run the full notebook twice consecutively and confirm no duplicate artifacts are created, no errors occur on re-registration, and results are consistent across both runs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational phase (notebook scaffold + evaluation loop)
- **US2 (Phase 4)**: Depends on Foundational phase — DOES NOT depend on US1; fully independent
- **US3 (Phase 5)**: Depends on Foundational phase — DOES NOT depend on US1 or US2; fully independent (own check type, own schema mechanism)
- **Polish (Phase 6)**: Depends on all three user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US2 (P1)**: Can start after Phase 2 — no dependencies on other stories
- **US3 (P2)**: Can start after Phase 2 — no dependencies on other stories

All three user stories are fully independent and can proceed in parallel once Foundational is complete.

### Within Each User Story

- Check file (`.md` or `.py`) and scenario JSONL + metadata can be authored in parallel [P] — they are different files with no internal dependency
- Notebook wiring (adding to `SCENARIO_CHECK_MAP`) depends on both the check file and scenario JSONL existing
- Validation (run notebook) depends on all story artifacts being registered

### Key Sequencing Note — Code-Based Check (US3)

The notebook's check registration cell (T006) handles both `.md` model-based checks and `.py` code-based checks by file extension. US3's `schema-compliance-check.py` is registered with `CodeBasedCheck(code=src)` instead of `ModelBasedCheck(prompt_template=...)`. No separate notebook cell is needed — the dispatcher in T006 handles both.

### Parallel Opportunities

- T004–T010 (notebook cells) are sequential within Phase 2 — each cell builds on the prior
- T003 (driver file) is parallelizable with T004–T010 since it targets a different file
- Within US1: T011 (check), T012 (scenario JSONL), T013 (metadata) are all [P] — different files
- Within US2: T015 (check), T016 (scenario JSONL), T017 (metadata) are all [P] — different files
- Within US3: T019 (check), T020 (scenario JSONL), T021 (metadata) are all [P] — different files
- US1, US2, and US3 can all run in parallel after Phase 2 completes
- T023–T026 in Phase 6 can run in parallel (different files / read-only verification tasks)

---

## Parallel Example: Phase 2 + User Stories

```text
# Phase 1: T001, T002 (sequential, fast)

# Phase 2: T003 can run in parallel with T004-T010
T003: Create pass-through-driver.md        ─┐ (different file)
T004-T010: Build notebook cells            ─┘ (sequential within notebook)

# After Phase 2 completes, launch all user stories in parallel:
US1: T011 + T012 + T013 (parallel) → T014 (validate)
US2: T015 + T016 + T017 (parallel) → T018 (validate)   ─── all 3 in parallel
US3: T019 + T020 + T021 (parallel) → T022 (validate)

# After all stories complete:
Phase 6: T023 → T024 + T025 + T026 (parallel) → T027 → T028
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T010)
3. Complete Phase 3: User Story 1 — Injection Payload Detection (T011–T014)
4. **STOP and VALIDATE**: Run notebook end-to-end against a target agent; confirm ~15 injection-eliciting prompts produce pass/fail results with evaluator rationale
5. This delivers immediate security signal: "Does this agent's output contain injection payloads?"

### Incremental Delivery

1. Setup + Foundational → Notebook scaffold ready
2. Add US1 (injection payload detection) → MVP: LLM05 output injection coverage
3. Add US2 (unsafe code generation) → Expanded: code/command safety coverage
4. Add US3 (schema violation) → Complete: structured output contract enforcement with deterministic checks
5. Polish → Production-ready LLM05 suite

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001–T010)
2. Once Foundational is done:
   - Developer A: US1 — injection payload detection (T011–T014)
   - Developer B: US2 — unsafe code generation (T015–T018)
   - Developer C: US3 — schema violation, code-based check (T019–T022, most technically distinct)
3. All stories complete and integrate into the same notebook via `SCENARIO_CHECK_MAP`

---

## Notes

- [P] tasks = different files, no dependencies on each other within same phase
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable by running the notebook with only that story's scenario JSONL and check file present
- All artifacts follow Constitution Principle VII (file-first) — create the file, then register via notebook
- Notebook check registration cell (T006) dispatches by extension: `.md` → `ModelBasedCheck`, `.py` → `CodeBasedCheck` — this single cell handles all three LLM05 checks without separate code paths
- Scenario JSONL `result` field doubles as the schema definition parameter for Scenario 3 — the code-based check reads `scenario_result` and parses it as JSON internally (per research decision R4)
- All three scenarios execute via `okareo.run_simulation(max_turns=1, first_turn="driver")` with the pass-through driver — consistent execution model across all LLM05 scenarios (per research decision R6)
- Total task count: **28 tasks** across 6 phases
