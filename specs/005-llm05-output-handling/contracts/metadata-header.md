# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)
**Inherits from**: `specs/001-llm01-prompt-injection/contracts/metadata-header.md` (no structural changes; LLM05-specific values below)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. For LLM05, all artifacts carry `owasp_category: LLM05` and `risk_severity: High`.

## Schema

### For Markdown files (model-based checks, driver)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM05
risk_severity: High
artifact_type: check | driver
status: complete | incomplete
version: "1.0.0"
name: "human-readable-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: single-turn
---
```

### For the Python code-based check

Python comment block at the top of the `.py` file (before any imports):

```python
# ---
# owasp_category: LLM05
# risk_severity: High
# artifact_type: check
# status: complete
# version: "1.0.0"
# name: "LLM05-schema-compliance-check"
# description: "Deterministic JSON schema validation: required fields, type contracts, no unexpected keys, no prototype-pollution-risk keys."
# evaluation_mode: single-turn
# check_type: code
# output_type: pass_fail
# ---
```

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory (Option A — preferred):

```yaml
---
owasp_category: LLM05
risk_severity: High
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM05-{scenario-short-name}"
description: "Description of what output risk this scenario elicits"
evaluation_mode: single-turn
row_count: N
---
```

## LLM05 Artifact Instances

| Artifact File | `artifact_type` | `check_type` | `evaluation_mode` |
|---|---|---|---|
| `injection-payload-detection.jsonl` + `_meta.md` | `scenario` | — | `single-turn` |
| `unsafe-code-generation.jsonl` + `_meta.md` | `scenario` | — | `single-turn` |
| `schema-violation.jsonl` + `_meta.md` | `scenario` | — | `single-turn` |
| `output-injection-detector.md` | `check` | `model` | `single-turn` |
| `unsafe-code-detector.md` | `check` | `model` | `single-turn` |
| `schema-compliance-check.py` | `check` | `code` | `single-turn` |
| `pass-through-driver.md` | `driver` | — | `single-turn` |

## Required Fields (all artifacts)

See `specs/001-llm01-prompt-injection/contracts/metadata-header.md` for field definitions and versioning rules. All fields are identical; only the constant values differ (`owasp_category: LLM05`, `risk_severity: High`).
