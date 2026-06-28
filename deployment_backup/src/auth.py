"""Moduł uwierzytelnienia w panelu UCP.

Odpowiada za logowanie do panelu UCP serwera Metin2 HARD
oraz weryfikację, czy użytkownik jest w stanie zalogowanym.
Selektory CSS zostały potwierdzone eksperymentem integracyjnym.
"""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from src.errors import AuthError
from src.models import AppConfig

# Timeout oczekiwania na elementy formularza i po zalogowaniu (ms)
_ELEMENT_TIMEOUT_MS = 10000


def login(page: Page, config: AppConfig) -> None:
    """Loguje się do panelu UCP.

    Workflow zgodny z rzeczywistym interfejsem panelu:
    1. Nawigacja do UCP
    2. Zamknięcie cookie consent (jeśli widoczny)
    3. Rozwinięcie formularza logowania (dropdown)
    4. Wypełnienie pól: login, hasło, PIN
    5. Wysłanie formularza
    6. Weryfikacja zalogowania

    Args:
        page: Instancja strony Playwright.
        config: Konfiguracja aplikacji z danymi logowania.

    Raises:
        AuthError: Gdy panel jest niedostępny, dane logowania są nieprawidłowe
                   lub wystąpił inny błąd podczas procesu logowania.
    """
    # Krok 1: Nawigacja do panelu UCP
    try:
        page.goto(config.ucp_url, timeout=config.timeout_ms)
    except PlaywrightTimeoutError as e:
        raise AuthError(
            "Panel UCP jest niedostępny: timeout połączenia"
        ) from e

    # Krok 2: Zamknięcie cookie consent (jeśli widoczny)
    cookie_btn = page.locator("#cok_accept")
    if cookie_btn.is_visible():
        cookie_btn.click()

    # Krok 3: Kliknięcie przycisku rozwijającego formularz logowania
    try:
        dropdown_btn = page.locator("button.dropdown-toggle.btn-success")
        dropdown_btn.wait_for(state="visible", timeout=_ELEMENT_TIMEOUT_MS)
        dropdown_btn.click()
    except PlaywrightTimeoutError as e:
        raise AuthError(
            "Nie znaleziono przycisku otwierającego formularz logowania"
        ) from e

    # Krok 4: Poczekaj na pojawienie się formularza i wypełnij pola
    try:
        login_input = page.locator('input[name="login"]')
        login_input.wait_for(state="visible", timeout=_ELEMENT_TIMEOUT_MS)
        login_input.fill(config.username)

        password_input = page.locator('input[name="pass"]')
        password_input.fill(config.password)

        pin_input = page.locator('input[name="_pin"]')
        pin_input.fill(config.pin)
    except PlaywrightTimeoutError as e:
        raise AuthError(
            "Nie znaleziono pól formularza logowania na stronie UCP"
        ) from e

    # Krok 5: Wysłanie formularza
    try:
        submit_btn = page.locator('button[type="submit"].btn-success')
        submit_btn.click()
    except PlaywrightTimeoutError as e:
        raise AuthError(
            "Nie znaleziono przycisku logowania na stronie UCP"
        ) from e

    # Krok 6: Poczekaj na załadowanie strony po logowaniu
    try:
        page.wait_for_load_state("networkidle", timeout=_ELEMENT_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        pass

    # Krok 7: Weryfikacja sukcesu logowania
    if not verify_logged_in(page):
        raise AuthError(
            "Nieprawidłowe dane logowania — serwer odrzucił uwierzytelnienie"
        )


def verify_logged_in(page: Page) -> bool:
    """Sprawdza czy strona wskazuje na zalogowany stan.

    Strategia negatywno-pozytywna:
    - Negatywna: formularz logowania NIE jest widoczny
    - Pozytywna: obecny jest element charakterystyczny dla stanu zalogowanego
      (potwierdzone eksperymentem integracyjnym)

    Args:
        page: Instancja strony Playwright.

    Returns:
        True jeśli użytkownik jest zalogowany, False w przeciwnym razie.
    """
    # Weryfikacja negatywna: pole hasła z formularza logowania nie powinno być widoczne
    login_form_visible = page.locator('input[name="pass"]').is_visible()
    if login_form_visible:
        return False

    # Weryfikacja pozytywna: szukamy elementów potwierdzonych eksperymentalnie
    # h5[id^="character-name-"] — nagłówki z nazwami postaci (niezależne od języka UI)
    # h2.main-title — nagłówek sekcji "Your characters" / "Twoje postacie"
    logged_in_indicators = page.locator(
        'h5[id^="character-name-"], h2.main-title'
    )

    return logged_in_indicators.count() > 0
