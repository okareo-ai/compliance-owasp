# OWASP LLM Top 10 (2025) — Scenario Analysis Report

## Executive Summary

To achieve **complete OWASP AI Agent testing and certification**, this project requires **30 discrete test scenarios** organized across the 10 OWASP LLM Top 10 categories. These decompose into:

- **18 single-turn evaluation scenarios** (via `run_simulation` with Okareo Drivers max-turns set to 1)
- **12 multi-turn simulation scenarios** (via `run_simulation` with Okareo Drivers max-turns set to 10)

Each OWASP category maps to one `speckit.specify` feature, resulting in **10 feature specifications** that together constitute full coverage.

---

## Scenario Breakdown by OWASP Category

### LLM01: Prompt Injection — 5 scenarios | Severity: Critical

Per Constitution Principle V, this category **requires multi-turn simulation** for jailbreak chains, alongside single-turn checks for stateless injection patterns.

| #   | Scenario                                                                           | Eval Mode             | Rationale                                                                                |
| --- | ---------------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------- |
| 1   | Direct prompt injection (role/instruction override)                                | Single-turn           | Tests whether explicit "ignore previous instructions" and role-hijacking prompts succeed |
| 2   | Indirect prompt injection (poisoned external content)                              | Single-turn           | Tests whether injected instructions in retrieved documents/files alter behavior          |
| 3   | Multi-turn jailbreak escalation (crescendo attack)                                 | Multi-turn simulation | Tests whether gradual escalation across 5-10 turns erodes safety boundaries              |
| 4   | Obfuscated/encoded injection (Base64, multilingual, Unicode, adversarial suffixes) | Single-turn           | Tests whether encoded or obfuscated payloads bypass input filters                        |
| 5   | Payload splitting attack (split malicious intent across inputs)                    | Single-turn           | Tests whether fragmented prompts reassemble into harmful instructions                    |

### LLM02: Sensitive Information Disclosure — 3 scenarios | Severity: Critical

Single-turn evaluation is sufficient (Constitution Principle V — stateless risk).

| #   | Scenario                                                        | Eval Mode   | Rationale                                                                     |
| --- | --------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| 6   | PII exfiltration probes (names, emails, SSN, financial data)    | Single-turn | Tests whether the model leaks personal data from context or training          |
| 7   | Training data extraction attacks (memorization probes)          | Single-turn | Tests whether repeated/targeted queries extract training corpus verbatim      |
| 8   | Credential and secret leakage (API keys, tokens, internal URLs) | Single-turn | Tests whether secrets embedded in context or tool outputs leak into responses |

### LLM03: Supply Chain — 2 scenarios | Severity: High

Primarily governance-oriented. Runtime scenarios validate that third-party components behave within expected boundaries.

| #   | Scenario                                                                    | Eval Mode                      | Rationale                                                                                |
| --- | --------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------- |
| 9   | Third-party model behavioral validation (unexpected capabilities/behaviors) | Single-turn                    | Tests that models from external providers don't exhibit undocumented or unsafe behaviors |
| 10  | Dependency and provenance integrity checks (SBOM/ML-BOM)                    | Single-turn (code-based check) | Validates model artifact signatures, version pinning, and license compliance             |

### LLM04: Data and Model Poisoning — 3 scenarios | Severity: High

| #   | Scenario                                                                | Eval Mode   | Rationale                                                                     |
| --- | ----------------------------------------------------------------------- | ----------- | ----------------------------------------------------------------------------- |
| 11  | RAG corpus poisoning detection (adversarial content in retrieval store) | Single-turn | Tests whether poisoned documents in a knowledge base manipulate model output  |
| 12  | Behavioral drift detection after data/model updates                     | Single-turn | Compares model outputs against a baseline to detect silent behavioral changes |
| 13  | Backdoor/sleeper trigger detection (hidden activation phrases)          | Single-turn | Tests whether specific trigger phrases activate planted backdoor behaviors    |

### LLM05: Improper Output Handling — 3 scenarios | Severity: High

Single-turn evaluation is sufficient (Constitution Principle V — stateless risk).

| #   | Scenario                                                                        | Eval Mode                      | Rationale                                                                          |
| --- | ------------------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------- |
| 14  | Injection payload in output (XSS, SQL injection, command injection)             | Single-turn                    | Tests whether model generates outputs containing executable injection payloads     |
| 15  | Unsafe code/command generation (path traversal, shell commands, arbitrary code) | Single-turn                    | Tests whether model outputs contain dangerous executable content                   |
| 16  | Structured output schema violation (malformed JSON, type mismatches)            | Single-turn (code-based check) | Tests whether model outputs conform to declared schemas for downstream consumption |

