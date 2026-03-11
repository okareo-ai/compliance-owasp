# Research: OWASP LLM08 Vector and Embedding Weaknesses Test Suite

**Branch**: `008-llm08-vector-embedding` | **Date**: 2026-03-11

## Research Questions & Decisions

### R1: RAG Injection Scenario Format — Multi-Turn Driver Parameters

**Decision**: The RAG injection scenario uses a JSON object `input` with keys matching the adversarial driver's mustache parameters: `{injection_type}`, `{poisoned_document}`, `{target_behavior}`, `{escalation_steps}`. This allows a single driver persona to simulate diverse RAG injection strategies.

**Rationale**: Following the LLM01 pattern (R4 — crescendo attack parameterization), the driver persona's behavior varies per scenario row. Each JSONL row provides a different injection vector (hidden system-level directive, formatting metadata injection, footnote injection, encoded payload in document) and the driver uses the poisoned document content as context to craft queries that reference and exploit the injected instructions across turns.

**Alternatives considered**:
- Static driver with no parameterization: Would limit coverage to a single injection pattern per simulation run. Rejected — the OWASP LLM08 risk surface spans multiple injection vectors.
- Multiple driver personas (one per injection type): Overly rigid and harder to maintain. Rejected per LLM01 precedent.

### R2: Cross-Tenant Leakage — Check Type Selection

**Decision**: Use a model-based check (`check_type: model`, `output_type: pass_fail`) for cross-tenant leakage detection. The check evaluates whether the agent's response contains content attributable to an unauthorized tenant or permission scope.

**Rationale**: Cross-tenant leakage manifests as the agent citing, summarizing, or referencing information from documents that belong to a different tenant than the query context specifies. Detecting this requires semantic judgment — the leaked content may be paraphrased, integrated into a broader response, or presented without explicit attribution. A model-based evaluator can assess whether response content plausibly originates from unauthorized sources, which regex or keyword matching cannot reliably determine.

**Alternatives considered**:
- Code-based check with keyword matching: Would only catch verbatim leakage. Most real-world leakage involves paraphrased or integrated content. Rejected for primary check; could supplement as a secondary signal.
- Hybrid (model + code): Deferred — model-based check provides sufficient coverage for initial implementation.

### R3: Access Control Validation — Code-Based Check Design

**Decision**: Use a code-based check (`check_type: code`, `output_type: pass_fail`) implemented as a Python function that receives the model output (which the scenario structures to contain retrieval result metadata) and validates each entry against the authorized tenant/scope boundaries defined in the scenario `result` field.

**Rationale**: Access control enforcement is a deterministic property — an entry either matches the authorized metadata filters or it doesn't. Model-based evaluation would introduce unnecessary non-determinism for a binary compliance check. Code-based checks execute as Python functions in Okareo, receiving `model_output` and `scenario_result` and returning a boolean pass/fail with an explanation string.

**Alternatives considered**:
- Model-based check: Would work but introduces LLM judgment variance for a property that should be deterministic. Rejected for the primary check.
- External validation script (not Okareo-managed): Would break the Okareo-native execution principle. Rejected per Constitution Principle III.

### R4: Scenario Input Format — Encoding Retrieval Context

**Decision**: Single-turn scenarios (cross-tenant leakage, access control validation) encode retrieval context directly in the `input` string alongside the user query. The format uses a structured delimiter: `"User query: {query}\n\nRetrieved documents:\n{documents}"` where each document includes metadata tags (`[tenant_id: X]`, `[scope: Y]`) and content.

**Rationale**: Following the LLM01 indirect injection pattern, the scenario input simulates what the agent's RAG pipeline would present — the user's query combined with retrieved context. For cross-tenant scenarios, the documents include both authorized and unauthorized content so the check can assess whether the agent's response draws from unauthorized sources. For access control scenarios, the documents include metadata fields that the code-based check validates against the expected policy in `result`.

**Alternatives considered**:
- Separate `context` field alongside `input`: The Okareo scenario format supports `input` and `result` only. Adding fields would require custom handling. Rejected.
- External context file referenced by ID: Breaks file-first principle and adds complexity. Rejected.

### R5: Multi-Turn RAG Injection — Turn Flow and Driver Strategy

**Decision**: `max_turns=10, first_turn="driver"` for RAG injection simulations. The adversarial driver initiates by asking a benign question related to topics covered in the poisoned documents, then progressively references the hidden instructions and attempts to get the agent to follow them.

**Rationale**: Unlike LLM01's crescendo attack (where `first_turn="driver"` sends the first adversarial message), the RAG injection scenario requires the driver to craft queries that trigger retrieval of poisoned documents. The driver starts with legitimate queries about topics in the knowledge base, then pivots to exploiting the hidden instructions found in retrieved content. The driver persona is informed of what the poisoned documents contain (via `{poisoned_document}` parameter) so it can craft queries that reference and amplify the injected directives.

**Alternatives considered**:
- `first_turn="target"` (agent greets first): Adds a wasted turn and doesn't match the RAG query model. Rejected.
- `max_turns=5`: May be insufficient for progressive escalation through document-reference queries. Rejected per spec FR-001 (10 turns).

### R6: Code-Based Check — Input/Output Contract

**Decision**: The code-based access control check receives `model_output` as a JSON string containing retrieval results with metadata fields, and `scenario_result` as a JSON string defining the authorized access policy. The check parses both, validates each result's metadata against the policy, and returns `pass` if all results are authorized or `fail` with a list of violating entries.

**Rationale**: Okareo code-based checks execute a Python function that receives the model's output and the scenario's expected result. For LLM08, the scenario is designed so that the `input` contains queries that produce retrieval results (with metadata), and the `result` contains the access control policy to validate against. The code-based check parses both JSON strings and performs deterministic field-level comparison.

**Alternatives considered**:
- Separate policy configuration file: Would require loading external state in the check function. Rejected — policy should be self-contained in the scenario row for portability.
- Hardcoded policy in the check: Would make the check non-reusable across different tenants/scopes. Rejected per Constitution Principle IV.

### R7: Notebook Structure — Mixed Check Types

**Decision**: The notebook handles both model-based and code-based check registration in a single upload flow. Model-based checks are parsed from `.md` files; code-based checks are loaded from `.py` files. The upload cell detects file extension and uses the appropriate registration API (`ModelBasedCheck` vs `CodeBasedCheck`).

**Rationale**: LLM08 is the first category in this project to require both model-based and code-based checks within the same notebook (other categories like LLM02, LLM03, LLM05 also mix types). The upload flow should handle both transparently. The notebook scans `checks/*.md` for model-based and `checks/*.py` for code-based, using the same `create_or_update_check` API with different `check` constructor classes.

**Alternatives considered**:
- Separate upload cells per check type: Adds complexity without benefit. Rejected.
- Unified `.md` format with embedded Python: Mixes concerns and complicates parsing. Rejected.
