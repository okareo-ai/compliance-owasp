# Quickstart: OWASP LLM09 Misinformation Test Suite

**Branch**: `009-llm09-misinformation` | **Date**: 2026-03-11

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

## Run the LLM09 Misinformation Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM09-misinformation/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–8)

Scans the local folder structure and registers all scenarios and checks in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 9–15)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes all 3 scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- 3 single-turn tests: pass-through `Driver` with `max_turns=1, first_turn="driver"`, each with its paired model-based check

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-prompt assessments with evaluator rationale explaining why each response passed or failed

Each result includes OWASP traceability: category ID (LLM09), risk severity (Medium), scenario name, and check name.

## What's Being Tested

| Scenario | Misinformation Type | Domains | Rows |
|----------|-------------------|---------|------|
| 1 | Factual hallucination (confident falsehoods) | History, science, geography, current affairs | ~12 |
| 2 | Fabricated citations/references | Paper titles, authors, DOIs, URLs | ~12 |
| 3 | Misleading high-stakes output | Medical, legal, financial | ~12 |

## Customization

- **Add prompts**: Append rows to the `.jsonl` files in `owasp/LLM09-misinformation/scenarios/`, update `row_count` in the companion `_meta.md` file, then re-run the notebook.
- **Modify checks**: Edit the `.md` files in `owasp/LLM09-misinformation/checks/`, then re-run the notebook.
- **Add domains**: For high-stakes scenarios, add rows covering additional domains (e.g., engineering safety, pharmaceutical) following the same `input`/`result` format.
