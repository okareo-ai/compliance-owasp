# Implementation Plan: Target Agent Auth Flow Configuration

**Branch**: `011-target-auth-flow` | **Date**: 2026-03-12 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/011-target-auth-flow/spec.md`

## Summary

Extend the shared Target agent configuration (`owasp/target.env`) to support the full Okareo flow: Auth → Start → Next → End. Only Next is required; Auth, Start, and End are optional. Each step has its own URL, HTTP method, request body template, and response mapping. The primary addition is the Auth step (credential authentication) for agents that require token acquisition before interaction. Update `owasp/common.build_target()` to load and apply Auth config when present, and extend `owasp/target.env.example` with the new variables. All OWASP category notebooks continue to use `build_target(CATEGORY_DIR)` unchanged.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `okareo` (Okareo Python SDK), `python-dotenv`, `jupyter`  
**Storage**: Repository files only — `owasp/target.env`, `owasp/target.env.example`. No database.  
**Testing**: Manual validation via notebook execution; verify Auth flow with an auth-protected agent or mock  
**Target Platform**: Any environment with Python 3.11+ and Jupyter (macOS, Linux, CI)  
**Project Type**: Configuration extension — modifies shared target loader and env template  
**Performance Goals**: N/A (config load is one-time per notebook run)  
**Constraints**: Okareo Python SDK must support auth in CustomEndpointTarget (or equivalent); sensitive credentials via env vars, not plain text in config  
**Scale/Scope**: 1 config file extension, 1 shared module (`owasp/common.py`) update, 0 new OWASP category artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | OWASP-Complete Coverage | **PASS** | No new OWASP category; extends shared target config used by all categories. Does not reduce coverage. |
| II | Explainability & Transparency | **PASS** | New config vars documented in target.env.example with comments. Adopters understand Auth/Start/Next/End flow. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP used for discovery (create_or_update_target auth_params). Production operations remain notebook-driven. |
| IV | Composability, Reusability & Forkability | **PASS** | Target config remains externalized; Auth/Start/Next/End are optional. Backward compatible. Clone-and-run preserved. |
| V | Simulation-Driven Coverage | **PASS** | No change to simulation patterns; Auth enables more agents to be tested. |
| VI | Traceability & Auditability | **PASS** | Config schema documented in data-model; no new artifacts requiring metadata. |
| VII | File-First Artifact Persistence | **PASS** | Config lives in target.env (file); no remote-only state. |
| VIII | Notebook-Driven Execution | **PASS** | Notebooks continue to call build_target(); no MCP push for target in production. |

**Gate result**: ALL PASS — no violations.

### Post-Design Re-Check (after Phase 1)

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|----------------------|
| I | OWASP-Complete Coverage | **PASS** | No new category; extends shared config used by all. |
| II | Explainability & Transparency | **PASS** | target-env-schema.md and quickstart.md document all variables. |
| III | Okareo MCP for Discovery & Analysis | **PASS** | MCP used for discovery; production remains notebook-driven. |
| IV | Composability, Reusability & Forkability | **PASS** | Target config externalized; Auth/Start/End optional; backward compatible. |
| V | Simulation-Driven Coverage | **PASS** | Auth enables more agents to be tested. |
| VI | Traceability & Auditability | **PASS** | data-model.md documents schema. |
| VII | File-First Artifact Persistence | **PASS** | Config in target.env (file). |
| VIII | Notebook-Driven Execution | **PASS** | build_target() remains single path; no MCP push for target. |

**Post-design gate result**: ALL PASS — design is fully constitution-compliant.

## Project Structure

### Documentation (this feature)

```text
specs/011-target-auth-flow/
├── plan.md              # This file
├── research.md          # Phase 0: SDK auth support, env var substitution
├── data-model.md        # Phase 1: SharedTargetConfiguration entity
├── quickstart.md        # Phase 1: Adopter guide for Auth config
├── contracts/
│   └── target-env-schema.md   # target.env variable contract
├── checklists/
│   └── requirements.md       # (existing from /speckit.specify)
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
owasp/
├── common.py                  # MODIFY: build_target() — add Auth, extend Start/End/Next config
├── target.env.example         # MODIFY: add TARGET_AUTH_* vars, document Start/End body/method
└── target.env                # (user copy; gitignored) — adopters fill in values

# No new category folders. All OWASP category notebooks (LLM01–LLM10) use build_target()
# unchanged — they automatically gain Auth support when config is present.
```

**Structure Decision**: Configuration-only change. Modifies `owasp/common.py` and `owasp/target.env.example`. No new artifact folders. All 10 OWASP category notebooks inherit the extended target builder without code changes.
