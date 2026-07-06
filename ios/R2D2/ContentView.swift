import SwiftUI

struct ContentView: View {
    @EnvironmentObject var viewModel: ChatViewModel
    @State private var inputText = ""
    @State private var showSettings = false
    @State private var showImagePicker = false
    @State private var showVideoPicker = false
    @State private var imagePickerSource: UIImagePickerController.SourceType = .photoLibrary
    @State private var selectedImageData: Data?
    @State private var selectedVideoURL: URL?
    @FocusState private var isInputFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerView

            // Stats Bar
            statsBar

            // Chat or Welcome
            if viewModel.messages.isEmpty {
                welcomeView
            } else {
                chatView
            }

            // Input Bar
            inputBar
        }
        .background(Color(red: 0.02, green: 0.035, blue: 0.055))
        .task { await viewModel.checkStatus() }
        .onReceive(NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)) { _ in
            Task { await viewModel.checkStatus() }
        }
        .sheet(isPresented: $showSettings) { SettingsView() }
        .sheet(isPresented: $showImagePicker) {
            ImagePicker(imageData: $selectedImageData, videoURL: .constant(nil),
                       sourceType: .photoLibrary, mediaTypes: ["public.image"])
                .onDisappear {
                    if let data = selectedImageData {
                        viewModel.sendPhoto(data)
                        selectedImageData = nil
                    }
                }
        }
        .sheet(isPresented: $showVideoPicker) {
            ImagePicker(imageData: .constant(nil), videoURL: $selectedVideoURL,
                       sourceType: .photoLibrary, mediaTypes: ["public.movie"])
                .onDisappear {
                    if let url = selectedVideoURL {
                        viewModel.sendVideo(url)
                        selectedVideoURL = nil
                    }
                }
        }
    }

    // MARK: - Header

    var headerView: some View {
        HStack(spacing: 12) {
            // Brand icon
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(LinearGradient(colors: [.blue, .indigo], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 32, height: 32)
                Text("R")
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }

            VStack(alignment: .leading, spacing: 0) {
                Text("R2D2")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.white)
                Text("QS-MoUE · 17.3T params")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }

            Spacer()

            // Status badge
            HStack(spacing: 4) {
                Circle()
                    .fill(viewModel.isOnline ? Color.green : Color.red)
                    .frame(width: 6, height: 6)
                Text("r2d2-1b · \(viewModel.isOnline ? "online" : "offline")")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundColor(.gray)
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(Color(white: 0.1))
            .cornerRadius(12)

            Button { viewModel.clearChat() } label: {
                Image(systemName: "trash")
                    .font(.system(size: 13))
                    .foregroundColor(.gray)
                    .frame(width: 32, height: 32)
                    .background(Color(white: 0.08))
                    .cornerRadius(6)
            }

            Button { showSettings = true } label: {
                Image(systemName: "gearshape")
                    .font(.system(size: 13))
                    .foregroundColor(.gray)
                    .frame(width: 32, height: 32)
                    .background(Color(white: 0.08))
                    .cornerRadius(6)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Color(red: 0.025, green: 0.04, blue: 0.065))
        .overlay(Divider(), alignment: .bottom)
    }

    // MARK: - Stats Bar

    var statsBar: some View {
        HStack(spacing: 14) {
            StatItem(label: "latency", value: viewModel.stats.lastLatency > 0
                ? String(format: "%.1fs", viewModel.stats.lastLatency) : "—")
            StatDivider()
            StatItem(label: "tokens", value: "\(viewModel.stats.totalTokens)")
            StatDivider()
            StatItem(label: "hallucinations", value: "0.00%", color: .green)
            StatDivider()
            StatItem(label: "ctx", value: "∞")
        }
        .font(.system(size: 10, design: .monospaced))
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(Color(red: 0.025, green: 0.04, blue: 0.065))
        .overlay(Divider(), alignment: .bottom)
    }

    // MARK: - Welcome

    var welcomeView: some View {
        VStack(spacing: 16) {
            Spacer()

            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(LinearGradient(colors: [.blue, .indigo, .purple],
                                         startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 80, height: 80)
                Text("✦")
                    .font(.system(size: 36, weight: .light))
                    .foregroundColor(.white.opacity(0.9))
            }
            .overlay(
                RoundedRectangle(cornerRadius: 24)
                    .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                    .frame(width: 88, height: 88)
            )

            Text("R2D2-1B")
                .font(.system(size: 24, weight: .semibold))
                .foregroundColor(.white)

            Text("Quantum-Sparse Mixture-of-Universal-Experts\nZero-shot general intelligence · Zero hallucination guarantee")
                .font(.system(size: 12, design: .monospaced))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)

            // Capability chips
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 6), count: 3), spacing: 6) {
                ForEach(["NLP", "Vision", "Audio", "3D Reasoning", "Code", "Math", "8432 Languages", "Infinite Context", "Multimodal"], id: \.self) { cap in
                    Text(cap)
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundColor(.gray)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(white: 0.08))
                        .cornerRadius(4)
                }
            }
            .padding(.horizontal, 40)

            Spacer()
        }
    }

    // MARK: - Chat

    var chatView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 6) {
                    ForEach(viewModel.messages) { msg in
                        MessageBubble(message: msg)
                            .id(msg.id)
                    }

                    // Streaming indicator
                    if viewModel.isStreaming {
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                HStack(spacing: 8) {
                                    Text("R2D2-1B")
                                        .font(.system(size: 10, weight: .semibold, design: .monospaced))
                                        .foregroundColor(.blue)
                                    Spacer()
                                    Text(Date(), style: .time)
                                        .font(.system(size: 9, design: .monospaced))
                                        .foregroundColor(.gray)
                                }
                                HStack(spacing: 0) {
                                    Text(viewModel.currentResponse)
                                        .font(.system(size: 15))
                                        .foregroundColor(.white)
                                    CursorBlink()
                                }
                            }
                            .padding(12)
                            .background(Color(red: 0.05, green: 0.08, blue: 0.12))
                            .cornerRadius(12)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color(white: 0.12), lineWidth: 1)
                            )
                            Spacer()
                        }
                        .padding(.horizontal, 16)
                        .id("streaming")
                    }
                }
                .padding(.vertical, 12)
            }
            .onChange(of: viewModel.messages.count) { _ in
                if let last = viewModel.messages.last {
                    withAnimation { proxy.scrollTo(last.id, anchor: .bottom) }
                }
            }
            .onChange(of: viewModel.currentResponse) { _ in
                proxy.scrollTo("streaming", anchor: .bottom)
            }
        }
    }

    // MARK: - Input Bar

    var inputBar: some View {
        VStack(spacing: 0) {
            Divider().background(Color(white: 0.1))

            HStack(spacing: 8) {
                HStack {
                    TextField("Enter your prompt...", text: $inputText)
                        .font(.system(size: 14))
                        .foregroundColor(.white)
                        .focused($isInputFocused)
                        .onSubmit { send() }
                        .disabled(viewModel.isStreaming)

                    // Multimodal buttons
                    Button { startRecording() } label: {
                        Image(systemName: viewModel.isRecording ? "stop.circle.fill" : "mic")
                            .font(.system(size: 13))
                            .foregroundColor(viewModel.isRecording ? .red : .gray)
                    }
                    .disabled(viewModel.isStreaming)

                    Button { showImagePicker = true } label: {
                        Image(systemName: "photo")
                            .font(.system(size: 13))
                            .foregroundColor(.gray)
                    }

                    Button { showVideoPicker = true } label: {
                        Image(systemName: "video")
                            .font(.system(size: 13))
                            .foregroundColor(.gray)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(Color(white: 0.08))
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(isInputFocused ? Color.blue : Color(white: 0.12), lineWidth: 1)
                )

                Button(action: send) {
                    Text("↵")
                        .font(.system(size: 18, weight: .medium, design: .monospaced))
                        .foregroundColor(.white)
                        .frame(width: 44, height: 44)
                        .background(inputText.trimmingCharacters(in: .whitespaces).isEmpty || viewModel.isStreaming ? Color.gray.opacity(0.3) : Color.blue)
                        .cornerRadius(10)
                }
                .disabled(inputText.trimmingCharacters(in: .whitespaces).isEmpty || viewModel.isStreaming)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .padding(.bottom, 8)
        }
        .background(Color(red: 0.025, green: 0.04, blue: 0.065))
    }

    private func send() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        viewModel.sendMessage(text)
        inputText = ""
    }

    private func startRecording() {
        if viewModel.isRecording {
            viewModel.stopRecording()
        } else {
            viewModel.startRecording()
        }
    }
}

