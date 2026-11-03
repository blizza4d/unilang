# ADR-001: Multi-Agent Control Tower with LangGraph

## Status
Accepted

## Context
Monolithic LLM prompts attempting to perform vision OCR, tabular extraction, language translation, and mathematical validation simultaneously suffer from high hallucination rates, inability to verify calculations accurately, and degraded schema compliance on edge cases.

## Decision
We architected the backend as a decoupled multi-agent state graph using LangGraph:
1. **Vision Ingestion Agent:** Processes multimodal images or multi-page PDFs rendered via Poppler.
2. **Schema Extractor Agent:** Employs structured outputs with Pydantic V2 to enforce schema conformance.
3. **Adversarial Judge Agent:** Specifically tasked with auditing and challenging the extracted fields.
4. **Deterministic Math Override:** Pure Python arithmetic validator that cannot be overridden by model hallucinations.

## Consequences
- Significant reduction in mathematical discrepancies.
- Highly modular and testable agents with isolated prompts.
- Ability to independently swap or benchmark vision vs. extractor models (e.g. Gemini 2.5 Flash for multimodal vision + GPT-4o for complex extraction).
