# openPlaud

Własna aplikacja do transkrypcji i podsumowań nagrań — zamiennik limitu minut PLAUD.
Transkrypcja lokalnie (Whisper), podsumowania lokalnie lub opcjonalnie przez własny klucz API.

## Struktura

| Folder | Zawartość |
|---|---|
| `apps/apple/` | Aplikacja SwiftUI: iPhone, iPad, Mac (Apple Silicon) |
| `apps/web/` | Aplikacja webowa (PWA): Windows 11, Mac Intel, przeglądarka |
| `backend/` | Supabase (region UE): logowanie, synchronizacja tekstu |
| `spikes/` | Testy wykonalności z iteracji 0 |
| `docs/` | Decyzje, ryzyka, kryteria akceptacji, backlog |

## Status

Iteracja 0 — testy wykonalności. Zobacz `docs/backlog.md`.
