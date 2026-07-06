import Foundation

struct ChatMessage: Identifiable, Codable, Equatable {
    let id: String
    let role: MessageRole
    let content: String
    let language: String?
    let timestamp: Date

    init(id: String = UUID().uuidString, role: MessageRole, content: String, language: String? = nil, timestamp: Date = Date()) {
        self.id = id
        self.role = role
        self.content = content
        self.language = language
        self.timestamp = timestamp
    }

    enum MessageRole: String, Codable {
        case user
        case assistant
    }
}

struct R2D2Stats {
    var totalTokens: Int = 0
    var lastLatency: TimeInterval = 0
}
