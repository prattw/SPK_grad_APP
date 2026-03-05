//
//  ResultsView.swift
//  SPK Grad App – Analysis results (count + size distribution in mm)
//

import SwiftUI

struct ResultsView: View {
    var imageData: Data?
    var result: AnalysisResult
    var onRetake: () -> Void

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if let data = imageData, let uiImage = UIImage(data: data) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFit()
                        .frame(maxHeight: 300)
                        .cornerRadius(12)
                }

                Text("Analysis Results")
                    .font(.title2)
                    .fontWeight(.semibold)

                VStack(alignment: .leading, spacing: 8) {
                    if let error = result.error, !error.isEmpty {
                        Text(error)
                            .foregroundColor(.red)
                    }
                    Text("Grain count: \(result.grainCount)")
                        .font(.headline)
                    if let method = result.method {
                        Text("Method: \(method)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.green.opacity(0.15))
                .cornerRadius(12)

                if let sizes = result.sizeDistributionMm, !sizes.isEmpty {
                    Text("Size distribution (mm)")
                        .font(.headline)
                    Text(sizes.map { String(format: "%.1f", $0) }.joined(separator: ", "))
                        .font(.subheadline)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                }

                Button(action: onRetake) {
                    Text("Retake")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(12)
                }
            }
            .padding()
        }
    }
}
