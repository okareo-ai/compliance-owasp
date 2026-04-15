---
owasp_category: LLM04
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM04-corpus-poisoning"
description: "RAG corpus poisoning detection prompts testing whether adversarial content injected into a retrieval store manipulates model outputs. Covers four poisoning strategies: factual manipulation, embedded adversarial instructions, authority spoofing, and topic-targeted poisoning."
evaluation_mode: single-turn
checks: "LLM04-corpus-poisoning-detector"
row_count: 12
---
