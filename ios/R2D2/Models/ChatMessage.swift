import Foundation

struct ChatMessage: Identifiable, Codable, Equatable {
    let id: String
    let role: MessageRole
    let content: String
    let language: String?
    let timestamp: Date
    let mediaType: MediaType?
    let mediaURL: String?

    init(id: String = UUID().uuidString, role: MessageRole, content: String, language: String? = nil,
         timestamp: Date = Date(), mediaType: MediaType? = nil, mediaURL: String? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.language = language
        self.timestamp = timestamp
        self.mediaType = mediaType
        self.mediaURL = mediaURL
    }

    enum MessageRole: String, Codable { case user, assistant }
    enum MediaType: String, Codable { case voice, photo, video, r2d2Sound, r2d2Expression, r2d2Animation }
}

struct R2D2Stats {
    var totalTokens: Int = 0
    var lastLatency: TimeInterval = 0
}

enum R2D2Expression: String, CaseIterable {
    case happy, sad, angry, surprised, sleeping, thinking, excited, confused, wink, scared, dance

    var emoji: String {
        switch self {
        case .happy: return "😊"
        case .sad: return "😢"
        case .angry: return "😠"
        case .surprised: return "😮"
        case .sleeping: return "😴"
        case .thinking: return "🤔"
        case .excited: return "🤩"
        case .confused: return "😕"
        case .wink: return "😉"
        case .scared: return "😨"
        case .dance: return "💃"
        }
    }

    var beep: String {
        switch self {
        case .happy: return "Happy beep!"
        case .sad: return "Sad boop..."
        case .angry: return "Angry buzz!"
        case .surprised: return "Surprised chirp!"
        case .sleeping: return "Zzz beep..."
        case .thinking: return "Hmm beep?"
        case .excited: return "Excited beep!!"
        case .confused: return "Confused boop?"
        case .wink: return "Wink beep!"
        case .scared: return "Scared beep!!"
        case .dance: return "Dance boop!"
        }
    }
}
