# Research: OWASP LLM05 Improper Output Handling Test Suite

**Branch**: `005-llm05-output-handling` | **Date**: 2026-03-10

## Research Questions & Decisions

### R1: Okareo Check Discovery — Existing vs Custom

**Decision**: Build two custom model-based checks (Scenarios 1 and 2) and one custom code-based check (Scenario 3). Do not use any existing built-in Okareo checks as the sole evaluation mechanism.

**Rationale**: `list_checks` returns 175 checks in the Okareo account. None are purpose-built for LLM05 output injection payload detection or unsafe code generation. The closest existing checks are:
- `is_json` — validates syntactic JSON well-formedness only; does not validate schema, required fields, type contracts, or prototype-pollution keys. Insufficient as a standalone Scenario 3 check but confirmed as a pattern to incorporate inside the custom code-based check.
- `owasp_prompt_injection_guard` — detects behavioral change from *injected instructions*, not *injection payloads in outputs*. Wrong direction (input → agent behavior, not agent output → downstream harm). Cannot be reused.
- `behavior_adherence`, `model_refusal` — generic checks that do not assess output payload safety. Too coarse for LLM05.
Custom checks are required for all three scenarios. Two OWASP checks already exist for LLM01 and LLM07 (`owasp_prompt_injection_guard`, `owasp_system_prompt_not_leaked`, `owasp_scope_boundary`) — this confirms the pattern of registering named OWASP checks per category.

**Alternatives considered**:
- Using `behavior_adherence` as a proxy for Scenarios 1–2: Evaluates instruction-following, not output payload safety. Semantically misaligned. Rejected.
- Using `is_json` alone for Scenario 3: Validates syntactic JSON only; misses type mismatches, missing fields, unexpected keys, and prototype-pollution vectors. Rejected as sole check; incorporated as internal logic within the custom code-based check.

---

### R2: Check Type Selection — Model-Based vs Code-Based per Scenario

**Decision**:
- **Scenarios 1 and 2** → Model-based checks (`.md` prompt templates, `ModelBasedCheck`, `CheckOutputType.PASS_FAIL`)
- **Scenario 3** → Code-based check (`.py` Python module, `CodeBasedCheck`, `CheckResponse(score=bool)`)

**Rationale**:
Scenarios 1 and 2 require **semantic judgment**: determining whether an agent's output contains an injection payload or unsafe code pattern that is dangerous in context requires understanding the rendering environment, containment (escaped vs unescaped), and purpose (educational documentation vs live generation). The same string `<script>alert(1)</script>` is safe inside a triple-backtick markdown code fence explaining a vulnerability and dangerous in raw HTML output. This distinction requires an evaluator LLM, not a regex.

Scenario 3 requires **deterministic validation**: a JSON schema check has no ambiguity. Either the field `score` is an integer or it is not. Either `__proto__` is present or it is not. Model-based evaluation on a deterministic contract produces unnecessary variance and risks false negatives on clear violations. The `check_code` template confirms the `CodeBasedCheck` / `CheckResponse` pattern is the correct implementation.

**Alternatives considered**:
- Code-based checks for Scenarios 1–2 using regex: Cannot distinguish escaped/documented patterns from live payloads. High false-positive rate on educational content. Rejected per spec FR-004.
- Model-based check for Scenario 3: Introduces variance on a deterministic contract; a model might "understand" the intent and pass a technically invalid response. Rejected per spec FR-005 and SC-004.
- Hybrid (model + code) for Scenarios 1–2: Could add code-based regex as a secondary signal, but adds complexity without proportional benefit in the initial implementation. Deferred.

---

### R3: Check Prompt Template Placeholders and Evaluation Design

**Decision**: Both model-based checks (Scenarios 1 and 2) use `{scenario_input}` + `{model_output}` + `{scenario_result}` placeholders. The prompt template instructs the evaluator to assess the output's safety in the context of how it would be consumed, not in isolation.

**Rationale**: The `boolean_check_prompt` template confirms the standard placeholder set: `{scenario_input}`, `{model_output}`, `{scenario_result}`. For LLM05, the `{scenario_input}` (the eliciting prompt) provides context for what the agent was asked to generate. The `{scenario_result}` field in each scenario row carries a description of what makes the output safe or unsafe for that row (e.g., "Response must not contain raw SQL injection patterns in query output context"). The evaluator prompt must include explicit pass/fail criteria, a list of specific payload families to look for, and a context-assessment instruction (escaped/documented content in a clearly explanatory context is not a failure).

**Alternatives considered**:
- Omitting `{scenario_input}` from the check prompt: The evaluator would have to assess the output without knowing what was asked. This loses the context needed to distinguish "explaining a vulnerability" from "generating a vulnerability." Rejected.
- Using `{scenario_result}` as the full criterion: The scenario result describes expected behavior per row, but the check prompt also needs to enumerate the payload families — this is more maintainable in the check template than duplicated in every scenario row. Decision: check template enumerates payload families; `{scenario_result}` provides per-row expected behavior description.

---

### R4: Code-Based Schema Check Architecture (Scenario 3)

**Decision**: The Scenario 3 code-based check uses Python's `json` standard library for parsing plus inline schema validation logic. The schema is embedded in the scenario JSONL `result` field as a JSON string describing expected fields, their types, and any disallowed keys. The check function parses the schema from `scenario_result`, then validates `model_output` against it.

