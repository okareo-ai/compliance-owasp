# Research: OWASP LLM06 Excessive Agency Test Suite

**Branch**: `004-llm06-excessive-agency` | **Date**: 2026-03-10

## Research Questions & Decisions

### R1: Scenario JSONL Input Schema for Three Distinct Multi-Turn Scenarios

**Decision**: Each of the 3 scenarios uses a JSON object `input` with keys matching its dedicated driver's mustache parameters. The input schemas differ per scenario because the adversarial strategies are fundamentally different.

**Scenario 1 (Unauthorized Tool Invocation)**:
- `manipulation_strategy`: How the adversary convinces the agent (e.g., "social engineering", "tool hallucination induction", "scope reframing")
- `permitted_tools`: Description of the agent's granted tool set
- `target_tool`: The unauthorized tool the adversary wants invoked
- `cover_story`: The legitimate-sounding reason for the request
- `escalation_steps`: Turn-by-turn manipulation plan

**Scenario 2 (Permission Escalation)**:
- `escalation_strategy`: The specific escalation technique (e.g., "incremental request widening", "gaslighting", "batch embedding")
- `initial_permission_level`: Starting permission scope (e.g., "read-only file access")
- `target_permission_level`: Goal permission scope (e.g., "admin-level write and delete")
- `cover_story`: The legitimate-sounding context for the escalation
- `escalation_steps`: Turn-by-turn escalation plan

**Scenario 3 (Autonomous Action Without Approval)**:
- `bypass_strategy`: How the adversary tries to bypass the confirmation gate (e.g., "urgency fabrication", "false pre-approval claim", "impersonation")
- `target_action`: The high-impact action to execute (e.g., "delete all user records", "transfer $50,000", "send data to external API")
- `urgency_pretext`: The fake urgency scenario justifying immediate execution
- `escalation_steps`: Turn-by-turn pressure escalation plan

**Rationale**: Unlike LLM01 where a single driver covered all multi-turn scenarios with the same 4 parameters, LLM06's three attack vectors require structurally different manipulation approaches. Unauthorized tool invocation is about scope, permission escalation is about privilege levels, and approval bypass is about urgency and social engineering. Sharing a single input schema would force awkward field overloading.

**Alternatives considered**:
- Single unified input schema with superset of all fields: Would result in unused fields per scenario, making scenario authoring confusing and driver templates unnecessarily complex. Rejected.
- Using the same 4 fields as LLM01 (`escalation_strategy`, `initial_topic`, `target_behavior`, `escalation_steps`): Too generic for the domain-specific parameters LLM06 scenarios need (permitted tools, permission levels, target actions). Rejected.

### R2: Driver Architecture — One Driver per Scenario vs Shared Driver

**Decision**: Three dedicated adversarial driver personas, one per scenario. Each driver is a separate `.md` file with scenario-specific mustache parameters, manipulation tactics, and hard rules.

1. `LLM06-tool-scope-manipulator` — Attempts to trick the agent into calling unauthorized tools
2. `LLM06-privilege-escalator` — Attempts to progressively widen the agent's permissions
3. `LLM06-approval-gate-bypasser` — Attempts to pressure the agent into executing high-impact actions without confirmation

**Rationale**: The three attack vectors require fundamentally different adversarial personas and conversation strategies. A tool-scope manipulator needs to understand tool APIs and capability claims. A privilege escalator needs to gradually widen permissions while appearing benign. An approval-gate bypasser needs to fabricate urgency and false authority. A single parameterized driver cannot effectively capture these distinct behavioral patterns without becoming unwieldy.

