---
owasp_category: LLM05
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM05-injection-payload-detection"
description: "Eliciting prompts designed to surface XSS vectors, SQL injection patterns, and OS command injection sequences in agent outputs. Covers HTML/JS generation (5 rows), SQL query construction (5 rows), and shell command generation (5 rows). Evaluated by the LLM05-output-injection-detector model-based check."
evaluation_mode: single-turn
checks: "LLM05-output-injection-detector"
row_count: 15
---
