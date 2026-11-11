# Demo Video Script: DataNova Extract v1.0.0-rc.1 (DEMO_VIDEO_SCRIPT.md)

**Target Video Duration:** 2 minutes 45 seconds (165 seconds)  
**Format:** 1080p (1920×1080), 30 fps, clean desktop profile, smooth cursor highlight, system notifications muted  
**Target Audience:** Hackathon Judges, Enterprise FinOps, Engineering Leads  

---

## Pre-Recording Checklist & Recording Settings
- [ ] Browser resolution set to 1920×1080 at 100% zoom (clean dark background).
- [ ] Backend is pre-warmed (`curl https://backend-tau-livid-81.vercel.app/health`).
- [ ] Sample invoices loaded in file explorer or quick-access panel.
- [ ] **DO NOT SHOW:** Real API keys, personal user credentials, terminal windows containing unmasked tokens.
- [ ] Cursor highlight tool enabled with soft cyan halo on click.

---

## Shot-by-Shot Timeline & Narration

| Timestamp | Visual Action (Screen) | Narration (Voiceover) | Caption (Subtitle) |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:15** | Open on live landing page (`https://uni-lang.vercel.app/`). Nova Droid stands quietly on the left panel. Clean Analog AI interface. | "Global companies process thousands of invoices every day across dozens of languages and currencies. Manual data entry is slow, but standard LLMs hallucinate numbers—which leads to expensive accounting discrepancies." | Processing multilingual invoices is slow, and LLMs often hallucinate financial totals. |
| **0:15 - 0:40** | Drag and drop `sample_de_math_error.pdf` onto the dropzone. Nova's eyes light up, legs walk across the canvas toward the document, and a laser scanning bar moves vertically. Stage indicators tick from Ingestion to Vision to Extraction. | "Watch what happens when we upload a German invoice with European comma decimals. Our kinematic companion, Nova, walks to the document and tracks each pipeline stage in real time." | Dragging German invoice with comma decimals. Nova walks to document and tracks stages. |
| **0:40 - 1:10** | Extraction completes. The right panel populates with extracted fields. The header banner glows amber: `REQUIRES HUMAN REVIEW`. Total amount (`€3,475.00`) is outlined in glowing amber with a warning tooltip. | "The extraction finishes, but notice the status: Needs Review. Why? Because DataNova Extract doesn't blindly trust model outputs. Our deterministic arithmetic engine verified the math and caught that the stated total was five hundred euros higher than the sum of items and tax." | Deterministic arithmetic validator catches €500 calculation discrepancy. Status: Needs Review. |
| **1:10 - 1:45** | Press `R` or click `Review Mode`. Click the flagged Total Amount field. The PDF viewer on the left automatically pans and highlights the bounding box around the total on the original invoice. Correct `3,475.00` to `2,975.00`. | "Pressing 'R' enters Review Mode. Hovering over any field highlights its exact visual bounding box on the source document. We correct the total to two thousand nine hundred seventy-five euros. Instantly, the arithmetic reconciles." | Interactive review with visual grounding. Correcting the total reconciles the arithmetic. |
| **1:45 - 2:05** | The status badge shifts to emerald sage: `APPROVED`. Nova celebrates with a cheerful bounce and green aura. Click `Export -> Excel (.xlsx)`. Open the spreadsheet showing clean formulas and cell values. | "The document status upgrades to Approved, and Nova celebrates. We can now export directly to Excel with native formulas, CSV, or an audit-ready PDF." | Document status: Approved. One-click export to Excel, CSV, or audited PDF. |
| **2:05 - 2:25** | Click `Batch` in the header. Queue three multilingual invoices (Hindi GST, Arabic RTL, English SaaS). All three process concurrently with live progress indicators. | "In production, high volume matters. Our batch queue handles up to 20 documents simultaneously across non-Latin scripts including Devanagari, Arabic, Tamil, and CJK." | Batch queue processing multiple documents across Latin, Devanagari, and Arabic scripts. |
| **2:25 - 2:45** | Architecture slide / view showing LangGraph multi-agent flow: Vision Agent -> Extractor Agent -> Deterministic Math Override -> Judge Agent -> Human Review. | "Under the hood, LangGraph orchestrates specialized Vision, Extractor, and Judge agents, reinforced by strict client-side cost controls and a zero-drift math validator. Try it yourself right now at uni-lang.vercel.app." | Powered by LangGraph multi-agent architecture and deterministic math validation. Live at uni-lang.vercel.app. |

---

## B-Roll & Cutaway Suggestions
1. **Kinematic Rig Close-up (1080p):** Close-up of Nova's leg articulation during the walk cycle, showing smooth sine-wave foot planting.
2. **Bounding Box Parity:** Split screen showing cursor moving across line items on the right while corresponding bounding box rectangles light up on the PDF.
3. **Excel Formulas:** Close-up of downloaded `.xlsx` showing `=SUM(C2:C5)` formulas rather than hardcoded text.
