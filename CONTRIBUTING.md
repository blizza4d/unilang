# Contributing to DataNova Extract

Thank you for your interest in contributing to DataNova Extract!

## Release Freeze Notice
> [!IMPORTANT]
> **Active Release Freeze in Effect for `v1.0.0-rc.1`**
> Until the final hackathon submission and evaluation are completed, the codebase is in a strict **Release Freeze**.
> - **Zero Feature Work:** No new product features or architectural changes are permitted.
> - **Defect Fixes Only:** Only verified defect fixes accompanied by a root-cause explanation and regression tests are accepted.
> - **Pre-Merge Validation:** Every pull request must pass the automated release gate (`python scripts/release_gate.py`).

---

## Development Workflow

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/blizza4d/unilang.git
cd unilang

# Backend setup
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Running Local Services
```bash
# Terminal 1 - Backend (FastAPI on http://localhost:8000)
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend (Next.js on http://localhost:3000)
cd frontend
npm run dev
```

### 3. Verification & Testing
Before opening any pull request:
1. **Backend Tests:** Run the full test suite in randomized order:
   ```bash
   cd backend
   pytest -v --randomly-seed=42
   ```
2. **Frontend Typecheck & Build:**
   ```bash
   cd frontend
   npm run build
   ```
3. **Claims Audit:** Ensure all numeric claims match `docs/NUMBERS.md`:
   ```bash
   python scripts/check_claims.py
   ```
4. **Release Gate:** Verify all launch checks pass:
   ```bash
   python scripts/release_gate.py
   ```

---

## Pull Request Checklist
- [ ] Code follows project formatting and design tokens (`frontend/styles/tokens.css`).
- [ ] No hardcoded colors, arbitrary spacing, or untracked dependencies.
- [ ] Every bug fix includes a reproduction test that fails before the fix and passes after.
- [ ] No API keys, credentials, or sensitive tokens committed.
- [ ] `CHANGELOG.md` updated under the unreleased / candidate section.
