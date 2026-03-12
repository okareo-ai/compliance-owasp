# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting for LLM10 Unbounded Consumption artifacts.

## Schema

### For Markdown files (checks, drivers)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM10
risk_severity: Medium
artifact_type: check | driver
status: complete | incomplete
version: "1.0.0"
name: "human-readable-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: multi-turn
---
```

**Additional fields for checks**:

| Field | Value | Description |
|-------|-------|-------------|
| `check_type` | `model` | All LLM10 checks are model-based |
| `output_type` | `pass_fail` | Binary assessment |

**Additional fields for drivers**:

| Field | Type | Description |
|-------|------|-------------|
| `temperature` | float | Driver LLM temperature (e.g., 0.6) |

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

File: `infinite-loop_meta.md`
```yaml
---
owasp_category: LLM10
risk_severity: Medium
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM10-infinite-loop"
description: "Infinite tool/agent loop detection — prompts designed to induce recursive or circular tool call chains"
evaluation_mode: multi-turn
row_count: 6
---
```

## Required Fields

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `owasp_category` | string | `LLM10` | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `Medium` | Risk severity per OWASP guidance |
| `artifact_type` | enum | `scenario`, `check`, `driver` | Type of artifact |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | Lowercase hyphenated | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `multi-turn` | All LLM10 artifacts are multi-turn |

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand coverage domains
- MAJOR: Change pass/fail semantics, restructure prompt template
