---
owasp_category: LLM04
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM04-backdoor-trigger"
description: "Backdoor/sleeper trigger detection prompts testing whether specific trigger phrases activate planted backdoor behaviors. Uses paired triggered and clean control prompts across four trigger patterns: rare token sequences, specific code words, Unicode homoglyphs, and benign-seeming phrases."
evaluation_mode: single-turn
row_count: 10
---
