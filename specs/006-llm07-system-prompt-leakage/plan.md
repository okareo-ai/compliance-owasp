# Implementation Plan: OWASP LLM07 System Prompt Leakage Test Suite

**Branch**: `006-llm07-system-prompt-leakage` | **Date**: 2026-03-10 | **Spec**: `specs/006-llm07-system-prompt-leakage/spec.md`  
**Input**: Feature specification from `/specs/006-llm07-system-prompt-leakage/spec.md`

## Summary

Build a complete OWASP LLM07 System Prompt Leakage compliance test suite consisting of 3 discrete attack scenarios (direct extraction, iterative multi-turn extraction, tool schema/config leakage), 2 model-based checks (single-turn leakage detector + multi-turn cumulative extraction detector), and 1 probing driver persona. All artifacts are file-first (JSONL scenarios, Markdown checks/drivers), uploaded and executed via a single idempotent Jupyter notebook against any target agent registered as a `CustomEndpointTarget`. Scenarios 1 and 3 use `okareo.run_simulation()` with a pass-through `Driver` (`max_turns=1, first_turn="driver"`); Scenario 2 uses a probing driver persona with `max_turns=10, first_turn="target"` (agent greets first, then driver begins iterative probing). Checks apply a three-category disclosure taxonomy: verbatim reproduction, structural disclosure, and behavioral confirmation — all three scored as failures.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `okareo` (Okareo Python SDK), `python-dotenv`, `jupyter`  
**Storage**: Repository files only — `.jsonl` scenarios, `.md` checks/drivers, `.env` config. No database.  
**Testing**: Manual validation via notebook execution; check quality measured by pass/fail accuracy against known-good and known-bad agent responses  
**Target Platform**: Any environment with Python 3.11+ and Jupyter (macOS, Linux, CI)  
**Project Type**: Compliance test suite — static artifact repository + executable notebook  
**Performance Goals**: N/A (batch evaluation, not real-time)  
**Constraints**: Requires Okareo API key and a deployed agent endpoint; multi-turn simulations bounded to 10 turns max  
**Scale/Scope**: 3 scenarios (~37 total seed rows), 2 checks, 1 probing driver, 1 pass-through driver, 1 notebook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | OWASP-Complete Coverage | **PASS** | LLM07 category fully covered with 3 scenarios spanning all specified leakage vectors |
| II | Explainability & Transparency | **PASS** | Every artifact includes OWASP category ID (LLM07), risk severity (High), description, and pass/fail interpretation. Check prompts include explicit three-category disclosure taxonomy. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP tools used for discovery during planning. All production operations go through the notebook. |
| IV | Composability, Reusability & Forkability | **PASS** | All artifacts are agent-agnostic. Target config externalized to `owasp/target.env`. No hardcoded model assumptions. Repo is clone-and-run. |
| V | Simulation-Driven Coverage | **PASS** | Scenario 2 (iterative extraction) uses `run_simulation(max_turns=10, first_turn="target")` with probing `Driver` persona. |
| VI | Traceability & Auditability | **PASS** | All artifacts carry full metadata header: `owasp_category`, `risk_severity`, `artifact_type`, `status`, `version`. Scenarios include companion `_meta.md` files. |
| VII | File-First Artifact Persistence | **PASS** | All artifacts saved as files (`.jsonl`, `.md`) before registration in Okareo. File is source of truth. |
| VIII | Notebook-Driven Execution | **PASS** | Single `run-evaluation.ipynb` notebook handles upload + execution. Idempotent, self-contained, SDK-based. |

**Gate result**: ALL PASS — no violations.

### Post-Design Re-Check (after Phase 1)

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|----------------------|
| I | OWASP-Complete Coverage | **PASS** | 3 scenarios (37 rows), 2 checks, 1 probing driver, 1 pass-through driver, 1 notebook — all leakage vectors from spec covered |
| II | Explainability & Transparency | **PASS** | All `.md` artifacts include YAML front matter with `description`, `evaluation_mode`. Check prompts include explicit three-category disclosure taxonomy with pass/fail rationale. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP `get_templates` used during planning for SDK patterns. Notebook is the sole production execution path. |
| IV | Composability, Reusability & Forkability | **PASS** | Target externalized to `owasp/target.env`. All checks use generic placeholders (`{scenario_input}`, `{model_output}`, `{simulation_message_history}`). Driver is parameterized via mustache substitution. |
| V | Simulation-Driven Coverage | **PASS** | `iterative-extraction` scenario uses `run_simulation(max_turns=10, first_turn="target")` with `prompt-extraction-prober` driver persona. |
| VI | Traceability & Auditability | **PASS** | Contracts define the 7-field metadata schema. All artifact files carry complete headers (3x `.jsonl` companion `_meta.md` + 2x check `.md` + 1x driver `.md` + 1x pass-through driver `.md`). |
| VII | File-First Artifact Persistence | **PASS** | Artifacts: 3x `.jsonl` + 3x `_meta.md` + 2x check `.md` + 2x driver `.md` = 10 files. Notebook loads from files, not inline definitions. |
| VIII | Notebook-Driven Execution | **PASS** | `run-evaluation.ipynb`: idempotent (upsert via Okareo APIs), self-contained (`%pip install`), SDK-based (`okareo` package). |

