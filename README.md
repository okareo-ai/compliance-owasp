# OWASP LLM Top 10 & Agentic AI Top 10 Compliance Suite

A standalone, forkable repository for running **OWASP LLM Top 10 (2025)** and **OWASP Agentic AI Top 10 (2026)** compliance testing against your AI agents using [Okareo](https://okareo.com). All scenarios, checks, drivers, and execution notebooks are included as files—no database or external state beyond an Okareo API key.

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip
- **Okareo account** — [Sign up](https://app.okareo.com) and obtain an API key

### 1. Clone and configure

```bash
git clone https://github.com/okareo-ai/compliance-owasp.git
cd compliance-owasp
cp owasp/config.env.example .env

# If your target is non-streaming, then copy the vanilla example
cp owasp/target.json.example owasp/target.json

# If your target is streaming, then copy the streaming example
cp owasp/target.json.streaming-example owasp/target.json

# Edit .env (OKAREO_API_KEY/OKAREO_BASE_URL) and owasp/target.json (your agent)
```

### 2. Install dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install .
```

### 3. Run an evaluation

```bash
# Via CLI (if venv is activated)
python run_suite.py --dir LLM01-prompt-injection

# Or via uv (no activation needed)
uv run python run_suite.py --dir LLM01-prompt-injection

# Or via notebook
# Open owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb and run all cells
```

### CLI Runner (`run_suite.py`)

`run_suite.py` is a command-line alternative to the notebooks. It uploads all artifacts (scenarios, checks, drivers) and runs the full evaluation in one command.

```bash
# Run a full suite
python run_suite.py --dir LLM06-excessive-agency

# Override max turns for multi-turn simulations
python run_suite.py --dir LLM06-excessive-agency --max-turns 8

# Run a single simulation by name substring
python run_suite.py --dir LLM07-system-prompt-leakage --sim iterative-extraction

# Upload artifacts only (no evaluation)
python run_suite.py --dir LLM01-prompt-injection --upload-only

# Use a different target config (e.g. for a separate environment)
python run_suite.py --dir LLM01-prompt-injection --target owasp/target.prod.json

# Run an agentic AI category
python run_suite.py --dir ASI01-agent-goal-hijack

# Run ASI08 bridge simulation (monitor auto-created when required by selected simulation config)
python run_suite.py --dir ASI08-cascading-failures
```

| Flag | Description |
|------|-------------|
| `--dir` | **(required)** Category directory name under `owasp/` (e.g. `LLM01-prompt-injection` or `ASI01-agent-goal-hijack`) |
| `--max-turns` | Override max turns for all multi-turn simulations |
| `--sim` | Run only simulations whose scenario name contains this substring |
| `--upload-only` | Upload artifacts without running evaluation |
| `--eval-only` | Run evaluation only (assumes artifacts are already uploaded) |
| `--target` | Path to target config file (default: `owasp/target.json`) |

Simulation entries in `eval_config.json` can declare monitor behavior via:
- `"requires_monitor": true`
- Optional `"monitor_checks": ["..."]` (defaults to that simulation's `checks`)

When a selected simulation requires monitor setup, `run_suite.py` automatically ensures the monitor before evaluation.
For ASI08 trace-bridge, monitor checks are scoped to `ASI08-cascade-failure-trace-bridge-detector`.

#### ASI08 Trace-Bridge Quick Start

The ASI08 category includes a trace-simulation bridge that links live OTEL traces to simulation runs via `context_token`/`session.id`. Use the dedicated target example and bridge notebook for this flow:

```bash
# 1) Configure environment and trace-bridge target
cp owasp/config.env.example .env
cp owasp/target.json.trace-bridge-example owasp/target.json
# Edit .env (OKAREO_API_KEY) and owasp/target.json (your agent endpoint)
uv sync

# 2) Upload only the ASI08 trace-bridge artifacts
uv run python run_suite.py --dir ASI08-cascading-failures --sim pipeline-cascade-failure --upload-only

# 3) Run only the bridge simulation (shared ASI08 monitor is auto-created)
uv run python run_suite.py --dir ASI08-cascading-failures --sim pipeline-cascade-failure --max-turns 8

# 4) Continue with the trace-bridge notebook for OTEL trace ingestion
#    and online datapoint evaluation:
#    owasp/ASI08-cascading-failures/notebooks/run-trace-bridge-evaluation.ipynb
```

The CLI path automatically performs monitor setup for selected simulations that require it (via per-simulation `"requires_monitor": true` in `eval_config.json`). This creates (or reuses) a single category monitor instead of creating one monitor per session/context token, and updates monitor checks when needed. The remaining trace-simulation bridge steps (OTEL trace ingestion and online datapoint evaluation) still run in the dedicated notebook. See `.copilot/design/asi08-integration-notes.md` for ADK `session.id` wiring guidance.

---

## 1. Purpose and Approach

### What This Project Does

This project provides a complete test suite for validating AI agents against the **OWASP LLM Top 10** and **OWASP Agentic AI Top 10** security and safety controls. It covers 20 categories (LLM01–LLM10, ASI01–ASI10) with:

- **60 discrete test scenarios** — single-turn evaluations and multi-turn simulations
- **Adversarial driver personas** — synthetic attackers that probe for vulnerabilities
- **Model-based and code-based checks** — detect injection, leakage, excessive agency, and more
- **Reproducible, auditable execution** — Jupyter notebooks that upload artifacts and run evaluations

### Approach

| Principle | Description |
|-----------|-------------|
| **File-first** | All scenarios (`.jsonl`), checks (`.md` / `.py`), and drivers (`.md`) live in the repo. Okareo is a deployment target; the repo is the source of truth. |
| **Notebook-driven** | Every OWASP category has a `run-evaluation.ipynb` that uploads artifacts and runs tests. Re-running is idempotent. |
| **Simulation for agent risks** | Multi-turn simulation (via Okareo Drivers) is used for LLM01, LLM06, LLM07, LLM10 and most ASI categories (ASI01–ASI03, ASI06, ASI09, ASI10). Single-turn checks suffice for stateless risks (LLM02, LLM05, LLM09). |
| **Explainable** | Every artifact includes OWASP category ID, risk severity, and plain-language descriptions. Results are traceable for compliance reporting. |

### OWASP Categories Covered

| ID | Category | Severity |
|----|----------|----------|
| LLM01 | Prompt Injection | Critical |
| LLM02 | Sensitive Information Disclosure | Critical |
| LLM03 | Supply Chain Vulnerabilities | High |
| LLM04 | Data and Model Poisoning | High |
| LLM05 | Improper Output Handling | High |
| LLM06 | Excessive Agency | Critical |
| LLM07 | System Prompt Leakage | High |
| LLM08 | Vector and Embedding Weaknesses | High |
| LLM09 | Misinformation | Medium |
| LLM10 | Unbounded Consumption | Medium |

### OWASP Agentic AI Categories Covered

| ID | Category | Severity |
|----|----------|----------|
| ASI01 | Agent Goal Hijack | Critical |
| ASI02 | Tool Misuse and Exploitation | Critical |
| ASI03 | Identity and Privilege Abuse | Critical |
| ASI04 | Agentic Supply Chain Vulnerabilities | High |
| ASI05 | Unexpected Code Execution (RCE) | Critical |
| ASI06 | Memory & Context Poisoning | Critical |
| ASI07 | Insecure Inter-Agent Communication | High |
| ASI08 | Cascading Failures | High |
| ASI09 | Human-Agent Trust Exploitation | High |
| ASI10 | Rogue Agents | Critical |

---

## 2. Setup: Notebooks and Okareo

### Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip
- **Okareo account** — [Sign up](https://app.okareo.com) and obtain an API key
- **Jupyter** — for running notebooks (included as a dev dependency, or use VS Code / Cursor)

### Step 1: Clone the Repository

```bash
git clone https://github.com/okareo-ai/compliance-owasp.git
cd compliance-owasp
```

### Step 2: Install Dependencies

```bash
# Using uv (recommended) — creates a virtualenv and installs all dependencies
uv sync

# Or using pip in your own virtualenv
python -m venv .venv && source .venv/bin/activate
pip install .
```

### Step 3: Configure Okareo API Key

```bash
cp owasp/config.env.example .env
```

Edit `.env` and set your Okareo API key:

```
OKAREO_API_KEY=your_okareo_api_key_here

# Optional: override the Okareo API base URL (defaults to https://api.okareo.com)
# OKAREO_BASE_URL=https://api.okareo.com
```

### Step 4: Configure Your Target Agent

Two example configs are provided — choose the one that matches your target:

```bash
# Standard (non-streaming) target
cp owasp/target.json.example owasp/target.json

# SSE streaming target (e.g. OpenAI-compatible or custom streaming endpoint)
cp owasp/target.json.streaming-example owasp/target.json
```

Edit `owasp/target.json` with your agent's endpoint and request format:

- `name` — human-readable name for the agent
- `endpoint_url` — HTTP endpoint that accepts user messages and returns responses
- `request_body` — JSON object template (use `{latest_message}` for the user message)
- `response_path` — JSONPath to the assistant's response text (e.g. `response` or `choices[0].message.content`)

See `owasp/target.json.example` for full options (auth, session management). The streaming example additionally includes `streaming.stop` and `streaming.select` conditions for SSE event parsing.

### Step 5: Run a Notebook

Open any category notebook, for example:

```
owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb
```

Run all cells. The notebook will:

1. Upload scenarios, checks, and drivers from the local folder
2. Run the evaluation against your target agent
3. Display results

### Project Layout

```
owasp/
├── config.env.example      # → copy to .env (OKAREO_API_KEY)
├── target.json.example     # → copy to owasp/target.json (agent config)
├── common.py               # Shared utilities for all notebooks
├── LLM01-prompt-injection/
│   ├── scenarios/         # .jsonl test inputs
│   ├── checks/            # Model-based (.md) and code-based (.py) checks
│   ├── drivers/           # Adversarial personas (.md)
│   └── notebooks/
│       └── run-evaluation.ipynb
├── LLM02-sensitive-info-disclosure/
│   └── ...
├── ... (LLM03–LLM10)
├── ASI01-agent-goal-hijack/
│   ├── scenarios/
│   ├── checks/
│   ├── drivers/
│   └── notebooks/
│       └── run-evaluation.ipynb
├── ASI02-tool-misuse-exploitation/
│   └── ...
└── ... (ASI03–ASI10)
```

---

## 3. Fork and Modify for Your Agent

### Fork the Repo

1. **Fork** this repository to your organization or personal account.
2. **Clone** your fork locally.

### Point at Your Agent

1. Copy `owasp/target.json.example` to `owasp/target.json`.
2. Set `endpoint_url` to your agent's chat/API endpoint.
3. Adjust `request_body` and `response_path` to match your API contract.

All category notebooks read from `owasp/target.json`, so one config drives the full suite.

### Customize for Your Use Case

| What to Change | Where | Notes |
|----------------|--------|-------|
| **Scenarios** | `owasp/LLMxx-*/scenarios/*.jsonl` or `owasp/ASIxx-*/scenarios/*.jsonl` | Add or edit seed inputs for your domain (e.g. network, finance, healthcare). |
| **Checks** | `owasp/LLMxx-*/checks/*.md` or `owasp/ASIxx-*/checks/*.md` (or `*.py`) | Add model-based or code-based checks for your policies. |
| **Drivers** | `owasp/LLMxx-*/drivers/*.md` or `owasp/ASIxx-*/drivers/*.md` | Add adversarial personas that match your threat model. |
| **Target config** | `owasp/target.json` | Use different config files (e.g. `target.prod.json`) for multiple environments. |

### Example: Network Infrastructure Agent

See `agent-use-cases/network-infrastructure-agent-analysis.md` for a worked example mapping a multi-agent network assurance system (Ciena Navigator RSD) to this suite. It shows how to:

- Map domain threats (e.g. BGP injection, NETCONF misuse) to OWASP categories
- Add domain-specific scenarios and checks
- Handle indirect injection via mocked API responses

### Artifact Conventions

- **Scenarios**: JSON Lines (`.jsonl`), one row per seed input.
- **Checks**: Markdown (`.md`) with frontmatter and `## Prompt Template`, or Python (`.py`) with a check function.
- **Drivers**: Markdown (`.md`) with frontmatter and `## Persona Prompt Template`.

All artifacts should include metadata: `owasp_category`, `risk_severity`, `artifact_type`, `status`, `version`.

---

## 4. Specify / Spec-Kit

This project uses [Spec-Kit](https://github.com/github/spec-kit) for spec-driven development. Spec-Kit provides a **Specify → Plan → Tasks → Implement** workflow with Cursor integration.

### What Spec-Kit Provides

- **Specification-first** — feature specs before implementation
- **Slash commands** — `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, etc.
- **Constitution** — project principles in `.specify/memory/constitution.md`
- **Templates** — specs, plans, tasks in `.specify/templates/`

### Setting Up Spec-Kit

1. **Install the Spec-Kit CLI** (optional, for `specify` commands):

   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```

2. **Initialize in an existing project** (if starting fresh):

   ```bash
   specify init --here
   ```

3. **Use Cursor commands** — This repo already includes Spec-Kit integration in `.cursor/commands/` and `.cursor/rules/`. The slash commands are:

   | Command | Purpose |
   |---------|---------|
   | `/speckit.specify` | Create a feature specification from a description |
   | `/speckit.clarify` | Ask clarification questions about the spec |
   | `/speckit.plan` | Create a technical implementation plan |
   | `/speckit.tasks` | Break the plan into dependency-ordered tasks |
   | `/speckit.checklist` | Generate a requirements quality checklist |
   | `/speckit.analyze` | Cross-artifact consistency analysis |
   | `/speckit.implement` | Execute implementation from the task list |
   | `/speckit.taskstoissues` | Convert tasks into GitHub issues |

4. **Key references**:
   - **Constitution**: `.specify/memory/constitution.md` — non-negotiable project principles
   - **Templates**: `.specify/templates/` — spec, plan, tasks, checklist templates
   - **Scripts**: `.specify/scripts/bash/` — setup and feature-creation scripts

### Spec-Kit Resources

- **GitHub**: [github/spec-kit](https://github.com/github/spec-kit)
- **Documentation**: See the repo README and `.specify/` folder in this project

