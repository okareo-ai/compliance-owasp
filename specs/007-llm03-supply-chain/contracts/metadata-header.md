# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting.

## Schema

### For Markdown files (model-based checks)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM03
risk_severity: High
artifact_type: check
status: complete | incomplete
version: "1.0.0"
name: "human-readable-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: single-turn
check_type: model
output_type: pass_fail
---
```

### For Python files (code-based checks)

Python comment block at the top of the file:

```python
# ---
# owasp_category: LLM03
# risk_severity: High
# artifact_type: check
# status: complete | incomplete
# version: "1.0.0"
# name: "check-name"
# description: "Plain-language description"
# evaluation_mode: single-turn
# check_type: code
# output_type: pass_fail
# ---
```

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

File: `behavioral-validation_meta.md`
```yaml
---
owasp_category: LLM03
risk_severity: High
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM03-behavioral-validation"
description: "Third-party model behavioral validation probes testing for undocumented capabilities"
evaluation_mode: single-turn
row_count: 15
---
```

## Required Fields

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `owasp_category` | string | `LLM01` through `LLM10` | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `Critical`, `High`, `Medium`, `Low` | Risk severity per OWASP guidance |
| `artifact_type` | enum | `scenario`, `check`, `driver`, `simulation` | Type of artifact |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | Lowercase hyphenated | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `single-turn`, `multi-turn` | How the artifact is used in evaluation |

## LLM03-Specific Fields

| Field | Type | Applies To | Description |
|-------|------|------------|-------------|
| `check_type` | enum: `model`, `code` | Checks | Whether the check is model-based or code-based |
| `output_type` | enum: `pass_fail` | Checks | Output format of the check |
| `row_count` | integer | Scenario `_meta.md` | Number of data rows in the JSONL file |

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand validation dimensions
- MAJOR: Change pass/fail semantics, restructure prompt template or check logic
