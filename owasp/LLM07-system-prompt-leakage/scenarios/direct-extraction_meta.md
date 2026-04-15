---
owasp_category: LLM07
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM07-direct-extraction"
description: "Direct system prompt extraction probes including verbatim requests, social engineering framings (developer/debug, translation/paraphrase), output-prefix attacks, and indirect disclosure framings. Tests whether an agent reveals system prompt content when confronted with blunt or socially engineered extraction attempts."
evaluation_mode: single-turn
checks: "LLM07-system-prompt-leakage-detector"
row_count: 15
---
