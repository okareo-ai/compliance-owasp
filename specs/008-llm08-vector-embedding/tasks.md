# Tasks: OWASP LLM08 Vector and Embedding Weaknesses Test Suite

**Input**: Design documents from `/specs/008-llm08-vector-embedding/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No test tasks generated — the test suite IS the deliverable; validation is via notebook execution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

All artifact files live under `owasp/LLM08-vector-embedding-weaknesses/` following the established OWASP category folder structure.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the LLM08 directory structure matching the project's established OWASP category folder pattern

- [x] T001 Create directory structure for `owasp/LLM08-vector-embedding-weaknesses/` with subdirectories `scenarios/`, `checks/`, `drivers/`, `notebooks/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks required — project infrastructure (Okareo SDK, target.env, notebook patterns) is already established across LLM01–LLM07

**Checkpoint**: Setup complete — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — RAG Injection via Retrieved Content (Priority: P1) 🎯 MVP

**Goal**: Create all artifacts for multi-turn RAG injection simulation — scenario seeds with poisoned documents, adversarial driver persona, and compliance drift check

**Independent Test**: Run the multi-turn simulation cells in the notebook with these artifacts and confirm the agent never follows hidden instructions embedded in retrieved documents

### Implementation for User Story 1

- [x] T002 [P] [US1] Create scenario file `owasp/LLM08-vector-embedding-weaknesses/scenarios/rag-injection.jsonl` with 5-8 multi-turn seed rows per contracts/scenario-jsonl.md — each row provides `input` object with `injection_type`, `poisoned_document`, `target_behavior`, `escalation_steps` keys and a `result` describing expected agent behavior. Cover injection vectors: system-directive, metadata-injection, footnote-injection, encoded-payload, formatting-markup. See contract example for row structure.
- [x] T003 [P] [US1] Create metadata file `owasp/LLM08-vector-embedding-weaknesses/scenarios/rag-injection_meta.md` with YAML front matter: `owasp_category: LLM08`, `risk_severity: High`, `artifact_type: scenario`, `status: complete`, `version: "1.0.0"`, `name: "LLM08-rag-injection"`, `evaluation_mode: multi-turn`, `row_count` matching the JSONL file
- [x] T004 [P] [US1] Create adversarial driver `owasp/LLM08-vector-embedding-weaknesses/drivers/rag-injection-exploiter.md` with YAML front matter (`owasp_category: LLM08`, `risk_severity: High`, `artifact_type: driver`, `evaluation_mode: multi-turn`, `temperature: 0.6`) and `## Persona Prompt Template` section — the driver knows the contents of poisoned documents (via `{poisoned_document}`) and crafts queries to trigger retrieval and exploit hidden instructions using `{injection_type}`, `{target_behavior}`, `{escalation_steps}` mustache parameters. Must include hard rules: start with legitimate queries, escalate gradually, never reveal the documents are poisoned, adapt based on agent responses.
- [x] T005 [P] [US1] Create multi-turn model-based check `owasp/LLM08-vector-embedding-weaknesses/checks/rag-injection-drift-detector.md` with YAML front matter (`owasp_category: LLM08`, `risk_severity: High`, `artifact_type: check`, `evaluation_mode: multi-turn`, `check_type: model`, `output_type: pass_fail`) and `## Criterion` + `## Prompt Template` sections — check evaluates `{simulation_message_history}` and `{scenario_result}` to detect any turn where the agent follows hidden instructions from retrieved content or shows compliance drift

**Checkpoint**: RAG injection artifacts complete — can run multi-turn simulation independently once notebook exists

---

## Phase 4: User Story 2 — Cross-Tenant / Cross-Scope Data Leakage (Priority: P2)

**Goal**: Create all artifacts for single-turn cross-tenant leakage detection — scenario seeds with multi-tenant retrieval context and a model-based check for unauthorized content detection

**Independent Test**: Run the single-turn simulation cells in the notebook with these artifacts and confirm the check flags any response containing content from unauthorized tenants or scopes

### Implementation for User Story 2