**Alternatives considered**:
- Single parameterized driver (like LLM01's jailbreak-escalator): LLM01's single driver works because all crescendo attacks share the same fundamental pattern — gradual escalation from benign to harmful. LLM06's three scenarios differ not just in strategy but in the fundamental nature of the manipulation. Rejected.
- Two drivers (shared escalation driver + one for tool invocation): Partial sharing doesn't save enough complexity to justify the compromise in persona specificity. Rejected.

### R3: Check Architecture — Shared vs Per-Scenario Checks

**Decision**: Two model-based checks that cover all three scenarios:

1. **`LLM06-excessive-agency-detector`** — Evaluates the full conversation transcript to determine whether the agent exceeded its authority boundaries at any point. Uses `{simulation_message_history}` and `{scenario_result}` to assess against scenario-specific expected behavior. This is the primary pass/fail check.

2. **`LLM06-agency-boundary-drift-detector`** — Evaluates whether the agent's resistance to authority-exceeding requests progressively weakened across turns, even if no single turn constitutes a full violation. Detects soft failures: increasingly permissive language, partial concessions, weakening refusals. Analogous to LLM01's compliance-drift-detector.

**Rationale**: The `{scenario_result}` placeholder provides scenario-specific evaluation context, allowing a single check prompt to correctly assess unauthorized tool invocation, permission escalation, and approval bypassing. The drift detector adds a second evaluation dimension that catches progressive weakening — a pattern critical for multi-turn excessive agency attacks where each individual step may appear benign.

**Alternatives considered**:
- Three per-scenario checks: Would duplicate 80% of evaluation logic. The difference between "did the agent call an unauthorized tool" and "did the agent execute without approval" is captured by `{scenario_result}`, not by different check prompts. Rejected.
- Single check only: Missing the drift-detection dimension. An agent could resist at every individual turn but progressively soften its resistance, creating risk. Rejected.

### R4: Multi-Turn Simulation Configuration

**Decision**: All 3 scenarios use `max_turns=10` and `first_turn="target"`. The target agent speaks first (greeting/introduction), then the adversarial driver begins manipulation.

**Rationale**: Matching the established convention from LLM01's multi-turn crescendo attack. `first_turn="target"` is appropriate because excessive agency attacks begin with the user engaging an already-active agent — the agent should establish its role and boundaries first, then the adversary tests those boundaries. 10 turns provides sufficient room for gradual escalation across 5 pairs of driver-target exchanges.

**Alternatives considered**:
- `first_turn="driver"`: Would have the adversary speak first, which doesn't match the real-world pattern where a user initiates with a deployed agent that has an established role. Rejected.
- `max_turns=6`: Insufficient for multi-stage escalation. Permission escalation in particular requires several turns of legitimate-seeming requests before the escalation becomes apparent. Rejected.

### R5: Notebook Structure — Single Combined Notebook

**Decision**: One notebook (`run-evaluation.ipynb`) that handles both artifact upload and simulation execution, matching the LLM01 pattern. Since all 3 LLM06 scenarios are multi-turn, the notebook does not need a single-turn execution path. Each scenario is run against its dedicated driver and both shared checks.

**Rationale**: Follows the established single-notebook-per-category convention. A combined notebook ensures adopters can run the complete LLM06 evaluation in one sequential execution. Since there are no single-turn scenarios (unlike LLM01 which had both), the notebook is simpler — all simulations use the same multi-turn parameters with only the scenario name, driver name varying per run.

**Alternatives considered**:
- Separate upload and evaluation notebooks: Would add complexity without benefit for 3 scenarios. The upload step is lightweight (3 JSONL files, 2 checks, 3 drivers). Rejected.
- One notebook per scenario: Excessive fragmentation. The shared target configuration and check registration would be duplicated. Rejected.

### R6: Temperature Setting for Adversarial Drivers

**Decision**: All three adversarial drivers use `temperature: 0.7` (slightly higher than LLM01's `0.6`).

**Rationale**: Excessive agency attacks benefit from more creative adversarial approaches. Unlike jailbreak escalation where consistent strategy is key, tool-scope manipulation and approval-gate bypassing benefit from varied phrasing and creative social engineering. A slightly higher temperature produces more diverse manipulation attempts across rows while staying deterministic enough for reproducible evaluation.

**Alternatives considered**:
- `temperature: 0.6` (same as LLM01): Would work but slightly constrains the diversity of manipulation tactics. The LLM06 drivers benefit from more creativity since they're testing social engineering against tool boundaries, not just safety refusals. Rejected.
- `temperature: 1.0`: Too high — risks incoherent driver outputs that don't effectively test the agent's boundaries. Rejected.

### R7: Target Agent Assumptions — Tool Manifest in System Prompt

**Decision**: The test suite assumes the target agent's system prompt or configuration describes its permitted tools, permission level, and actions requiring human approval. The scenarios and checks are written to evaluate against these stated boundaries, not against a specific tool implementation.

**Rationale**: Different adopters will have agents with different tool sets, permission models, and approval gates. The scenarios test whether an agent maintains whatever boundaries it has declared, not whether it has a specific set of tools. The scenario `result` field describes expected behavior in terms of "the agent should not exceed its stated scope" rather than "the agent should refuse to call function X."

**Alternatives considered**:
- Hardcoding specific tool names (e.g., "delete_user", "send_payment"): Would make scenarios non-portable across adopters. Rejected per Constitution Principle IV (Composability & Forkability).
- Providing a reference system prompt template: Out of scope for the scenario/check/driver artifacts. The target agent's configuration is the adopter's responsibility. Could be added as a documentation recommendation in quickstart.md.
