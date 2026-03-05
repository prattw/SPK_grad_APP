//
//  ContentView.swift
//  SPK Grad App – Main navigation
//

import SwiftUI

struct ContentView: View {
    @State private var showCapture = true
    @State private var capturedImage: Data?
    @State private var scaleMmPerPixel: Double?
    @State private var showResults = false
    @State private var analysisResult: AnalysisResult?

    var body: some View {
        NavigationStack {
            Group {
                if showResults, let result = analysisResult {
                    ResultsView(
                        imageData: capturedImage,
                        result: result,
                        onRetake: {
                            analysisResult = nil
                            capturedImage = nil
                            scaleMmPerPixel = nil
                            showResults = false
                            showCapture = true
                        }
                    )
                } else if showCapture {
                    ARKitCaptureView(
                        onCaptured: { imageData, scale in
                            capturedImage = imageData
                            scaleMmPerPixel = scale
                            runAnalysis(imageData: imageData, scale: scale)
                        }
                    )
                } else {
                    ProgressView("Analyzing…")
                }
            }
            .navigationTitle("SPK Grain Analysis")
            .navigationBarTitleDisplayMode(.inline)
        }
        .onChange(of: analysisResult) { _, new in
            if new != nil {
                showResults = true
                showCapture = false
            }
        }
    }

    private func runAnalysis(imageData: Data, scale: Double?) {
        showCapture = false
        Task {
            let service = BackendService()
            let result = await service.analyzeImage(imageData: imageData, scaleMmPerPixel: scale)
            await MainActor.run {
                analysisResult = result
            }
        }
    }
}

#Preview {
    ContentView()
}
