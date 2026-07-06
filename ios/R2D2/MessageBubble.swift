import SwiftUI

struct MessageBubble: View {
    let message: ChatMessage

    private let languageFlags: [String: String] = [
        "ru": "🇷🇺", "en": "🇺🇸", "zh": "🇨🇳",
        "ja": "🇯🇵", "ko": "🇰🇷", "ar": "🇦🇪",
        "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸"
    ]

    var body: some View {
        HStack {
            if message.role == .user {
                Spacer()
            }

            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                // Meta row
                HStack(spacing: 8) {
                    Text(message.role == .user ? "You" : "R2D2-1B")
                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                        .foregroundColor(message.role == .user ? .orange : .blue)

                    if let lang = message.language, let flag = languageFlags[lang] {
                        Text("\(flag) \(lang.uppercased())")
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundColor(.gray)
                            .padding(.horizontal, 4)
                            .padding(.vertical, 1)
                            .background(Color(white: 0.12))
                            .cornerRadius(3)
                    }

                    Spacer()

                    Text(message.timestamp, style: .time)
                        .font(.system(size: 9, design: .monospaced))
                        .foregroundColor(.gray)
                }

                Text(message.content)
                    .font(.system(size: 15))
                    .foregroundColor(.white)
                    .fixedSize(horizontal: false, vertical: true)

                // Stats line for R2D2 responses
                if message.role == .assistant {
                    HStack(spacing: 4) {
                        Text("⟐")
                            .foregroundColor(.gray)
                        Text("\(message.content.count) chars · \(message.content.split(separator: " ").count) words")
                            .font(.system(size: 9, design: .monospaced))
                            .foregroundColor(.gray)
                    }
                    .padding(.top, 2)
                }
            }
            .padding(12)
            .background(message.role == .user
                ? Color(red: 0.06, green: 0.11, blue: 0.22)
                : Color(red: 0.05, green: 0.08, blue: 0.12))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(message.role == .user
                        ? Color.blue.opacity(0.15)
                        : Color(white: 0.12), lineWidth: 1)
            )

            if message.role == .assistant {
                Spacer()
            }
        }
        .padding(.horizontal, 16)
    }
}
