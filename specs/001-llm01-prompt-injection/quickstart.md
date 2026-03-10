# Quickstart: OWASP LLM01 Prompt Injection Test Suite

**Branch**: `001-llm01-prompt-injection` | **Date**: 2026-03-09

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

## Run the LLM01 Prompt Injection Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–10)

Scans the local folder structure and registers all scenarios, checks, and the driver persona in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 11–22)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes all scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- 4 single-turn tests (Scenarios 1, 2, 4, 5): pass-through `Driver` with `max_turns=1, first_turn="driver"`
- 1 multi-turn simulation (Scenario 3): adversarial `Driver` (jailbreak escalator) with `max_turns=10, first_turn="target"`

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario
- **Detailed**: Per-prompt assessments with evaluator rationale
- **Multi-turn transcripts**: Full conversation history with per-turn compliance assessments

## What's Being Tested

| Scenario | Attack Type | Eval Mode |
|----------|-------------|-----------|
| 1 | Direct prompt injection (role/instruction override) | Single-turn |
| 2 | Indirect injection (poisoned RAG/file content) | Single-turn |
| 3 | Multi-turn jailbreak escalation (crescendo attack) | Multi-turn simulation |
| 4 | Obfuscated/encoded injection (Base64, multilingual, Unicode) | Single-turn |
| 5 | Payload splitting (fragmented malicious intent) | Single-turn |

## Customization

- **Add prompts**: Append rows to the `.jsonl` files in `owasp/LLM01-prompt-injection/scenarios/`, then re-run the notebook.
- **Modify checks**: Edit the `.md` files in `owasp/LLM01-prompt-injection/checks/`, then re-run the notebook.
- **Adjust simulation turns**: Change `max_turns` in the multi-turn simulation cell.
