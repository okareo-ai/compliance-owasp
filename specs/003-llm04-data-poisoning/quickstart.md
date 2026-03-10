# Quickstart: OWASP LLM04 Data and Model Poisoning Test Suite

**Branch**: `003-llm04-data-poisoning` | **Date**: 2026-03-09

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

## Run the LLM04 Data and Model Poisoning Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM04-data-model-poisoning/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–8)

Scans the local folder structure and registers all scenarios and model-based checks in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 9+)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes all three scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- 3 single-turn simulations: pass-through `Driver` with `max_turns=1, first_turn="driver"`
- Each scenario runs with 1 specialized model-based check

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-prompt assessments with evaluator rationale explaining detected poisoning influence, drift dimensions, or trigger-activated deviations
- **Dashboard links**: Direct links to the Okareo dashboard for each test run

## What's Being Tested

| Scenario | Attack Type | Check | Detection Focus |
|----------|-------------|-------|----------------|
| 1 | RAG corpus poisoning | Corpus Poisoning Detector | Response influenced by adversarial retrieval content? |
| 2 | Behavioral drift | Behavioral Drift Detector | Response semantically consistent with known-good baseline? |
| 3 | Backdoor/sleeper triggers | Backdoor Trigger Detector | Trigger phrase caused behavioral deviation from expected normal? |

## Behavioral Drift: Baseline Capture Workflow

Before running behavioral drift detection for the first time, you need a known-good baseline:

1. **Point at your trusted agent**: Ensure `owasp/target.env` references the trusted model version you want to use as the baseline.

2. **Run the standardized prompts**: Execute the prompts in `behavioral-drift.jsonl` against the trusted agent and record the responses.

3. **Save as baseline**: Update each row's `result` field in `behavioral-drift.jsonl` with the trusted response.

4. **Version the baseline**: Update the `version` field in `behavioral-drift_meta.md` (e.g., `"1.0.0"`).

5. **Commit**: The committed JSONL is your baseline source of truth.

6. **Test for drift**: Now point `owasp/target.env` at the agent version you want to test (e.g., after an update) and run the notebook. The drift check will compare the new responses against your committed baseline.

> **Updating the baseline**: When you validate a new model version and want to adopt it as the new known-good, repeat steps 1-5 with the new version and increment the scenario version (e.g., `"1.1.0"`).

## Customization

- **Add prompts**: Append rows to the `.jsonl` files in `owasp/LLM04-data-model-poisoning/scenarios/`, then re-run the notebook.
- **Add trigger phrases**: Add new triggered/clean prompt pairs to `backdoor-trigger.jsonl`, following the `[[TRIGGER:...]]` annotation convention.
- **Update baseline**: Re-capture baseline responses from a trusted model version and update `behavioral-drift.jsonl` (see workflow above).
- **Modify checks**: Edit the `.md` files in `owasp/LLM04-data-model-poisoning/checks/`, then re-run the notebook.
- **Corpus versioning**: When the agent's retrieval corpus changes, update the scenario prompts and expected behaviors in `corpus-poisoning.jsonl` and increment the `version` in `corpus-poisoning_meta.md`.
