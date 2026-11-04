# DataNova Extract: Production Deployment & Verification Runbook

This guide details the complete deployment process for **DataNova Extract**, covering both the **Next.js 15 Frontend (Vercel)** and the **FastAPI + LangGraph Backend (Render / Docker / VPS)**.

---

## 1. Architecture Overview

```
[ Browser / Client ]
        |
        | HTTPS
        v
[ Vercel Edge / CDN ] ---------> Serves Next.js 15 Static UI (uni-lang.vercel.app)
        |
        | CORS (X-Request-ID, Content-Type)
        v
[ Backend Container ] ---------> FastAPI + LangGraph Control Tower
   (Render / Docker)             - /api/v1/extract (Unary)
                                 - /api/v1/extract/stream (SSE)
                                 - /api/v1/batch (Queue)
                                 - /api/v1/documents (Persistence)
                                 - /health & /health/deep
```

---

## 2. Step 1: Deploy Backend Container (Render Blueprint)

The backend requires Python 3.11+, Poppler utilities (`pdftoppm`), and persistent storage.

### Option A: 1-Click Render Deployment (Recommended)
1. Fork or push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New** -> **Blueprint**.
3. Connect your repository. Render will automatically detect `render.yaml`.
4. Supply the following environment variables when prompted:
   - `OPENAI_API_KEY`: Your OpenAI API key (for GPT-4o).
   - `GOOGLE_API_KEY`: Your Google Gemini API key (for Gemini 2.5 Flash).
   - `ALLOWED_ORIGINS`: `http://localhost:3000,https://uni-lang.vercel.app`
   - `ALLOWED_ORIGIN_REGEX`: `^https:\/\/.*\.vercel\.app$`
5. Click **Apply**. Render will build and deploy the container.
6. Note your assigned service URL (e.g., `https://datanova-backend.onrender.com`).

### Option B: Docker Compose (Self-Hosted / VPS)
```bash
# Clone and build
git clone https://github.com/blizza4d/unilang.git
cd unilang

# Set your API keys in docker-compose.yml or .env
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."

# Start backend container
docker-compose up -d --build backend
```

---

## 3. Step 2: Configure Vercel Frontend

The frontend is deployed at `https://uni-lang.vercel.app/`.

### Critical Step: Inlining `NEXT_PUBLIC_API_URL`
Because Next.js inlines environment variables prefixed with `NEXT_PUBLIC_` **at build time**, you must configure the backend URL in the Vercel dashboard:

1. Open your project in the [Vercel Dashboard](https://vercel.com/).
2. Navigate to **Settings** -> **Environment Variables**.
3. Add the following variable:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://your-deployed-backend.onrender.com` (use your actual backend HTTPS URL, **no trailing slash**)
   - **Target Environments:** Check `Production`, `Preview`, and `Development`.
4. Trigger a redeployment:
   - Go to **Deployments** tab.
   - Click the three dots on the latest deployment -> **Redeploy** (do NOT use cached build artifacts).

> [!WARNING]
> If `NEXT_PUBLIC_API_URL` is omitted, the frontend falls back to `http://localhost:8000`. Modern browsers will block requests due to Mixed Content security rules (HTTPS frontend loading insecure HTTP).

---

## 4. Step 3: Deployment Verification & Smoke Testing

Run the automated verification script from your terminal:

```bash
# Verify local or remote deployment
python scripts/check_deployment.py --url https://your-deployed-backend.onrender.com
```

The script verifies:
1. **Liveness (`/health`):** Verifies Uvicorn server is up and responsive.
2. **Readiness (`/health/deep`):** Verifies database connectivity and model provider keys.
3. **CORS Preflight Simulation:** Sends an `OPTIONS` request with `Origin: https://uni-lang.vercel.app` and asserts `Access-Control-Allow-Origin` is returned.

---

## 5. Troubleshooting Matrix

| Symptom | Root Cause | Resolution |
|---|---|---|
| `Cannot reach the extraction server` on Vercel | Mixed content block or missing `NEXT_PUBLIC_API_URL` | Set `NEXT_PUBLIC_API_URL` in Vercel settings and trigger a fresh redeploy. |
| `CORS Error: No 'Access-Control-Allow-Origin' header` | Origin not whitelisted on backend | Add your frontend domain to `ALLOWED_ORIGINS` in backend environment or check regex match. |
| `503 Service Unavailable` on `/health/deep` | Missing API keys while demo mode is disabled | Set `FEATURE_DEMO_MODE=true` or supply valid `OPENAI_API_KEY` and `GOOGLE_API_KEY`. |
| CSV export downloads as `.zip` | Expected behavior | The CSV export includes both `header.csv` and `line_items.csv` bundled in a clean UTF-8 ZIP archive. |
| PDF rendering fails | Poppler utilities missing | Ensure `poppler-utils` is installed on your Linux host (`apt-get install -y poppler-utils`). |