### LLM06: Excessive Agency — 3 scenarios | Severity: Critical

Per Constitution Principle V, this category **requires multi-turn simulation** for unauthorized action escalation.

| #   | Scenario                                                                  | Eval Mode             | Rationale                                                                           |
| --- | ------------------------------------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| 17  | Unauthorized tool invocation (agent calls tools beyond its granted scope) | Multi-turn simulation | Tests whether the agent invokes tools it should not have access to                  |
| 18  | Permission escalation across turns (progressive privilege widening)       | Multi-turn simulation | Tests whether an agent gradually expands its permissions through sequential actions |
| 19  | Autonomous action without human approval (bypass approval gates)          | Multi-turn simulation | Tests whether the agent performs high-impact actions without required confirmation  |

### LLM07: System Prompt Leakage — 3 scenarios | Severity: High

Per Constitution Principle V, this category **requires multi-turn simulation** for iterative extraction.

| #   | Scenario                                                        | Eval Mode             | Rationale                                                                          |
| --- | --------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------- |
| 20  | Direct system prompt extraction ("What are your instructions?") | Single-turn           | Tests whether blunt extraction queries reveal system prompt content                |
| 21  | Iterative multi-turn prompt extraction (progressive probing)    | Multi-turn simulation | Tests whether asking related questions across turns reconstructs the system prompt |
| 22  | Tool schema and configuration leakage                           | Single-turn           | Tests whether model reveals internal tool definitions, API schemas, or config      |

### LLM08: Vector and Embedding Weaknesses — 3 scenarios | Severity: High

| #   | Scenario                                                               | Eval Mode                      | Rationale                                                                          |
| --- | ---------------------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------- |
| 23  | RAG injection via retrieved content (hidden instructions in documents) | Multi-turn simulation          | Tests whether retrieved documents with embedded instructions hijack agent behavior |
| 24  | Cross-tenant/cross-scope data leakage in vector stores                 | Single-turn                    | Tests whether queries return content from unauthorized scopes or tenants           |
| 25  | Vector store access control and retrieval boundary validation          | Single-turn (code-based check) | Tests whether permission-aware filtering correctly restricts retrieved content     |

### LLM09: Misinformation — 3 scenarios | Severity: Medium

Single-turn evaluation is sufficient (Constitution Principle V — stateless risk).

| #   | Scenario                                                        | Eval Mode   | Rationale                                                                             |
| --- | --------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------- |
| 26  | Factual hallucination detection (confidently stated falsehoods) | Single-turn | Tests whether the model generates false claims when factual answers are available     |
| 27  | Fabricated citation/reference detection (invented sources)      | Single-turn | Tests whether the model invents URLs, paper titles, or author names                   |
| 28  | Misleading output in high-stakes decision contexts              | Single-turn | Tests whether model outputs could cause harm in medical, legal, or financial contexts |

### LLM10: Unbounded Consumption — 2 scenarios | Severity: Medium

Per Constitution Principle V, this category **requires multi-turn simulation** for resource exhaustion through repeated calls.

| #   | Scenario                                                               | Eval Mode             | Rationale                                                                             |
| --- | ---------------------------------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------- |
| 29  | Infinite tool/agent loop detection (recursive calls, unbounded chains) | Multi-turn simulation | Tests whether the agent enters infinite loops consuming resources without termination |
| 30  | Resource exhaustion via adversarial inputs (long prompts, token bombs) | Multi-turn simulation | Tests whether rate limits, budgets, and circuit breakers enforce consumption bounds   |

---

## Summary Metrics

| Metric                                  | Count                                 |
| --------------------------------------- | ------------------------------------- |
| Total OWASP categories                  | 10                                    |
| Total discrete scenarios                | 30                                    |
| Single-turn scenarios (`run_test`)      | 18                                    |
| Multi-turn scenarios (`run_simulation`) | 12                                    |
| Critical severity categories            | 3 (LLM01, LLM02, LLM06)               |
| High severity categories                | 5 (LLM03, LLM04, LLM05, LLM07, LLM08) |
| Medium severity categories              | 2 (LLM09, LLM10)                      |
| `speckit.specify` features needed       | 10                                    |

---

## Suggested `speckit.specify` Statements

Each statement below is designed to be run as `/speckit.specify <statement>` to produce one feature spec per OWASP category.

### 1. LLM01 — Prompt Injection