// MARK: - Image Picker

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var imageData: Data?
    @Binding var videoURL: URL?
    var sourceType: UIImagePickerController.SourceType
    var mediaTypes: [String]
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = sourceType
        picker.mediaTypes = mediaTypes
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        init(_ parent: ImagePicker) { self.parent = parent }
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage,
               let data = image.jpegData(compressionQuality: 0.8) {
                parent.imageData = data
            }
            if let url = info[.mediaURL] as? URL {
                parent.videoURL = url
            }
            parent.dismiss()
        }
    }
}

// MARK: - Cursor Blink Animation

struct CursorBlink: View {
    @State private var visible = true

    var body: some View {
        Rectangle()
            .fill(Color.blue)
            .frame(width: 6, height: 16)
            .opacity(visible ? 1 : 0)
            .onAppear {
                withAnimation(Animation.easeInOut(duration: 0.7).repeatForever(autoreverses: true)) {
                    visible.toggle()
                }
            }
    }
}

// MARK: - Stat Helpers

struct StatItem: View {
    let label: String
    let value: String
    var color: Color = .gray

    var body: some View {
        HStack(spacing: 4) {
            Text(label + ":")
                .foregroundColor(.gray)
            Text(value)
                .foregroundColor(color)
        }
    }
}

struct StatDivider: View {
    var body: some View {
        Rectangle()
            .fill(Color(white: 0.15))
            .frame(width: 1, height: 12)
    }
}
