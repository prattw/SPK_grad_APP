# Run SPK Grad App on iPhone and iPad

The app runs on **iPhone and iPad** as a **web app** (no App Store). The **mobile-frontend** is already built for iOS: camera capture, safe areas, and “Add to Home Screen” support.

## 1. Repo location

- **Cloned (ZIP):** `C:\Users\CYRUS\SPK_grad_APP-main`
- To use Git later: install [Git for Windows](https://git-scm.com/download/win), then:
  ```bash
  cd C:\Users\CYRUS
  git clone https://github.com/prattw/SPK_grad_APP.git
  ```

## 2. One server for app + API

The backend serves both the **API** and the **mobile web app**. Run a single server, then open its URL on your iPhone or iPad.

### On your Windows PC

1. **Install Python 3** (e.g. from [python.org](https://www.python.org/downloads/)).

2. **Open a terminal** in the repo:
   ```powershell
   cd C:\Users\CYRUS\SPK_grad_APP-main\backend
   ```

3. **Create a virtual environment and install dependencies:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Start the server** (listens on all interfaces so your phone can reach it):
   ```powershell
   python server.py
   ```
   You should see the app listening on `http://0.0.0.0:5001` (or the port shown).

5. **Find your PC’s IP address** (e.g. in WiFi settings or run):
   ```powershell
   ipconfig
   ```
   Use the **IPv4 Address** of your active adapter (e.g. `192.168.1.100`).

### On iPhone or iPad

1. Connect the device to the **same Wi‑Fi network** as your PC.
2. In **Safari**, open:
   ```text
   http://<YOUR_PC_IP>:5001
   ```
   Example: `http://192.168.1.100:5001`
3. Use the app: enter email, take a photo, analyze, view results.
4. **Optional – app icon on home screen:** In Safari, tap **Share** → **Add to Home Screen**. The app will open like a native app and use the full screen.

## 3. Email (optional)

To enable “Accept” and email results, set environment variables before starting the server. Copy `.env.example` to `.env` and fill in your SMTP details (e.g. Gmail app password). See `backend/README.md` for details.

## 4. Troubleshooting

- **“Can’t reach this page” on the phone**  
  - PC and iPhone/iPad must be on the same Wi‑Fi.  
  - Try temporarily turning off the PC firewall for the Python process, or allow inbound TCP on port 5001.

- **Camera not working**  
  - Use **Safari** (Chrome on iOS may limit camera).  
  - Allow camera permission when the site asks.

- **Analysis fails**  
  - Ensure the backend started without errors and that you’re using `http://<PC_IP>:5001` (not `localhost`).

## Summary

| Step | Where | Action |
|------|--------|--------|
| 1 | PC | `cd backend`, create venv, `pip install -r requirements.txt`, `python server.py` |
| 2 | PC | Note your IP (e.g. `192.168.1.100`) |
| 3 | iPhone/iPad | Safari → `http://<PC_IP>:5001` |
| 4 | iPhone/iPad | Optional: Share → Add to Home Screen |

The **Android app** in `mobile-app/` is separate (Kotlin/ExecuTorch). For **iPhone and iPad**, use the web app at `http://<PC_IP>:5001` as above.
