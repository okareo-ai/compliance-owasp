---
owasp_category: LLM08
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM08-rag-injection"
description: "Multi-turn RAG injection scenario data. Each row parameterizes a distinct injection vector (system-directive, metadata-injection, footnote-injection, encoded-payload, formatting-markup, authority-impersonation) for the rag-injection-exploiter driver. Used with run_simulation at max_turns=10."
evaluation_mode: multi-turn
row_count: 6
---
