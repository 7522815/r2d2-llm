import Foundation
import Combine
import AVFoundation

@MainActor
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isStreaming = false
    @Published var isOnline = false
    @Published var stats = R2D2Stats()
    @Published var currentResponse = ""
    @Published var isRecording = false

    private var streamingTask: URLSessionTask?
    private var audioRecorder: AVAudioRecorder?
    private var audioSession: AVAudioSession?

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

    // MARK: - Voice Recording

    func startRecording() {
        audioSession = AVAudioSession.sharedInstance()
        guard let session = audioSession else { return }
        try? session.setCategory(.playAndRecord, mode: .default)
        try? session.setActive(true)

        let url = FileManager.default.temporaryDirectory.appendingPathComponent("r2d2_recording.wav")
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatLinearPCM),
            AVSampleRateKey: 44100,
            AVNumberOfChannelsKey: 1,
            AVLinearPCMBitDepthKey: 16
        ]

        guard let recorder = try? AVAudioRecorder(url: url, settings: settings) else { return }
        audioRecorder = recorder
        recorder.record()
        isRecording = true
    }

    func stopRecording() {
        audioRecorder?.stop()
        isRecording = false
        try? audioSession?.setActive(false)

        guard let url = audioRecorder?.url,
              FileManager.default.fileExists(atPath: url.path) else { return }

        // Play random R2D2 sound
        Task {
            let soundName = await R2D2SoundService.shared.playRandomSound()

            let userMsg = ChatMessage(role: .user, content: "🎤 Voice input",
                                    mediaType: .voice, mediaURL: url.lastPathComponent)

            let beeps = ["Beep boop!", "Bee-bee-boo!", "Boop!", "Bleep-bloop!",
                        "Bwip-bwop!", "Bzzzt!", "Wooop!", "Dee-doo-dee!"]
            let reply = beeps.randomElement() ?? "Beep boop!"
            let r2Msg = ChatMessage(role: .assistant, content: reply,
                                   language: Self.detectLanguage(reply),
                                   mediaType: .r2d2Sound, mediaURL: soundName)

            messages.append(contentsOf: [userMsg, r2Msg])
            stats.totalTokens += 1
            audioRecorder = nil
        }
    }

    // MARK: - Photo Input

    func sendPhoto(_ data: Data) {
        let userMsg = ChatMessage(role: .user, content: "📷 Photo input", mediaType: .photo)
        let exp = R2D2Expression.allCases.randomElement() ?? .happy
        let reply = "\(exp.beep) \(exp.emoji)"
        let r2Msg = ChatMessage(role: .assistant, content: reply,
                               language: Self.detectLanguage(reply),
                               mediaType: .r2d2Expression, mediaURL: exp.rawValue)
        messages.append(contentsOf: [userMsg, r2Msg])
        stats.totalTokens += 1
    }

    // MARK: - Video Input

    func sendVideo(_ url: URL) {
        let userMsg = ChatMessage(role: .user, content: "🎬 Video input", mediaType: .video)
        let r2Msg = ChatMessage(role: .assistant, content: "✨ Animation complete!",
                               language: "en", mediaType: .r2d2Animation)
        messages.append(contentsOf: [userMsg, r2Msg])
        stats.totalTokens += 1
        // Note: Full canvas animation would require WKWebView or Metal
    }
}
