import Foundation

actor R2D2APIService {
    static let shared = R2D2APIService()

    private var baseURL: String {
        UserDefaults.standard.string(forKey: "api_url") ?? "https://ilukha.com"
    }

    private var modelName: String {
        UserDefaults.standard.string(forKey: "model_name") ?? "r2d2-1b"
    }

    // MARK: - Check Server Status

    func checkStatus() async -> Bool {
        guard let url = URL(string: "\(baseURL)/v1/models") else { return false }
        do {
            let request = URLRequest(url: url, timeoutInterval: 5)
            let (_, response) = try await URLSession.shared.data(for: request)
            return (response as? HTTPURLResponse)?.statusCode == 200
        } catch {
            return false
        }
    }

    // MARK: - Streaming Chat

    func streamChat(
        message: String,
        onToken: @escaping (String) -> Void,
        onFinish: @escaping (Result<String, Error>) -> Void
    ) -> URLSessionTask? {
        guard let url = URL(string: "\(baseURL)/v1/chat/completions") else {
            onFinish(.failure(URLError(.badURL)))
            return nil
        }

        var request = URLRequest(url: url, timeoutInterval: 30)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")

        let body: [String: Any] = [
            "model": modelName,
            "messages": [["role": "user", "content": message]],
            "stream": true
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        let delegate = SSEStreamDelegate(onToken: onToken, onFinish: onFinish)
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        let task = session.dataTask(with: request)
        task.resume()

        // Store session reference to prevent deallocation
        delegate.retainSession(session)

        return task
    }
}

// MARK: - SSE Stream Delegate

private class SSEStreamDelegate: NSObject, URLSessionDataDelegate {
    private let onToken: (String) -> Void
    private let onFinish: (Result<String, Error>) -> Void
    private var buffer = ""
    private var fullText = ""
    private var session: URLSession?

    init(onToken: @escaping (String) -> Void, onFinish: @escaping (Result<String, Error>) -> Void) {
        self.onToken = onToken
        self.onFinish = onFinish
    }

    func retainSession(_ session: URLSession) {
        self.session = session
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        guard let text = String(data: data, encoding: .utf8) else { return }
        buffer += text

        let lines = buffer.components(separatedBy: "\n")
        buffer = lines.last ?? ""
        let completeLines = lines.dropLast()

        for line in completeLines {
            let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
            guard trimmed.hasPrefix("data: ") else { continue }
            let payload = String(trimmed.dropFirst(6))

            if payload == "[DONE]" {
                onFinish(.success(fullText))
                return
            }

            guard let jsonData = payload.data(using: .utf8),
                  let json = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                  let choices = json["choices"] as? [[String: Any]],
                  let delta = choices.first?["delta"] as? [String: Any],
                  let content = delta["content"] as? String
            else { continue }

            fullText += content
            onToken(content)
        }
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        if let error = error {
            onFinish(.failure(error))
        } else if !fullText.isEmpty {
            onFinish(.success(fullText))
        }
        self.session?.invalidateAndCancel()
        self.session = nil
    }
}