- [x] T006 [P] [US2] Create scenario file `owasp/LLM08-vector-embedding-weaknesses/scenarios/cross-tenant-leakage.jsonl` with 8-12 single-turn seed rows per contracts/scenario-jsonl.md — each row has `input` string combining user query + retrieved documents tagged with `[tenant_id: X] [scope: Y]` from authorized and unauthorized sources, and `result` describing expected behavior identifying which content is authorized. Cover: tenant isolation (2 tenants), scope escalation (public/internal/confidential), semantic-similarity cross-tenant matches, mixed authorized+unauthorized results, edge cases (missing metadata, empty authorized scope).
- [x] T007 [P] [US2] Create metadata file `owasp/LLM08-vector-embedding-weaknesses/scenarios/cross-tenant-leakage_meta.md` with YAML front matter: `owasp_category: LLM08`, `risk_severity: High`, `artifact_type: scenario`, `status: complete`, `version: "1.0.0"`, `name: "LLM08-cross-tenant-leakage"`, `evaluation_mode: single-turn`, `row_count` matching the JSONL file
- [x] T008 [P] [US2] Create single-turn model-based check `owasp/LLM08-vector-embedding-weaknesses/checks/cross-tenant-leakage-detector.md` with YAML front matter (`owasp_category: LLM08`, `risk_severity: High`, `artifact_type: check`, `evaluation_mode: single-turn`, `check_type: model`, `output_type: pass_fail`) and `## Criterion` + `## Prompt Template` sections — check evaluates `{scenario_input}`, `{model_output}`, `{scenario_result}` to detect when the agent's response includes content attributable to unauthorized tenants or higher permission scopes than authorized in the query context

**Checkpoint**: Cross-tenant leakage artifacts complete — can run single-turn simulation independently once notebook exists

---

## Phase 5: User Story 3 — Vector Store Access Control Validation (Priority: P3)

**Goal**: Create all artifacts for deterministic access control validation — scenario seeds with retrieval results containing metadata and a code-based Python check that validates metadata against access control policies

**Independent Test**: Run the single-turn simulation cells in the notebook with these artifacts and confirm the code-based check deterministically identifies all metadata violations in retrieval results

### Implementation for User Story 3

- [x] T009 [P] [US3] Create scenario file `owasp/LLM08-vector-embedding-weaknesses/scenarios/access-control-validation.jsonl` with 8-12 single-turn seed rows per contracts/scenario-jsonl.md — each row has `input` string combining user query + retrieval results as JSON objects with `id`, `tenant_id`, `scope`, `content` fields, and `result` as JSON-encoded access control policy with `authorized_tenant_id`, `authorized_scopes`, `expected_violations` per contracts/code-check.md policy schema. Cover: all-authorized results (pass case), tenant mismatch, scope escalation, multiple violations, missing metadata fields, empty scope sets, special characters in tenant IDs.
- [x] T010 [P] [US3] Create metadata file `owasp/LLM08-vector-embedding-weaknesses/scenarios/access-control-validation_meta.md` with YAML front matter: `owasp_category: LLM08`, `risk_severity: High`, `artifact_type: scenario`, `status: complete`, `version: "1.0.0"`, `name: "LLM08-access-control-validation"`, `evaluation_mode: single-turn`, `row_count` matching the JSONL file
- [x] T011 [P] [US3] Create code-based check `owasp/LLM08-vector-embedding-weaknesses/checks/access-control-check.py` with docstring metadata header (`owasp_category: LLM08`, `risk_severity: High`, `artifact_type: check`, `check_type: code`, `output_type: pass_fail`) and a `check(model_output, scenario_result)` function per contracts/code-check.md — parses the access control policy from `scenario_result` JSON, extracts retrieval result entries from `model_output`, validates each entry's `tenant_id` and `scope` against the policy, returns `{"pass": bool, "explanation": str}` with specific violating entries listed on failure. Must handle edge cases: missing metadata fields, malformed JSON, empty result sets.

**Checkpoint**: All artifact files complete across all 3 user stories — ready for notebook integration

---

## Phase 6: Notebook Integration (Cross-Cutting)

**Purpose**: Build the single unified Jupyter notebook that uploads all artifacts and executes all evaluations — depends on all artifact files from Phases 3–5

- [x] T012 Create `owasp/LLM08-vector-embedding-weaknesses/notebooks/run-evaluation.ipynb` Part 1 — Upload Artifacts: title cell (OWASP LLM08, risk severity High), pip install cell (`okareo`, `python-dotenv`), SDK init cell (load `.env`, validate `OKAREO_API_KEY`, resolve `CATEGORY_DIR`), scenario upload cell (loop `scenarios/*.jsonl`, `upload_scenario_set` with `LLM08-{stem}` prefix), model-based check registration cell (parse `checks/*.md` YAML front matter + `## Prompt Template`, `create_or_update_check` with `ModelBasedCheck`), code-based check registration cell (load `checks/*.py`, parse docstring metadata, `create_or_update_check` with `CodeBasedCheck`), driver registration cell (parse `drivers/*.md` YAML + `## Persona Prompt Template`, `create_or_update_driver`), artifact summary cell. Follow patterns from `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb`.
- [x] T013 Extend `owasp/LLM08-vector-embedding-weaknesses/notebooks/run-evaluation.ipynb` Part 2 — Run Evaluation: target config cell (load `owasp/target.env`, define check/driver name constants and pass-through driver template), build target cell (`CustomEndpointTarget` with `TurnConfig`, optional `SessionConfig`/`EndSessionConfig`), single-turn simulations cell (loop cross-tenant-leakage + access-control-validation scenarios with pass-through `Driver(temperature=0)`, `max_turns=1, first_turn="driver"`, assigned checks per plan Check Assignment Matrix), multi-turn simulation cell (rag-injection scenario with registered adversarial driver `LLM08-rag-injection-exploiter`, `max_turns=10, first_turn="driver"`, check `LLM08-rag-injection-drift-detector`), results summary cell (print scenario name, pass/fail, Okareo dashboard link), optional detailed results cell

