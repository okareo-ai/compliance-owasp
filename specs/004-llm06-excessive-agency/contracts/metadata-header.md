# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting for LLM06 Excessive Agency test artifacts.

## Schema

### For Markdown files (checks, drivers)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM06
risk_severity: Critical
artifact_type: check | driver
status: complete | incomplete
version: "1.0.0"
name: "LLM06-artifact-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: multi-turn
---
```

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

File: `unauthorized-tool-invocation_meta.md`
```yaml
---
owasp_category: LLM06
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM06-unauthorized-tool-invocation"
description: "Multi-turn adversarial scenario testing whether agents invoke tools beyond their granted scope"
evaluation_mode: multi-turn
row_count: 5
---
```

## Required Fields

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `owasp_category` | string | `LLM06` | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `Critical` | Risk severity — always Critical for LLM06 |
| `artifact_type` | enum | `scenario`, `check`, `driver` | Type of artifact |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | `LLM06-{descriptor}` | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `multi-turn` | All LLM06 artifacts are multi-turn |

## Additional Fields (type-specific)

| Field | Applies To | Description |
|-------|-----------|-------------|
| `check_type` | checks | `model` (all LLM06 checks are model-based) |
| `output_type` | checks | `pass_fail` (binary authority assessment) |
| `temperature` | drivers | Response randomness (default: `0.7` for LLM06 drivers) |
| `row_count` | scenario metadata | Number of rows in the companion `.jsonl` file |

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand scope
- MAJOR: Change pass/fail semantics, restructure prompt template
