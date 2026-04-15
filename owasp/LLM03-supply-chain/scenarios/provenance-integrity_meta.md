---
owasp_category: LLM03
risk_severity: High
artifact_type: scenario
status: complete
version: "1.0.0"
name: "LLM03-provenance-integrity"
description: "Dependency and provenance integrity test data containing structured metadata samples for deterministic validation of model artifact signatures, version pinning, SBOM/ML-BOM completeness, and license compatibility. Includes both valid (passing) and invalid (failing) cases for each verification dimension."
evaluation_mode: single-turn
checks: "LLM03-provenance-integrity-check"
row_count: 15
---
