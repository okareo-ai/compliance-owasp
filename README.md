# OWASP LLM Top 10 Compliance Suite

A standalone, forkable repository for running **OWASP LLM Top 10 (2025)** compliance testing against your AI agents using [Okareo](https://okareo.com). All scenarios, checks, drivers, and execution notebooks are included as files—no database or external state beyond an Okareo API key.

---

## 1. Purpose and Approach

### What This Project Does

This project provides a complete test suite for validating AI agents against the **OWASP LLM Top 10** security and safety controls. It covers all 10 categories (LLM01–LLM10) with:

- **30 discrete test scenarios** — single-turn evaluations and multi-turn simulations
- **Adversarial driver personas** — synthetic attackers that probe for vulnerabilities
- **Model-based and code-based checks** — detect injection, leakage, excessive agency, and more
- **Reproducible, auditable execution** — Jupyter notebooks that upload artifacts and run evaluations

### Approach

| Principle | Description |
|-----------|-------------|
| **File-first** | All scenarios (`.jsonl`), checks (`.md` / `.py`), and drivers (`.md`) live in the repo. Okareo is a deployment target; the repo is the source of truth. |
| **Notebook-driven** | Every OWASP category has a `run-evaluation.ipynb` that uploads artifacts and runs tests. Re-running is idempotent. |
| **Simulation for agent risks** | Multi-turn simulation (via Okareo Drivers) is used for LLM01, LLM06, LLM07, LLM10. Single-turn checks suffice for stateless risks (LLM02, LLM05, LLM09). |
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

---

## 2. Setup: Notebooks and Okareo

### Prerequisites

- **Python 3.11+**
- **Okareo account** — [Sign up](https://app.okareo.com) and obtain an API key
- **Jupyter** — for running notebooks (e.g. `pip install jupyter` or use VS Code / Cursor)

### Step 1: Clone the Repository

```bash
git clone https://github.com/okareo-ai/compliance-owasp.git
cd compliance-owasp
```

### Step 2: Configure Okareo API Key

```bash
cp owasp/config.env.example .env
```

Edit `.env` and set your Okareo API key:

```
OKAREO_API_KEY=your_okareo_api_key_here
```

### Step 3: Configure Your Target Agent

```bash
cp owasp/target.env.example owasp/target.env
```

Edit `owasp/target.env` with your agent’s endpoint and request format:

- `TARGET_NAME` — human-readable name for the agent
- `TARGET_ENDPOINT_URL` — HTTP endpoint that accepts user messages and returns responses
- `TARGET_REQUEST_BODY` — JSON template (use `{latest_message}` for the user message)
- `TARGET_RESPONSE_PATH` — JSONPath to the assistant’s response text (e.g. `response` or `choices[0].message.content`)

See `owasp/target.env.example` for full options (auth, session management, etc.).

### Step 4: Install Dependencies and Run a Notebook

Each notebook installs `okareo` and `python-dotenv` via `%pip install` in the first cell. You can also install them globally:

```bash
pip install okareo python-dotenv
```

Then open any category notebook, for example:

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
├── target.env.example      # → copy to owasp/target.env (agent config)
├── common.py               # Shared utilities for all notebooks
├── LLM01-prompt-injection/
│   ├── scenarios/         # .jsonl test inputs
│   ├── checks/            # Model-based (.md) and code-based (.py) checks
│   ├── drivers/           # Adversarial personas (.md)
│   └── notebooks/
│       └── run-evaluation.ipynb
├── LLM02-sensitive-info-disclosure/
│   └── ...
└── ... (LLM03–LLM10)
```

---

## 3. Fork and Modify for Your Agent

### Fork the Repo

1. **Fork** this repository to your organization or personal account.
2. **Clone** your fork locally.

### Point at Your Agent

1. Copy `owasp/target.env.example` to `owasp/target.env`.
2. Set `TARGET_ENDPOINT_URL` to your agent’s chat/API endpoint.
3. Adjust `TARGET_REQUEST_BODY` and `TARGET_RESPONSE_PATH` to match your API contract.

All category notebooks read from `owasp/target.env`, so one config drives the full suite.

### Customize for Your Use Case

| What to Change | Where | Notes |
|----------------|--------|-------|
| **Scenarios** | `owasp/LLMxx-*/scenarios/*.jsonl` | Add or edit seed inputs for your domain (e.g. network, finance, healthcare). |
| **Checks** | `owasp/LLMxx-*/checks/*.md` or `*.py` | Add model-based or code-based checks for your policies. |
| **Drivers** | `owasp/LLMxx-*/drivers/*.md` | Add adversarial personas that match your threat model. |
| **Target config** | `owasp/target.env` | Use different env files (e.g. `target.prod.env`) for multiple environments. |

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

---

## Quick Start Summary

```bash
# 1. Clone and configure
git clone https://github.com/okareo-ai/compliance-owasp.git
cd compliance-owasp
cp owasp/config.env.example .env
cp owasp/target.env.example owasp/target.env
# Edit .env (OKAREO_API_KEY) and owasp/target.env (your agent)

# 2. Run an evaluation
# Open owasp/LLM01-prompt-injection/notebooks/run-evaluation.ipynb
# Execute all cells
```

