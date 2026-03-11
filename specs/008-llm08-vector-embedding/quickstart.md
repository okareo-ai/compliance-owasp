# Quickstart: OWASP LLM08 Vector and Embedding Weaknesses Test Suite

**Branch**: `008-llm08-vector-embedding` | **Date**: 2026-03-11

## Prerequisites

- Python 3.11+
- Jupyter Notebook or JupyterLab
- An Okareo API key (get one at https://app.okareo.com)
- A deployed agent accessible via an HTTP endpoint that uses RAG (Retrieval-Augmented Generation)

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

## Run the LLM08 Vector and Embedding Weaknesses Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM08-vector-embedding-weaknesses/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–12)

Scans the local folder structure and registers all scenarios, checks (both model-based and code-based), and the driver persona in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 13–22)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes all scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- 2 single-turn tests (Scenarios 2, 3): pass-through `Driver` with `max_turns=1, first_turn="driver"`
- 1 multi-turn simulation (Scenario 1): adversarial `Driver` (RAG injection exploiter) with `max_turns=10, first_turn="driver"`

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-prompt assessments with evaluator rationale
- **Multi-turn transcripts**: Full conversation history with per-turn compliance assessments
- **Code-based check output**: Deterministic pass/fail with identified access control violations

## What's Being Tested

| Scenario | Attack Type | Eval Mode | Check Type |
|----------|-------------|-----------|------------|
| 1 | RAG injection via poisoned retrieved content | Multi-turn simulation | Model-based (drift detection) |
| 2 | Cross-tenant / cross-scope data leakage | Single-turn | Model-based (leakage detection) |
| 3 | Vector store access control validation | Single-turn | Code-based (deterministic) |

## Customization

- **Add scenarios**: Append rows to the `.jsonl` files in `owasp/LLM08-vector-embedding-weaknesses/scenarios/`, then re-run the notebook.
- **Modify checks**: Edit the `.md` or `.py` files in `owasp/LLM08-vector-embedding-weaknesses/checks/`, then re-run the notebook.
- **Adjust simulation turns**: Change `max_turns` in the multi-turn simulation cell.
- **Add tenants/scopes**: Extend the cross-tenant scenarios with new tenant IDs and permission scopes in the JSONL files.
