"""Moduł wykrywania postaci na koncie UCP.

Identyfikuje wszystkie postacie widoczne na stronie głównej panelu
po zalogowaniu i zwraca ich dane potrzebne do dalszego scrapowania.
Selektory potwierdzone eksperymentem integracyjnym nr 2.
"""

from __future__ import annotations

from playwright.sync_api import Page

from src.errors import CharacterDetectionError
from src.models import Character


def detect_characters(page: Page) -> list[Character]:
    """Wykrywa wszystkie postacie na stronie głównej UCP.

    Szuka elementów h5 z ID w formacie 'character-name-{numericID}'.
    Dla każdej postaci buduje selektor umożliwiający późniejsze
    kliknięcie przycisku logów sprzedaży.

    Args:
        page: Instancja strony Playwright (po zalogowaniu).

    Returns:
        Lista obiektów Character z nazwą i selektorem panelu.

    Raises:
        CharacterDetectionError: Gdy nie znaleziono żadnej postaci na stronie.
    """
    # Szukaj nagłówków postaci — selektor potwierdzony eksperymentalnie
    char_headers = page.locator('h5[id^="character-name-"]').all()

    if not char_headers:
        raise CharacterDetectionError(
            "Nie wykryto żadnej postaci na stronie UCP"
        )

    characters: list[Character] = []

    for header in char_headers:
        # Ekstrakcja nazwy postaci
        name = header.text_content()
        if name:
            name = name.strip()

        # Ekstrakcja ID z atrybutu id (format: "character-name-XXXXX")
        dom_id = header.get_attribute("id") or ""
        data_id = dom_id.replace("character-name-", "")

        if not name or not data_id:
            continue

        # Budowa selektora do przycisku "Sales logs" dla tej postaci
        # Używamy data-id bo id="offshop_logs" nie jest unikalny
        panel_selector = f'a#offshop_logs[data-id="{data_id}"]'

        characters.append(Character(name=name, panel_selector=panel_selector))

    if not characters:
        raise CharacterDetectionError(
            "Nie wykryto żadnej postaci na stronie UCP"
        )

    return characters
