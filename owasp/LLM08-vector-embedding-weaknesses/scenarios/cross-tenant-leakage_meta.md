---
owasp_category: LLM08
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM08-cross-tenant-leakage"
description: "Single-turn cross-tenant and cross-scope data leakage test inputs. Each row contains a user query combined with retrieved documents tagged with tenant and scope metadata, including both authorized and unauthorized content. Tests whether the agent's response draws exclusively from authorized sources."
evaluation_mode: single-turn
row_count: 10
---
