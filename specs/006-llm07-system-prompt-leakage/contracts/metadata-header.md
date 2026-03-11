# Contract: Artifact Metadata Header (LLM07)

**Version**: 1.0.0 | **Constitution Ref**: Principle VI (Traceability & Auditability)  
**Base Contract**: `specs/001-llm01-prompt-injection/contracts/metadata-header.md` — schema is identical; this document adds LLM07-specific field values.

## LLM07-Specific Field Values

| Field | LLM07 Value |
|-------|-------------|
| `owasp_category` | `LLM07` |
| `risk_severity` | `High` |
| `artifact_type` | `scenario` \| `check` \| `driver` \| `simulation` |
| `status` | `complete` \| `incomplete` |

## Example Headers

### Scenario companion file (`_meta.md`)

```yaml
---
owasp_category: LLM07
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM07-direct-extraction"
description: "Direct system prompt extraction probes including verbatim requests, social engineering framings, output-prefix attacks, and indirect disclosure framings."
evaluation_mode: single-turn
row_count: 15
---
```

### Model-based check (`.md`)

```yaml
---
owasp_category: LLM07
risk_severity: High
artifact_type: check
status: complete
version: "1.0.0"
name: "LLM07-system-prompt-leakage-detector"
description: "Evaluates whether an AI agent revealed system prompt content via verbatim reproduction, structural disclosure, or behavioral confirmation of hypothetical prompt fragments."
evaluation_mode: single-turn
check_type: model
output_type: pass_fail
---
```

### Driver persona (`.md`)

```yaml
---
owasp_category: LLM07
risk_severity: High
artifact_type: driver
status: complete
version: "1.0.0"
name: "LLM07-prompt-extraction-prober"
description: "Probing driver persona that uses a three-phase iterative strategy to reconstruct system prompt content across 10 conversational turns: capability mapping, constraint probing, and hypothesis confirmation."
evaluation_mode: multi-turn
temperature: 0.7
---
```
