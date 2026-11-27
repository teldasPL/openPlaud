import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @StateObject private var m = SpikeModel()
    @State private var showImporter = false

    var body: some View {
        NavigationStack {
            Form {
                Section("1. Model") {
                    Picker("Model", selection: $m.selectedModel) {
                        ForEach(SpikeModel.models, id: \.self) { Text($0.replacingOccurrences(of: "openai_whisper-", with: "")).tag($0) }
                    }
                    Button(m.modelReady ? "Załaduj ponownie" : "Pobierz i załaduj model") { m.loadModel() }
                        .disabled(m.busy)
                }

                Section("2. Nagranie") {
                    Picker("Język", selection: $m.language) {
                        ForEach(SpikeModel.languages, id: \.self) { Text(SpikeModel.languageName($0)).tag($0) }
                    }
                    Button("Wybierz plik audio") { showImporter = true }
                        .disabled(m.busy)
                    if let url = m.fileURL {
                        Text(url.lastPathComponent).font(.footnote).foregroundStyle(.secondary)
                    }
                }

                Section("3. Transkrypcja") {
                    Button("Transkrybuj") { m.transcribe() }
                        .disabled(m.busy || !m.modelReady || m.fileURL == nil)
                    if m.busy || m.progress > 0 {
                        ProgressView(value: m.progress)
                        Text("\(Int(m.progress * 100))%").font(.footnote)
                    }
                    Text(m.status).font(.callout)
                }

                if !m.report.isEmpty {
                    Section("Raport") {
                        Text(m.report).font(.system(.footnote, design: .monospaced)).textSelection(.enabled)
                        if let url = m.exportURL {
                            ShareLink(item: url) { Label("Udostępnij wynik (.txt)", systemImage: "square.and.arrow.up") }
                        }
                    }
                    Section("Transkrypcja") {
                        Text(m.transcript).font(.footnote).textSelection(.enabled)
                    }
                }
            }
            .navigationTitle("openPlaud · test T2")
            .fileImporter(isPresented: $showImporter,
                          allowedContentTypes: [.audio, .wav, .mpeg4Audio, .mp3],
                          onCompletion: m.importFile)
        }
    }
}
