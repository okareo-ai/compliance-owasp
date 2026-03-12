# Contract: Model-Based Check File Format

**Version**: 1.0.0 | **Constitution Ref**: Principle VII (File-First Artifact Persistence)

## Purpose

Defines the file format for model-based checks used in LLM10 Unbounded Consumption evaluations. All LLM10 checks are model-based (`.md`).

## File Format

- Extension: `.md`
- Location: `owasp/LLM10-unbounded-consumption/checks/`
- Structure: YAML front matter + prompt template body

## Placeholders (Multi-Turn)

LLM10 checks use multi-turn placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{simulation_message_history}` | Full conversation transcript (driver + target messages across all turns) |
| `{scenario_result}` | Expected behavior from the scenario row's `result` field |

## File Structure

```markdown
---
owasp_category: LLM10
risk_severity: Medium
artifact_type: check
status: complete
version: "1.0.0"
name: "LLM10-loop-detection-check"
description: "Evaluates multi-turn transcript for recursive/circular tool call chains and unbounded continuation"
evaluation_mode: multi-turn
check_type: model
output_type: pass_fail
---

# Check: [Check Name]

## Criterion

[Plain-language description of what constitutes pass vs fail]

## Prompt Template

[Evaluator instructions with placeholders]

Return ONLY "true" or "false".
```

## Check Instances

1. **loop-detection-check.md** — Evaluates transcript for infinite loops, circular tool patterns, unbounded continuation. Handles tool-less agents (N/A → pass).
2. **resource-policy-enforcement-check.md** — Evaluates whether system enforced rate limits, token budgets, timeouts when subjected to adversarial inputs.
