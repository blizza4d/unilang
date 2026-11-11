# Hackathon Pre-Submission Checklist (SUBMISSION_CHECKLIST.md)

Use this checklist immediately before submitting DataNova Extract to the hackathon portal (Devpost, DoraHacks, or internal judge review).

---

## 1. Codebase & Git Status
- [ ] On clean branch `release/1.0.0-rc1` (or merged to `main` via PR).
- [ ] `git status` shows zero uncommitted changes or untracked temporary files.
- [ ] Latest commit pushed to remote: `https://github.com/blizza4d/unilang`.
- [ ] Tag `v1.0.0-rc.1` created and pushed (`git push origin --tags`).

---

## 2. Automated Release Gates & Quality Verification
- [ ] Backend tests passing in randomized order:
  ```bash
  cd backend && pytest -v --randomly-seed=42
  ```
- [ ] Frontend builds with zero TypeScript errors or ESLint warnings:
  ```bash
  cd frontend && npm run build
  ```
- [ ] Claims audit verifies zero undocumented metrics:
  ```bash
  python scripts/check_claims.py
  ```
- [ ] Full automated release gate passes all 12 criteria:
  ```bash
  python scripts/release_gate.py
  ```

---

## 3. Deployment & Live Verification
- [ ] Frontend live at: **https://uni-lang.vercel.app/**.
- [ ] Backend live at: **https://backend-tau-livid-81.vercel.app**.
- [ ] Live rehearsal script passes:
  ```bash
  python scripts/rehearsal.py
  ```
- [ ] Footer on live site reads `v1.0.0-rc.1` with commit SHA `(859bfd9)` and `Production` badge.
- [ ] Tested on desktop browser (Chrome/Edge/Firefox) in an incognito window.
- [ ] Tested on mobile browser (Safari on iOS or Chrome on Android).

---

## 4. Submission Package & Links
- [ ] `docs/SUBMISSION.md` copied into submission portal:
  - [ ] Project title & tagline (under 80 chars).
  - [ ] Short description (under 300 chars).
  - [ ] Long description (400–600 words).
  - [ ] Tech stack tags selected.
  - [ ] Team members and roles filled in (`[USER: ...]` replaced).
- [ ] Demo video recorded (2.5 minutes) using `docs/DEMO_VIDEO_SCRIPT.md` and uploaded.
- [ ] Video URL pasted into submission form.
- [ ] Presentation slides link pasted into submission form.

---

## 5. Emergency Preparedness & Fallback
- [ ] Offline demo fixtures verified (works 100% without external API keys).
- [ ] `docs/LIVE_FAILURE_PLAYBOOK.md` reviewed for live demo day.
- [ ] Spend limits verified in OpenAI and Google Cloud consoles ($10/day).
