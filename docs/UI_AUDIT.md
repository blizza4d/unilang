# DataNova Extract: Comprehensive UI & Droid Character Motion Audit

**Product:** DataNova Extract (v2.0 / v3.0)  
**Date:** 2026-11-08  
**Auditors:** Principal Product Designer & Senior Front-End Motion Engineer  
**Status:** Audit Completed; Execution Underway (Phases U0–U10)  

---

## 1. Droid Discovery Procedure (Section 0.3)

In accordance with Section 0.3 of the UI Excellence & Droid Animation Directive, a full discovery procedure was executed across the repository prior to writing any design or component code:

1. **Keyword Search:** Executed recursive case-insensitive search across the codebase for `droid`, `robot`, `mascot`, `bot`, `walker`, `walk`, `android`, `character`, `sprite`, `avatar`.
   - **Result:** No matches related to a character or mascot component. Matches found were only text strings (`"Start Interactive Product Walkthrough"` in `CommandPalette.tsx` and `GuidedTour.tsx`) and npm dependencies with `fs.walk`.
2. **Animation Primitive Search:** Executed search for `useAnimationControls`, `useAnimate`, `steps(`, `lottie`, `rive`, `canvas`, `svg` in `frontend/`.
   - **Result:** No sprite sheets, no character canvas, no Lottie/Rive JSON, no multi-part character SVG rigs.
3. **Asset Directory Inspection:** Checked `frontend/public/` and `frontend/components/`.
   - **Result:** Only `frontend/public/samples/` exists (containing sample PDFs). No character graphics or SVG avatars.
4. **Tailwind & CSS Keyframes Inspection:** Inspected `frontend/tailwind.config.ts` and `frontend/app/globals.css`.
   - **Result:** Found `scan`, `amber-pulse`, `fade-up`. No walking or limb rotation keyframes exist.
5. **Conclusion:** **No droid component exists in the repository.** Per Directive Section 0.3.5 and Section 5, Nova the inspection droid will be designed and built from scratch as an inline SVG multi-group rig driven by a continuous mathematical walk cycle engine.

---

## 2. Heuristic UI Audit & Defect Table

The following defects and areas for visual excellence have been identified across the current application interface:

