# Production Launch, Monitoring & Rollback Runbook (LAUNCH_RUNBOOK.md)

This runbook documents the operational procedure for launching DataNova Extract v1.0.0-rc.1, real-time telemetry monitoring for the first 48 hours, and automated rollback protocols.

---

## 1. Go-Live Deployment Procedure

### Step 1: Automated Preflight Gate
Run the automated release gate from a clean checkout:
```bash
python scripts/release_gate.py
```
*Requirement:* All 12 gates must return `PASS`.

### Step 2: Merge Release Candidate to Main
```bash
git checkout main
git merge --no-ff release/1.0.0-rc1 -m "release: 1.0.0-rc.1 DataNova Extract"
git push origin main
```

### Step 3: Git Tagging & GitHub Release
```bash
git tag -a v1.0.0-rc.1 -m "Release Candidate 1.0.0-rc.1"
git push origin v1.0.0-rc.1
```
Create a GitHub Release on repository `https://github.com/blizza4d/unilang/releases/tag/v1.0.0-rc.1` attaching `CHANGELOG.md` notes.

### Step 4: Vercel Production Deployment Verification
1. Open the [Vercel Deployment Dashboard](https://vercel.com/blizza4d/uni-lang).
2. Confirm the production build succeeded from the `v1.0.0-rc.1` tag or commit.
3. Open `https://uni-lang.vercel.app` in an incognito window.
4. Verify the footer reads: `v1.0.0-rc.1 (859bfd9) • PRODUCTION`.

### Step 5: Backend Service Verification
1. Run the live deployment test:
   ```bash
   python scripts/rehearsal.py
   ```
2. Verify `/health` returns status `ready`.
3. In demo mode or if spend caps are active, verify the client gracefully activates synthetic fixtures.

---

## 2. 48-Hour Monitoring Architecture

### What to Monitor
1. **Application Health & Uptime:** Free external uptime ping (e.g. Better Uptime or Cron-Job.org) pinging `GET https://backend-tau-livid-81.vercel.app/health` every 5 minutes. (This also prevents cold-start sleeping).
2. **Budget Spend Gauges:** Monitor `backend/middleware/budget_limit.py` state:
   - Alert threshold: Hourly spend > $1.80 (90% of $2.00 ceiling).
   - Alert threshold: Daily spend > $8.00 (80% of $10.00 ceiling).
3. **Client-Side Error Beacon:** The `/api/v1/client-errors` endpoint receives unhandled runtime exceptions from the frontend. Watch for repeated spike signatures.
4. **CORS & Rate Limiting (429s):** Monitor access logs for IP addresses exceeding 30 req/min.

---

## 3. Incident Response Playbooks

### Incident A: LLM Provider Outage or 429 Rate Limit
- **Detection:** Health check `/health/deep` reports `extractor_provider: false` or consecutive 429/500 errors in logs.
- **Action:**
  1. The middleware automatically activates `FEATURE_DEMO_MODE=true`.
  2. The frontend displays the yellow "Demo Active (Provider Standby)" badge.
  3. No downtime is experienced by end-users; sample fixtures continue processing cleanly.

### Incident B: Accidental Key Leak
- **Detection:** Automated scanner alert or commit anomaly.
- **Action:**
  1. Immediately revoke compromised keys in OpenAI and Google Cloud consoles.
  2. Generate new keys.
  3. Update Vercel / hosting environment variables:
     `vercel env add OPENAI_API_KEY production`
     `vercel env add GOOGLE_API_KEY production`
  4. Trigger instant redeployment: `vercel --prod`.

### Incident C: Corrupted Deployment / Bad Rollout
- **Recovery SLA:** < 60 seconds.
- **Vercel Rollback:**
  1. In the Vercel Dashboard, navigate to **Deployments**.
  2. Find the last known-good deployment (SHA `859bfd9`).
  3. Click the three dots (`...`) -> **Promote to Production**.
- **Backend Rollback:**
  ```bash
  git revert HEAD --no-edit
  git push origin main
  ```

---

## 4. Privacy & Post-Event Purge Policy
Within 48 hours following the hackathon event:
1. Run the manual upload purge:
   ```bash
   cd backend
   python -c "import shutil, os; shutil.rmtree('./storage_data', ignore_errors=True); print('Ephemeral storage purged.')"
   ```
2. Rotate temporary API keys and disable unrestricted public access codes.
3. Export and archive benchmark evaluation results in `docs/backup/`.