**Post-design gate result**: ALL PASS — design is fully constitution-compliant.

## Project Structure

### Documentation (this feature)

```text
specs/006-llm07-system-prompt-leakage/
├── plan.md                          # This file
├── research.md                      # Phase 0: research decisions
├── data-model.md                    # Phase 1: entity definitions + relationships
├── quickstart.md                    # Phase 1: adopter onboarding guide
├── contracts/
│   ├── metadata-header.md           # Metadata header schema (Principle VI) — references LLM01 contract
│   ├── scenario-jsonl.md            # Scenario JSONL row format (LLM07-specific multi-turn schema)
│   ├── check-prompt.md              # Model-based check file format + disclosure taxonomy
│   └── driver-prompt.md             # Driver persona file format + three-phase probing strategy
├── checklists/
│   └── requirements.md              # Requirements quality checklist (complete — all pass)
└── tasks.md                         # Implementation tasks (Phase 2 output, not created here)
```

### Source Code (repository root)

```text
owasp/
├── config.env.example               # (existing) Okareo API key template → .env
├── target.env.example               # (existing) Shared agent target template → owasp/target.env
│
└── LLM07-system-prompt-leakage/
    ├── scenarios/
    │   ├── direct-extraction.jsonl          # ~15 rows — blunt queries + known extraction techniques
    │   ├── direct-extraction_meta.md
    │   ├── iterative-extraction.jsonl       # ~5 rows — multi-turn driver parameters (object input)
    │   ├── iterative-extraction_meta.md
    │   ├── tool-schema-leakage.jsonl        # ~12 rows — tool definition + config disclosure probes
    │   └── tool-schema-leakage_meta.md
    ├── checks/
    │   ├── system-prompt-leakage-detector.md    # Single-turn: 3-category disclosure taxonomy
    │   └── iterative-extraction-detector.md     # Multi-turn: cumulative disclosure across turns
    ├── drivers/
    │   ├── pass-through-driver.md               # Single-turn: verbatim delivery to target
    │   └── prompt-extraction-prober.md          # Multi-turn: 3-phase iterative probing persona
    └── notebooks/
        └── run-evaluation.ipynb                 # Upload + evaluate (single notebook)
```

**Structure Decision**: File-based compliance artifact repository with an executable notebook layer, following the Constitution's Artifact Taxonomy (`owasp/{LLMXX}-{risk-name}/{artifact-type}/`) with a single unified notebook per category (upload + evaluation combined). No traditional source code project structure needed.

## Notebook Execution Pattern

Follows the established two-part pattern from LLM01 (all OWASP categories use this pattern):

### Part 1 — Upload Artifacts (idempotent)

1. **SDK init**: `Okareo(OKAREO_API_KEY)`, resolve category directory
2. **Upload scenarios**: `okareo.upload_scenario_set(scenario_name, file_path)` for each `.jsonl`
3. **Register checks**: Parse `.md` YAML front matter + prompt template body → `okareo.create_or_update_check(name, description, check=ModelBasedCheck(prompt_template, CheckOutputType.PASS_FAIL))`
4. **Register drivers**: Parse `.md` YAML front matter + persona prompt → `okareo.create_or_update_driver(driver=Driver(name, prompt_template, temperature))`
5. Keep all registered objects in-memory for Part 2

### Part 2 — Run Evaluation

1. **Load target config**: `dotenv_values("owasp/target.env")` → build `CustomEndpointTarget(next_turn=TurnConfig(...))`
2. **Single-turn simulations** (Scenarios 1 and 3): inline pass-through `Driver(temperature=0)` → `okareo.run_simulation(target, driver, scenario, max_turns=1, first_turn="driver", checks=["LLM07-system-prompt-leakage-detector"])`
3. **Multi-turn simulation** (Scenario 2): probing `Driver` with `max_turns=10, first_turn="target"` → `okareo.run_simulation(target, driver, scenario, max_turns=10, first_turn="target", checks=["LLM07-iterative-extraction-detector"])`
4. **Results summary**: Print scenario name, status, pass rate, and Okareo dashboard link

### Key Configuration Differences from LLM01

- **Scenario 2 uses `first_turn="target"`**: The agent greets the user first, after which the probing driver begins Phase 1 of its iterative extraction strategy. This mirrors realistic user-agent interaction where the attacker is responding to an agent that initiated the session.
- **Two distinct checks** (vs. LLM01's two): `system-prompt-leakage-detector` covers both Scenarios 1 and 3 (same disclosure taxonomy applies); `iterative-extraction-detector` covers Scenario 2 exclusively (cumulative transcript analysis).
- **LLM07-specific disclosure taxonomy**: The single-turn check evaluates three failure categories — verbatim reproduction, structural disclosure, behavioral confirmation — rather than a binary injection compliance check.

## Complexity Tracking

> No constitution violations — table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
