# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting.

## Schema

### For Markdown files (checks, drivers)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM01
risk_severity: Critical
artifact_type: check | driver
status: complete | incomplete
version: "1.0.0"
name: "human-readable-name"
description: "Plain-language description of what this artifact does"
evaluation_mode: single-turn | multi-turn
---
```

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory, OR the first line of the JSONL file is a metadata record with a `_meta` key:

**Option A — Companion file** (preferred):

File: `direct-injection_meta.md`
```yaml
---
owasp_category: LLM01
risk_severity: Critical
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM01-direct-injection"
description: "Direct prompt injection test prompts targeting role/instruction override"
evaluation_mode: single-turn
row_count: 15
---
```

**Option B — Inline first record**:
```json
{"_meta": {"owasp_category": "LLM01", "risk_severity": "Critical", "artifact_type": "scenario", "status": "complete", "version": "1.0.0", "name": "LLM01-direct-injection", "description": "Direct prompt injection test prompts", "evaluation_mode": "single-turn"}}
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

## Versioning Rules

- PATCH: Fix typos, improve prompt wording without changing evaluation behavior
- MINOR: Add new evaluation criteria, expand scope
- MAJOR: Change pass/fail semantics, restructure prompt template
