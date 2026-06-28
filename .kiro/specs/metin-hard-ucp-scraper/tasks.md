# Plan Implementacji: Metin Hard UCP Scraper

## Przegląd

Implementacja jednorazowego skryptu w Pythonie z Playwright (sync API) do automatycznego pobierania logów sprzedaży z panelu UCP serwera Metin2 i eksportu do CSV. Struktura modularna z testami property-based (Hypothesis) i jednostkowymi (pytest).

## Zadania

- [x] 1. Konfiguracja projektu i struktura podstawowa
  - [x] 1.1 Utworzenie struktury katalogów i plików konfiguracyjnych projektu
    - Utworzyć katalog główny z plikami: `pyproject.toml`, `config.toml.example`
    - Skonfigurować zależności: `playwright`, `pytest`, `hypothesis`
    - Utworzyć strukturę katalogów: `src/`, `tests/`, `tests/property/`, `tests/unit/`
    - Utworzyć plik `src/__init__.py` i `tests/__init__.py`
    - _Wymagania: 5.2, 5.3 (uruchamianie z wiersza poleceń), Ograniczenia (Python, Playwright)_

  - [x] 1.2 Implementacja modułu błędów (`src/errors.py`)
    - Zdefiniować hierarchię wyjątków: `ScraperError` (bazowy) z polem `stage`
    - Zdefiniować klasy pochodne: `AuthError`, `CharacterDetectionError`, `PaginationError`, `ParseError`, `SessionExpiredError`, `ExportError`, `ConfigError`
    - Każdy wyjątek ma przypisany `stage` odpowiadający etapowi przepływu
    - _Wymagania: 7.1, 7.3 (czytelne komunikaty błędów z informacją o etapie)_

  - [x] 1.3 Implementacja modeli danych (`src/models.py`)
    - Zdefiniować `@dataclass` dla: `AppConfig`, `Character`, `SaleEntry`, `PaginationInfo`, `ExecutionStats`
    - `SaleEntry` musi zawierać pole `extra_fields: dict[str, str]` na dodatkowe kolumny
    - `ExecutionStats` musi zawierać pola: `characters_found`, `pages_processed`, `entries_collected`, `csv_filepath`, `status`, `error_stage`
    - _Wymagania: 3.4, 3.5, 4.5, 4.6, 6.1–6.6_

- [x] 2. Moduł konfiguracji
  - [x] 2.1 Implementacja ładowania i walidacji konfiguracji (`src/config.py`)
    - Zaimplementować funkcję `load_config(config_path: Path) -> AppConfig`
    - Używać `tomllib` (Python 3.11+) do parsowania pliku TOML
    - Walidować obecność wymaganych pól: `username`, `password`, `pin`, `output.directory`
    - Walidować że `pin` składa się z dokładnie 5 znaków
    - Walidować istnienie folderu wyjściowego (`output.directory`)
    - Rzucać `ConfigError` z czytelnym komunikatem przy brakujących polach lub nieistniejącym folderze
    - Obsługiwać wartości domyślne: `ucp_url`, `timeout_ms`, `page_load_delay_ms`
    - _Wymagania: 8.1, 8.2, 8.3, 8.4, 1.4_

  - [ ]* 2.2 Testy property-based dla walidacji konfiguracji
    - **Property 10: Walidacja konfiguracji wykrywa brakujące pola**
    - Generować losowe konfiguracje TOML z brakującymi wymaganymi polami
    - Weryfikować że `load_config` rzuca `ConfigError` ze wskazaniem brakującego pola
    - **Waliduje: Wymagania 8.3**

  - [ ]* 2.3 Testy jednostkowe dla modułu konfiguracji
    - Testować poprawne ładowanie pełnej konfiguracji
    - Testować wartości domyślne gdy sekcja `[scraper]` jest pominięta
    - Testować błędy: brak pliku, puste pola, nieistniejący folder
    - _Wymagania: 8.1, 8.2, 8.3, 8.4_

- [x] 3. Moduł uwierzytelnienia
  - [x] 3.1 Implementacja logowania do UCP (`src/auth.py`)
    - Zaimplementować `login(page: Page, config: AppConfig) -> None`
    - Zaimplementować `verify_logged_in(page: Page) -> bool`
    - Zamknąć cookie consent banner (`#cok_accept`) jeśli widoczny
    - Kliknąć przycisk rozwijający formularz (`button.btn-success.dropdown-toggle`)
    - Wypełnić pola: `input[name='login']`, `input[name='pass']`, `input[name='_pin']`
    - Kliknąć submit (`button[type='submit'].btn-success`)
    - Weryfikować sukces: brak formularza logowania + obecność elementów zalogowanego stanu
    - Rzucać `AuthError` jeśli formularz nadal widoczny lub komunikat błędu
    - Stosować `timeout_ms` z konfiguracji
    - _Wymagania: 1.1, 1.2, 1.3_

