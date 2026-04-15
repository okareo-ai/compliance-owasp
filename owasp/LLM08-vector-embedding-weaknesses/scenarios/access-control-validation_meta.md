---
owasp_category: LLM08
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM08-access-control-validation"
description: "Single-turn access control validation test inputs. Each row contains retrieval results with structured metadata (tenant_id, scope) and a JSON-encoded access control policy defining authorized boundaries. Used with the code-based access-control-check for deterministic metadata validation."
evaluation_mode: single-turn
checks: "LLM08-access-control-check"
row_count: 10
---
