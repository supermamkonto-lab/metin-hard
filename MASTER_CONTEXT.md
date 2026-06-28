# METIN HARD LOG — Kontekst Projektu

## Cel projektu

Automatyczne pobieranie logów sprzedaży (Offline Shop) ze wszystkich postaci na koncie w panelu UCP serwera Metin2 (https://projekt-hard.eu/ucp) i zapisywanie ich do plików Excel (XLSX) oraz CSV.

Program uruchamiany ręcznie lub przez Harmonogram Zadań Windows. Wykonuje zadanie i kończy działanie (nie jest usługą).

## Filozofia projektu

- Evidence Required — nie zgadujemy, działamy na podstawie dowodów
- Audit First — przed implementacją sprawdzamy rzeczywisty stan panelu UCP
- Requirements First — wymagania biznesowe przed decyzjami technicznymi
- Master Admin decyduje — Kiro nie podejmuje decyzji architektonicznych samodzielnie
- Deployment jako osobny produkt — użytkownik końcowy nie musi znać Pythona
- Profesjonalny UX — program wygląda jak aplikacja Windows, nie jak skrypt

## Branding

Oficjalna nazwa: METIN HARD LOG — Eksporter Logów Sprzedaży v1.0

## Architektura

config.toml -> load_config() -> AppConfig -> login(page, config) -> detect_characters(page) -> scrape_sales_logs(page, char, config) -> export_xlsx() + export_csv() -> raport końcowy

Technologie: Python 3.11+, Playwright (sync API), openpyxl, headless=False domyślnie.

## Moduły źródłowe (src/)

- models.py — AppConfig, Character, SaleEntry, PaginationInfo, ExecutionStats
- errors.py — ScraperError (bazowy) -> AuthError, CharacterDetectionError, PaginationError, ParseError, SessionExpiredError, ExportError, ConfigError
- config.py — load_config(path) -> AppConfig (TOML, walidacja PIN 5 znaków)
- auth.py — login(page, config), verify_logged_in(page)
- characters.py — detect_characters(page) -> list[Character]
- scraper.py — scrape_sales_logs(page, character, config) -> list[SaleEntry]

## Selektory UCP (potwierdzone eksperymentalnie)

Strona logowania: #cok_accept, button.dropdown-toggle.btn-success, input[name="login"], input[name="pass"], input[name="_pin"], button[type="submit"].btn-success

Strona po zalogowaniu: h5[id^="character-name-"], a#offshop_logs[data-id="{ID}"], div#offshop_logs_modal, #offshop_logs_table, #offshop_logs_table_info, #offshop_logs_table_next

## Format eksportu v1.0

Pliki: XLSX + CSV. Nazwa: POSTAĆ_DD_MM_RRRR_GG_MM. Kolumny: Postać, Nazwa przedmiotu, Ilość, Cena, Typ ceny, Data i godzina. Data: HH:MM YYYY-MM-DD. CSV separator: ;, UTF-8 BOM.

## deployment_V2

Samodzielny, przenośny pakiet. Zawiera: START.cmd, main.py, src/, launcher/, output/, logs/, tests/, config.toml.example. Po skopiowaniu na nowy komputer użytkownik klika START.cmd i korzysta z menu.

## Wykonane Taski

Task 1-6 ukończone + Task 6A (pierwszy eksport). CR-001 wykonany (PIN, selektory). 41 testów PASS.

## Znane ograniczenia

1. Tryb headless nie pobiera logów (serwer blokuje). Domyślnie show_browser=true.
2. Puste body dla MiesoMielone w AJAX — rozwiązane przez fetchLogs() JavaScript.
3. Duplikat ID w DOM UCP — rozwiązane przez data-id i div#.

## Konto testowe

Panel: https://projekt-hard.eu/ucp. Login: hubiklewyJinoo. Postacie: awsuk (0 logów), MiesoMielone (145 logów).

## INIT PROMPT

Poniższy prompt należy użyć na początku nowej sesji:

---

Jesteś Kiro — wykonawcą projektu METIN HARD LOG. Projekt jest w trakcie implementacji. Nie zaczynaj od nowa.

Przeczytaj: 1) MASTER_CONTEXT.md 2) .kiro/steering/ 3) .kiro/specs/metin-hard-ucp-scraper/ (requirements, design, tasks)

Po przeczytaniu: przedstaw stan projektu (po polsku), nie implementuj kodu, oczekuj decyzji Master Admin.

Zasady: język polski, kod angielski, workflow Task->Test->Raport->Review->Decyzja, nie zgaduj, nie zmieniaj specyfikacji bez zgody.

Stan: Task 1-6 done, CR-001 done, 41 testów PASS, deployment_V2 działa, następny krok: decyzja Master Admin.
