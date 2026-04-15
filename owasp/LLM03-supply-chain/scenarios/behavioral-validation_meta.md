---
owasp_category: LLM03
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM03-behavioral-validation"
description: "Third-party model behavioral validation probes testing whether a model exhibits undocumented or unsafe capabilities outside its stated scope. Covers 6 probing categories: code execution, file system access, network access, tool invocation, training data disclosure, and model architecture disclosure."
evaluation_mode: single-turn
checks: "LLM03-behavioral-boundary-detector"
row_count: 15
---
