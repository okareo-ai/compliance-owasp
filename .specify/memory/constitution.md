<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0 (MINOR — new principles and material section expansion)
Modified principles:
  - III. Okareo-Native Execution → III. Okareo MCP for Discovery & Analysis (scope narrowed to read/analysis)
  - IV. Composability & Reusability → IV. Composability, Reusability & Forkability (expanded with standalone repo goal)
Added sections:
  - VII. File-First Artifact Persistence (new principle)
  - VIII. Notebook-Driven Execution (new principle)
  - Artifact Taxonomy rewritten with common/ + per-category folder structure
  - Development Workflow rewritten to reflect file → notebook → Okareo pipeline
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check gates align — no structural change needed)
  - .specify/templates/spec-template.md ✅ (no structural changes required)
  - .specify/templates/tasks-template.md ✅ (task phases align with new file → notebook workflow)
Deferred TODOs: None — all placeholders resolved.
-->

# Okareo OWASP Constitution

> **Project Goal**: Provide a standalone, forkable repository that any team can clone and use
> to run OWASP LLM Top 10 compliance testing against their own AI agents via Okareo. The repo
> MUST be self-contained — all scenarios, checks, drivers, and execution notebooks are included
> as files, with no dependency on external state beyond an Okareo API key.

## Core Principles

### I. OWASP-Complete Coverage (NON-NEGOTIABLE)

Every category in the OWASP LLM Top 10 MUST have at least one scenario, one check,
and one driver artifact defined before the project can be considered complete. Coverage
is tracked at the category level (LLM01–LLM10). Partial coverage is acceptable as an
intermediate state but MUST be explicitly marked as `[INCOMPLETE]` in artifact metadata.

**Rationale**: The entire purpose of this project is to provide a reusable OWASP compliance
foundation. Gaps in coverage would give false confidence to adopters.

Covered categories (OWASP LLM Top 10, 2025):
- LLM01: Prompt Injection
- LLM02: Sensitive Information Disclosure
- LLM03: Supply Chain Vulnerabilities
- LLM04: Data and Model Poisoning
- LLM05: Improper Output Handling
- LLM06: Excessive Agency
- LLM07: System Prompt Leakage
- LLM08: Vector and Embedding Weaknesses
- LLM09: Misinformation
- LLM10: Unbounded Consumption

### II. Explainability & Transparency (NON-NEGOTIABLE)

Every artifact (scenario, check, driver) MUST be self-documenting. Each artifact MUST
include:
- The OWASP category ID it targets (e.g., `LLM01`)
- A plain-language description of what is being tested and why it matters
- Instructions for interpreting the test result (what pass/fail means in context)
- The risk severity level (Critical / High / Medium / Low) per OWASP guidance

No artifact may rely on opaque scoring without an accompanying explanation. Black-box
checks are prohibited. Human reviewers MUST be able to understand a test result without
inspecting implementation code.

**Rationale**: This project is a foundation for any OWASP testing. Explainability ensures
adopters can adapt, extend, and trust the artifacts rather than treating them as a magic
compliance stamp.

### III. Okareo MCP for Discovery & Analysis (NON-NEGOTIABLE)

The Okareo MCP tools MUST be used as the primary interface for **discovery, exploration,
and analysis** during artifact development. This includes:
- Listing existing scenarios, checks, models, and targets to avoid duplication
- Retrieving test run results and simulation transcripts for analysis
- Inspecting check definitions and driver configurations
- Generating check drafts via `generate_check` for AI-assisted authoring
- Querying Okareo documentation via `get_docs` and `get_templates`

MCP tools MUST NOT be the primary mechanism for pushing artifacts to Okareo in production
workflows. All artifact registration, scenario upload, and test execution in the standard
workflow MUST go through the project's Jupyter notebooks (see Principle VIII). This ensures
that every push operation is reproducible, version-controlled, and auditable as code.

**When MCP push operations are acceptable**:
- During interactive development and rapid prototyping (before artifacts are finalized)
- For one-off exploratory test runs during artifact authoring
- These MUST be treated as ephemeral — the canonical artifact always lives as a file
  in the repository (see Principle VII)

**Rationale**: MCP tools provide an excellent interactive interface for understanding
what exists in Okareo and for rapid experimentation. However, a forkable compliance repo
must not depend on interactive tool sessions for its core operations. Notebooks provide
the reproducible, scriptable execution path that adopters need.

### IV. Composability, Reusability & Forkability

Every test artifact MUST be designed as a standalone, reusable building block:
- A scenario MUST be usable independently or as part of a composed suite
- A check MUST be applicable to any model output that matches its evaluation domain
- A driver MUST encapsulate exactly one adversarial persona or user role

Artifacts MUST NOT hardcode assumptions about a specific target model or deployment.
Parameterization (e.g., system prompt, model name, endpoint) MUST be externalized.

