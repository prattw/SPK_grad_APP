# Todo / Plan

Use for current plan with checkable items. Verify plan before implementation; track progress and document results here.

---

## Get app online for iPhone 16 & iPad Pro

- [ ] **1. Put repo on GitHub**  
  Create a repo (e.g. `SPK_grad_APP`), then:  
  `git init` (if needed), `git add -A`, `git commit -m "Initial"`, `git remote add origin <url>`, `git push -u origin main`.  
  Ensure no `.env` or secrets are committed (use `backend/.env.example` only).

- [ ] **2. Deploy backend to Render**  
  - Go to [render.com](https://render.com), sign in with GitHub.  
  - **New → Web Service**, connect your repo.  
  - **Root Directory:** `backend`  
  - **Build:** `pip install -r requirements.txt`  
  - **Start:** `gunicorn -b 0.0.0.0:$PORT server:app`  
  - Add env vars in dashboard: `SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD` (for email).  
  - Deploy and note the backend URL (e.g. `https://spkgrad-backend.onrender.com`).

- [ ] **3. Point frontend at backend**  
  In `mobile-frontend/config.js`, set:  
  `window.BACKEND_URL = 'https://YOUR-RENDER-URL.onrender.com';`  
  Commit and push.

- [ ] **4. Deploy frontend to GitHub Pages**  
  - Repo **Settings → Pages**.  
  - **Build and deployment → Source:** GitHub Actions.  
  - Push to `main` (or run workflow **Deploy site to GitHub Pages**).  
  - Site URL: `https://<username>.github.io/<repo-name>/`.

- [ ] **5. Use on iPhone / iPad**  
  - Open the GitHub Pages URL in **Safari**.  
  - Optional: **Share → Add to Home Screen** for an app-like icon.

---

## Review
*(Add review section after completing work)*
