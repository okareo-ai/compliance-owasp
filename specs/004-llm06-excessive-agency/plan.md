# Implementation Plan: OWASP LLM06 Excessive Agency Test Suite

**Branch**: `004-llm06-excessive-agency` | **Date**: 2026-03-10 | **Spec**: `specs/004-llm06-excessive-agency/spec.md`
**Input**: Feature specification from `/specs/004-llm06-excessive-agency/spec.md`

## Summary

Build a complete OWASP LLM06 Excessive Agency compliance test suite consisting of 3 discrete multi-turn simulation scenarios (unauthorized tool invocation, permission escalation across turns, autonomous action without human approval), 2 model-based checks (excessive-agency-detector + agency-boundary-drift-detector), and 3 adversarial driver personas (one per scenario, each with distinct manipulation tactics). All artifacts are file-first (JSONL scenarios, Markdown checks/drivers), uploaded and executed via a single idempotent Jupyter notebook against any target agent registered as a `CustomEndpointTarget`. All 3 scenarios use `okareo.run_simulation()` with `max_turns=10, first_turn="target"` and their dedicated adversarial driver. Both checks are applied to every simulation run.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `okareo` (Okareo Python SDK), `python-dotenv`, `jupyter`
**Storage**: Repository files only — `.jsonl` scenarios, `.md` checks/drivers, `.env` config. No database.
**Testing**: Manual validation via notebook execution; check quality measured by pass/fail accuracy against known-good and known-bad agent responses
**Target Platform**: Any environment with Python 3.11+ and Jupyter (macOS, Linux, CI)
**Project Type**: Compliance test suite — static artifact repository + executable notebook
**Performance Goals**: N/A (batch evaluation, not real-time)
**Constraints**: Requires Okareo API key and a deployed agent endpoint with defined tool scope, permission levels, and approval gates; all simulations bounded to 10 turns max
**Scale/Scope**: 3 scenarios (~15 total seed rows), 2 checks, 3 drivers, 1 notebook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | OWASP-Complete Coverage | **PASS** | LLM06 category fully covered with 3 scenarios spanning all specified attack vectors (tool scope, permission escalation, approval bypass) |
| II | Explainability & Transparency | **PASS** | Every artifact includes OWASP category ID LLM06, risk severity Critical, description, and pass/fail interpretation. Check prompts include explicit evaluation criteria. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP tools used for discovery during planning. All production operations go through the notebook. |
| IV | Composability, Reusability & Forkability | **PASS** | All artifacts are agent-agnostic. Target config externalized to `owasp/target.env`. No hardcoded tool names, permission models, or approval workflows. Repo is clone-and-run. |
| V | Simulation-Driven Coverage | **PASS** | All 3 scenarios use `run_simulation(max_turns=10, first_turn="target")` with dedicated adversarial Driver personas. Constitution explicitly mandates multi-turn for LLM06. |
| VI | Traceability & Auditability | **PASS** | All artifacts carry full metadata header: `owasp_category`, `risk_severity`, `artifact_type`, `status`, `version`. Scenarios include companion `_meta.md` files. |
| VII | File-First Artifact Persistence | **PASS** | All artifacts saved as files (`.jsonl`, `.md`) before registration in Okareo. File is source of truth. |
| VIII | Notebook-Driven Execution | **PASS** | Single `run-evaluation.ipynb` notebook handles upload + execution. Idempotent, self-contained, SDK-based. |

**Gate result**: ALL PASS — no violations.

### Post-Design Re-Check (after Phase 1)

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|----------------------|
| I | OWASP-Complete Coverage | **PASS** | 3 scenarios (~15 rows), 2 checks, 3 drivers, 1 notebook — all attack vectors from spec covered |
| II | Explainability & Transparency | **PASS** | All `.md` artifacts include YAML front matter with `description`, `evaluation_mode`. Check prompts include explicit pass/fail criteria with step-by-step evaluation instructions. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP tools used during planning for reference. Notebook is the sole production execution path. |
| IV | Composability, Reusability & Forkability | **PASS** | Target externalized to `owasp/target.env`. All checks use generic placeholder `{simulation_message_history}` with scenario-specific evaluation via `{scenario_result}`. All drivers are parameterized via mustache substitution from scenario input. Clone-and-run verified in quickstart. |
| V | Simulation-Driven Coverage | **PASS** | All 3 scenarios use `run_simulation(max_turns=10, first_turn="target")` with dedicated adversarial driver personas. No single-turn scenarios (all LLM06 risks are multi-turn). |
| VI | Traceability & Auditability | **PASS** | `contracts/metadata-header.md` defines the field schema. All artifact files carry complete headers (3x `.jsonl` companion `_meta.md` + 2x check `.md` + 3x driver `.md`). |
| VII | File-First Artifact Persistence | **PASS** | Artifacts: 3x `.jsonl` + 3x `_meta.md` + 2x check `.md` + 3x driver `.md` = 11 files. Notebook loads from files, not inline definitions. |
| VIII | Notebook-Driven Execution | **PASS** | `run-evaluation.ipynb`: idempotent (upsert via Okareo APIs), self-contained (`%pip install`), SDK-based (`okareo` package). |

