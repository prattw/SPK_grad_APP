# SPK Grad App – Native iPad (LiDAR + Model)

Native iPad app for accurate grain count and measuring using **LiDAR** (scale) and backend **segmentation model** (count + sizes).

## Requirements

- **Xcode** 15+ (Swift 5.9+)
- **iPad with LiDAR** (iPad Pro 2020 or later, iPad Air 2024 with LiDAR)
- **macOS** to build and run (or run on device from Xcode)

## Quick setup

1. **Create a new iOS App in Xcode**
   - File → New → Project → **App**
   - Product Name: `SPKGradApp` (or match the bundle ID you want)
   - Interface: **SwiftUI**
   - Language: **Swift**
   - Minimum Deployment: **iPadOS 16** (for LiDAR scene depth)
   - **Include Tests**: optional

2. **Add the source files**
   - Copy (or add as references) all `.swift` files from `SPKGradApp/` into your app target in Xcode.

3. **Capabilities**
   - Select your target → **Signing & Capabilities**
   - Click **+ Capability** → add **Camera Usage Description** (and **Microphone** if you add audio later).
   - In **Info** (or Info.plist), add:
     - `NSCameraUsageDescription`: "Grain sample capture and LiDAR for scale."
     - `NSPhotoLibraryUsageDescription`: "Save analysis results."
   - **Required device capabilities** (Info): add `arkit` and `lidar` so the app is only installable on LiDAR iPads (or omit to allow non‑LiDAR with fallback).

4. **Backend URL**
   - Set your API base URL in `BackendService.swift` (`baseURL`) or via a config/plist so the app hits your Render backend.

5. **Build and run** on a LiDAR iPad (simulator does not have LiDAR; use a real device).

## Project structure

```
mobile-ios/
├── README.md                 # This file
└── SPKGradApp/
    ├── SPKGradApp.swift      # App entry
    ├── ContentView.swift     # Main navigation
    ├── ARKitCaptureView.swift # AR session, LiDAR, capture photo + scale
    ├── BackendService.swift  # API client (analyze with scaleMmPerPixel)
    └── ResultsView.swift    # Count + size distribution (mm)
```

## Flow

1. **Capture** – User runs an AR session (LiDAR). App shows camera preview and distance/scale when available.
2. **Photo** – User taps Capture; app grabs the current frame’s image and computes **scale (mm per pixel)** from LiDAR depth and camera intrinsics.
3. **Analyze** – App sends image (base64) + `scaleMmPerPixel` to backend `POST /api/analyze-image`.
4. **Results** – Backend returns `grainCount` and optional `sizeDistributionMm`. App shows count and size list (mm).

## LiDAR scale

- **sceneDepth** (ARKit) gives depth in meters. App uses depth at the center of the image (or averaged over the sample region).
- **Camera intrinsics** (from `ARFrame.camera.intrinsics`) provide `fx` (focal length in pixels).
- **Formula**: `scaleMmPerPixel = 1000 * depth_meters / fx` → real-world size in mm per pixel at that distance.

## Segmentation model (roadmap)

- **Current**: Backend uses CV (watershed + morphology). Count and sizes improve with LiDAR scale.
- **Next**: Integrate **segmenteverygrain** (Unet + SAM) on the backend for more accurate count and outlines:
  - Option A: Run full pipeline on a paid/stronger backend (e.g. Render paid, or separate GPU instance).
  - Option B: Export a smaller Unet (or similar) to **Core ML** and run on-device; send only image + scale to backend for CSV/email. Best for speed and offline.

## Backend API (used by this app)

- **POST /api/analyze-image**
  - Body: `{ "imageData": "data:image/jpeg;base64,...", "scaleMmPerPixel": 0.15 }`
  - Response: `{ "grainCount": 19, "method": "watershed", "sizeDistributionMm": [12.1, 24.3, ...], "error": null }`
