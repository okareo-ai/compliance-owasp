---
owasp_category: ASI01
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "ASI01-goal-drift-manipulation"
description: "Multi-turn crescendo scenarios testing whether gradual, subtle reframing across 8-10 conversational turns can cause an AI agent to drift from its stated objectives. Target-agnostic — driver discovers the agent's actual scope in early turns, then applies incremental drift. Covers scope expansion, standard erosion, and bias normalization. Each row parameterizes the goal-drift-manipulator driver with a drift target and incremental escalation strategy. Used with run_simulation at max_turns=10."
evaluation_mode: multi-turn
related_llm_categories: ["LLM01", "LLM06"]
row_count: 3
---
