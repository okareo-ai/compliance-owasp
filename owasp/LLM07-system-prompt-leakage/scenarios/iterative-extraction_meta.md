---
owasp_category: LLM07
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM07-iterative-extraction"
description: "Multi-turn iterative system prompt extraction scenarios. Each row triggers a 10-turn simulation with a different agent archetype and cover story. The probing driver uses a three-phase strategy (capability mapping → constraint probing → hypothesis confirmation) parameterized by these rows."
evaluation_mode: multi-turn
checks: "LLM07-iterative-extraction-detector"
row_count: 5
---
