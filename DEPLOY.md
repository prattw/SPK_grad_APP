# Deploy SPK Grad App to GitHub, Backend & Website

## 1. Push to GitHub

```bash
cd /path/to/SPKgradAPP
git add -A
git status   # confirm no .env or secrets
git commit -m "Add rock counting, iPhone 16 UX, env-based config, deploy setup"
git push origin main
```

**Secrets:** Backend no longer has credentials in code. Set them as environment variables where you run the backend (see below). Locally, copy `backend/.env.example` to `backend/.env` and fill in real values.

---

## 2. Backend (API)

The backend runs the Flask app in `backend/` (rock counting + email APIs). Deploy it to a host that runs Python and sets `PORT`.

### Option A: Render (recommended, free tier)

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New → Web Service**.
3. Connect the repo **prattw/SPK_grad_APP** (or your fork).
4. Set:
   - **Name:** `spkgrad-backend`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -b 0.0.0.0:$PORT server:app`
5. **Environment:** Add variables (Secret or Plain):
   - `SMTP_SERVER` (e.g. `smtp.gmail.com`)
   - `SMTP_PORT` (e.g. `587`)
   - `EMAIL_USERNAME` (your sending address)
   - `EMAIL_PASSWORD` (app password)
6. Create Web Service. Note the URL, e.g. `https://spkgrad-backend.onrender.com`.

**Alternative:** If the repo has a `render.yaml`, you can use **New → Blueprint** and point at this repo; then add the env vars in the Render dashboard.

### Option B: Run locally (development)

```bash
cd backend
cp .env.example .env
# Edit .env with real SMTP and EMAIL_* values
pip install -r requirements.txt
python server.py
# API at http://localhost:5001
```

---

## 3. Website (frontend)

The site is the static files in `mobile-frontend/`. It must know the backend URL so "Analyze Sample" can call the API.

### Option A: GitHub Pages (free)

1. In the repo: **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main` (or run the "Deploy site to GitHub Pages" workflow). The workflow deploys the `mobile-frontend` folder.
4. Site URL will be like `https://<username>.github.io/SPK_grad_APP/` (or your repo name).

**Point the site at your backend:**

- Edit **`mobile-frontend/config.js`** and set your backend URL:
  ```js
  window.BACKEND_URL = 'https://spkgrad-backend.onrender.com';
  ```
  (Leave as `''` for same-origin or local.) The analysis and results pages use this for `/api/analyze-image` and `/api/send-results`. The backend allows CORS from any origin.

### Option B: Netlify or Vercel

1. Connect the repo to [Netlify](https://netlify.com) or [Vercel](https://vercel.com).
2. **Publish directory:** `mobile-frontend`.
3. Set the backend URL the same way (e.g. `window.BACKEND_URL` in `index.html` or via env at build time if you add a build step).

---

## 4. Quick checklist

| Step | Action |
|------|--------|
| Push code | `git add -A && git commit -m "..." && git push origin main` |
| Backend env | Create backend `.env` locally; on Render, add SMTP + EMAIL_* in dashboard |
| Backend URL | Note the live API URL (e.g. `https://spkgrad-backend.onrender.com`) |
| Pages | Repo **Settings → Pages → Source: GitHub Actions** |
| Frontend API | Set `window.BACKEND_URL` in `mobile-frontend/config.js` to your backend URL |
| Test | Open the site, enter email, take/upload photo, Analyze Sample, check results |

---

## Repo layout

- `backend/` – Flask API (rock count, email, CSV)
- `mobile-frontend/` – Static site (index, analysis, results)
- `render.yaml` – Optional Render blueprint for the backend
- `.github/workflows/deploy-pages.yml` – Deploys `mobile-frontend` to GitHub Pages
