# Quickstart: OWASP LLM02 Sensitive Information Disclosure Test Suite

**Branch**: `002-llm02-sensitive-disclosure` | **Date**: 2026-03-09

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

## Run the LLM02 Sensitive Information Disclosure Suite

Open and run the single unified notebook:

```bash
jupyter notebook owasp/LLM02-sensitive-info-disclosure/notebooks/run-evaluation.ipynb
```

The notebook runs in two parts:

**Part 1 — Upload Artifacts** (cells 1–12)

Scans the local folder structure and registers all scenarios, model-based checks, and the code-based regex check in Okareo. This is idempotent — re-running will not create duplicates. Registered objects are held in memory and passed directly to the evaluation steps below.

**Part 2 — Run Evaluation** (cells 13+)

The configuration cell automatically loads `owasp/target.env` — no inline edits needed. Run all cells.

The evaluation executes all three scenarios using `okareo.run_simulation()` targeting your registered `CustomEndpointTarget`:

- 3 single-turn simulations: pass-through `Driver` with `max_turns=1, first_turn="driver"`
- Each scenario runs with 2 checks simultaneously:
  - **Regex check** (`sensitive-pattern-detector.py`): Deterministic pattern detection
  - **Model-based check** (scenario-specific `.md`): Contextual leakage evaluation

## Review Results

Results are displayed inline in the notebook:

- **Aggregate**: Pass/fail rates per scenario, with breakdown by check type
- **Detailed**: Per-prompt assessments showing which check(s) flagged each row
- **Pattern matches**: When the regex check fails, the explanation lists every detected pattern category and matched value

## What's Being Tested

| Scenario | Attack Type | Checks Applied |
|----------|-------------|---------------|
| 1 | PII exfiltration probes (SSN, email, phone, financial data) | Regex + Sensitive Info Leakage Detector |
| 2 | Training data extraction (memorization probes, verbatim reproduction) | Regex + Training Data Extraction Detector |
| 3 | Credential/secret leakage (API keys, tokens, URLs, connection strings) | Regex + Sensitive Info Leakage Detector |

## Dual-Check Architecture

Every agent response is evaluated by two independent checks:

```text
Agent Response
     │
     ├──→ Regex Check (code-based)
     │       Catches: SSNs, emails, API keys, JWTs, connection strings, etc.
     │       Strength: Zero false negatives for known formats
     │
     └──→ Model-Based Check (prompt template)
            Catches: Contextual leakage, paraphrased secrets, fabricated PII
            Strength: Semantic understanding of leakage context

A row FAILS if EITHER check flags it.
```

## Customization

- **Add prompts**: Append rows to the `.jsonl` files in `owasp/LLM02-sensitive-info-disclosure/scenarios/`, then re-run the notebook.
- **Add regex patterns**: Edit `owasp/LLM02-sensitive-info-disclosure/checks/sensitive-pattern-detector.py` to add new pattern categories, then re-run the notebook.
- **Modify model-based checks**: Edit the `.md` files in `owasp/LLM02-sensitive-info-disclosure/checks/`, then re-run the notebook.
- **International PII**: Add regex patterns for non-US PII formats (e.g., EU national IDs, IBAN) to the code-based check.
