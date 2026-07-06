import Foundation
import AVFoundation

actor R2D2SoundService {
    static let shared = R2D2SoundService()
    private var audioPlayer: AVAudioPlayer?

    // Generate R2D2 beep sounds using AVFoundation
    func playRandomSound() -> String {
        let sounds = [
            ("Happy Chirp", generateBeep(frequencies: [(800, 0.15, 1.5)], type: .sine)),
            ("Sad Beep", generateBeep(frequencies: [(600, 0.25, 0.5)], type: .sine)),
            ("Question Trill", generateBeep(frequencies: [(500, 0.08, 1.2), (700, 0.08, 1.2), (900, 0.08, 1.2)], type: .sine)),
            ("Excited Rapid", generateBeep(frequencies: [(1200, 0.05, 1.0), (900, 0.05, 1.0), (1200, 0.05, 1.0), (900, 0.05, 1.0), (1200, 0.05, 1.0)], type: .square)),
            ("Angry Buzz", generateBeep(frequencies: [(200, 0.3, 0.8)], type: .sawtooth)),
            ("Curious Warble", generateBeep(frequencies: [(700, 0.1, 1.0), (800, 0.1, 1.0), (600, 0.1, 1.0), (900, 0.1, 1.0)], type: .triange)),
            ("Affirmative", generateBeep(frequencies: [(1000, 0.2, 1.0)], type: .triangle)),
            ("Negative", generateBeep(frequencies: [(700, 0.2, 0.8), (500, 0.2, 0.6)], type: .sine)),
            ("Charge Up", generateBeep(frequencies: [(300, 0.3, 0.5), (800, 0.3, 0.8), (1500, 0.3, 1.0)], type: .sine)),
            ("Alert", generateBeep(frequencies: [(800, 0.1, 1.0), (1200, 0.1, 1.0), (800, 0.1, 1.0)], type: .sine)),
            ("Greeting", generateBeep(frequencies: [(523, 0.1, 1.0), (659, 0.1, 1.0), (784, 0.1, 1.0), (1047, 0.1, 1.0)], type: .sine)),
            ("Laugh", generateBeep(frequencies: [(600, 0.06, 1.0), (800, 0.06, 1.0), (700, 0.06, 1.0), (900, 0.06, 1.0), (650, 0.06, 1.0), (850, 0.06, 1.0)], type: .sine)),
        ]
        let idx = Int.random(in: 0..<sounds.count)
        let (name, data) = sounds[idx]
        playAudioData(data)
        return name
    }

    private func generateBeep(frequencies: [(freq: Double, duration: Double, volume: Double)], type: AVFreqType) -> Data {
        let sampleRate: Double = 44100
        let totalSamples = Int(frequencies.reduce(0) { $0 + $1.duration } * sampleRate)
        var samples = [Float](repeating: 0, count: totalSamples)

        var sampleOffset = 0
        for (freq, duration, volume) in frequencies {
            let numSamples = Int(duration * sampleRate)
            for i in 0..<numSamples {
                let t = Double(i) / sampleRate
                let envelope = exp(-3.0 * t / duration) * Float(volume)
                let value: Float
                switch type {
                case .sine: value = sin(2.0 * .pi * freq * t)
                case .square: value = sin(2.0 * .pi * freq * t) >= 0 ? 1.0 : -1.0
                case .sawtooth: value = Float(2.0 * (freq * t - floor(freq * t + 0.5)))
                case .triangle: value = Float(2.0 * abs(2.0 * (freq * t - floor(freq * t + 0.5))) - 1.0)
                }
                if sampleOffset + i < totalSamples {
                    samples[sampleOffset + i] = value * envelope
                }
            }
            sampleOffset += numSamples
        }

        // Convert to WAV format
        var header = Data()
        let dataSize = totalSamples * 2 // 16-bit
        let fileSize = 36 + dataSize

        // RIFF header
        header.append(contentsOf: [0x52, 0x49, 0x46, 0x46]) // "RIFF"
        header.append(contentsOf: withUnsafeBytes(of: Int32(fileSize).littleEndian) { Data($0) })
        header.append(contentsOf: [0x57, 0x41, 0x56, 0x45]) // "WAVE"

        // fmt chunk
        header.append(contentsOf: [0x66, 0x6D, 0x74, 0x20]) // "fmt "
        header.append(contentsOf: withUnsafeBytes(of: Int32(16).littleEndian) { Data($0) }) // chunk size
        header.append(contentsOf: withUnsafeBytes(of: Int16(1).littleEndian) { Data($0) }) // PCM
        header.append(contentsOf: withUnsafeBytes(of: Int16(1).littleEndian) { Data($0) }) // mono
        header.append(contentsOf: withUnsafeBytes(of: Int32(sampleRate).littleEndian) { Data($0) }) // sample rate
        header.append(contentsOf: withUnsafeBytes(of: Int32(sampleRate * 2).littleEndian) { Data($0) }) // byte rate
        header.append(contentsOf: withUnsafeBytes(of: Int16(2).littleEndian) { Data($0) }) // block align
        header.append(contentsOf: withUnsafeBytes(of: Int16(16).littleEndian) { Data($0) }) // bits per sample

        // data chunk
        header.append(contentsOf: [0x64, 0x61, 0x74, 0x61]) // "data"
        header.append(contentsOf: withUnsafeBytes(of: Int32(dataSize).littleEndian) { Data($0) })

        var audioData = header
        for sample in samples {
            let intSample = Int16(max(-32768, min(32767, sample * 32767)))
            audioData.append(contentsOf: withUnsafeBytes(of: intSample.littleEndian) { Data($0) })
        }

        return audioData
    }

    private func playAudioData(_ data: Data) {
        guard let player = try? AVAudioPlayer(data: data) else { return }
        audioPlayer = player
        player.play()
    }
}

enum AVFreqType {
    case sine, square, sawtooth, triangle
}