- [x] 4. Moduł wykrywania postaci
  - [x] 4.1 Implementacja wykrywania postaci (`src/characters.py`)
    - Zaimplementować `detect_characters(page: Page) -> list[Character]`
    - Szukać powtarzalnych elementów DOM reprezentujących panele postaci
    - Ekstrakcja nazwy postaci z tekstu panelu
    - Zapis selektora CSS do panelu (do późniejszego użycia przez scraper)
    - Rzucać `CharacterDetectionError` jeśli brak postaci
    - _Wymagania: 2.1, 2.2, 2.4_

  - [ ]* 4.2 Testy property-based dla wykrywania postaci
    - **Property 1: Kompletność wykrywania postaci**
    - Generować losowy HTML z N panelami postaci (N ≥ 1)
    - Weryfikować że `detect_characters` zwraca dokładnie N obiektów z unikalnymi, niepustymi nazwami
    - **Waliduje: Wymagania 2.1, 2.2**

- [x] 5. Punkt kontrolny — Weryfikacja fundamentów
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Moduł scrapera — parsowanie tabel i paginacja
  - [x] 6.1 Implementacja parsowania informacji o paginacji (`src/scraper.py` — część 1)
    - Zaimplementować `parse_pagination_info(text: str) -> PaginationInfo`
    - Parsować format: "Pozycje od X do Y z Z łącznie"
    - Rzucać `ParseError` jeśli format nierozpoznany
    - Zaimplementować `parse_table_headers(table_element) -> list[str]`
    - Zaimplementować `parse_table_row(row_element, headers: list[str], character_name: str) -> SaleEntry`
    - Mapować znane kolumny na dedykowane pola, resztę na `extra_fields`
    - _Wymagania: 3.3, 3.4, 3.5_

  - [ ]* 6.2 Testy property-based dla parsowania paginacji
    - **Property 3: Parsowanie informacji o paginacji**
    - Generować losowe trójki (X, Y, Z) gdzie 1 ≤ X ≤ Y ≤ Z
    - Weryfikować poprawność parsowania stringa "Pozycje od X do Y z Z łącznie"
    - **Waliduje: Wymagania 3.3**

  - [ ]* 6.3 Testy property-based dla parsowania wierszy tabeli
    - **Property 5: Kompletność parsowania wierszy**
    - Generować losowe wiersze HTML z K ≥ 5 kolumnami
    - Weryfikować że `parse_table_row` ekstrahuje wartości dla wszystkich K kolumn
    - **Waliduje: Wymagania 3.4, 3.5**

  - [x] 6.4 Implementacja logiki pobierania logów z paginacją (`src/scraper.py` — część 2)
    - Zaimplementować `scrape_sales_logs(page: Page, character: Character, config: AppConfig) -> list[SaleEntry]`
    - Otwierać modal "Logi sprzedaży" dla postaci
    - Iterować przez strony: parsować wiersze → kliknąć "Następna" → powtarzać
    - Walidować kompletność: `len(collected) == PaginationInfo.total`
    - Wykrywać wygaśnięcie sesji (formularz logowania po kliknięciu)
    - Obsługiwać timeout z retry (1 próba ponowna)
    - Zamknąć modal po zakończeniu
    - _Wymagania: 3.1, 3.2, 3.3, 3.6, 7.2_

  - [ ]* 6.5 Testy property-based dla kompletności paginacji
    - **Property 4: Kompletność paginacji**
    - Generować dane rozłożone na ceil(Z/10) stronach
    - Mockować interakcje z przeglądarką
    - Weryfikować że scraper zbiera dokładnie Z wpisów
    - **Waliduje: Wymagania 3.1, 3.2**

- [x] 7. Moduł eksportu CSV
  - [x] 7.1 Implementacja eksportu do CSV (`src/csv_export.py`)
    - Zaimplementować `export_to_csv(entries: list[SaleEntry], output_dir: Path) -> Path`
    - Zaimplementować `generate_filename() -> str` (format: `sales_log_YYYY-MM-DD_HH-MM-SS.csv`)
    - Zaimplementować `build_csv_headers(entries: list[SaleEntry]) -> list[str]`
    - Kolumny stałe: Character, Nazwa przedmiotu, Ilość, Cena, Typ ceny, Data + dynamiczne z `extra_fields`
    - Kodowanie: UTF-8 z BOM (`utf-8-sig`)
    - Separator: `,` (standardowy)
    - Cytowanie pól zawierających separator, cudzysłów lub nową linię
    - Rzucać `ExportError` przy problemach z zapisem
    - _Wymagania: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

  - [ ]* 7.2 Testy property-based dla round-trip CSV
    - **Property 6: Round-trip CSV — dane wejściowe = dane wyjściowe**
    - Generować losowe listy `SaleEntry` z różnymi postaciami
    - Eksportować do CSV, odczytać i porównać z oryginałem
    - **Waliduje: Wymagania 4.1, 4.5, 4.6, 4.7**

  - [ ]* 7.3 Testy property-based dla zachowania Unicode w CSV
    - **Property 7: Zachowanie znaków Unicode w CSV**
    - Generować `SaleEntry` z polskimi znakami, emoji, znakami specjalnymi
    - Eksportować i odczytać — weryfikować identyczność
    - **Waliduje: Wymagania 4.3**