**Rationale**: This approach requires no external dependencies beyond the Python standard library (no `jsonschema` package), which simplifies the check deployment in Okareo's code-based check execution environment. The `CodeBasedCheck` / `CheckResponse` pattern (from `check_code` template) receives `(model_output, scenario_input, scenario_result)`. Embedding the schema in `scenario_result` allows different scenario rows to test different schema shapes using the same check function — a single check definition covers multiple schema contracts.

The check validates in order:
1. JSON parseability (extract JSON from raw response, handling preamble/fences)
2. Required field presence
3. Type correctness for each declared field
4. No extra unexpected keys (strict mode)
5. No prototype-pollution-risk keys (`__proto__`, `constructor`, `__defineGetter__`, etc.) at any nesting level

**Alternatives considered**:
- Using the `jsonschema` library: More expressive schema language but requires an external dependency that may not be available in Okareo's code-based check sandbox. Rejected for initial implementation; can be upgraded if environment supports it.
- Separate check functions per schema: Each schema would need its own registered check, creating N checks for N schemas. The single parameterized check is more maintainable. Rejected.
- Using the built-in `is_json` check for Scenario 3: Only validates syntactic well-formedness; misses type contracts, required fields, and proto-pollution. Rejected as the sole check.

---

### R5: Scenario JSONL Format — Eliciting Prompts and Result Fields

**Decision**: All three scenarios use the same JSONL row format as LLM01 single-turn scenarios: `{"input": "<eliciting prompt>", "result": "<expected behavior or schema>"}`. For Scenarios 1–2, `result` describes what a safe response looks like. For Scenario 3, `result` is a JSON string encoding the schema definition used by the code-based check.

**Rationale**: All three scenarios use single-turn evaluation (`max_turns=1, first_turn="driver"`). The LLM01 established pattern uses `input` (string prompt) and `result` (expected behavior description). This is the correct format for Okareo's `save_scenario` with the SDK. For Scenario 3, the `result` field doubles as the schema definition parameter for the code-based check, which receives `scenario_result` as a string — the check function parses it as JSON internally.

**Scenario row counts (target)**:
- Scenario 1 (injection payload detection): ~15 rows covering XSS (5), SQL injection (5), command injection (5) eliciting prompts
- Scenario 2 (unsafe code/command generation): ~15 rows covering path traversal (5), shell execution (5), unsafe API calls (5) eliciting prompts
- Scenario 3 (schema violation): ~10 rows covering different schema shapes and violation types (missing fields, type mismatches, extra keys, proto-pollution keys, non-JSON preamble)

**Alternatives considered**:
- Separating scenario rows by payload family into multiple JSONL files per scenario: Adds granular per-family reporting but creates 6+ files and complicates notebook orchestration. Deferred — single file per scenario is the initial approach, with tags indicating family.
- Using `result` as a regex pattern for code-based assertion: More fragile than a structured schema definition. Rejected for Scenario 3 in favor of a JSON-encoded schema object.

---

### R6: Target Configuration and Execution Model

**Decision**: All three LLM05 scenarios use `okareo.run_simulation()` with a pass-through `Driver` constrained to `max_turns=1, first_turn="driver"`. Target configuration is loaded from the shared `owasp/target.env` file, identical to all other OWASP categories. No per-category target configuration.

**Rationale**: All LLM05 risks are stateless single-exchange risks (per Constitution Principle V). The pass-through driver pattern established by LLM01 is directly reusable: `Driver(temperature=0)` with a template that repeats the scenario input verbatim. The shared `owasp/target.env` centralizes agent configuration across the full OWASP suite.

The code-based check for Scenario 3 receives the raw agent response string from `run_simulation()`. The check must handle JSON extraction from that raw string (stripping markdown code fences, preamble prose, trailing content) before parsing — this is part of the check's responsibility per the spec Assumption.

**Alternatives considered**:
- Using `okareo.run_test()` with a `GenerationModel` instead of `run_simulation()` with `CustomEndpointTarget`: Tests a raw LLM, not a deployed agent. OWASP compliance testing is about agent behavior. Rejected — consistent with LLM01–LLM04 pattern.
- Per-scenario target configuration: Not needed; all three scenarios test the same agent. Rejected per FR-013.

---

### R7: Notebook Idempotency and Artifact Registration

**Decision**: Single unified notebook (`run-evaluation.ipynb`) handles upload + evaluation for all three scenarios. Uses Okareo's native upsert semantics: `save_scenario` (returns existing by name), `create_or_update_check` (upserts model-based and code-based checks by name). Registered objects held in-memory for the evaluation phase.

**Rationale**: The unified single-notebook pattern is established by LLM01 and works identically for LLM05. All three LLM05 scenarios are single-turn; there is no multi-turn/single-turn split requiring separate notebook sections. Code-based check registration uses the same `create_or_update_check` API as model-based checks — the `check` parameter receives a `CodeBasedCheck` instance instead of a `ModelBasedCheck` instance.

For code-based checks, the check class source code (the `.py` file content) is read from disk and passed to `create_or_update_check` as the `check` parameter. This maintains the file-first principle: the `.py` file is the source of truth, and the notebook reads and deploys it at registration time.

**Alternatives considered**:
- Separate upload and evaluation notebooks: Adds a step for the adopter with no benefit given single-turn scenarios. Rejected.
- Defining the code-based check inline in the notebook: Violates Constitution Principle VII (file-first). Rejected.
