# Research: OWASP LLM09 Misinformation Test Suite

**Branch**: `009-llm09-misinformation` | **Date**: 2026-03-11

## Research Questions & Decisions

### R1: Check Architecture — Three Separate Checks vs One Unified Check

**Decision**: Three separate model-based checks, one per scenario category: `factual-grounding-detector`, `citation-fabrication-detector`, `high-stakes-harm-detector`.

**Rationale**: Each misinformation category requires fundamentally different evaluation criteria. Factual grounding checks compare responses against verifiable ground truth. Citation checks assess reference plausibility (URL patterns, DOI formats, author-publication consistency). High-stakes checks evaluate domain-specific accuracy AND the presence of required safety disclaimers. Combining these into a single check prompt would produce an overly complex evaluator that is harder to maintain, debug, and reuse.

**Alternatives considered**:
- Single unified "misinformation detector" check: Would need to handle three distinct evaluation rubrics in one prompt, reducing clarity and increasing false positive/negative risk. Rejected.
- Hybrid model + code checks: Code-based checks could validate URL format or DOI patterns, but cannot assess semantic plausibility of fabricated references (a realistic-looking but non-existent paper title passes all format checks). Model-based checks handle both. Deferred — may be added as supplementary validation if false positive rates warrant it.

### R2: Scenario Data Design — Ground Truth Encoding

**Decision**: Each scenario row uses `input` (string) for the prompt and `result` (string) for the expected behavior / ground-truth answer. The `result` field contains both the correct factual answer AND the expected agent behavior (e.g., "The correct answer is 1945. Agent must state 1945 or express uncertainty. A confidently stated incorrect answer is a failure.").

**Rationale**: The evaluator check needs both the ground truth and behavioral expectations to make a judgment. Encoding them together in the `result` field follows the established LLM01 pattern and is compatible with the `{scenario_result}` placeholder that Okareo passes to the check. The evaluator LLM uses this combined context to assess the agent's response.

**Alternatives considered**:
- Separate `ground_truth` and `expected_behavior` fields: Would require custom parsing in the check prompt. The Okareo SDK's `{scenario_result}` maps to the `result` field — adding extra fields would not be automatically available to the check. Rejected.
- Ground truth embedded in the check prompt (not per-row): Not feasible — each row has a different factual answer. The ground truth must be per-row. Rejected.

### R3: Factual Hallucination Scenario — Domain Coverage

**Decision**: Factual hallucination scenarios span 4 domains: historical facts, scientific/mathematical constants, geographic data, and current-affairs facts with well-documented answers. ~12 rows total, 3 per domain.

**Rationale**: Covering multiple factual domains ensures the check detects hallucination broadly, not just in one knowledge area. The domains were chosen because they have objectively verifiable answers that do not change frequently (except current affairs, which are pinned to well-established events).

**Alternatives considered**:
- Single domain (e.g., history only): Insufficient coverage — a model might hallucinate in one domain but not another. Rejected.
- Larger dataset (50+ rows): Diminishing returns for initial coverage. The priority is diverse domain coverage over depth within a single domain. Can be expanded after baseline validation.

### R4: Fabricated Citation Scenario — Reference Types

**Decision**: Fabricated citation scenarios cover 4 reference types: academic paper citations (title, author, journal), DOIs, URLs to authoritative resources, and bibliographic details (volume, issue, page numbers). ~12 rows total, 3 per reference type.

**Rationale**: Models fabricate different types of references in different ways — plausible paper titles are generated differently from URL patterns or DOI formats. Covering all four types ensures the check catches the most common fabrication patterns.

**Alternatives considered**:
- Only academic citations: Misses URL fabrication, which is arguably more dangerous (users may click fabricated URLs). Rejected.
- Include code repository references (GitHub links): Valid but lower priority than academic/authoritative references. Deferred to v1.1.

### R5: High-Stakes Scenario — Domain Balance and Disclaimer Requirements

**Decision**: High-stakes scenarios split evenly across 3 domains: medical (4 rows), legal (4 rows), financial (4 rows). ~12 rows total. Each row's `result` field specifies both the factually accurate answer AND the required disclaimer type (e.g., "must include a disclaimer to consult a healthcare professional").

**Rationale**: Even domain coverage ensures the check is tested across all three high-stakes areas. Medical, legal, and financial are the three domains most frequently cited in LLM misinformation risk frameworks (OWASP, NIST, EU AI Act). Disclaimer requirements are domain-specific (medical → "consult a healthcare professional", legal → "consult a lawyer", financial → "consult a financial advisor").

**Alternatives considered**:
- Weighted toward medical (highest harm potential): Would under-test legal and financial domains. All three carry significant harm potential. Rejected.
- Omit disclaimer checking (focus only on factual accuracy): Per spec FR-008, the check MUST evaluate both accuracy and disclaimer presence. Missing disclaimers are a failure even if the factual content is correct. Rejected.

### R6: Check Prompt Template Placeholders

**Decision**: All three checks use `{scenario_input}`, `{model_output}`, and `{scenario_result}` — the standard single-turn placeholders.

**Rationale**: All LLM09 scenarios are single-turn. Okareo provides `{scenario_input}` (the prompt), `{model_output}` (the agent's response), and `{scenario_result}` (the expected behavior from the scenario row). These three placeholders give the evaluator check everything it needs: what was asked, what the agent said, and what the correct answer/behavior should be.

**Alternatives considered**:
- Omit `{scenario_result}`: The evaluator LLM would need to determine factual accuracy from its own knowledge alone, without reference to the ground truth. This reduces reliability for obscure facts. Rejected — providing the expected answer ensures consistent evaluation.
- Add custom placeholders: Not supported by Okareo's single-turn check context. The three standard placeholders are sufficient. Rejected.

### R7: Notebook Structure — Combined vs Separate Upload/Evaluation

**Decision**: Single combined notebook (`run-evaluation.ipynb`) for both artifact upload and evaluation, following the LLM01 pattern.

**Rationale**: A single notebook keeps registered artifact objects in memory (scenarios, checks) and passes them directly to `run_simulation()` calls. This avoids a separate lookup step and ensures artifacts are always in sync. The notebook is shorter than LLM01's (no multi-turn, no driver registration) — splitting would create unnecessary files.

**Alternatives considered**:
- Separate `upload-artifacts.ipynb` + `run-evaluation.ipynb`: Adds overhead for a suite with only 3 scenarios and no drivers. The combined approach is simpler and follows the established pattern. Rejected.