- [x] 8. Moduł raportu
  - [x] 8.1 Implementacja raportu zakończenia (`src/report.py`)
    - Zaimplementować `format_report(stats: ExecutionStats) -> str`
    - Zaimplementować `print_report(stats: ExecutionStats) -> None`
    - Format raportu: ramka z polami Status, Postaci wykrytych, Stron przetworzonych, Wpisów pobranych, Plik CSV
    - Obsługiwać zarówno scenariusz sukcesu jak i błędu
    - Przy błędzie: zawrzeć etap i opis błędu
    - _Wymagania: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 8.2 Testy property-based dla kompletności raportu
    - **Property 8: Kompletność raportu zakończenia**
    - Generować losowe `ExecutionStats` (sukces i błąd)
    - Weryfikować że `format_report` zawiera wszystkie wymagane pola
    - **Waliduje: Wymagania 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

  - [ ]* 8.3 Testy property-based dla identyfikacji etapu błędu
    - **Property 9: Identyfikacja etapu błędu**
    - Generować losowe `ScraperError` z różnymi wartościami `stage`
    - Weryfikować że komunikat błędu zawiera informację o etapie
    - **Waliduje: Wymagania 7.1**

- [x] 9. Punkt kontrolny — Weryfikacja modułów
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Orkiestracja i punkt wejścia
  - [x] 10.1 Implementacja głównej funkcji orkiestrującej (`src/main.py`)
    - Zaimplementować `main() -> int` — zwraca exit code
    - Przepływ: load_config → login → detect_characters → scrape_sales_logs (pętla) → export_to_csv → print_report
    - Łapać wszystkie `ScraperError` na najwyższym poziomie i tłumaczyć na czytelne komunikaty + raport
    - Obsługiwać nieoczekiwane wyjątki: generyczny raport błędu
    - Zbierać statystyki (`ExecutionStats`) w trakcie wykonania
    - Uruchamiać Playwright: `sync_playwright()`, `browser.new_page()`
    - Zapewnić zamknięcie przeglądarki w bloku `finally`
    - _Wymagania: 5.1, 5.4, 2.3, 7.1, 7.3_

  - [x] 10.2 Utworzenie skryptu uruchomieniowego (`main.py` w katalogu głównym)
    - Utworzyć plik `main.py` z blokiem `if __name__ == "__main__"`
    - Wywołać `sys.exit(main())` dla poprawnych kodów wyjścia
    - _Wymagania: 5.2, 5.3, 5.4_

  - [ ]* 10.3 Testy property-based dla kompletności przetwarzania postaci
    - **Property 2: Kompletność przetwarzania postaci**
    - Generować losowe listy postaci (1–10)
    - Mockować `scrape_sales_logs` i weryfikować że wywoływany dla każdej postaci
    - **Waliduje: Wymagania 2.3**

- [x] 11. Punkt kontrolny końcowy
  - Ensure all tests pass, ask the user if questions arise.

## Uwagi

- Zadania oznaczone `*` są opcjonalne i mogą zostać pominięte dla szybszego MVP
- Każde zadanie odwołuje się do konkretnych wymagań w celu śledzenia pokrycia
- Punkty kontrolne zapewniają inkrementalną walidację
- Testy property-based walidują uniwersalne właściwości poprawności z dokumentu projektowego
- Testy jednostkowe walidują konkretne przykłady i przypadki brzegowe
- Projekt wymaga Python 3.11+ (natywny `tomllib`)
- Wszystkie moduły operują na sync API Playwright

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3"] },
    { "id": 2, "tasks": ["2.1", "3.1", "4.1"] },
    { "id": 3, "tasks": ["2.2", "2.3", "4.2", "6.1"] },
    { "id": 4, "tasks": ["6.2", "6.3", "6.4", "7.1", "8.1"] },
    { "id": 5, "tasks": ["6.5", "7.2", "7.3", "8.2", "8.3"] },
    { "id": 6, "tasks": ["10.1"] },
    { "id": 7, "tasks": ["10.2", "10.3"] }
  ]
}
```



