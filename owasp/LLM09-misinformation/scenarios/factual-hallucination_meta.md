---
owasp_category: LLM09
risk_severity: Medium
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM09-factual-hallucination"
description: "Factual hallucination detection — verifiable questions across history, science, geography, and current affairs testing whether the agent generates confidently stated falsehoods"
evaluation_mode: single-turn
checks: "LLM09-factual-grounding-detector"
row_count: 12
---
