# Rejestr ryzyk

| # | Ryzyko | Wpływ | Prawdop. | Działanie |
|---|---|---|---|---|
| R1 | API PLAUD (klient Plaud CLI) nie jest przeznaczone dla aplikacji firm trzecich — może się zmienić lub zostać zablokowane; kwestia regulaminu | Wysoki | Średnie | Zapas: import plików; etap 3: BLE. Przed publikacją w App Store — analiza regulaminu |
| R2 | Logowanie PLAUD na iOS: adres zwrotny OAuth to `http://localhost:8199`. Logowanie Google zwykle nie działa w osadzonym WebView | Średni | Średnie | Test: ASWebAuthenticationSession + lokalny nasłuch na porcie 8199; zapas: WKWebView + hasło do konta PLAUD (ustawiane przez „Nie pamiętam hasła”) |
| R3 | Czas transkrypcji długich nagrań (targi, kilka godzin) i ograniczenia iOS w tle | Średni | Wysokie | Kolejka nocna podczas ładowania; pomiar w iteracji 0; zapas: Mac M5 |
| R4 | Jakość lokalnych podsumowań po polsku; nieznane wsparcie PL w Apple Foundation Models | Średni | Średnie | Test w iteracji 0; opcja klucza API lub własnego serwera (np. Ollama) |
| R5 | Prawne aspekty nagrywania rozmów i spotkań (RODO, dobra osobiste) | Wysoki | Niskie–średnie | Przypomnienia o informowaniu uczestników; polityka prywatności; konsultacja prawna przed publikacją |
| R6 | Darmowe konto Apple: aplikacja wygasa po 7 dniach, brak TestFlight i Sign in with Apple | Niski | Pewne | Zakup konta 99 USD przed etapem 2 |
| R7 | Nazwa i znak towarowy: nie można używać „PLAUD” w nazwie aplikacji | Niski | — | Nazwa repozytorium „openPlaud” (prywatnie OK); przed App Store zmiana nazwy — istnieje już projekt OpenPlaud (ByteFine/openplaud) i znak PLAUD |
| R8 | Przechowywanie audio w chmurze (do odtwarzania na www) — koszty po przekroczeniu darmowych limitów | Niski | Średnie | Domyślnie synchronizujemy tylko tekst; audio opcjonalnie |
