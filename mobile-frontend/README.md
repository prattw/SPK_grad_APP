# USACE Sacramento District – Rock Sample App (Mobile Frontend)

Mobile-friendly web app for capturing a photo of a rock sample and getting an automated rock count. Optimized for **iPhone 16 and later**.

## How the app works (user flow)

1. **Open the app**  
   User goes to the app website (e.g. `index.html` or your hosted URL).

2. **Enter USACE email**  
   User enters their USACE (or approved domain) email address.  
   Allowed domains: `@usace.army.mil`, `@usgs.gov`.

3. **Take a picture**  
   After submitting the form, the iPhone camera opens.  
   User holds the phone **6–12 inches** from the rocks and takes a picture.

4. **Confirm the photo**  
   The app shows the captured image.  
   User can **Retake** or choose **Use this photo** to continue.

5. **Review and analyze**  
   On the next screen, the same photo is shown for a final check.  
   User taps **Analyze Sample** to run the analysis.

6. **See results**  
   The app calls the backend to count rocks in the image, then shows the **rock count** and an option to **Accept** (e.g. email results) or **Retake Photo**.

## What’s included

- Email validation (USACE / USGS only)
- Camera capture (with 6–12 inch guidance)
- Photo review and confirm step
- Backend call to `/api/analyze-image` for rock count
- Results page with count and Accept / Retake
- File upload fallback if the camera isn’t available
- Test rock sample option for development

## Running it

- **Frontend:** Serve the `mobile-frontend` folder (e.g. any static server or open `index.html`).
- **Backend:** Run the Flask server so `/api/analyze-image` and `/api/send-results` are available.  
  If the frontend is on a different origin, set `window.BACKEND_URL` to the backend base URL (e.g. `http://localhost:5001`).

## Files

- `index.html` – Landing, email, camera, and “Use this photo”
- `analysis.html` – Confirm photo and “Analyze Sample”
- `results.html` – Rock count and Accept / Retake
