# Backlog i kryteria akceptacji

## Iteracja 0 — testy wykonalności

| # | Test | Kryterium akceptacji | Status |
|---|---|---|---|
| T1 | Połączenie z kontem PLAUD (`spikes/plaud_connect`) | Logowanie w przeglądarce, lista nagrań, pobrany plik audio; żadna minuta transkrypcji nie zużyta | ✅ Zaliczony 2026-11-26 (patrz `spikes/plaud_connect/RESULTS.md`) |
| T2 | Whisper PL na iPhonie 15 Pro | Transkrypcja 10 min prawdziwego nagrania; zmierzony czas i oceniona jakość (Ty oceniasz 1–5) | Do zrobienia |
| T3 | Podsumowanie PL: lokalnie vs klucz API | Dwa podsumowania tej samej transkrypcji; ocena 1–5 | Do zrobienia |
| T4 | Logowanie PLAUD z poziomu iOS (ryzyko R2) | Token uzyskany w aplikacji testowej na iPhonie | Do zrobienia |

## Etap 1 — szkielet (MVP)

1. Źródła nagrań: konto PLAUD, import plików, nagrywanie w aplikacji.
2. Transkrypcja lokalna: polski domyślnie, automatyczne wykrywanie języka, słownik własnych terminów.
3. Podsumowania: szablony (spotkanie, szkolenie, rozmowa, targi), własne polecenia, lista zadań, mapa myśli.
4. Własne notatki: tekst i głos, przypięte do nagrania lub samodzielne.
5. Wyszukiwanie, foldery, tagi, eksport TXT/DOCX/PDF/SRT/Markdown.
6. Logowanie Google + e-mail, synchronizacja tekstu, aplikacja webowa do podglądu i edycji.
7. Interfejs PL/EN według języka systemu.
8. Opcja „lepsza wersja online”: własny klucz API (OpenAI, Anthropic, własny serwer).

## Etap 2

- Sign in with Apple, TestFlight.
- Rozpoznawanie mówców (TODO z wymagań) + rozpoznawanie znanych głosów w kolejnych nagraniach (inspiracja: BetterScribe).
- Przypomnienia i wydarzenia w kalendarzu wyciągane z nagrań (BetterScribe).
- „Zapytaj AI” o wszystkie nagrania.
- Nagrywanie z Apple Watch (BetterScribe).
- Audio na www, dopracowanie iPada i Maca.

## Etap 3

- Bezpośrednia synchronizacja z PLAUD Note Pro przez BLE (inżynieria wsteczna).
- Lokalna transkrypcja na Windows (opcjonalny pomocnik whisper.cpp).
- Przygotowanie do App Store: polityka prywatności, analiza regulaminu PLAUD, nazwa.
