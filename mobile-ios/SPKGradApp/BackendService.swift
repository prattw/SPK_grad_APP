//
//  BackendService.swift
//  SPK Grad App – API client for analyze-image (with optional LiDAR scale)
//

import Foundation

struct AnalysisResult {
    var grainCount: Int
    var sizeDistributionMm: [Double]?
    var error: String?
    var method: String?
}

struct BackendService {
    /// Set to your Render backend URL, or use a config/plist in production.
    var baseURL: String = "https://spkgrad-backend.onrender.com"

    /// Analyze image and optionally send LiDAR-derived scale for size distribution in mm.
    func analyzeImage(imageData: Data, scaleMmPerPixel: Double?) async -> AnalysisResult {
        let base64 = imageData.base64EncodedString()
        let dataURL = "data:image/jpeg;base64,\(base64)"

        var body: [String: Any] = ["imageData": dataURL]
        if let scale = scaleMmPerPixel, scale > 0 {
            body["scaleMmPerPixel"] = scale
        }

        guard let url = URL(string: "\(baseURL)/api/analyze-image"),
              let httpBody = try? JSONSerialization.data(withJSONObject: body) else {
            return AnalysisResult(grainCount: 0, sizeDistributionMm: nil, error: "Invalid request", method: nil)
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = httpBody

        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let http = response as? HTTPURLResponse else {
                return AnalysisResult(grainCount: 0, sizeDistributionMm: nil, error: "No response", method: nil)
            }
            guard http.statusCode == 200 else {
                return AnalysisResult(grainCount: 0, sizeDistributionMm: nil, error: "Server error \(http.statusCode)", method: nil)
            }

            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] ?? [:]
            let count = json["grainCount"] as? Int ?? 0
            let method = json["method"] as? String
            let errorMsg = json["error"] as? String
            let sizes = json["sizeDistributionMm"] as? [Double]

            return AnalysisResult(
                grainCount: count,
                sizeDistributionMm: sizes,
                error: errorMsg,
                method: method
            )
        } catch {
            return AnalysisResult(grainCount: 0, sizeDistributionMm: nil, error: error.localizedDescription, method: nil)
        }
    }
}
