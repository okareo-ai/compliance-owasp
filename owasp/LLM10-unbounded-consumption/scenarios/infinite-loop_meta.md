---
owasp_category: LLM10
risk_severity: Medium
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM10-infinite-loop"
description: "Infinite tool/agent loop detection — prompts designed to induce recursive or circular tool call chains. Tests whether the agent terminates within bounds or enters unbounded loops."
evaluation_mode: multi-turn
checks: "LLM10-loop-detection-check"
row_count: 6
---
