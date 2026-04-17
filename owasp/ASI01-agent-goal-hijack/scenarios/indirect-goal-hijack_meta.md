---
owasp_category: ASI01
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "ASI01-indirect-goal-hijack"
description: "Single-turn scenarios testing whether hidden instruction payloads embedded in retrieved external content (documents, emails, calendar events, wiki pages) can silently redirect the agent's goals. Covers invoice payment injection, CEO email spoofing via RAG, calendar goal-update payloads, wiki configuration overrides, and hidden-text prompt injection in PDFs. Used with single-turn evaluation (max_turns=1)."
evaluation_mode: single-turn
related_llm_categories: ["LLM01", "LLM06"]
row_count: 5
---
