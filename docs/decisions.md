# Rejestr decyzji (ADR)

| # | Data | Decyzja | Uzasadnienie |
|---|---|---|---|
| D1 | 2026-11-26 | Natywny Swift/SwiftUI na iPhone/iPad/Mac + aplikacja webowa dla Windows/Mac Intel | iPhone wykonuje ciężką pracę (WhisperKit/Core ML najszybszy natywnie); inne urządzenia głównie przeglądają |
| D2 | 2026-11-26 | Transkrypcja lokalna: Whisper large-v3-turbo przez WhisperKit | Apple SpeechTranscriber nie obsługuje polskiego |
| D3 | 2026-11-26 | Chmura jako opcja „lepsza transkrypcja / lepsze podsumowanie” z własnym kluczem API | Wymaganie właściciela produktu |
| D4 | 2026-11-26 | Źródło nagrań nr 1: konto PLAUD przez OAuth (jak oficjalny Plaud CLI), pobranie `presigned_url` | Transfer do konta PLAUD nie zużywa minut; brak inżynierii wstecznej BLE na start |
| D5 | 2026-11-26 | Źródło nr 2: import plików (Pliki / Udostępnij). Źródło nr 3 (etap 3): BLE bezpośrednio z Note Pro | Odporność na zmiany API PLAUD |
| D6 | 2026-11-26 | Rozmowy telefoniczne: tryb rozmów PLAUD Note Pro → konto PLAUD → openPlaud | Aplikacje firm trzecich na iOS nie mogą nagrywać rozmów |
| D7 | 2026-11-26 | Backend: Supabase UE; logowanie Google + e-mail w etapie 1, Apple po zakupie konta Apple Developer | Sign in with Apple wymaga płatnego członkostwa |
| D8 | 2026-11-26 | W aplikacji PLAUD wyłączona Auto-transkrypcja | Inaczej zużywa 300 min |
| D9 | 2026-11-26 | Budowanie aplikacji iOS na MacBooku M5 | MacBook Intel może nie uruchomić najnowszego Xcode (do weryfikacji) |
