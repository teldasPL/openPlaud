import AVFoundation
import Foundation
import UIKit
import WhisperKit

/// Test T2: lokalna transkrypcja Whisper na iPhonie — pomiar czasu i jakości.
@MainActor
final class SpikeModel: ObservableObject {
    static let models = [
        "openai_whisper-large-v3-v20240930_turbo_632MB",
        "openai_whisper-large-v3-v20240930_626MB",
        "openai_whisper-large-v3_turbo_954MB",
        "openai_whisper-small",
    ]
    static let languages = ["pl", "auto", "en"]
    static func languageName(_ code: String) -> String {
        switch code {
        case "pl": return "Polski"
        case "en": return "Angielski"
        default: return "Wykryj automatycznie"
        }
    }

    @Published var selectedModel = SpikeModel.models[0]
    @Published var language = "pl"
    @Published var status = "1. Pobierz i załaduj model"
    @Published var busy = false
    @Published var modelReady = false
    @Published var fileURL: URL?
    @Published var progress: Double = 0
    @Published var report = ""
    @Published var transcript = ""
    @Published var exportURL: URL?

    private var kit: WhisperKit?
    private var loadedModel: String?
    private var loadSeconds: Double = 0

    func loadModel() {
        guard !busy else { return }
        busy = true
        modelReady = false
        status = "Pobieram i ładuję model \(selectedModel)…\nPierwszy raz: kilka minut (ok. 0,6–1 GB, użyj Wi-Fi)."
        let name = selectedModel
        Task {
            let t0 = Date()
            do {
                let config = WhisperKitConfig(model: name, verbose: false, logLevel: .error,
                                              prewarm: true, load: true, download: true)
                kit = try await WhisperKit(config)
                loadedModel = name
                loadSeconds = Date().timeIntervalSince(t0)
                modelReady = true
                status = String(format: "Model gotowy (%.0f s). 2. Wybierz plik audio.", loadSeconds)
            } catch {
                status = "Błąd ładowania modelu: \(error.localizedDescription)"
            }
            busy = false
        }
    }

    func importFile(_ result: Result<URL, Error>) {
        switch result {
        case .failure(let error):
            status = "Nie udało się otworzyć pliku: \(error.localizedDescription)"
        case .success(let picked):
            let scoped = picked.startAccessingSecurityScopedResource()
            defer { if scoped { picked.stopAccessingSecurityScopedResource() } }
            let dest = FileManager.default.temporaryDirectory.appendingPathComponent(picked.lastPathComponent)
            try? FileManager.default.removeItem(at: dest)
            do {
                try FileManager.default.copyItem(at: picked, to: dest)
                fileURL = dest
                status = modelReady ? "3. Naciśnij „Transkrybuj”." : "Plik wybrany. Załaduj model."
            } catch {
                status = "Nie udało się skopiować pliku: \(error.localizedDescription)"
            }
        }
    }

    func transcribe() {
        guard let kit, let fileURL, !busy else { return }
        busy = true
        progress = 0
        transcript = ""
        report = ""
        exportURL = nil
        status = "Transkrybuję… Nie blokuj ekranu i nie przełączaj aplikacji."
        UIApplication.shared.isIdleTimerDisabled = true

        let lang = language
        let modelName = loadedModel ?? selectedModel
        let poller = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            Task { @MainActor in
                guard let self, let kit = self.kit else { return }
                self.progress = kit.progress.fractionCompleted
            }
        }

        Task {
            defer {
                poller.invalidate()
                UIApplication.shared.isIdleTimerDisabled = false
                busy = false
            }
            do {
                let audioSeconds = try await CMTimeGetSeconds(AVURLAsset(url: fileURL).load(.duration))
                let options = DecodingOptions(
                    verbose: false,
                    task: .transcribe,
                    language: lang == "auto" ? nil : lang,
                    detectLanguage: lang == "auto",
                    chunkingStrategy: .vad
                )
                let thermalStart = ProcessInfo.processInfo.thermalState
                let batteryStart = Self.batteryLevel()
                let t0 = Date()
                let results = try await kit.transcribe(audioPath: fileURL.path, decodeOptions: options)
                let seconds = Date().timeIntervalSince(t0)
                let batteryEnd = Self.batteryLevel()

                let segments = results.flatMap(\.segments)
                transcript = segments.map { "[\(Self.clock($0.start))] \($0.text.trimmingCharacters(in: .whitespaces))" }
                    .joined(separator: "\n")
                if transcript.isEmpty { transcript = results.map(\.text).joined(separator: " ") }

                let detected = results.first?.language ?? "?"
                report = """
                Urządzenie: \(Self.deviceModel()), iOS \(UIDevice.current.systemVersion)
                Model: \(modelName)
                Język: \(lang) (wykryty: \(detected))
                Długość nagrania: \(Self.clock(Float(audioSeconds)))
                Ładowanie modelu: \(String(format: "%.0f s", loadSeconds))
                Czas transkrypcji: \(Self.clock(Float(seconds)))
                Szybkość: \(String(format: "%.1f", audioSeconds / max(seconds, 1)))× czasu rzeczywistego
                1 godzina nagrania ≈ \(String(format: "%.0f", 60 * seconds / max(audioSeconds, 1))) min
                Bateria: \(batteryStart) → \(batteryEnd)
                Temperatura: \(Self.thermal(thermalStart)) → \(Self.thermal(ProcessInfo.processInfo.thermalState))
                """
                progress = 1
                status = "Gotowe. Udostępnij wynik i wklej go do czatu."
                exportURL = try writeExport()
            } catch {
                status = "Błąd transkrypcji: \(error.localizedDescription)"
            }
        }
    }

    private func writeExport() throws -> URL {
        let name = (fileURL?.deletingPathExtension().lastPathComponent ?? "transkrypcja") + "_whisper.txt"
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(name)
        try ("RAPORT T2\n" + report + "\n\nTRANSKRYPCJA\n" + transcript).write(to: url, atomically: true, encoding: .utf8)
        return url
    }

    // MARK: - Pomocnicze

    static func clock(_ s: Float) -> String {
        let t = Int(s)
        return String(format: "%d:%02d:%02d", t / 3600, t % 3600 / 60, t % 60)
    }

    static func batteryLevel() -> String {
        UIDevice.current.isBatteryMonitoringEnabled = true
        let level = UIDevice.current.batteryLevel
        return level < 0 ? "?" : "\(Int(level * 100))%"
    }

    static func thermal(_ s: ProcessInfo.ThermalState) -> String {
        switch s {
        case .nominal: return "normalna"
        case .fair: return "podwyższona"
        case .serious: return "wysoka"
        case .critical: return "krytyczna"
        @unknown default: return "?"
        }
    }

    static func deviceModel() -> String {
        var info = utsname()
        uname(&info)
        return withUnsafeBytes(of: &info.machine) { buf in
            String(decoding: buf.prefix(while: { $0 != 0 }), as: UTF8.self)
        }
    }
}
