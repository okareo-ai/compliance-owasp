# Contract: Artifact Metadata Header (LLM04)

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)

## Purpose

Every file-based artifact (scenario, check) MUST begin with a structured metadata header. This header enables traceability, auditability, and compliance reporting. This contract reuses the LLM01-defined schema (see `specs/001-llm01-prompt-injection/contracts/metadata-header.md`) with LLM04-specific values.

## Schema

### For Markdown files (checks)

YAML front matter at the top of the file:

```yaml
---
owasp_category: LLM04
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

### For JSONL files (scenarios)

An accompanying `_meta.md` file in the same directory:

```yaml
---
owasp_category: LLM04
risk_severity: High
artifact_type: scenario
status: complete | incomplete
version: "1.0.0"
name: "LLM04-corpus-poisoning"
description: "RAG corpus poisoning detection prompts testing adversarial content influence"
evaluation_mode: single-turn
row_count: 12
---
```

## LLM04-Specific Values

| Field | Value | Notes |
|-------|-------|-------|
| `owasp_category` | `LLM04` | Fixed for all LLM04 artifacts |
| `risk_severity` | `High` | Per OWASP LLM Top 10 2025 guidance |
| `evaluation_mode` | `single-turn` | All LLM04 scenarios are single-turn |
| `check_type` | `model` | All LLM04 checks are model-based |

## Versioning for Corpus and Baseline Tracking

The `version` field in scenario `_meta.md` files serves a dual purpose for LLM04:

1. **Standard artifact versioning**: PATCH/MINOR/MAJOR per the LLM01 contract
2. **Corpus/baseline version tracking**: When the retrieval corpus changes (corpus poisoning scenarios) or a new baseline is captured (behavioral drift scenarios), the scenario version MUST be incremented. This enables tracing test results back to the specific corpus state or baseline version that was in effect.

## Required Fields

Same as LMM01 contract — see `specs/001-llm01-prompt-injection/contracts/metadata-header.md` for the complete field listing and versioning rules.
