# Implementation Plan: OWASP LLM10 Unbounded Consumption Test Suite

**Branch**: `010-llm10-unbounded-consumption` | **Date**: 2026-03-11 | **Spec**: `specs/010-llm10-unbounded-consumption/spec.md`
**Input**: Feature specification from `/specs/010-llm10-unbounded-consumption/spec.md`

## Summary

Build a complete OWASP LLM10 Unbounded Consumption compliance test suite consisting of 2 discrete multi-turn simulation scenarios (infinite tool/agent loop detection, resource exhaustion via adversarial inputs), 2 model-based checks (loop-detection-check, resource-policy-enforcement-check), and 2 adversarial driver personas (loop-inducing-driver, resource-exhaustion-driver). All artifacts are file-first (JSONL scenarios, Markdown checks/drivers), uploaded and executed via a single idempotent Jupyter notebook against any target agent registered as a `CustomEndpointTarget`. Both scenarios use `okareo.run_simulation()` with `max_turns=10` and their dedicated adversarial driver. Per Constitution Principle V, LLM10 requires multi-turn simulation for resource exhaustion through repeated calls.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `okareo` (Okareo Python SDK), `python-dotenv`, `jupyter`
**Storage**: Repository files only — `.jsonl` scenarios, `.md` checks/drivers, `.env` config. No database.
**Testing**: Manual validation via notebook execution; check quality measured by pass/fail accuracy against known-good and known-bad agent responses
**Target Platform**: Any environment with Python 3.11+ and Jupyter (macOS, Linux, CI)
**Project Type**: Compliance test suite — static artifact repository + executable notebook
**Performance Goals**: N/A (batch evaluation, not real-time)
**Constraints**: Requires Okareo API key and a deployed agent endpoint; all simulations bounded to 10 turns max
**Scale/Scope**: 2 scenarios (~12–18 total seed rows), 2 checks, 2 drivers, 1 notebook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | OWASP-Complete Coverage | **PASS** | LLM10 category fully covered with 2 scenarios spanning infinite-loop and resource-exhaustion vectors |
| II | Explainability & Transparency | **PASS** | Every artifact includes OWASP category ID (LLM10), risk severity (Medium), description, and pass/fail interpretation. Check prompts include explicit evaluation criteria. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP tools used for discovery during planning. All production operations go through the notebook. |
| IV | Composability, Reusability & Forkability | **PASS** | All artifacts are agent-agnostic. Target config externalized to `owasp/target.env`. No hardcoded tool names or resource policies. Repo is clone-and-run. |
| V | Simulation-Driven Coverage | **PASS** | Both scenarios use `run_simulation(max_turns=10)` with adversarial drivers. Constitution explicitly mandates multi-turn for LLM10. |
| VI | Traceability & Auditability | **PASS** | All artifacts carry full metadata header: `owasp_category`, `risk_severity`, `artifact_type`, `status`, `version`. Scenarios include companion `_meta.md` files. |
| VII | File-First Artifact Persistence | **PASS** | All artifacts saved as files (`.jsonl`, `.md`) before registration in Okareo. File is source of truth. |
| VIII | Notebook-Driven Execution | **PASS** | Single `run-evaluation.ipynb` notebook handles upload + execution. Idempotent, self-contained, SDK-based. |

**Gate result**: ALL PASS — no violations.

### Post-Design Re-Check (after Phase 1)

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|----------------------|
| I | OWASP-Complete Coverage | **PASS** | 2 scenarios (~12–18 rows), 2 checks, 2 drivers, 1 notebook — both unbounded consumption vectors from spec covered |
| II | Explainability & Transparency | **PASS** | All `.md` artifacts include YAML front matter with `description`, `evaluation_mode`. Check prompts include explicit pass/fail criteria with step-by-step evaluation instructions. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP used during planning for reference. Notebook is the sole production execution path. |
| IV | Composability, Reusability & Forkability | **PASS** | Target externalized to `owasp/target.env`. All checks use generic placeholder `{simulation_message_history}` with scenario-specific evaluation via `{scenario_result}`. All drivers are parameterized via mustache substitution from scenario input. Clone-and-run verified in quickstart. |
| V | Simulation-Driven Coverage | **PASS** | Both scenarios use `run_simulation(max_turns=10)` with dedicated adversarial driver personas. No single-turn scenarios (all LLM10 risks are multi-turn). |
| VI | Traceability & Auditability | **PASS** | `contracts/metadata-header.md` defines the field schema. All artifact files carry complete headers (2x `.jsonl` companion `_meta.md` + 2x check `.md` + 2x driver `.md`). |
| VII | File-First Artifact Persistence | **PASS** | Artifacts: 2x `.jsonl` + 2x `_meta.md` + 2x check `.md` + 2x driver `.md` = 8 files. Notebook loads from files, not inline definitions. |
| VIII | Notebook-Driven Execution | **PASS** | `run-evaluation.ipynb`: idempotent (upsert via Okareo APIs), self-contained (`%pip install`), SDK-based (`okareo` package). |

