"""Testy property-based dla modułu wykrywania postaci.

Property 1: Kompletność wykrywania postaci.
Dla dowolnego N ≥ 1, jeśli strona zawiera N paneli postaci,
detect_characters zwraca dokładnie N obiektów Character
z unikalnymi, niepustymi nazwami.

**Validates: Requirements 2.1, 2.2**
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings, strategies as st

from src.characters import detect_characters
from src.errors import CharacterDetectionError
from src.models import Character


# Strategia generowania nazw postaci (niepuste, unikalne, alfanumeryczne)
char_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=3,
    max_size=20,
)


def _create_mock_page(names: list[str]) -> MagicMock:
    """Tworzy mock obiektu Page z N panelami postaci.

    Symuluje zachowanie page.locator('h5[id^="character-name-"]').all()
    zwracając listę mocków nagłówków z odpowiednimi metodami.
    """
    page = MagicMock()

    mock_headers = []
    for i, name in enumerate(names):
        header = MagicMock()
        # text_content() zwraca nazwę postaci
        header.text_content.return_value = name
        # get_attribute("id") zwraca pełny DOM id w formacie "character-name-XXXXX"
        header.get_attribute.return_value = f"character-name-{10000 + i}"
        mock_headers.append(header)

    # page.locator(...).all() zwraca listę nagłówków
    locator_mock = MagicMock()
    locator_mock.all.return_value = mock_headers
    page.locator.return_value = locator_mock

    return page


@given(
    names=st.lists(
        char_name_strategy,
        min_size=1,
        max_size=10,
        unique=True,
    )
)
@settings(max_examples=100)
def test_detect_characters_returns_all_characters(names: list[str]) -> None:
    """Property 1: Kompletność wykrywania postaci.

    Dla N postaci na stronie, detect_characters zwraca dokładnie N
    obiektów Character z poprawnymi, unikalnymi nazwami.

    **Validates: Requirements 2.1, 2.2**
    """
    page = _create_mock_page(names)

    result = detect_characters(page)

    # Sprawdź liczbę wykrytych postaci
    assert len(result) == len(names), (
        f"Oczekiwano {len(names)} postaci, otrzymano {len(result)}"
    )

    # Sprawdź że wszystkie nazwy są obecne i poprawne
    result_names = [c.name for c in result]
    assert set(result_names) == set(names)

    # Sprawdź że nazwy są niepuste
    assert all(c.name.strip() for c in result)

    # Sprawdź że selektory są niepuste i unikalne
    selectors = [c.panel_selector for c in result]
    assert all(s for s in selectors)
    assert len(set(selectors)) == len(selectors), "Selektory muszą być unikalne"

    # Sprawdź format selektora (zgodny z implementacją)
    for char in result:
        assert char.panel_selector.startswith('a#offshop_logs[data-id="')
        assert char.panel_selector.endswith('"]')


def test_detect_characters_raises_on_empty_page() -> None:
    """Brak postaci → CharacterDetectionError.

    **Validates: Requirements 2.4**
    """
    page = MagicMock()
    locator_mock = MagicMock()
    locator_mock.all.return_value = []
    page.locator.return_value = locator_mock

    with pytest.raises(CharacterDetectionError) as exc_info:
        detect_characters(page)

    assert "postaci" in str(exc_info.value).lower()
