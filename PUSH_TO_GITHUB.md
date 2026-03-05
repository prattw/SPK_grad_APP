# Update Existing GitHub Repo

Use this to push your current code to the repo that’s **already on GitHub** (no new repo).

---

## 1. Install Git (if needed)

On Windows: [Git for Windows](https://git-scm.com/download/win).  
Choose **"Git from the command line and also from 3rd-party software"**. Restart Cursor/terminal after installing.

---

## 2. Option A – This folder is already a clone (has `.git`)

If you originally cloned the repo into this folder (or `SPK_grad_APP` without `-main`), just update and push:

```powershell
cd C:\Users\CYRUS\SPK_grad_APP-main
git add -A
git status
# Confirm no .env or secrets; only backend/.env.example is fine
git commit -m "Updates: workflow rules, deploy docs, config"
git push origin main
```

If the branch is `master` instead of `main`, use `git push origin master`.

---

## 3. Option B – This folder is not a clone (no `.git`)

Your code is in `SPK_grad_APP-main` but this folder was never cloned from GitHub (e.g. you unzipped it). Use one of the following.

### B1. Clone repo, then replace with your code (safest)

```powershell
cd C:\Users\CYRUS
git clone https://github.com/prattw/SPK_grad_APP.git SPK_grad_APP-update
cd SPK_grad_APP-update
# Copy everything from SPK_grad_APP-main into this folder (overwrite), except .git
# Or: xcopy /E /Y C:\Users\CYRUS\SPK_grad_APP-main\* . 
# Then:
git add -A
git status
git commit -m "Sync local changes: workflow, deploy, config"
git push origin main
```

Then you can use `SPK_grad_APP-update` as your main folder, or copy the updated content back.

### B2. Turn this folder into the repo and push (replace remote)

Only if you’re okay **replacing** the current contents of the GitHub repo with this folder:

```powershell
cd C:\Users\CYRUS\SPK_grad_APP-main
git init
git add -A
git status
git commit -m "Sync: workflow rules, deploy docs, config for production"
git branch -M main
git remote add origin https://github.com/prattw/SPK_grad_APP.git
git push -u origin main --force
```

**Warning:** `--force` overwrites the branch on GitHub with your local history. Use only if you don’t need to keep existing commits on the remote.

---

## 4. Authentication

- **HTTPS:** Use your GitHub username and a **Personal Access Token** (not your password). Create one: GitHub → Settings → Developer settings → Personal access tokens.
- **SSH:** Use the SSH URL: `git@github.com:prattw/SPK_grad_APP.git`.

**Repo URL:** `https://github.com/prattw/SPK_grad_APP`

---

## 5. After pushing

- **GitHub Pages:** Repo → Settings → Pages → Source: **GitHub Actions**.
- **Backend:** Deploy to Render; set `window.BACKEND_URL` in `mobile-frontend/config.js`.
- See `DEPLOY.md` and `tasks/todo.md` for the full checklist.
