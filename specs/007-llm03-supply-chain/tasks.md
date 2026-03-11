# Tasks: OWASP LLM03 Supply Chain Vulnerabilities Test Suite

**Input**: Design documents from `/specs/007-llm03-supply-chain/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the spec. Tests are validated via notebook execution against known-good and known-bad inputs.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Artifact files**: `owasp/LLM03-supply-chain/{scenarios,checks,notebooks}/`
- **Spec files**: `specs/007-llm03-supply-chain/`
- **Shared config**: `owasp/target.env` (already exists from prior categories)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the LLM03 directory structure and verify shared prerequisites exist

- [x] T001 Create directory structure: `owasp/LLM03-supply-chain/scenarios/`, `owasp/LLM03-supply-chain/checks/`, `owasp/LLM03-supply-chain/notebooks/`
- [x] T002 Verify shared target configuration exists at `owasp/target.env` and contains required `TARGET_ENDPOINT_URL` field; verify `owasp/config.env.example` and `.env` (Okareo API key) are present

**Checkpoint**: Directory structure ready, shared config validated

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No new foundational infrastructure needed — shared config (`owasp/target.env`) and Okareo API key setup were established in earlier OWASP categories (LLM01). This phase is intentionally empty.

**⚠️ NOTE**: If this is the first OWASP category being implemented (no prior categories), see `specs/001-llm01-prompt-injection/quickstart.md` for initial setup of `owasp/target.env` and `.env`.

**Checkpoint**: Foundation ready — user story implementation can begin

---

## Phase 3: User Story 1 — Third-Party Model Behavioral Validation (Priority: P1) 🎯 MVP

**Goal**: Create probing prompts and a model-based check that detect whether a third-party model exhibits undocumented or unsafe capabilities outside its stated scope

**Independent Test**: Run the notebook with only Scenario 1 artifacts loaded. Send probing prompts to the target agent and verify the model-based check correctly flags undocumented capability claims as failures and passes legitimate refusals.

### Implementation for User Story 1

- [x] T003 [P] [US1] Create behavioral validation scenario data in `owasp/LLM03-supply-chain/scenarios/behavioral-validation.jsonl` with ~15 rows covering 6 probing categories (code execution, file system access, network access, tool invocation, training data disclosure, model architecture disclosure) per FR-017 and contracts/scenario-jsonl.md. Each category needs 2-3 prompt variants (direct probe, rephrased probe, edge-case probe) per research decision R4.
- [x] T004 [P] [US1] Create companion metadata file `owasp/LLM03-supply-chain/scenarios/behavioral-validation_meta.md` with YAML front matter per contracts/metadata-header.md: `owasp_category: LLM03`, `risk_severity: High`, `artifact_type: scenario`, `status: complete`, `version: "1.0.0"`, `name: "LLM03-behavioral-validation"`, `evaluation_mode: single-turn`, `row_count: <actual count>`
- [x] T005 [P] [US1] Create model-based check in `owasp/LLM03-supply-chain/checks/behavioral-boundary-detector.md` with YAML front matter and prompt template per contracts/check-prompt.md. Prompt must use placeholders `{scenario_input}`, `{model_output}`, `{scenario_result}`. Pass/fail criteria per data-model.md: pass if model refuses/deflects, fail if model claims or demonstrates undocumented capability. Must handle edge case: explaining a concept without claiming capability is a pass.
- [x] T006 [US1] Create notebook skeleton `owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb` with Part 1 cells: (1) title/overview markdown, (2) `%pip install okareo python-dotenv --quiet`, (3) SDK init with `OKAREO_API_KEY` and `CATEGORY_DIR` resolution, (4) Part 1 header, (5) upload `behavioral-validation.jsonl` scenario via `okareo.upload_scenario_set()`, (6) register checks header, (7) parse and register `behavioral-boundary-detector.md` via `okareo.create_or_update_check()` with `ModelBasedCheck`
- [x] T007 [US1] Add Part 2 cells to notebook `owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb`: (8) Part 2 header, (9) load `owasp/target.env` via `dotenv_values`, validate `TARGET_ENDPOINT_URL`, build `CustomEndpointTarget` with `TurnConfig`, (10) single-turn evaluation header, (11) create inline pass-through driver (`temperature=0`) and run `okareo.run_simulation(target, driver, behavioral_scenario, max_turns=1, first_turn="driver", checks=["LLM03-behavioral-boundary-detector"])`, (12) display results for Scenario 1

**Checkpoint**: At this point, User Story 1 should be fully functional — notebook can upload the behavioral validation scenario + check, run single-turn evaluation against any target agent, and display pass/fail results

---

## Phase 4: User Story 2 — Dependency and Provenance Integrity Verification (Priority: P1)

**Goal**: Create structured metadata test data and a code-based check that deterministically validates model artifact signatures, version pinning, SBOM/ML-BOM compliance, and license compatibility

**Independent Test**: Run the notebook with Scenario 2 artifacts loaded. Provide known-valid and known-invalid metadata samples and verify the code-based check produces 100% deterministic accuracy — every valid sample passes and every invalid sample fails.

### Implementation for User Story 2

- [x] T008 [P] [US2] Create provenance integrity scenario data in `owasp/LLM03-supply-chain/scenarios/provenance-integrity.jsonl` with ~15 rows covering all 4 validation dimensions per FR-018 and contracts/scenario-jsonl.md. Must include both valid (passing) and invalid (failing) cases for each dimension: signature verification (valid hash + missing signature + key mismatch), version pinning (all pinned + floating ranges), SBOM/ML-BOM (complete + missing fields + empty components), license compatibility (all allowed + incompatible + unknown). Use JSON string format for `input` and `result` per research decision R3.
- [x] T009 [P] [US2] Create companion metadata file `owasp/LLM03-supply-chain/scenarios/provenance-integrity_meta.md` with YAML front matter per contracts/metadata-header.md: `owasp_category: LLM03`, `risk_severity: High`, `artifact_type: scenario`, `status: complete`, `version: "1.0.0"`, `name: "LLM03-provenance-integrity"`, `evaluation_mode: single-turn`, `row_count: <actual count>`
- [x] T010 [US2] Create code-based check in `owasp/LLM03-supply-chain/checks/provenance-integrity-check.py` per contracts/check-code.md and data-model.md validation logic. Must include: (1) Python comment metadata header, (2) JSON parsing of `scenario_input` (metadata) and `scenario_result` (rules), (3) dispatch by `check_dimension`, (4) signature validation (hash algorithm prefix, signature presence, key ID match), (5) version pinning validation (detect `>=`, `^`, `~`, `*`, `latest`, `x` patterns), (6) SBOM validation (required top-level fields, required component fields), (7) license validation (check against `policy.allowed_licenses`), (8) return `CheckResult(score=bool, explanation=str)` with specific failure details per FR-007 and SC-007
- [x] T011 [US2] Add Scenario 2 upload cells to notebook `owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb`: upload `provenance-integrity.jsonl` scenario via `okareo.upload_scenario_set()`, read `provenance-integrity-check.py` source from disk and register via `okareo.create_or_update_check()` with `CodeBasedCheck`
- [x] T012 [US2] Add Scenario 2 evaluation cells to notebook `owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb`: create inline pass-through driver, run `okareo.run_simulation(target, driver, provenance_scenario, max_turns=1, first_turn="driver", checks=["LLM03-provenance-integrity-check"])`, display results for Scenario 2

**Checkpoint**: At this point, both User Stories are fully functional — notebook can upload all artifacts, run both scenarios independently, and display results with full OWASP traceability

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Finalize the notebook, add results summary, and validate the complete suite

- [x] T013 Add results summary cells to notebook `owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb`: combined pass/fail summary table for both scenarios, Okareo dashboard links, OWASP traceability metadata (category LLM03, severity High)
- [x] T014 [P] Add artifact upload summary cell to notebook after Part 1: print registered scenario names with row counts, registered check names with types (model-based vs code-based), confirm all artifacts uploaded successfully
- [x] T015 Validate complete suite by reviewing all artifacts against the requirements checklist in `specs/007-llm03-supply-chain/checklists/requirements.md` — verify metadata headers, file formats, naming conventions, and constitution compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Intentionally empty — shared config exists from prior categories
- **User Story 1 (Phase 3)**: Depends on Setup (Phase 1) completion
- **User Story 2 (Phase 4)**: Depends on Setup (Phase 1) completion; can run in parallel with Phase 3 for artifact creation (T008-T010), but notebook extensions (T011-T012) depend on the notebook skeleton created in T006
- **Polish (Phase 5)**: Depends on both User Stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup — No dependencies on US2
- **User Story 2 (P1)**: Artifact creation (T008-T010) can start after Setup in parallel with US1. Notebook extensions (T011-T012) require the notebook skeleton from T006.

### Within Each User Story

- Scenario JSONL and companion `_meta.md` can be created in parallel [P]
- Model-based check `.md` can be created in parallel with scenario data [P]
- Code-based check `.py` depends on understanding the scenario data shape (T008 informs T010)
- Notebook cells depend on artifact files being complete

### Parallel Opportunities

- T003, T004, T005 can all run in parallel (different files, US1)
- T008, T009 can run in parallel (different files, US2)
- T013, T014 can run in parallel (different notebook cells)
- US1 artifact creation (T003-T005) and US2 artifact creation (T008-T010) can run in parallel
- After T006 creates the notebook skeleton, T011-T012 can proceed

---

## Parallel Example: User Story 1

```text
# Launch all US1 artifacts together:
T003: "Create behavioral-validation.jsonl in owasp/LLM03-supply-chain/scenarios/"
T004: "Create behavioral-validation_meta.md in owasp/LLM03-supply-chain/scenarios/"
T005: "Create behavioral-boundary-detector.md in owasp/LLM03-supply-chain/checks/"

