---
owasp_category: LLM05
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM05-schema-violation"
description: "Structured output prompts designed to test JSON schema conformance. Each row's result field encodes a JSON schema definition (required_fields, disallowed_keys, strict) consumed by the LLM05-schema-compliance-check code-based check. Covers: clean conformant output (5 rows), type mismatch (1 row), unexpected extra key (1 row), prototype-pollution key injection (2 rows), and non-JSON preamble (1 row)."
evaluation_mode: single-turn
checks: "LLM05-schema-compliance-check"
row_count: 10
---
