# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting. Follows the schema established in LLM01 with LLM08-specific values.

## Schema

### For Markdown files (checks, drivers)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM08
risk_severity: High
artifact_type: check | driver
status: complete | incomplete
version: "1.0.0"
name: "human-readable-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: single-turn | multi-turn
---
```

### For Python files (code-based checks)

Docstring-based metadata block at the top of the file:

```python
"""
---
owasp_category: LLM08
risk_severity: High
artifact_type: check
status: complete
version: "1.0.0"
name: "LLM08-access-control-check"
description: "Deterministic validation of vector store access control metadata"
evaluation_mode: single-turn
check_type: code
output_type: pass_fail
---
"""
```

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

```yaml
---
owasp_category: LLM08
risk_severity: High
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM08-scenario-name"
description: "Plain-language description of the scenario"
evaluation_mode: single-turn | multi-turn
row_count: N
---
```

## Required Fields

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `owasp_category` | string | `LLM08` | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `High` | Risk severity per OWASP guidance (always High for LLM08) |
| `artifact_type` | enum | `scenario`, `check`, `driver` | Type of artifact |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | `LLM08-` prefix, lowercase hyphenated | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `single-turn`, `multi-turn` | How the artifact is used in evaluation |

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand scope
- MAJOR: Change pass/fail semantics, restructure prompt template
