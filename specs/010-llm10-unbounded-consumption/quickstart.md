# Quickstart: OWASP LLM10 Unbounded Consumption Test Suite

**Branch**: `010-llm10-unbounded-consumption` | **Date**: 2026-03-11

## Prerequisites

- Python 3.11+
- Jupyter Notebook or JupyterLab
- An Okareo API key (get one at https://app.okareo.com)
- A deployed agent accessible via an HTTP endpoint (all OWASP controls target the same agent)

## Setup

1. Clone the repository:

```bash
git clone <repo-url>
cd compliance-owasp
```

2. Configure your Okareo API key:

```bash
cp owasp/config.env.example .env
# Edit .env and set OKAREO_API_KEY=your_key_here
```

3. Configure the shared agent target:

```bash
cp owasp/target.env.example owasp/target.env
# Edit owasp/target.env and set:
#   TARGET_ENDPOINT_URL=https://your-agent.example.com/chat
#   TARGET_NAME=my-agent
#   TARGET_API_KEY=optional_auth_key
```

> **One target, all controls.** `owasp/target.env` is the single place that defines the agent under test.
> Every OWASP category notebook reads from this file. To switch agents, edit only this file.
>
> **Dependencies are installed by the notebook.** The first cell in `run-evaluation.ipynb` runs `%pip install okareo python-dotenv --quiet`, so no manual install step is required.
>
> **Key confirmation**: On initialization the notebook prints `✓ Okareo SDK initialized (key: ...XXXXX)` showing the last 5 characters of the active Okareo credential.

## Run the LLM10 Unbounded Consumption Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM10-unbounded-consumption/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–8)

Scans the local folder structure and registers all scenarios, checks, and drivers in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 9–15)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes both scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- **Scenario 1 (infinite-loop)**: Multi-turn simulation with `loop-inducing-driver` at `max_turns=10, first_turn="target"`, evaluated by `loop-detection-check`
- **Scenario 2 (resource-exhaustion)**: Multi-turn simulation with `resource-exhaustion-driver` at `max_turns=10, first_turn="driver"`, evaluated by `resource-policy-enforcement-check`

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-row assessments with evaluator rationale explaining why each simulation passed or failed

Each result includes OWASP traceability: category ID (LLM10), risk severity (Medium), scenario name, and check name.

## What's Being Tested

| Scenario | Risk Type | Driver | Rows |
|----------|-----------|--------|------|
| 1 | Infinite tool/agent loop detection | Loop-inducing (recursive/circular tool chains) | 5–8 |
| 2 | Resource exhaustion via adversarial inputs | Abusive (long prompts, rapid queries, token bombs) | 6–10 |

## Customization

- **Add prompts**: Append rows to the `.jsonl` files in `owasp/LLM10-unbounded-consumption/scenarios/`, update `row_count` in the companion `_meta.md` file, then re-run the notebook.
- **Modify checks**: Edit the `.md` files in `owasp/LLM10-unbounded-consumption/checks/`, then re-run the notebook.
- **Adjust driver behavior**: Edit the `.md` files in `owasp/LLM10-unbounded-consumption/drivers/` to change adversarial personas.