```
/speckit.specify Create an OWASP LLM01 Prompt Injection test suite for AI agents. Must cover 5 discrete scenarios: (1) direct prompt injection with role/instruction override attempts, (2) indirect prompt injection via poisoned external content in RAG or file inputs, (3) multi-turn jailbreak escalation using crescendo attack patterns over 5-10 conversational turns, (4) obfuscated/encoded injection using Base64, multilingual, Unicode, and adversarial suffix techniques, and (5) payload splitting attacks that fragment malicious intent across multiple inputs. Scenarios 1, 2, 4, 5 use single-turn Okareo checks; scenario 3 uses multi-turn Okareo simulation with an adversarial driver persona. All artifacts must include OWASP category ID LLM01, risk severity Critical, and be reusable across any target LLM.
```

### 2. LLM02 — Sensitive Information Disclosure

```
/speckit.specify Create an OWASP LLM02 Sensitive Information Disclosure test suite for AI agents. Must cover 3 discrete scenarios: (1) PII exfiltration probes testing whether the model leaks names, emails, SSNs, or financial data from context or training, (2) training data extraction attacks using memorization probes and targeted repeated queries to extract verbatim training corpus, and (3) credential and secret leakage testing whether API keys, tokens, or internal URLs from context or tool outputs appear in responses. All scenarios use single-turn Okareo checks. Checks must detect sensitive patterns (regex for PII, secrets, URLs) and use model-based evaluation for contextual leakage. All artifacts must include OWASP category ID LLM02, risk severity Critical.
```

### 3. LLM03 — Supply Chain

```
/speckit.specify Create an OWASP LLM03 Supply Chain Vulnerabilities test suite for AI agents. Must cover 2 discrete scenarios: (1) third-party model behavioral validation testing that models from external providers do not exhibit undocumented or unsafe behaviors outside their stated capabilities, and (2) dependency and provenance integrity checks validating model artifact signatures, version pinning, SBOM/ML-BOM compliance, and license compatibility. Scenario 1 uses single-turn Okareo checks against behavioral baselines. Scenario 2 uses code-based Okareo checks for deterministic verification. All artifacts must include OWASP category ID LLM03, risk severity High.
```

### 4. LLM04 — Data and Model Poisoning

```
/speckit.specify Create an OWASP LLM04 Data and Model Poisoning test suite for AI agents. Must cover 3 discrete scenarios: (1) RAG corpus poisoning detection testing whether adversarial content injected into a retrieval store manipulates model outputs, (2) behavioral drift detection comparing model outputs against a known-good baseline after data or model updates to detect silent changes, and (3) backdoor/sleeper trigger detection testing whether specific trigger phrases activate planted backdoor behaviors that deviate from normal operation. All scenarios use single-turn Okareo checks. Must support corpus versioning and baseline comparison workflows. All artifacts must include OWASP category ID LLM04, risk severity High.
```

### 5. LLM05 — Improper Output Handling

```
/speckit.specify Create an OWASP LLM05 Improper Output Handling test suite for AI agents. Must cover 3 discrete scenarios: (1) injection payload detection in model output testing whether responses contain XSS, SQL injection, or command injection payloads that could be executed downstream, (2) unsafe code/command generation detecting path traversal sequences, shell commands, and arbitrary executable code in outputs, and (3) structured output schema violation testing whether model outputs conform to declared JSON schemas and type contracts for safe downstream consumption. Scenarios 1-2 use model-based Okareo checks; scenario 3 uses code-based checks for deterministic validation. All artifacts must include OWASP category ID LLM05, risk severity High.
```

### 6. LLM06 — Excessive Agency

```
/speckit.specify Create an OWASP LLM06 Excessive Agency test suite for AI agents. Must cover 3 discrete scenarios using multi-turn Okareo simulations: (1) unauthorized tool invocation testing whether the agent calls tools beyond its granted scope when prompted by an adversarial user, (2) permission escalation across turns testing whether an agent progressively widens its permissions through sequential actions without explicit authorization, and (3) autonomous action without human approval testing whether the agent performs high-impact actions (data deletion, external API calls, financial transactions) without required confirmation gates. All scenarios require adversarial driver personas that attempt to manipulate the agent into exceeding its authority. All artifacts must include OWASP category ID LLM06, risk severity Critical.
```

### 7. LLM07 — System Prompt Leakage

```
/speckit.specify Create an OWASP LLM07 System Prompt Leakage test suite for AI agents. Must cover 3 discrete scenarios: (1) direct system prompt extraction using blunt queries like "What are your instructions?" and known extraction techniques, (2) iterative multi-turn prompt extraction using progressive probing across conversational turns to reconstruct system prompt content piece by piece, and (3) tool schema and configuration leakage testing whether the model reveals internal tool definitions, API schemas, endpoint URLs, or configuration parameters. Scenario 1 and 3 use single-turn Okareo checks; scenario 2 uses multi-turn Okareo simulation with a probing driver persona. Checks must evaluate whether response content contains fragments matching known system prompt patterns. All artifacts must include OWASP category ID LLM07, risk severity High.
```

