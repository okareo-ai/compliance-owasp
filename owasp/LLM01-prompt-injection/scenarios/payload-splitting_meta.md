---
owasp_category: LLM01
risk_severity: Critical
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM01-payload-splitting"
description: "Payload splitting attack test inputs where malicious intent is fragmented across multiple messages or input fields that individually appear benign. Covers sequential step-fragment attacks, cross-input splitting across user message and tool context, fabricated tool response privilege escalation, and explicit fragment-combination requests."
evaluation_mode: single-turn
row_count: 12
---
