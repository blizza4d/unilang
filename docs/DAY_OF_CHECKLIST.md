# Day-of-Presentation Checklist (DAY_OF_CHECKLIST.md)

Print or keep this single-page checklist visible on your secondary device during presentation day.

---

## ⏰ T-Minus 60 Minutes (Environment Warm-Up)
- [ ] Connect laptop to power adapter (do not present on battery).
- [ ] Connect to venue Wi-Fi and verify mobile hotspot is active as backup.
- [ ] Ping live backend to prevent cold start:
  ```bash
  curl -s https://backend-tau-livid-81.vercel.app/health
  ```
- [ ] Start offline local Docker container:
  ```bash
  docker compose up -d
  ```
- [ ] Verify `http://localhost:3000` is accessible locally in case venue internet drops.

---

## ⏰ T-Minus 30 Minutes (Browser Preparation)
- [ ] Open a dedicated clean browser window (no personal bookmarks or unrelated tabs).
- [ ] **Tab 1:** Live landing page at `https://uni-lang.vercel.app/`.
- [ ] **Tab 2:** Pre-loaded German invoice (`sample_de_math_error.pdf`) showing `REQUIRES_HUMAN_REVIEW`.
- [ ] **Tab 3:** Slide deck at `docs/SLIDES.md` or Google Slides full-screen mode.
- [ ] **Tab 4:** Backup 1080p demo video paused at `0:00`.
- [ ] Set browser zoom to 100% (`Ctrl + 0`).
- [ ] Mute all desktop notifications, Slack, Discord, and email clients.

---

## ⏰ T-Minus 5 Minutes (Stage Readiness)
- [ ] Test projector connection (verify split-screen workspace is centered without horizontal scrolling).
- [ ] Check microphone audio levels.
- [ ] Keep `docs/LIVE_FAILURE_PLAYBOOK.md` minimized on screen.
- [ ] Have the live URL ready to share: `https://uni-lang.vercel.app`.

---

## 🚀 During the Presentation (3-Minute Flow)
1. **[0:00 - 0:45]** State the problem: LLMs hallucinate financial arithmetic.
2. **[0:45 - 1:30]** Show architecture: LangGraph vision + deterministic Decimal math validator.
3. **[1:30 - 2:15]** Live Demo: Drop German sample, show math failure alert, press `R`, hover grounding, correct total, celebrate with Nova!
4. **[2:15 - 3:00]** Cite numbers: 95.58% Macro F1, 100% discrepancy catch rate, 103 kB bundle. Invite judges to try live URL.
