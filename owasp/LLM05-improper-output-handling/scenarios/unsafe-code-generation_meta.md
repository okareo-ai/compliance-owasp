---
owasp_category: LLM05
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM05-unsafe-code-generation"
description: "Eliciting prompts designed to surface path traversal sequences, unconstrained shell execution constructs, and OS execution API calls with unsanitized user input in agent-generated code. Covers file path handling (5 rows), shell script generation (5 rows), and OS execution API usage (5 rows). Evaluated by the LLM05-unsafe-code-detector model-based check."
evaluation_mode: single-turn
checks: "LLM05-unsafe-code-detector"
row_count: 15
---