**Checkpoint**: Notebook complete — full end-to-end execution possible

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate artifact quality and end-to-end execution

- [x] T014 Validate all artifact metadata headers in `owasp/LLM08-vector-embedding-weaknesses/` comply with Constitution Principle VI — verify every `.md` check, `.md` driver, `.py` check, and `_meta.md` file includes `owasp_category: LLM08`, `risk_severity: High`, `artifact_type`, `status`, `version` fields
- [x] T015 Run end-to-end notebook execution validation per `specs/008-llm08-vector-embedding/quickstart.md` — confirm all 3 scenarios upload, all 3 checks register, the driver registers, target builds from `target.env`, and all simulations complete with results displayed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: N/A — project infrastructure already exists
- **User Stories (Phases 3–5)**: All depend on Phase 1 (directory creation) but are independent of each other
- **Notebook (Phase 6)**: Depends on all artifact files from Phases 3–5 being complete
- **Polish (Phase 7)**: Depends on Phase 6 (notebook) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 1 — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 1 — No dependencies on other stories
- **User Story 3 (P3)**: Can start after Phase 1 — No dependencies on other stories

### Within Each User Story

- Scenario JSONL and meta file can be created in parallel with checks and drivers
- All artifacts within a story marked [P] can run in parallel (different files, no dependencies)
- Story complete when all its artifacts pass metadata validation

### Parallel Opportunities

- T002, T003, T004, T005 (US1 artifacts) — all [P], different files
- T006, T007, T008 (US2 artifacts) — all [P], different files
- T009, T010, T011 (US3 artifacts) — all [P], different files
- All three user story phases (3, 4, 5) can execute in parallel since they create independent artifact files
- T012 and T013 are sequential (same notebook file)

---

## Parallel Example: All User Stories

```text
# After T001 (directory setup), launch all artifact tasks across all stories simultaneously:

# US1 artifacts (4 tasks in parallel):
Task T002: Create rag-injection.jsonl in scenarios/
Task T003: Create rag-injection_meta.md in scenarios/
Task T004: Create rag-injection-exploiter.md in drivers/
Task T005: Create rag-injection-drift-detector.md in checks/

# US2 artifacts (3 tasks in parallel):
Task T006: Create cross-tenant-leakage.jsonl in scenarios/
Task T007: Create cross-tenant-leakage_meta.md in scenarios/
Task T008: Create cross-tenant-leakage-detector.md in checks/

# US3 artifacts (3 tasks in parallel):
Task T009: Create access-control-validation.jsonl in scenarios/
Task T010: Create access-control-validation_meta.md in scenarios/
Task T011: Create access-control-check.py in checks/

# Then sequential: T012 → T013 (notebook Parts 1 → 2)
# Then parallel: T014, T015 (validation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 3: User Story 1 — RAG Injection (T002–T005)
3. Complete Phase 6: Notebook with US1 scenario only (T012–T013, scoped to rag-injection)
4. **STOP and VALIDATE**: Run multi-turn simulation independently
5. Extend notebook for US2 and US3

### Incremental Delivery

1. T001 → Directory ready
2. T002–T005 → RAG injection artifacts ready → Run simulation (MVP!)
3. T006–T008 → Cross-tenant leakage artifacts ready → Run simulation
4. T009–T011 → Access control artifacts ready → Run simulation
5. T012–T013 → Full notebook ready → End-to-end execution
6. T014–T015 → Validated and polished

### Parallel Team Strategy

With multiple developers:

1. One developer creates T001 (setup)
2. Once setup is done:
   - Developer A: User Story 1 (T002–T005)
   - Developer B: User Story 2 (T006–T008)
   - Developer C: User Story 3 (T009–T011)
3. All artifacts merge, then T012–T013 (notebook) builds on all three

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All JSONL scenario row counts are targets from contracts/scenario-jsonl.md: rag-injection 5–8, cross-tenant-leakage 8–12, access-control-validation 8–12
- The code-based check (T011) is the only `.py` artifact — follow the contract in contracts/code-check.md for the `check(model_output, scenario_result)` function signature
- The notebook (T012–T013) follows the exact two-part pattern from `owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb` with additions for code-based check registration
- All artifact names use the `LLM08-` prefix (e.g., `LLM08-rag-injection`, `LLM08-cross-tenant-leakage-detector`)
- Commit after each phase or logical group