The repository as a whole MUST be forkable and functional with minimal setup:
- A new adopter MUST be able to clone the repo, provide an Okareo API key, point
  notebooks at their target agent, and run the full OWASP compliance suite
- No artifact may depend on state that exists only in a specific Okareo project —
  all scenarios, checks, and driver content MUST be committed as files in the repo
- Configuration (API keys, model endpoints) MUST be externalized via environment
  variables or a single config file, never hardcoded

**Rationale**: The project's value is as a generic foundation. Tightly coupled artifacts
limit reuse. A repo that cannot be forked and run independently fails its core mission.

### V. Simulation-Driven Coverage for Agent Risks

For OWASP risks that manifest over multiple conversational turns or through agent
decision-making sequences, multi-turn simulation via Okareo Drivers MUST be used.
Single-turn checks are insufficient for:
- LLM01 (Prompt Injection — multi-turn jailbreak chains)
- LLM06 (Excessive Agency — unauthorized action escalation)
- LLM07 (System Prompt Leakage — iterative extraction)
- LLM10 (Unbounded Consumption — resource exhaustion through repeated calls)

Single-turn evaluations (via `run_test`) are appropriate for stateless risks such as
LLM02, LLM05, and LLM09.

**Rationale**: Agents fail quietly across turns. A single-turn snapshot cannot detect
behavioral drift, escalation patterns, or iterative exploitation techniques.

### VI. Traceability & Auditability

Every artifact MUST carry a structured metadata header that includes:
- `owasp_category`: the LLM Top 10 category ID (e.g., `LLM06`)
- `risk_severity`: Critical / High / Medium / Low
- `artifact_type`: scenario | check | driver | simulation
- `status`: complete | incomplete
- `version`: semantic version of the artifact

All test run results MUST be linked back to their OWASP category and severity. Result
summaries MUST include an audit trail sufficient for compliance reporting — i.e., "this
system was tested for LLM06 at version X on date Y with result Z."

**Rationale**: Adopters use this project for compliance. Without traceability, results
cannot be cited in audits or remediation plans.

### VII. File-First Artifact Persistence (NON-NEGOTIABLE)

Every Okareo artifact MUST be saved as a file in the repository **before** being pushed
to Okareo. The file is the source of truth; the Okareo platform instance is a derived
deployment target.

Required file formats by artifact type:

| Artifact Type | File Format | Extension | Example |
|---------------|-------------|-----------|---------|
| Scenario | JSON Lines (one row per seed input) | `.jsonl` | `direct-injection.jsonl` |
| Driver Prompt | Markdown with structured metadata header | `.md` | `red-team-escalator.md` |
| Model-based Check | Markdown with prompt template and metadata | `.md` | `pii-detection.md` |
| Code-based Check | Python module with check function and metadata | `.py` | `schema-compliance.py` |

File naming MUST follow the pattern: `{short-descriptor}.{ext}` (lowercase, hyphen-separated).

Every artifact file MUST begin with the structured metadata header defined in Principle VI.
For `.jsonl` files, metadata MUST appear as a comment block in an accompanying `_meta.md`
file or as a header field in the first record.

**Rationale**: A compliance repo that stores artifacts only in a remote platform is not
forkable, not diffable, and not auditable via standard version control. File-first ensures
every artifact is code-reviewed, versioned, and portable.

### VIII. Notebook-Driven Execution (NON-NEGOTIABLE)

All artifact uploads, scenario registration, and test/simulation execution MUST be
performed through Jupyter notebooks committed to the repository. Notebooks serve as
the reproducible, auditable execution layer.

Each OWASP category folder MUST contain a notebook (or set of notebooks) that:
1. Loads artifact files from the local folder structure
2. Uploads scenarios to Okareo via the Okareo Python SDK
3. Registers or updates checks in Okareo
4. Configures and runs tests (`run_test`) or simulations (`run_simulation`)
5. Retrieves and displays results

Notebook design principles:
- **Templatized**: A single notebook template SHOULD be reusable across categories
  with minimal per-category customization (parameterized by category folder path,
  OWASP ID, and artifact manifest)
- **Idempotent**: Re-running a notebook MUST NOT create duplicate artifacts — use
  upsert semantics (create-or-update) for all Okareo operations
- **Self-contained**: Each notebook MUST include setup cells (imports, API key loading,
  SDK initialization) so it can run independently
- **SDK-based**: Notebooks MUST use the official Okareo Python SDK (`okareo`) for all
  platform interactions, not raw REST calls

A `common/` notebook MAY exist for uploading shared checks and drivers that span
multiple OWASP categories.

**Rationale**: Notebooks provide a literate, reproducible execution environment that
bridges the gap between static artifact files and the Okareo platform. They enable
adopters to understand, customize, and re-run the entire compliance pipeline without
relying on interactive MCP sessions.

