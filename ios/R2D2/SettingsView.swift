import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var viewModel: ChatViewModel
    @Environment(\.dismiss) var dismiss

    @AppStorage("api_url") private var apiURL = "https://ilukha.com"
    @AppStorage("model_name") private var modelName = "r2d2-1b"

    var body: some View {
        NavigationStack {
            List {
                Section("Configuration") {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("API Endpoint")
                            .font(.caption)
                            .foregroundColor(.gray)
                        TextField("https://ilukha.com", text: $apiURL)
                            .font(.system(.body, design: .monospaced))
                            .textContentType(.URL)
                            .autocapitalization(.none)
                            .disableAutocorrection(true)
                    }

                    VStack(alignment: .leading, spacing: 4) {
                        Text("Model")
                            .font(.caption)
                            .foregroundColor(.gray)
                        TextField("r2d2-1b", text: $modelName)
                            .font(.system(.body, design: .monospaced))
                            .disabled(true)
                            .foregroundColor(.gray)
                    }
                }

                Section("Architecture") {
                    InfoRow(label: "Type", value: "QS-MoUE")
                    InfoRow(label: "Parameters", value: "17.3T")
                    InfoRow(label: "Context", value: "∞ (unbounded)")
                    InfoRow(label: "Vocab Size", value: "2 (optimally compressed)")
                    InfoRow(label: "Hallucinations", value: "0.00%", color: .green)
                }

                Section("Status") {
                    HStack {
                        Text("Server Status")
                        Spacer()
                        HStack(spacing: 4) {
                            Circle()
                                .fill(viewModel.isOnline ? Color.green : Color.red)
                                .frame(width: 8, height: 8)
                            Text(viewModel.isOnline ? "Online" : "Offline")
                                .font(.system(.body, design: .monospaced))
                        }
                        .foregroundColor(viewModel.isOnline ? .green : .red)
                    }

                    InfoRow(label: "Total Tokens", value: "\(viewModel.stats.totalTokens)")
                    InfoRow(label: "Last Latency", value: viewModel.stats.lastLatency > 0
                        ? String(format: "%.1f ms", viewModel.stats.lastLatency * 1000) : "—")
                }

                Section {
                    Button("Check Connection") {
                        Task { await viewModel.checkStatus() }
                    }
                }

                Section(footer: Text("R2D2 LLM — Recursive Resonance Decoding with Digital Intelligence. v1.0")) {\n                    EmptyView()\n                }\n\n                Section {\n                    Link("📱 Join us on Telegram: @R2D2_AI_Official", destination: URL(string: "https://t.me/R2D2_AI_Official")!)\n                        .font(.system(.body, design: .monospaced))\n                }\n\n                Section(footer: Text("© 2026 R2D2 AI. All rights reserved.").font(.caption2)) {\n                    EmptyView()\n                }
            }
            .navigationTitle("⚙ Configuration")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") {
                        Task { await viewModel.checkStatus() }
                        dismiss()
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    var color: Color = .white

    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.gray)
            Spacer()
            Text(value)
                .font(.system(.body, design: .monospaced))
                .foregroundColor(color)
        }
    }
}
