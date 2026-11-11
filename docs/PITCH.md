# Pitch Deck Guide & Elevator Pitches (PITCH.md)

This document provides spoken pitches (30-second, 60-second, and 3-minute formats), presentation hooks, and audience-tailored narratives for DataNova Extract v1.0.0-rc.1.

---

## 1. The 30-Second Elevator Pitch
> "Global companies lose millions to manual invoice processing, but generative AI models hallucinate arithmetic—approving totals that don't match the items.  
> **DataNova Extract** is a multilingual document understanding studio that fixes this. We pair multi-agent vision models with a deterministic mathematical engine that enforces 100% arithmetic verification. If an invoice doesn't balance to the penny, it flags the field, grounds it to the source PDF, and routes it to an interactive review workspace. It's live right now at **uni-lang.vercel.app**."

---

## 2. The 60-Second Competition Pitch
> "In financial accounting, an AI model that is 99% accurate but hallucinates on the other 1% is a liability that causes audit failures and penalties.  
> We built **DataNova Extract** to make document AI mathematically trustable.  
> Powered by LangGraph, specialized vision and extraction agents parse invoices across six script families—including Devanagari Hindi GST, Arabic Right-to-Left, and European comma decimals.  
> But we never let the model approve its own math. Our deterministic Python Decimal engine independently calculates every line item and tax total with zero drift. On our 42-case realistic benchmark, we achieved a **95.58% Macro F1** and a **100% catch rate on arithmetic discrepancies**.  
> The interface is designed for real enterprise users: hover grounding lights up bounding boxes on the original PDF, exports generate native Excel formulas, and our kinematic companion Nova keeps users informed at every pipeline stage.  
> The codebase is open source and the live app is ready for you to test right now."

---

## 3. The 3-Minute Stage / Demo Pitch
> **[0:00 - 0:45] The Problem & The Danger of Generative Finance:**  
> "Judges, thank you. Every day, multinational enterprises ingest millions of invoices across different languages, currencies, and tax jurisdictions. The industry has tried two extremes: legacy OCR, which is brittle and fails on complex table layouts, and modern generative vision models, which are fluent but statistically prone to hallucinating financial calculations. A model will happily extract five line items and invent an incorrect total that never adds up. In finance, close enough isn't good enough."
>
> **[0:45 - 1:30] The Solution & Multi-Agent Architecture:**  
> "DataNova Extract introduces a hybrid paradigm: semantic AI understanding guarded by deterministic code invariants. We use LangGraph to orchestrate specialized agents. A vision agent processes multimodal documents rendered at 200 DPI. An extractor agent parses entities into structured Zod and Pydantic schemas.  
> But before any document is approved, all numerical values pass through our deterministic arithmetic validator. Code always trumps model reasoning. If calculated totals differ from stated totals by more than one cent, the system overrides the model, caps confidence at 70%, and routes the invoice to human review."
>
> **[1:30 - 2:15] Live Demonstration Highlights:**  
> "In our live interface, when you upload a German invoice with comma decimals, our kinematic SVG companion Nova walks across the screen, visually reflecting live Server-Sent Events. When a 500-euro discrepancy is detected, the field glows in amber. Pressing 'R' launches Review Mode: hovering over the total reveals its exact normalized bounding box on the original PDF. A quick keystroke corrects the number, Nova celebrates with an emerald aura, and you can export directly to Excel with live `=SUM()` formulas."
>
> **[2:15 - 3:00] Measured Rigor & Enterprise Viability:**  
> "We measure what matters. Across 42 realistic multilingual test cases in six script families, we achieved a 95.58% Macro F1 and a 100% true-positive catch rate on math errors. Our frontend is a blazing 103 kB bundle, and our backend enforces strict $2/hour spend caps and 24-hour ephemeral data retention. DataNova Extract proves that AI in finance can be fast, multilingual, and mathematically uncompromising. Visit uni-lang.vercel.app to test it live. Thank you!"

---

## 4. Key Presentation Hooks & Soundbites
- *"Generative AI should do the reading; deterministic code must do the math."*
- *"Code always trumps model reasoning."*
- *"A 99% accurate model that hallucinates 1% of your invoices is a financial audit waiting to happen."*
- *"From pixels to Python Decimal to Excel formulas in seconds."*
