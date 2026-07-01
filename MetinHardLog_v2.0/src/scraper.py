"""Moduł scrapera logów sprzedaży z panelu UCP.

Odpowiada za otwieranie modalu logów sprzedaży dla danej postaci,
parsowanie tabeli DataTables, obsługę paginacji i zebranie
wszystkich wpisów SaleEntry.

Selektory i struktura potwierdzone eksperymentami integracyjnymi.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from src.errors import PaginationError, ParseError, SessionExpiredError
from src.models import AppConfig, Character, PaginationInfo, SaleEntry
from src.retry import retry_on_timeout

# Liczba prob klikniecia "nastepna strona" przy przejsciowym timeoucie
_NEXT_PAGE_ATTEMPTS = 3


def _log_retry(attempt: int, attempts: int, delay: float) -> None:
    print(f"        Timeout przy zmianie strony (proba {attempt}/{attempts}), ponawiam za {delay:.0f}s...")

# Selektory potwierdzone eksperymentalnie (AUDYT-004, eksperyment nr 2)
_MODAL_SELECTOR = "div#offshop_logs_modal"
_TABLE_SELECTOR = "#offshop_logs_table"
_TABLE_INFO_SELECTOR = "#offshop_logs_table_info"
_NEXT_BTN_SELECTOR = "#offshop_logs_table_next"
_MODAL_CLOSE_SELECTOR = "#offshop_logs_modal .btn-close, #offshop_logs_modal [data-bs-dismiss='modal']"

# Timeout oczekiwania na elementy modalu (ms)
_MODAL_TIMEOUT_MS = 10000
_TABLE_TIMEOUT_MS = 10000

# Mapowanie nagłówków tabeli na pola SaleEntry (wielojęzyczne)
_COLUMN_MAP = {
    # Angielskie (potwierdzone w Playwright headless)
    "item name": "item_name",
    "name": "item_name",
    "quantity": "quantity",
    "count": "quantity",
    "price": "price",
    "price type": "price_type",
    "date": "date",
    "time": "date",
    # Polskie (potwierdzone na screenshocie Master Admin)
    "nazwa przedmiotu": "item_name",
    "ilość": "quantity",
    "cena": "price",
    "typ ceny": "price_type",
    "data": "date",
}


def scrape_sales_logs(
    page: Page, character: Character, config: AppConfig
) -> list[SaleEntry]:
    """Pobiera wszystkie logi sprzedaży dla danej postaci.

    Otwiera modal logów, parsuje tabelę DataTables z obsługą paginacji
    i zwraca kompletną listę wpisów.

    Args:
        page: Instancja strony Playwright (zalogowana).
        character: Postać, dla której pobieramy logi.
        config: Konfiguracja aplikacji.

    Returns:
        Lista obiektów SaleEntry (może być pusta jeśli postać nie ma logów).

    Raises:
        PaginationError: Gdy nie udało się przejść do następnej strony.
        ParseError: Gdy struktura tabeli jest nieoczekiwana.
        SessionExpiredError: Gdy sesja wygasła podczas pobierania.
    """
    # Krok 1: Kliknij przycisk "Sales logs" dla tej postaci
    _open_sales_modal(page, character, config)

    # Krok 2: Poczekaj na załadowanie tabeli
    _wait_for_table(page)

    # Krok 3: Odczytaj informację o paginacji
    pagination = _read_pagination_info(page)

    # Jeśli brak wpisów — zamknij modal i zwróć pustą listę
    if pagination.total == 0:
        _close_modal(page)
        return []

    # Krok 4: Parsuj nagłówki tabeli
    headers = parse_table_headers(page)

    # Krok 5: Zbieraj wpisy ze wszystkich stron
    all_entries: list[SaleEntry] = []
    page_num = 1

    while True:
        # Parsuj wiersze bieżącej strony
        rows = page.locator(f"{_TABLE_SELECTOR} tbody tr").all()
        for row in rows:
            entry = parse_table_row(row, headers, character.name)
            if entry is not None:
                all_entries.append(entry)

        # Sprawdź czy jest następna strona
        if not _has_next_page(page):
            break

        # Przejdź do następnej strony
        _go_to_next_page(page, config)
        page_num += 1

    # Krok 6: Zamknij modal
    _close_modal(page)

    return all_entries


def parse_pagination_info(text: str) -> PaginationInfo:
    """Parsuje tekst paginacji do obiektu PaginationInfo.

    Obsługuje formaty:
    - "Showing X to Y of Z entries" (angielski DataTables)
    - "Pozycje od X do Y z Z łącznie" (polski)

    Args:
        text: Tekst z elementu informacyjnego paginacji.

    Returns:
        PaginationInfo z wartościami start, end, total.

    Raises:
        ParseError: Gdy format tekstu nie jest rozpoznany.
    """
    text = text.strip()

    # Format angielski: "Showing X to Y of Z entries"
    match = re.search(
        r"Showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)", text, re.IGNORECASE
    )
    if match:
        return PaginationInfo(
            start=int(match.group(1)),
            end=int(match.group(2)),
            total=int(match.group(3)),
        )

    # Format polski: "Pozycje od X do Y z Z łącznie"
    match = re.search(r"od\s+(\d+)\s+do\s+(\d+)\s+z\s+(\d+)", text, re.IGNORECASE)
    if match:
        return PaginationInfo(
            start=int(match.group(1)),
            end=int(match.group(2)),
            total=int(match.group(3)),
        )

    # Format fallback: dowolny tekst z "X to Y of Z"
    match = re.search(r"(\d+)\s+to\s+(\d+)\s+of\s+(\d+)", text, re.IGNORECASE)
    if match:
        return PaginationInfo(
            start=int(match.group(1)),
            end=int(match.group(2)),
            total=int(match.group(3)),
        )

    raise ParseError(f"Nierozpoznany format paginacji: '{text}'")


def parse_table_headers(page: Page) -> list[str]:
    """Wyodrębnia nagłówki kolumn z tabeli logów sprzedaży.

    Args:
        page: Strona z widocznym modalem i tabelą.

    Returns:
        Lista nazw nagłówków kolumn (lowercase, stripped).

    Raises:
        ParseError: Gdy nie znaleziono nagłówków.
    """
    th_elements = page.locator(f"{_TABLE_SELECTOR} thead th").all()

    if not th_elements:
        raise ParseError("Nie znaleziono nagłówków tabeli logów sprzedaży")

    headers = []
    for th in th_elements:
        text = th.text_content() or ""
        headers.append(text.strip().lower())

    return headers


def parse_table_row(
    row_element, headers: list[str], character_name: str
) -> SaleEntry | None:
    """Parsuje pojedynczy wiersz tabeli na obiekt SaleEntry.

    Mapuje kolumny na pola SaleEntry na podstawie nagłówków.
    Nieznane kolumny trafiają do extra_fields.

    Args:
        row_element: Locator wiersza <tr> w tbody.
        headers: Lista nagłówków kolumn (lowercase).
        character_name: Nazwa postaci (do pola character).

    Returns:
        SaleEntry lub None jeśli wiersz jest pusty/nieparsowany.
    """
    cells = row_element.locator("td").all()

    if not cells:
        return None

    # Zbierz wartości komórek
    cell_values = []
    for cell in cells:
        text = cell.text_content() or ""
        cell_values.append(text.strip())

    # Pomijaj puste wiersze lub wiersze "No data"
    if not any(cell_values) or (
        len(cell_values) == 1 and "no data" in cell_values[0].lower()
    ):
        return None

    # Mapuj kolumny na pola SaleEntry
    fields = {
        "item_name": "",
        "quantity": "",
        "price": "",
        "price_type": "",
        "date": "",
    }
    extra_fields: dict[str, str] = {}

    for i, header in enumerate(headers):
        if i >= len(cell_values):
            break

        value = cell_values[i]
        mapped_field = _COLUMN_MAP.get(header)

        if mapped_field and mapped_field in fields:
            fields[mapped_field] = value
        else:
            # Nieznana kolumna → extra_fields
            extra_fields[header] = value

    return SaleEntry(
        character=character_name,
        item_name=fields["item_name"],
        quantity=fields["quantity"],
        price=fields["price"],
        price_type=fields["price_type"],
        date=fields["date"],
        extra_fields=extra_fields,
    )


# --- Funkcje pomocnicze (prywatne) ---


def _open_sales_modal(page: Page, character: Character, config: AppConfig) -> None:
    """Otwiera modal logów sprzedaży dla postaci.

    UCP ma duplikat id="offshop_logs" (jeden per postać), co powoduje
    że jQuery event delegation nie obsługuje poprawnie kliknięcia
    Playwright na inny niż pierwszy element. Dlatego wywołujemy
    AJAX + DataTable + modal programowo, replikując logikę fetchLogs.
    """
    # Pobierz atrybuty data z przycisku postaci
    try:
        btn = page.locator(character.panel_selector)
        btn.wait_for(state="visible", timeout=_MODAL_TIMEOUT_MS)
    except PlaywrightTimeoutError as e:
        raise PaginationError(
            f"Nie znaleziono przycisku logów sprzedaży dla postaci '{character.name}'"
        ) from e

    data_id = btn.get_attribute("data-id") or ""
    data_hash = btn.get_attribute("data-hash") or ""
    data_csfr = btn.get_attribute("data-csfr") or ""

    if not data_id:
        raise PaginationError(
            f"Brak atrybutu data-id na przycisku postaci '{character.name}'"
        )

    # Wywołaj AJAX + DataTable + modal show bezpośrednio przez JS
    # Replikuje logikę fetchLogs z UCP, ale z obsługą błędów
    result = page.evaluate(
        """
        ({dataId, dataHash, dataCsfr}) => {
            return new Promise((resolve) => {
                const url = '/inc/ajax.usr.php';
                const params = {action: 'offshop_logs', id: dataId, hash: dataHash, csfr: dataCsfr};

                $.getJSON(url, params, function(data) {
                    if (!data || !data.success) {
                        resolve({success: false, error: data ? data.message : 'empty response'});
                        return;
                    }

                    try {
                        $('#offshop_logs_table').DataTable({
                            destroy: true,
                            data: data.message,
                            columns: [
                                { data: 'name' },
                                { data: 'count', render: typeof renderNumber !== 'undefined' ? renderNumber : undefined },
                                { data: 'price', render: function(d, type) {
                                    return type === 'display'
                                        ? new Intl.NumberFormat('pl-PL', {style:'decimal', minimumFractionDigits:0}).format(d)
                                        : d;
                                }},
                                { data: 'price_type', render: (d) => d == 0 ? 'Yang' : 'Gold Bar' },
                                { data: 'time', render: typeof renderTime !== 'undefined' ? renderTime : undefined }
                            ],
                            order: [[4, 'desc']],
                            language: { url: '//cdn.datatables.net/plug-ins/1.13.1/i18n/en.json' },
                            responsive: true
                        });
                    } catch(e) {
                        resolve({success: false, error: 'DataTable init error: ' + e.message});
                        return;
                    }

                    $('#offshop_logs_modal').modal('show');
                    resolve({success: true, entries: Array.isArray(data.message) ? data.message.length : 0});
                }).fail(function(jqXHR, textStatus) {
                    // Serwer zwrócił puste body lub błąd parsowania JSON
                    resolve({success: false, error: 'AJAX fail: ' + textStatus, status: jqXHR.status});
                });
            });
        }
        """,
        {"dataId": data_id, "dataHash": data_hash, "dataCsfr": data_csfr},
    )

    if not result.get("success"):
        error_msg = result.get("error", "unknown")
        # Serwer może zwracać puste body dla postaci bez logów offshop
        # W takim przypadku otwórz modal ręcznie z pustą tabelą
        if "AJAX fail" in str(error_msg) or "empty response" in str(error_msg):
            # Fallback: otwórz modal z pustą tabelą
            page.evaluate(
                """
                () => {
                    try {
                        $('#offshop_logs_table').DataTable({
                            destroy: true,
                            data: [],
                            columns: [
                                { data: 'name', title: 'Name' },
                                { data: 'count', title: 'Quantity' },
                                { data: 'price', title: 'Price' },
                                { data: 'price_type', title: 'Price Type' },
                                { data: 'time', title: 'Date' }
                            ]
                        });
                    } catch(e) {}
                    $('#offshop_logs_modal').modal('show');
                }
                """
            )
        else:
            raise PaginationError(
                f"Nie udało się pobrać logów dla postaci '{character.name}': {error_msg}"
            )

    # Poczekaj na pojawienie się modalu
    try:
        page.locator(_MODAL_SELECTOR).wait_for(
            state="visible", timeout=_MODAL_TIMEOUT_MS
        )
    except PlaywrightTimeoutError as e:
        raise PaginationError(
            f"Modal logów sprzedaży nie pojawił się dla postaci '{character.name}'"
        ) from e


def _wait_for_table(page: Page) -> None:
    """Czeka na załadowanie tabeli DataTables w modalu."""
    try:
        page.locator(_TABLE_SELECTOR).wait_for(
            state="visible", timeout=_TABLE_TIMEOUT_MS
        )
    except PlaywrightTimeoutError as e:
        raise ParseError("Tabela logów sprzedaży nie załadowała się") from e

    # Dodatkowe oczekiwanie na DataTables info (sygnał że dane załadowane)
    try:
        page.locator(_TABLE_INFO_SELECTOR).wait_for(
            state="visible", timeout=_TABLE_TIMEOUT_MS
        )
    except PlaywrightTimeoutError:
        # Info może nie być widoczne jeśli brak danych — kontynuujemy
        pass


def _read_pagination_info(page: Page) -> PaginationInfo:
    """Odczytuje informację o paginacji z elementu DataTables info."""
    info_el = page.locator(_TABLE_INFO_SELECTOR)

    if info_el.count() == 0:
        # Brak elementu info — zakładamy 0 wpisów
        return PaginationInfo(start=0, end=0, total=0)

    text = info_el.text_content() or ""
    if not text.strip():
        return PaginationInfo(start=0, end=0, total=0)

    return parse_pagination_info(text)


def _has_next_page(page: Page) -> bool:
    """Sprawdza czy istnieje aktywny przycisk następnej strony."""
    next_btn = page.locator(_NEXT_BTN_SELECTOR)

    if next_btn.count() == 0:
        return False

    # DataTables dodaje klasę "disabled" do nieaktywnego przycisku
    classes = next_btn.get_attribute("class") or ""
    return "disabled" not in classes


def _go_to_next_page(page: Page, config: AppConfig) -> None:
    """Klika przycisk następnej strony i czeka na załadowanie.

    Kliknięcie jest ponawiane (do 3 prób) przy przejściowym timeoucie,
    zanim zgłoszony zostanie PaginationError.
    """
    next_btn = page.locator(_NEXT_BTN_SELECTOR)

    try:
        retry_on_timeout(
            next_btn.click,
            exceptions=(PlaywrightTimeoutError,),
            attempts=_NEXT_PAGE_ATTEMPTS,
            on_retry=_log_retry,
        )
    except PlaywrightTimeoutError as e:
        raise PaginationError(
            f"Nie udało się kliknąć przycisku następnej strony (po {_NEXT_PAGE_ATTEMPTS} próbach)"
        ) from e

    # Poczekaj na załadowanie nowych danych
    time.sleep(config.page_load_delay_ms / 1000)

    # Sprawdź czy sesja nie wygasła (formularz logowania widoczny)
    if page.locator('input[name="pass"]').is_visible():
        raise SessionExpiredError(
            "Sesja UCP wygasła podczas pobierania logów sprzedaży"
        )


def _close_modal(page: Page) -> None:
    """Zamyka modal logów sprzedaży i czeka na jego zniknięcie."""
    close_btn = page.locator(_MODAL_CLOSE_SELECTOR)
    if close_btn.count() > 0:
        close_btn.first.click()
    else:
        page.keyboard.press("Escape")

    # Poczekaj aż modal zniknie — Bootstrap animacja fade
    try:
        page.locator(_MODAL_SELECTOR).wait_for(state="hidden", timeout=5000)
    except Exception:
        # Fallback: krótkie oczekiwanie
        time.sleep(1)
