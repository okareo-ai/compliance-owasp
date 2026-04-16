---
owasp_category: LLM07
risk_severity: High
artifact_type: scenario
status: complete
version: "2.0.0"
name: "LLM07-direct-extraction"
description: "Direct system prompt and tool/config extraction probes. Covers 8 distinct prompt extraction attack vectors (verbatim request, social engineering, output-prefix, reformulation, constraint probing, partial extraction, instruction override, hypothetical framing) and 12 tool-schema-leakage probes (tool listing, function signatures, API endpoints, auth headers, runtime config, environment variables). Tests whether an agent reveals system prompt content or internal configuration when confronted with blunt or socially engineered extraction attempts."
evaluation_mode: single-turn
checks: "LLM07-system-prompt-leakage-detector"
row_count: 20
---