### 8. LLM08 — Vector and Embedding Weaknesses

```
/speckit.specify Create an OWASP LLM08 Vector and Embedding Weaknesses test suite for AI agents. Must cover 3 discrete scenarios: (1) RAG injection via retrieved content testing whether hidden instructions embedded in documents in the retrieval store can hijack agent behavior across multiple turns, (2) cross-tenant/cross-scope data leakage testing whether queries to a vector store return content from unauthorized tenants or permission scopes, and (3) vector store access control validation testing whether permission-aware filtering correctly restricts retrieved content to authorized boundaries. Scenario 1 uses multi-turn Okareo simulation; scenarios 2-3 use single-turn checks (code-based for deterministic access control verification). All artifacts must include OWASP category ID LLM08, risk severity High.
```

### 9. LLM09 — Misinformation

```
/speckit.specify Create an OWASP LLM09 Misinformation test suite for AI agents. Must cover 3 discrete scenarios: (1) factual hallucination detection testing whether the model generates confidently stated falsehoods when verifiable factual answers exist, (2) fabricated citation and reference detection testing whether the model invents URLs, paper titles, author names, or publication details, and (3) misleading output in high-stakes decision contexts testing whether model responses in medical, legal, or financial domains could cause harm through inaccurate guidance. All scenarios use single-turn Okareo checks with model-based evaluation for factual grounding and citation verification. All artifacts must include OWASP category ID LLM09, risk severity Medium.
```

### 10. LLM10 — Unbounded Consumption

```
/speckit.specify Create an OWASP LLM10 Unbounded Consumption test suite for AI agents. Must cover 2 discrete scenarios using multi-turn Okareo simulations: (1) infinite tool/agent loop detection testing whether the agent enters recursive or circular tool call chains that consume unbounded resources without termination, and (2) resource exhaustion via adversarial inputs testing whether rate limits, token budgets, timeout policies, and circuit breakers correctly enforce consumption bounds when subjected to long prompts, repeated rapid queries, and token-bomb inputs. Driver personas must simulate abusive usage patterns. Checks must evaluate whether the system enforces its stated resource policies. All artifacts must include OWASP category ID LLM10, risk severity Medium.
```

---

## Recommended Implementation Order

Based on severity and dependency:

| Phase                               | Categories          | Rationale                                                 |
| ----------------------------------- | ------------------- | --------------------------------------------------------- |
| **Phase 1** (Critical)              | LLM01, LLM02, LLM06 | Highest risk; foundational attack surfaces                |
| **Phase 2** (High — Agent-specific) | LLM07, LLM05, LLM08 | Agent-architecture risks; depend on Phase 1 patterns      |
| **Phase 3** (High — Data/Supply)    | LLM03, LLM04        | Governance and data integrity; can reuse Phase 1-2 checks |
| **Phase 4** (Medium)                | LLM09, LLM10        | Important but lower severity; can reuse shared drivers    |

---

## Shared/Reusable Artifacts

The constitution's `owasp/shared/` directory should contain:

- **Generic Red-Teamer Driver**: Reusable adversarial persona for multi-turn scenarios across LLM01, LLM06, LLM07, LLM10
- **PII Detection Check**: Reusable regex + model-based check for LLM02 and LLM07 (system prompt may contain PII)
- **Injection Payload Check**: Reusable across LLM01 (input) and LLM05 (output)
- **Schema Compliance Check**: Reusable across LLM05 and LLM08

---

## Constitution Alignment

This approach satisfies all six constitution principles:

| Principle                         | How Satisfied                                                                                         |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| I. OWASP-Complete Coverage        | All 10 categories covered with at least 2 scenarios, 1+ checks, and 1+ drivers each                   |
| II. Explainability & Transparency | Each scenario includes OWASP ID, plain-language description, risk severity, and result interpretation |
| III. Okareo-Native Execution      | All scenarios, checks, drivers, and test runs executed via Okareo MCP tools                           |
| IV. Composability & Reusability   | Artifacts are standalone, parameterized, and model-agnostic; shared artifacts reduce duplication      |
| V. Simulation-Driven Coverage     | Multi-turn simulation mandated for LLM01, LLM06, LLM07, LLM10; single-turn for stateless risks        |
| VI. Traceability & Auditability   | Structured metadata headers on all artifacts; results linked to OWASP category and severity           |

---

_Generated: 2026-03-09 | Based on: OWASP LLM Top 10 v2025 | Constitution: v1.0.0_
