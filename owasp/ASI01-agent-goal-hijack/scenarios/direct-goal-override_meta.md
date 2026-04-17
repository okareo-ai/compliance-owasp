---
owasp_category: ASI01
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "ASI01-direct-goal-override"
description: "Multi-turn adversarial scenarios testing whether an AI agent can be manipulated into abandoning its stated objectives via explicit goal-override prompts. Target-agnostic — driver discovers the agent's actual goal in early turns, then attempts manipulation. Covers budget/constraint removal, role redefinition, safety suppression, standard erosion, and forged authorization overrides. Each row parameterizes the goal-override-attacker driver with a manipulation category and escalation strategy. Used with run_simulation at max_turns=10."
evaluation_mode: multi-turn
related_llm_categories: ["LLM01", "LLM06"]
row_count: 5
---
