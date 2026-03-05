//
//  ARKitCaptureView.swift
//  SPK Grad App – AR session with LiDAR, capture photo + scale (mm per pixel)
//

import SwiftUI
import ARKit
import AVFoundation

struct ARKitCaptureView: View {
    var onCaptured: (Data, Double?) -> Void
    @State private var scaleMmPerPixel: Double?
    @State private var distanceMeters: Double?
    @State private var isReady = false
    @State private var showAlert = false
    @State private var alertMessage = ""

    var body: some View {
        ZStack {
            ARViewRepresentable(
                scaleMmPerPixel: $scaleMmPerPixel,
                distanceMeters: $distanceMeters,
                isReady: $isReady
            )
            .ignoresSafeArea()

            VStack {
                Spacer()
                if let scale = scaleMmPerPixel {
                    Text(String(format: "Scale: %.4f mm/px", scale))
                        .font(.caption)
                        .padding(8)
                        .background(.ultraThinMaterial)
                        .cornerRadius(8)
                }
                if let d = distanceMeters {
                    Text(String(format: "Distance: %.2f m", d))
                        .font(.caption)
                        .padding(8)
                        .background(.ultraThinMaterial)
                        .cornerRadius(8)
                }
                Button(action: capture) {
                    Text("Capture")
                        .font(.headline)
                        .frame(width: 120, height: 44)
                        .background(isReady ? Color.green : Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
                .disabled(!isReady)
                .padding(.bottom, 40)
            }
        }
        .alert("Capture", isPresented: $showAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(alertMessage)
        }
    }

    private func capture() {
        guard let (imageData, scale) = ARSessionManager.shared.captureCurrentFrame() else {
            alertMessage = "Could not capture frame. Ensure LiDAR is ready."
            showAlert = true
            return
        }
        onCaptured(imageData, scale)
    }
}

// MARK: - AR View (UIKit wrapper)

struct ARViewRepresentable: UIViewControllerRepresentable {
    @Binding var scaleMmPerPixel: Double?
    @Binding var distanceMeters: Double?
    @Binding var isReady: Bool

    func makeUIViewController(context: Context) -> ARCaptureViewController {
        let vc = ARCaptureViewController()
        vc.onScaleUpdate = { scale, dist in
            scaleMmPerPixel = scale
            distanceMeters = dist
        }
        vc.onReady = { isReady = $0 }
        return vc
    }

    func updateUIViewController(_ uiViewController: ARCaptureViewController, context: Context) { }
}

// MARK: - AR session manager (shared state for capture)

final class ARSessionManager {
    static let shared = ARSessionManager()
    var currentFrame: ARFrame?
    var session: ARSession?

    private init() { }

    /// Returns (jpeg data, scale mm/px) or nil if capture failed.
    func captureCurrentFrame() -> (Data, Double?)? {
        guard let frame = currentFrame,
              let imageBuffer = frame.capturedImage as CVPixelBuffer? else { return nil }

        let ciImage = CIImage(cvPixelBuffer: imageBuffer)
        let context = CIContext()
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else { return nil }
        let uiImage = UIImage(cgImage: cgImage)
        guard let jpeg = uiImage.jpegData(compressionQuality: 0.85) else { return nil }

        var scale: Double?
        if let depth = frame.sceneDepth?.depthMap, frame.camera.intrinsics.columns.0.x > 0 {
            scale = computeScaleMmPerPixel(depthMap: depth, intrinsics: frame.camera.intrinsics, imageWidth: ciImage.extent.width, imageHeight: ciImage.extent.height)
        }

        return (jpeg, scale)
    }

    /// Average depth in center region (meters), then scale = 1000 * depth / fx (mm per pixel).
    private func computeScaleMmPerPixel(depthMap: CVPixelBuffer, intrinsics: simd_float3x3, imageWidth: CGFloat, imageHeight: CGFloat) -> Double? {
        CVPixelBufferLockBaseAddress(depthMap, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(depthMap, .readOnly) }
        let w = CVPixelBufferGetWidth(depthMap)
        let h = CVPixelBufferGetHeight(depthMap)
        let rowBytes = CVPixelBufferGetBytesPerRow(depthMap)
        guard let base = CVPixelBufferGetBaseAddress(depthMap) else { return nil }
        let buffer = base.assumingMemoryBound(to: Float32.self)

        let cx = w / 2
        let cy = h / 2
        let r = min(w, h) / 4
        var sum: Float = 0
        var count: Int = 0
        for y in max(0, cy - r)..<min(h, cy + r) {
            for x in max(0, cx - r)..<min(w, cx + r) {
                let val = buffer[y * (rowBytes / 4) + x]
                if val.isFinite, val > 0 {
                    sum += val
                    count += 1
                }
            }
        }
        guard count > 0 else { return nil }
        let depthMeters = Double(sum / Float(count))
        let fx = Double(intrinsics.columns.0.x)
        guard fx > 0 else { return nil }
        return 1000 * depthMeters / fx
    }
}

// MARK: - UIKit AR view controller

import UIKit

class ARCaptureViewController: UIViewController, ARSessionDelegate {
    var onScaleUpdate: ((Double?, Double?) -> Void)?
    var onReady: ((Bool) -> Void)?

    private var arView: ARSCNView!
    private var session: ARSession { arView.session }

    override func viewDidLoad() {
        super.viewDidLoad()
        arView = ARSCNView(frame: view.bounds)
        arView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        arView.session.delegate = self
        view.addSubview(arView)
        ARSessionManager.shared.session = session
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        let config = ARWorldTrackingConfiguration()
        if ARWorldTrackingConfiguration.supportsFrameSemantics(.sceneDepth) {
            config.frameSemantics.insert(.sceneDepth)
        }
        session.run(config)
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        session.pause()
    }

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        ARSessionManager.shared.currentFrame = frame
        onReady?(true)

        guard let depth = frame.sceneDepth?.depthMap, frame.camera.intrinsics.columns.0.x > 0 else {
            DispatchQueue.main.async { self.onScaleUpdate?(nil, nil) }
            return
        }
        let scale = ARSessionManager.shared.captureCurrentFrame().map { $0.1 }
        let depthMeters: Double? = {
            CVPixelBufferLockBaseAddress(depth, .readOnly)
            defer { CVPixelBufferUnlockBaseAddress(depth, .readOnly) }
            let w = CVPixelBufferGetWidth(depth)
            let h = CVPixelBufferGetHeight(depth)
            let rowBytes = CVPixelBufferGetBytesPerRow(depth)
            guard let base = CVPixelBufferGetBaseAddress(depth) else { return nil }
            let buf = base.assumingMemoryBound(to: Float32.self)
            let cx = w / 2, cy = h / 2, r = min(w, h) / 4
            var sum: Float = 0
            var n = 0
            for y in max(0, cy - r)..<min(h, cy + r) {
                for x in max(0, cx - r)..<min(w, cx + r) {
                    let v = buf[y * (rowBytes / 4) + x]
                    if v.isFinite, v > 0 { sum += v; n += 1 }
                }
            }
            return n > 0 ? Double(sum / Float(n)) : nil
        }()
        DispatchQueue.main.async {
            self.onScaleUpdate?(scale, depthMeters)
        }
    }
}