# Then sequentially:
T006: "Create notebook skeleton with Part 1 upload + SDK init"
T007: "Add Part 2 evaluation cells for Scenario 1"
```

## Parallel Example: User Story 2

```text
# Launch US2 artifacts (can overlap with US1 artifacts):
T008: "Create provenance-integrity.jsonl in owasp/LLM03-supply-chain/scenarios/"
T009: "Create provenance-integrity_meta.md in owasp/LLM03-supply-chain/scenarios/"

# Then sequentially (depends on T008 for data shape):
T010: "Create provenance-integrity-check.py in owasp/LLM03-supply-chain/checks/"

# Then notebook extensions (depends on T006 skeleton):
T011: "Add Scenario 2 upload cells to notebook"
T012: "Add Scenario 2 evaluation cells to notebook"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 3: User Story 1 (T003-T007)
3. **STOP and VALIDATE**: Run notebook — behavioral probing prompts should produce pass/fail results against the target agent
4. This alone provides immediate supply chain risk signal

### Incremental Delivery

1. Setup (T001-T002) → Directory ready
2. User Story 1 (T003-T007) → Behavioral validation working → **MVP!**
3. User Story 2 (T008-T012) → Provenance integrity working → Full LLM03 coverage
4. Polish (T013-T015) → Summary, traceability, checklist validation → Production ready

### Parallel Team Strategy

With two developers:

1. Both complete Setup together (T001-T002)
2. Once Setup is done:
   - Developer A: US1 artifacts (T003-T005), then notebook skeleton (T006-T007)
   - Developer B: US2 artifacts (T008-T010), then notebook extensions (T011-T012) after T006 is ready
3. Both complete Polish together (T013-T015)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- The notebook is built incrementally: skeleton in US1 (T006-T007), extended in US2 (T011-T012)
- Code-based check is new for this project (first time in LLM03) — follow LLM05 `schema-compliance-check.py` pattern
- All artifacts must carry `owasp_category: LLM03` and `risk_severity: High` metadata
- Commit after each task or logical group