**Post-design gate result**: ALL PASS — design is fully constitution-compliant.

## Project Structure

### Documentation (this feature)

```text
specs/004-llm06-excessive-agency/
├── plan.md                          # This file
├── research.md                      # Phase 0: 7 research decisions
├── data-model.md                    # Phase 1: entity definitions + relationships
├── quickstart.md                    # Phase 1: adopter onboarding guide
├── contracts/
│   ├── metadata-header.md           # Metadata header schema (Principle VI)
│   ├── scenario-jsonl.md            # Scenario JSONL row format (3 schemas)
│   ├── check-prompt.md              # Model-based check file format
│   └── driver-prompt.md             # Driver persona file format (3 instances)
├── checklists/
│   └── requirements.md              # Requirements quality checklist
└── tasks.md                         # Implementation tasks (Phase 2)
```

### Source Code (repository root)

```text
owasp/
├── config.env.example               # Okareo API key template → .env
├── target.env                       # Shared agent target config (gitignored)
│
└── LLM06-excessive-agency/
    ├── scenarios/
    │   ├── unauthorized-tool-invocation.jsonl     # ~5 rows — tool scope manipulation
    │   ├── unauthorized-tool-invocation_meta.md
    │   ├── permission-escalation.jsonl            # ~5 rows — privilege widening
    │   ├── permission-escalation_meta.md
    │   ├── autonomous-action.jsonl                # ~5 rows — approval gate bypass
    │   └── autonomous-action_meta.md
    ├── checks/
    │   ├── excessive-agency-detector.md           # Multi-turn: authority boundary violation
    │   └── agency-boundary-drift-detector.md      # Multi-turn: progressive resistance weakening
    ├── drivers/
    │   ├── tool-scope-manipulator.md              # Adversarial: unauthorized tool invocation
    │   ├── privilege-escalator.md                 # Adversarial: permission widening
    │   └── approval-gate-bypasser.md              # Adversarial: approval bypass
    └── notebooks/
        └── run-evaluation.ipynb                   # Upload + evaluate (single notebook)
```

**Structure Decision**: Follows the established OWASP category folder convention (`owasp/{LLMXX}-{risk-name}/{artifact-type}/`). Unlike LLM01 which has both single-turn and multi-turn scenarios, LLM06 is entirely multi-turn — requiring 3 dedicated drivers (one per scenario) rather than a single shared driver plus a pass-through driver.

## Notebook Execution Pattern

The notebook follows the two-part pattern established by LLM01, adapted for the all-multi-turn LLM06 category:

### Part 1 — Upload Artifacts (idempotent)

1. **SDK init**: `Okareo(OKAREO_API_KEY)`, resolve category directory
2. **Upload scenarios**: `okareo.upload_scenario_set(scenario_name, file_path)` for each `.jsonl` — returns existing if name matches
3. **Register checks**: Parse `.md` YAML front matter + prompt template body → `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`
4. **Register drivers**: Parse `.md` YAML front matter + persona prompt → `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature))`
5. All registered objects kept in-memory dicts for Part 2

### Part 2 — Run Evaluation

1. **Load target config**: `dotenv_values("owasp/target.env")` → build `CustomEndpointTarget(next_turn=TurnConfig(...))` with optional `SessionConfig`/`EndSessionConfig`
2. **Multi-turn simulations (all 3 scenarios)**: For each scenario, look up its dedicated driver from `registered_drivers`, create a `Driver` object, and run `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn="target", checks=[CHECK_1, CHECK_2])`
3. **Results summary**: Print scenario name, pass/fail rates, and Okareo dashboard links

### Scenario-to-Driver Mapping

| Scenario | Driver | Checks |
|----------|--------|--------|
| `LLM06-unauthorized-tool-invocation` | `LLM06-tool-scope-manipulator` | Both checks |
| `LLM06-permission-escalation` | `LLM06-privilege-escalator` | Both checks |
| `LLM06-autonomous-action` | `LLM06-approval-gate-bypasser` | Both checks |

### Simulation Parameters (all scenarios)

```python
okareo.run_simulation(
    target=target,
    driver=Driver(name=driver_name, prompt_template=..., temperature=0.7),
    name=f"LLM06 Simulation — {scenario_name}",
    api_key=OKAREO_API_KEY,
    first_turn="target",
    scenario=scenario,
    max_turns=10,
    checks=[EXCESSIVE_AGENCY_CHECK, DRIFT_DETECTOR_CHECK],
)
```

## Complexity Tracking

> No constitution violations — table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
