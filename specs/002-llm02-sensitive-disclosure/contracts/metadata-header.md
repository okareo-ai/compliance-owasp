# Contract: Artifact Metadata Header

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check, driver) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting. This contract extends the LLM01-defined schema (see `specs/001-llm01-prompt-injection/contracts/metadata-header.md`) — the field schema is identical, only `owasp_category` changes to `LLM02`.

## Schema

### For Markdown files (model-based checks)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM02
risk_severity: Critical
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

A structured comment block at the top of the file, followed by the module docstring:

```python
# ---
# owasp_category: LLM02
# risk_severity: Critical
# artifact_type: check
# status: complete
# version: "1.0.0"
# name: "LLM02-sensitive-pattern-detector"
# description: "Regex-based detection of structured PII, credentials, and secret patterns in agent responses"
# evaluation_mode: single-turn
# check_type: code
# output_type: pass_fail
# ---
```

The comment-based header preserves valid Python syntax while maintaining the same metadata schema as Markdown artifacts. The notebook's check registration code can parse these comments to extract metadata.

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

```yaml
---
owasp_category: LLM02
risk_severity: Critical
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM02-pii-exfiltration"
description: "PII exfiltration probes testing whether the model leaks names, emails, SSNs, or financial data"
evaluation_mode: single-turn
row_count: 15
---
```

## Required Fields

Same as LLM01 — see `specs/001-llm01-prompt-injection/contracts/metadata-header.md` for the complete field listing.

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `owasp_category` | string | `LLM02` (for this suite) | OWASP LLM Top 10 category ID |
| `risk_severity` | enum | `Critical` (for LLM02) | Risk severity per OWASP guidance |
| `artifact_type` | enum | `scenario`, `check`, `driver` | Type of artifact |
| `status` | enum | `complete`, `incomplete` | Whether the artifact is finalized |
| `version` | string | Semver (e.g., `"1.0.0"`) | Artifact version |
| `name` | string | Lowercase hyphenated | Unique artifact identifier |
| `description` | string | Free text | Plain-language description |
| `evaluation_mode` | enum | `single-turn` (all LLM02 scenarios) | How the artifact is used in evaluation |

### Additional fields for checks

| Field | Type | Allowed Values | Description |
|-------|------|----------------|-------------|
| `check_type` | enum | `model`, `code` | Whether the check uses a prompt template or Python code |
| `output_type` | enum | `pass_fail` | Check output format |
