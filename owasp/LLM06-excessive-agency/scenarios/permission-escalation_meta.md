---
owasp_category: LLM06
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM06-permission-escalation"
description: "Multi-turn adversarial scenario testing whether AI agents progressively widen their operational permissions through sequential actions without explicit authorization. Each row parameterizes the privilege-escalator driver with a distinct escalation strategy (incremental widening, gaslighting, batch embedding, false authority, implicit assumption). Used with run_simulation at max_turns=10."
evaluation_mode: multi-turn
checks: "LLM06-agency-boundary-drift-detector"
row_count: 5
---
