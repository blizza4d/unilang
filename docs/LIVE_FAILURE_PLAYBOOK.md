# Live Demo Day Failure Playbook (LIVE_FAILURE_PLAYBOOK.md)

This playbook outlines immediate, single-action recoveries and spoken scripts for unexpected technical glitches during live hackathon demos or judge reviews.

---

## Failure Matrix & Recovery Actions

| Symptom / Failure | Root Cause | Immediate Recovery Action | What to Say to the Judges / Audience |
| :--- | :--- | :--- | :--- |
| **Backend Asleep or Cold (Waking Banner visible)** | Free-tier host idle sleep (spins down after 15 min of inactivity). | Nova Droid will show sleeping animation. Wait 20 seconds for the progress bar to fill, or switch to your pre-warmed backup browser tab. | *"Our cloud server is waking up from its low-power standby state. Notice how Nova reflects the sleep state while our cold-start progress bar tracks initialization."* |
| **LLM Provider Outage or 429 Rate Limit** | OpenAI / Google API rate limit exceeded or credit depletion. | Toggle demo mode in the status banner or use the sample buttons. Synthetic fixtures activate instantly with zero network delay. | *"We've intentionally hit our live hourly budget cap of $2.00. The platform instantly falls back to our recorded demo fixtures with full watermarking, ensuring zero downtime."* |
| **Inaccurate Extraction on an Audience File** | Messy font, unexpected table structure, or low-contrast scan. | Lean into human-in-the-loop: press `R`, highlight the bounding box, type the correction, and watch the status upgrade to `APPROVED`. | *"And this is the core value proposition of DataNova Extract: we don't expect AI to be perfect. The system flagged this field, grounded it to the original document, and allowed a one-second human verification."* |
| **Venue Wi-Fi Disconnects Completely** | Network drop or conference center proxy block. | Switch to local instance: `http://localhost:3000` (Docker container running locally) or switch to the 1080p recorded demo video. | *"While the conference Wi-Fi reconnects, let me switch to our offline container instance running locally on Docker."* |
| **Browser Crash / Accidental Tab Closure** | Memory spike or accidental shortcut misclick. | Reopen browser (`Ctrl+Shift+T`). Ingestion state is stored in LocalStorage; click the **History** button in the header to reload the document. | *"Thanks to our persistent client history store, reopening the session restores our full extraction state with a single click."* |
| **Projector Resolution Distorts Layout (4:3 or Low DPI)** | Conference projector set to 1024×768 or unusual aspect ratio. | Press `Ctrl + -` to zoom browser to 90%, or collapse the left document panel to focus on the extracted data table. | *"Let me zoom out slightly so the full split-workspace layout is visible on this projector."* |
| **Demo Video Audio Failure** | HDMI or Bluetooth speaker audio failure during video playback. | Mute video, enable subtitles using our provided `docs/demo_captions.srt`, and deliver the narration live following `docs/DEMO_VIDEO_SCRIPT.md`. | *"I will deliver the narration live while you follow along with the on-screen captions."* |

---

## 5-Minute Pre-Pitch Rehearsal Checklist
1. Ping backend health check: `curl -I https://backend-tau-livid-81.vercel.app/health`.
2. Open two tabs:
   - Tab 1: Live site at `https://uni-lang.vercel.app/`.
   - Tab 2: Pre-processed German math error invoice ready in Review Mode.
3. Keep local Docker container running in background as offline safety net (`docker compose up -d`).
4. Keep `docs/NUMBERS.md` open for rapid recall of exact figures during Q&A.