| Defect ID | Category | Subsystem | Severity | Finding & Ground Truth | Proposed Fix & Design Target |
|---|---|---|---|---|---|
| **U-001** | Character / Motion | Droid | **High** | No droid character or walking animation exists in the codebase. | Create "Nova" as a lightweight, inline SVG multi-group rig (`frontend/components/droid/`) with a continuous phase-driven walk cycle, believable limb kinematics, and real app state binding. |
| **U-002** | Design Tokens | Foundation | **High** | Color values, borders, and shadows are hardcoded across Tailwind classes without a centralized CSS custom property token foundation. | Create `frontend/styles/tokens.css` with semantic surfaces (`--bg-app`, `--bg-panel`, `--bg-elevated`, `--bg-overlay`), borders, text contrast tokens, and motion tokens. Bind into `tailwind.config.ts`. |
| **U-003** | Typography | Typography | **Medium** | Numerals and IDs across several panels do not consistently enforce tabular figures (`tabular-nums`), causing minor text jitter during live edits or score calculations. | Enforce `font-variant-numeric: tabular-nums` and monospace styling on all numerical totals, timestamps, and confidence percentages. |
| **U-004** | Hierarchy | Header | **Medium** | The version chip `"v2.0 • LangGraph Control Tower"` competes in prominence with the brand title; actions lack consistent keyboard hint cues. | Refine header as a slim glass bar with quiet secondary metadata, unified `Kbd` chip for `Cmd+K`, and a clear connection status dot with tooltips. |
| **U-005** | Empty States | Right Panel | **Medium** | The right pane when idle renders only plain text `"Extracted data will appear here"`, which lacks visual delight and structure. | Render an elegant ghosted blueprint skeleton showing the schema structure (Entity fields, line item table, validation summary) so users immediately understand what will appear. |
| **U-006** | Stage Strip | Left Panel | **Medium** | The dropzone bottom has no dedicated resting ground for document inspection or companion feedback. | Introduce an 88px Stage Strip below the dropzone with a subtle 1px ground line where Nova the droid can rest, walk, and react to pipeline stages without shifting layout. |
| **U-007** | Component Consistency | UI Primitives | **Medium** | Buttons, tooltips, dialogs, and segmented toggles use ad-hoc Tailwind classes with varying radii and hover states. | Standardize primitives (`Button`, `IconButton`, `Kbd`, `Tooltip`, `Popover`, `Dialog`, `SegmentedControl`, `ToastHost`) with typed props and consistent focus rings. |
| **U-008** | Palette Discipline | Color | **Medium** | Verify that `--accent-amber` is strictly reserved for `Needs Review` and `--accent-green` for `Approved/resolved`. Selection highlight currently uses amber. | Set default selection color to neutral cream/white overlay, reserving amber strictly for review-needed fields. |
| **U-009** | Micro-interactions | Review Mode | **Low** | Resolving a flagged field transitions instantly without a soft, delightful micro-celebration. | Add a subtle 160ms scale-and-glow transition from amber to sage with checkmark morphing when a field is corrected. |
| **U-010** | Accessibility | Motion | **High** | No unified `usePrefersReducedMotion` hook using `useSyncExternalStore` for SSR safety. | Implement `usePrefersReducedMotion.ts` with in-app toggle support. When active, all loops freeze into static poses with full color and text equivalents. |
| **U-011** | QA / Preview | Tooling | **Medium** | No dedicated developer gallery exists to audit component states, typography, and droid walk poses in isolation. | Create `frontend/app/_ui/page.tsx` rendering a comprehensive component catalog and interactive `DroidLab` scrubber. |

---

## 3. Prioritized Implementation Plan

1. **Phase U1 (Tokens & Foundations):**
   - Create `frontend/styles/tokens.css` with full Analog AI palette, elevations, and motion tokens.
   - Update `frontend/tailwind.config.ts` and `frontend/app/globals.css`.
   - Create `frontend/lib/motion.ts` with standardized Framer Motion variants.
   - Build unified primitives: `Button.tsx`, `IconButton.tsx`, `Kbd.tsx`, `Tooltip.tsx`, `SegmentedControl.tsx`.
2. **Phase U2 & U3 (Shell, Layout & Core Components):**
   - Polish `Header.tsx`, `SplitWorkspace.tsx`, and `FileDropzone.tsx`.
   - Enhance right pane idle state with ghosted blueprint preview.
   - Refine `ExtractedField.tsx`, `StatusBadge.tsx`, `ConfidenceRing.tsx`, and `LineItemsTable.tsx`.
3. **Phase U5 & U6 (Droid Rig & Walk Cycle Engineering):**
   - Build `frontend/components/droid/Droid.tsx` (SVG multi-group rig: torso, head, visor, antenna, arms, two-segment legs, foot, ground shadow).
   - Implement `frontend/components/droid/pose.ts` with exact kinematic walk tables (contact, down, passing, up).
   - Implement `frontend/components/droid/useWalkCycle.ts` driving direct ref transforms at 60 fps with zero React re-renders.
4. **Phase U7 & U8 (Companion Behavior & Accessibility):**
   - Create `frontend/components/droid/DroidCompanion.tsx` connecting to Zustand document and pipeline stores.
   - Create `frontend/components/droid/StageStrip.tsx` with reserved layout footprint.
   - Implement `frontend/hooks/usePrefersReducedMotion.ts` and test suite.
5. **Phase U9 & U10 (Verification, DroidLab & Docs):**
   - Build `frontend/app/_ui/page.tsx` (`DroidLab` scrubber, pose viewer, component gallery).
   - Create `docs/DESIGN_SYSTEM.md` and `docs/DROID.md`.
