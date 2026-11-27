# T2 — Whisper PL na iPhonie

Aplikacja testowa: lokalna transkrypcja (WhisperKit, model large-v3 turbo) i pomiar czasu.

## Przygotowanie (Mac)

```
brew install xcodegen ffmpeg
cd ~/openPlaud/spikes/plaud_connect && python3 plaud_test.py
cd ~/openPlaud/spikes/whisper_ios && xcodegen generate && open OpenPlaudSpike.xcodeproj
```

Skrypt `plaud_test.py` zapisuje w `spikes/plaud_connect/downloads/`:
- `<id>.ogg` — oryginał z PLAUD,
- `<id>.wav` — wersja dla iPhone'a (16 kHz, mono),
- `<id>_plaud_transkrypcja.txt` i `<id>_plaud_podsumowanie.md` — do porównania.

## Kryterium akceptacji

- Transkrypcja nagrania 25 min zakończona na iPhonie 15 Pro.
- Raport: czas, szybkość względem czasu rzeczywistego, bateria, temperatura.
- Ocena jakości 1–5 względem transkrypcji PLAUD.
