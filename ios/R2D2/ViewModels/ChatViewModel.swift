import Foundation
import Combine

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isStreaming = false
    @Published var isOnline = false
    @Published var stats = R2D2Stats()
    @Published var currentResponse = ""

    private var streamingTask: URLSessionTask?

    // MARK: - Language Detection

    static let languageNames: [String: String] = [
        "ru": "Русский", "en": "English", "zh": "中文",
        "ja": "日本語", "ko": "한국어", "ar": "العربية",
        "fr": "Français", "de": "Deutsch", "es": "Español"
    ]

    static let languageFlags: [String: String] = [
        "ru": "🇷🇺", "en": "🇺🇸", "zh": "🇨🇳",
        "ja": "🇯🇵", "ko": "🇰🇷", "ar": "🇦🇪",
        "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸"
    ]

    static func detectLanguage(_ text: String) -> String {
        let patterns: [(String, String)] = [
            ("ru", "[а-яёА-ЯЁ]"),
            ("zh", "[\\u4e00-\\u9fff]"),
            ("ja", "[\\u3040-\\u309f\\u30a0-\\u30ff]"),
            ("ko", "[\\uac00-\\ud7af]"),
            ("ar", "[\\u0600-\\u06ff]"),
            ("fr", "[àâäéèêëîïôöùûüÿœæçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸŒÆÇ]"),
            ("de", "[äöüßÄÖÜ]"),
            ("es", "[ñáéíóúü¿¡ÑÁÉÍÓÚÜ]"),
        ]
        for (lang, pattern) in patterns {
            if let regex = try? Regex(pattern), text.contains(regex) {
                return lang
            }
        }
        return "en"
    }

    // MARK: - Check Status

    func checkStatus() async {
        isOnline = await R2D2APIService.shared.checkStatus()
    }

    // MARK: - Send Message

    func sendMessage(_ text: String) {
        guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }

        let userMsg = ChatMessage(role: .user, content: text)
        messages.append(userMsg)
        isStreaming = true
        currentResponse = ""

        let startTime = CFAbsoluteTimeGetCurrent()

        streamingTask = R2D2APIService.shared.streamChat(
            message: text,
            onToken: { [weak self] token in
                Task { @MainActor in
                    self?.currentResponse += token
                    self?.stats.totalTokens += 1
                    self?.objectWillChange.send()
                }
            },
            onFinish: { [weak self] result in
                Task { @MainActor in
                    defer {
                        self?.isStreaming = false
                        self?.streamingTask = nil
                    }

                    let elapsed = CFAbsoluteTimeGetCurrent() - startTime
                    self?.stats.lastLatency = elapsed

                    switch result {
                    case .success(let fullText):
                        let lang = Self.detectLanguage(fullText)
                        let msg = ChatMessage(
                            role: .assistant,
                            content: fullText,
                            language: lang
                        )
                        self?.messages.append(msg)
                        self?.currentResponse = ""
                    case .failure(let error):
                        let msg = ChatMessage(
                            role: .assistant,
                            content: "⚠️ \(error.localizedDescription)",
                            language: "en"
                        )
                        self?.messages.append(msg)
                        self?.currentResponse = ""
                    }
                }
            }
        )
    }

    func cancelStreaming() {
        streamingTask?.cancel()
        streamingTask = nil
        isStreaming = false
        currentResponse = ""
    }

    func clearChat() {
        messages.removeAll()
        stats = R2D2Stats()
    }
}