## Artifact Taxonomy

The project organizes all test artifacts into the following structure:

```
owasp/
├── common/
│   ├── checks/              # Reusable checks applicable across categories
│   │   ├── pii-detection.md
│   │   ├── injection-payload.py
│   │   └── schema-compliance.py
│   ├── drivers/             # Reusable driver personas (e.g., generic red-teamer)
│   │   └── red-team-generalist.md
│   └── notebooks/
│       └── upload-common.ipynb
│
├── LLM01-prompt-injection/
│   ├── scenarios/           # .jsonl files — seed inputs for this category
│   │   ├── direct-injection.jsonl
│   │   └── crescendo-attack.jsonl
│   ├── checks/              # Category-specific checks (code or model-based)
│   │   └── injection-success-detector.md
│   ├── drivers/             # Category-specific adversarial personas
│   │   └── jailbreak-escalator.md
│   └── notebooks/
│       ├── upload-artifacts.ipynb    # Upload scenarios + register checks
│       └── run-evaluation.ipynb      # Execute tests/simulations + display results
│
├── LLM02-sensitive-info-disclosure/
│   ├── scenarios/
│   ├── checks/
│   ├── drivers/
│   └── notebooks/
│
... (one folder per OWASP LLM Top 10 category, same internal structure)
│
├── LLM10-unbounded-consumption/
│   ├── scenarios/
│   ├── checks/
│   ├── drivers/
│   └── notebooks/
│
├── templates/
│   ├── upload-artifacts-template.ipynb   # Base notebook template for uploads
│   └── run-evaluation-template.ipynb     # Base notebook template for execution
│
└── config.env.example       # Environment variable template (OKAREO_API_KEY, etc.)
```

**Naming convention**: `{LLMXX}-{short-risk-name}/{artifact-type}/{descriptor}.{ext}`

Each artifact file MUST begin with the structured metadata header defined in Principle VI.

**Folder rules**:
- `common/` contains ONLY artifacts used by two or more OWASP categories
- Category folders (e.g., `LLM01-prompt-injection/`) contain ONLY artifacts specific
  to that category
- If an artifact initially in a category folder is later needed by a second category,
  it MUST be moved to `common/` and both category notebooks updated to reference it

## Development Workflow

Adding a new OWASP test artifact follows this sequence:

1. **Discover** — Use Okareo MCP tools (`list_scenarios`, `list_checks`, `get_docs`,
   `get_templates`) to understand what exists, gather reference material, and avoid
   duplication.

2. **Analyze** — Use MCP tools to inspect existing check definitions, review past test
   run results, and study Okareo documentation for best practices relevant to the
   target OWASP category.

3. **Author artifact files** — Create the artifact as a file in the appropriate folder:
   - Scenarios: `.jsonl` file in `{category}/scenarios/`
   - Checks: `.md` (model-based) or `.py` (code-based) in `{category}/checks/` or
     `common/checks/`
   - Drivers: `.md` in `{category}/drivers/` or `common/drivers/`
   - Include the full metadata header per Principle VI

4. **Upload via notebook** — Use the category's upload notebook to push artifacts to
   Okareo. If the notebook does not yet exist, copy from `owasp/templates/` and
   customize.

5. **Execute via notebook** — Run tests or simulations using the category's execution
   notebook. Review results inline.

6. **Iterate** — If results reveal issues, update the artifact *file* first, then
   re-run the notebook. The file is always the source of truth.

7. **Commit** — Once validated, commit all artifact files and notebooks. Increment
   the artifact's `version` field following semver rules.

When modifying an existing artifact, always edit the file and re-run the notebook.
Never modify artifacts only in the Okareo platform — changes that exist only remotely
are considered lost.

## Governance

This constitution supersedes all other project practices and design decisions. Any
implementation choice that conflicts with the principles above MUST be explicitly justified
and approved before proceeding.

**Amendment procedure**:
- PATCH amendments (clarifications, wording): update directly, increment PATCH version.
- MINOR amendments (new principle or section): require a written rationale comment in
  the PR describing why the addition is necessary and backward-compatible.
- MAJOR amendments (removal or redefinition of a principle): require explicit team
  consensus, a migration plan for any artifacts affected, and must document the risk
  accepted by the change.

**Versioning policy**: `CONSTITUTION_VERSION` follows `MAJOR.MINOR.PATCH`.

**Compliance review**: Every new feature specification MUST include a Constitution Check
section in its plan. All artifacts MUST be validated against Principles I, II, III, VI,
VII, and VIII before merging.

**Runtime guidance**: See Okareo documentation at https://docs.okareo.com and the MCP
tool descriptors in `.cursor/projects/*/mcps/user-okareo/` for tool schemas.

**Version**: 1.1.0 | **Ratified**: 2026-03-09 | **Last Amended**: 2026-03-09