**Post-design gate result**: ALL PASS — design is fully constitution-compliant.

## Project Structure

### Documentation (this feature)

```text
specs/010-llm10-unbounded-consumption/
├── plan.md                          # This file
├── research.md                      # Phase 0: 7 research decisions
├── data-model.md                    # Phase 1: entity definitions + relationships
├── quickstart.md                    # Phase 1: adopter onboarding guide
├── contracts/
│   ├── metadata-header.md           # Metadata header schema (Principle VI)
│   ├── scenario-jsonl.md           # Scenario JSONL row format (2 schemas)
│   ├── check-prompt.md             # Model-based check file format
│   └── driver-prompt.md            # Driver persona file format
├── checklists/
│   └── requirements.md             # Requirements quality checklist
└── tasks.md                         # Implementation tasks (Phase 2 — /speckit.tasks)
```

### Source Code (repository root)

```text
owasp/
├── config.env.example               # Okareo API key template → .env
├── target.env                       # Shared agent target config (gitignored)
│
└── LLM10-unbounded-consumption/
    ├── scenarios/
    │   ├── infinite-loop.jsonl              # ~5–8 rows — loop-inducing prompts
    │   ├── infinite-loop_meta.md
    │   ├── resource-exhaustion.jsonl        # ~6–10 rows — abusive input patterns
    │   └── resource-exhaustion_meta.md
    ├── checks/
    │   ├── loop-detection-check.md          # Multi-turn: recursive/circular tool chains
    │   └── resource-policy-enforcement-check.md  # Multi-turn: rate limits, token budgets
    ├── drivers/
    │   ├── loop-inducing-driver.md          # Adversarial: induce tool loops
    │   └── resource-exhaustion-driver.md    # Abusive: long prompts, rapid queries, token bombs
    └── notebooks/
        └── run-evaluation.ipynb             # Upload + evaluate (single notebook)
```

**Structure Decision**: Follows the established OWASP category folder convention (`owasp/{LLMXX}-{risk-name}/{artifact-type}/`). LLM10 is entirely multi-turn — requiring 2 dedicated drivers (one per scenario), matching the LLM06 pattern for multi-turn categories.

## Notebook Execution Pattern

The notebook follows the two-part pattern established in LLM01 and LLM06:

### Part 1 — Upload Artifacts (idempotent)

1. **SDK init**: `Okareo(OKAREO_API_KEY)`, resolve category directory `owasp/LLM10-unbounded-consumption/`
2. **Upload scenarios**: `okareo.upload_scenario_set(scenario_name, file_path)` for each `.jsonl` — returns existing if name matches
3. **Register checks**: Parse `.md` YAML front matter + prompt template body → `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`
4. **Register drivers**: Parse `.md` driver files → `okareo.create_or_update_driver()` or equivalent — drivers are loaded per scenario with mustache substitution from scenario `input`
5. All registered objects kept in-memory for Part 2

### Part 2 — Run Evaluation

1. **Load target config**: `dotenv_values("owasp/target.env")` → build `CustomEndpointTarget(next_turn=TurnConfig(...))` with optional `SessionConfig`/`EndSessionConfig`
2. **Scenario 1 (infinite-loop)**: Load `loop-inducing-driver`, create `Driver` with template + scenario row `input` substitution. Run `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn="target", checks=["LLM10-loop-detection-check"])`
3. **Scenario 2 (resource-exhaustion)**: Load `resource-exhaustion-driver`, create `Driver` with template + scenario row `input` substitution. Run `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn="driver", checks=["LLM10-resource-policy-enforcement-check"])`
4. **Results summary**: Print scenario name, status, and Okareo dashboard link for each completed run

### first_turn Rationale

- **Scenario 1 (infinite-loop)**: `first_turn="target"` — agent sends greeting first; driver then begins loop-inducing prompts. Produces natural conversation flow.
- **Scenario 2 (resource-exhaustion)**: `first_turn="driver"` — driver immediately sends abusive input (long prompt, rapid query, token bomb). Maximizes pressure on the system from the first turn.

## Complexity Tracking

> No constitution violations — table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
