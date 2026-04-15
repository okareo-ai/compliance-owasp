---
owasp_category: LLM09
risk_severity: Medium
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM09-fabricated-citation"
description: "Fabricated citation and reference detection — prompts requesting academic papers, DOIs, URLs, and bibliographic details testing whether the agent invents non-existent references"
evaluation_mode: single-turn
checks: "LLM09-citation-fabrication-detector"
row_count: 12
---
