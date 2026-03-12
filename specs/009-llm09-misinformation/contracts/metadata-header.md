# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting for LLM09 Misinformation artifacts.

## Schema

### For Markdown files (checks)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM09
risk_severity: Medium
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

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

File: `factual-hallucination_meta.md`
```yaml
---
owasp_category: LLM09
risk_severity: Medium
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM09-factual-hallucination"
description: "Factual hallucination detection — verifiable questions across history, science, geography, and current affairs"
evaluation_mode: single-turn
row_count: 12
---
```

## Required Fields

| Field | Type | Allowed Values | Description |
|-------|------|---------------|-------------|
| `owasp_category` | string | `LLM09` | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `Medium` | Risk severity per OWASP guidance (Medium for LLM09) |
| `artifact_type` | enum | `scenario`, `check` | Type of artifact (no drivers in LLM09) |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | Lowercase hyphenated | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `single-turn` | All LLM09 artifacts are single-turn |

## Additional Fields (type-specific)

| Field | Applies To | Description |
|-------|-----------|-------------|
| `check_type` | checks | `model` (all LLM09 checks are model-based) |
| `output_type` | checks | `pass_fail` (binary assessment) |
| `row_count` | scenarios | Number of seed input rows in the JSONL file |

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand coverage domains
- MAJOR: Change pass/fail semantics, restructure prompt template
