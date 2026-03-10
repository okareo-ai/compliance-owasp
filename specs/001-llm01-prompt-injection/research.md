# Research: OWASP LLM01 Prompt Injection Test Suite

**Branch**: `001-llm01-prompt-injection` | **Date**: 2026-03-09

## Research Questions & Decisions

### R1: Okareo Scenario Format for Single-Turn vs Multi-Turn

**Decision**: Use JSONL files with `input` and `result` fields. Single-turn scenarios use string `input`; multi-turn scenarios use JSON object `input` with keys matching driver prompt mustache parameters.

**Rationale**: The Okareo SDK's `save_scenario` accepts a `file_path` to a `.jsonl` file, which is the preferred method for large datasets (avoids context window limits). Each line is a JSON object with `input` (string or object) and `result` (string). When used with `run_simulation`, the input object's keys populate the driver's mustache template parameters.

**Alternatives considered**:
- Inline `rows` parameter: Only suitable for <20 rows and not file-first. Rejected per Constitution Principle VII.
- CSV/TSV: Not supported by Okareo SDK. Rejected.

### R2: Check Type — Model-Based vs Code-Based

**Decision**: All five scenario checks are model-based (`check_type: "model"`, `output_type: "pass_fail"`) using prompt templates.

**Rationale**: Injection compliance detection requires semantic judgment — determining whether an agent's response "complied with" an injected instruction is a nuanced assessment that cannot be reliably performed with regex or keyword matching. Model-based checks leverage an evaluator LLM to make this judgment, with the prompt template providing structured evaluation criteria.

**Alternatives considered**:
- Code-based checks (Python): Only effective for surface-level pattern matching (e.g., detecting specific strings). Insufficient for semantic compliance assessment. Could supplement model-based checks as a secondary signal but would add complexity without proportional value in the initial implementation.
- Hybrid (model + code): Deferred — may be introduced if false positive/negative rates warrant a secondary validation layer.

### R3: Check Prompt Template Placeholders

**Decision**: Single-turn checks use `{scenario_input}` + `{model_output}`. Multi-turn checks use `{simulation_message_history}`.

**Rationale**: Okareo provides distinct placeholders for single-turn (`{scenario_input}`, `{model_output}`) and multi-turn (`{simulation_message_history}`) contexts. The multi-turn placeholder contains the full conversation transcript, enabling the evaluator to assess each turn and detect progressive drift.

**Alternatives considered**:
- Using `{message_history}` for multi-turn: This is the per-turn history available in driver prompts, not the full simulation transcript. `{simulation_message_history}` is the correct placeholder for post-simulation evaluation.

### R4: Driver Persona Architecture for Crescendo Attacks

**Decision**: Single driver persona (`jailbreak-escalator`) with parameterized escalation strategy. Scenario JSONL rows provide per-simulation variation via mustache parameter substitution.

**Rationale**: The Okareo driver template supports mustache parameters that are populated from scenario `input` fields. This allows a single driver definition to execute different escalation strategies (e.g., role-playing, hypothetical framing, educational framing) by varying the scenario data rows. This is more maintainable than creating multiple driver personas.

**Alternatives considered**:
- Multiple driver personas (one per escalation technique): More rigid, harder to maintain, duplicates driver infrastructure. Rejected in favor of parameterized single driver.
- Fully static driver (no parameterization): Would reduce simulation coverage since every run follows identical strategy. Rejected.

### R5: Target Configuration Strategy

**Decision**: All scenarios use `okareo.run_simulation()` with a `Driver` object targeting a registered `CustomEndpointTarget`. Target configuration (endpoint URL, auth, name) is stored in a single shared file `owasp/target.env`, loaded by all OWASP category notebooks. Single-turn scenarios use a pass-through `Driver` with `max_turns=1, first_turn="driver"`; multi-turn simulations use an adversarial `Driver` with `max_turns=10, first_turn="target"` (the agent greets first, then the driver begins escalation).

**Rationale**: The target is always an **agent**, not a raw generative model. Using `CustomEndpointTarget` + `run_simulation()` for all scenarios — including single-turn ones — preserves agent interaction semantics consistently across the entire suite. A single shared `owasp/target.env` file ensures all OWASP controls (LLM01–LLM10) evaluate the same agent; retargeting requires one file change. This satisfies FR-019 (centralized target) and the clarified FR-003 (single-turn via driver).

**Alternatives considered**:
- `GenerationModel` (Okareo-hosted LLM, e.g., `gpt-4o-mini`): Lower setup barrier but evaluates a raw model API, not a deployed agent. OWASP compliance testing is fundamentally about agent behavior under adversarial conditions, not isolated model capabilities. Rejected — the suite tests agents, not models.
- Per-category target configuration: Each notebook defines its own target. Would allow different OWASP categories to test different agents, but violates the "one agent under test" constraint and creates inconsistent compliance results across the suite. Rejected per FR-019.
- `generation` + `custom_endpoint` dual-mode: The original design before clarification. Adds two code paths, two execution patterns, and two registration APIs with no benefit once the agent-only constraint is established. Rejected.

**Single-turn driver template**: For single-turn scenarios (scenarios 1, 2, 4, 5), the notebook creates an inline pass-through `Driver(temperature=0)` with a template that instructs the driver to repeat the scenario input verbatim. This ensures the scenario's injection payload is delivered to the agent without transformation by the driver LLM. See `contracts/driver-prompt.md` for the full pattern.

### R6: Notebook Idempotency Strategy

**Decision**: Use Okareo's built-in upsert semantics — `save_scenario` returns existing scenario if same name; `create_or_update_check` and `create_or_update_driver` upsert by name.

**Rationale**: All three Okareo artifact registration APIs are idempotent by name. `save_scenario` returns the existing scenario (immutable after creation); checks and drivers use upsert. No custom idempotency logic needed in notebooks.

**Alternatives considered**:
- List-then-create pattern: Query existing artifacts first, skip if found. Adds unnecessary complexity when native upsert is available. Rejected.

### R7: Simulation Turn Count and Configuration

**Decision**: `max_turns=10, first_turn="driver"` for crescendo attack simulations (Scenario 3). `max_turns=1, first_turn="driver"` for all single-turn scenarios (Scenarios 1, 2, 4, 5). `first_turn="driver"` is used universally.

**Rationale**: The spec requires 5-10 turns for crescendo attacks; `max_turns=10` provides the full window. Single-turn scenarios constrain the simulation to one driver message + one agent response, producing single-exchange assessment while preserving the driver-agent interaction model (see R5). `first_turn="driver"` is used in all cases because the adversarial persona always initiates — for both attack delivery (single-turn) and escalation (multi-turn).

**Alternatives considered**:
- `max_turns=5` for crescendo: May be insufficient for gradual escalation. The spec explicitly requires 5-10 turns.
- `first_turn="target"` for single-turn: Would require the agent to speak first, which doesn't match the injection attack model where the attacker sends the malicious prompt.
- Different `max_turns` values per single-turn scenario: Unnecessary complexity; `max_turns=1` is canonical for all single-turn scenarios.
