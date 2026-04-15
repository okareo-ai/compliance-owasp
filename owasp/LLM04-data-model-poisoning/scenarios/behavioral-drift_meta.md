---
owasp_category: LLM04
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM04-behavioral-drift"
description: "Behavioral drift detection prompts comparing model outputs against known-good baseline responses to detect silent changes after data or model updates. Covers four behavioral dimensions: factual accuracy, safety/policy adherence, reasoning quality, and tone consistency."
evaluation_mode: single-turn
checks: "LLM04-behavioral-drift-detector"
row_count: 12
---
