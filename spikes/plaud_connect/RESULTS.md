# T1 — wynik (2026-11-26)

**Status: ZALICZONY**

| Sprawdzane | Wynik |
|---|---|
| Logowanie OAuth+PKCE przez przeglądarkę | Działa, także przy logowaniu przez Apple (konto z adresem przekaźnika Apple) |
| Lista nagrań | Działa (`/open/third-party/files/`), zawiera nazwy, daty, `serial_number` urządzenia |
| Rozmowy telefoniczne z trybu rozmów Note Pro | Widoczne na liście jak zwykłe nagrania |
| Pobranie audio (`presigned_url`) | 24:38 nagrania = 6,3 MB, `audio/ogg` (Opus, ok. 34 kb/s), 2,5 s |
| Czas trwania (`duration`) | W milisekundach |
| Zużycie minut | Brak — skrypt nie zleca transkrypcji |

## Wnioski

1. Ścieżka D4 potwierdzona: konto PLAUD jako źródło nagrań działa.
2. Nowe ryzyko R9: format Ogg/Opus wymaga własnego dekodera na iOS.
3. Problemy środowiskowe na Macu: brak certyfikatów w Pythonie z python.org (naprawa: Install Certificates.command); 403 dla domyślnego User-Agent Pythona (naprawa: własny User-Agent).
4. Nagrania z 26.11 mają już transkrypcję PLAUD — Auto-transkrypcja w aplikacji PLAUD była wtedy włączona.
