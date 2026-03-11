# Quickstart: OWASP LLM03 Supply Chain Vulnerabilities Test Suite

**Branch**: `007-llm03-supply-chain` | **Date**: 2026-03-11

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

## Run the LLM03 Supply Chain Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM03-supply-chain/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (idempotent)

Scans the local folder structure and registers all scenarios and checks in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation**

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes both scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- **Scenario 1 — Behavioral validation**: Pass-through `Driver` with `max_turns=1, first_turn="driver"`, checked by model-based `behavioral-boundary-detector`
- **Scenario 2 — Provenance integrity**: Pass-through `Driver` with `max_turns=1, first_turn="driver"`, checked by code-based `provenance-integrity-check`

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-row assessments with evaluator rationale (behavioral) or validation details (provenance)

## What's Being Tested

| Scenario | Risk Category | Eval Mode | Check Type |
|----------|---------------|-----------|------------|
| 1 | Third-party model behavioral validation (undocumented capabilities) | Single-turn | Model-based |
| 2 | Dependency and provenance integrity (signatures, versions, SBOM, licenses) | Single-turn | Code-based |

## Customization

- **Add behavioral probes**: Append rows to `owasp/LLM03-supply-chain/scenarios/behavioral-validation.jsonl`, then re-run the notebook.
- **Add provenance test cases**: Append rows to `owasp/LLM03-supply-chain/scenarios/provenance-integrity.jsonl`, then re-run the notebook.
- **Modify the behavioral check**: Edit `owasp/LLM03-supply-chain/checks/behavioral-boundary-detector.md`, then re-run the notebook.
- **Modify the provenance check**: Edit `owasp/LLM03-supply-chain/checks/provenance-integrity-check.py`, then re-run the notebook.
- **Adjust license policy**: Update the `policy.allowed_licenses` field in the provenance integrity scenario rows to match your organization's license requirements.
