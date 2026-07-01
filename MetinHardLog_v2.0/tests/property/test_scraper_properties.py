"""Testy property-based dla modułu scrapera.

Property 3: Parsowanie informacji o paginacji.
Property 5: Kompletność parsowania wierszy.

**Validates: Requirements 3.3, 3.4, 3.5**
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from hypothesis import given, settings, strategies as st

from src.scraper import parse_pagination_info, parse_table_row
from src.errors import ParseError
from src.models import PaginationInfo, SaleEntry


# --- Property 3: Parsowanie informacji o paginacji ---


@st.composite
def pagination_values(draw):
    """Generuje trójkę (x, y, z) spełniającą x ≤ y ≤ z."""
    x = draw(st.integers(min_value=1, max_value=10000))
    y = draw(st.integers(min_value=x, max_value=10000))
    z = draw(st.integers(min_value=y, max_value=100000))
    return x, y, z


@given(data=pagination_values())
@settings(max_examples=100)
def test_pagination_info_parsing_english(data: tuple[int, int, int]) -> None:
    """Property 3: Parsowanie paginacji format angielski.

    Dla dowolnych X, Y, Z gdzie X ≤ Y ≤ Z, parse_pagination_info
    na stringu "Showing X to Y of Z entries" zwraca PaginationInfo(X, Y, Z).

    **Validates: Requirements 3.3**
    """
    x, y, z = data

    text = f"Showing {x} to {y} of {z} entries"
    result = parse_pagination_info(text)

    assert result.start == x
    assert result.end == y
    assert result.total == z


@given(data=pagination_values())
@settings(max_examples=100)
def test_pagination_info_parsing_polish(data: tuple[int, int, int]) -> None:
    """Property 3: Parsowanie paginacji format polski.

    Dla dowolnych X, Y, Z gdzie X ≤ Y ≤ Z, parse_pagination_info
    na stringu "Pozycje od X do Y z Z łącznie" zwraca PaginationInfo(X, Y, Z).

    **Validates: Requirements 3.3**
    """
    x, y, z = data

    text = f"Pozycje od {x} do {y} z {z} łącznie"
    result = parse_pagination_info(text)

    assert result.start == x
    assert result.end == y
    assert result.total == z


def test_pagination_info_zero_entries() -> None:
    """Parsowanie 'Showing 0 to 0 of 0 entries' → PaginationInfo(0, 0, 0)."""
    result = parse_pagination_info("Showing 0 to 0 of 0 entries")
    assert result == PaginationInfo(start=0, end=0, total=0)


def test_pagination_info_invalid_format_raises() -> None:
    """Nierozpoznany format → ParseError."""
    with pytest.raises(ParseError):
        parse_pagination_info("This is not pagination text")


# --- Property 5: Kompletność parsowania wierszy ---


# Strategia generowania nazw kolumn
known_headers = ["item name", "quantity", "price", "price type", "date"]
extra_header_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L",)),
    min_size=3,
    max_size=15,
)


@given(
    extra_count=st.integers(min_value=0, max_value=5),
    values=st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "N", "P"))),
        min_size=5,
        max_size=10,
    ),
)
@settings(max_examples=100)
def test_parse_table_row_extracts_all_columns(extra_count: int, values: list[str]) -> None:
    """Property 5: Kompletność parsowania wierszy.

    Dla wiersza z K ≥ 5 kolumnami, parse_table_row ekstrahuje
    wartości dla wszystkich K kolumn — znane w dedykowanych polach,
    dodatkowe w extra_fields.

    **Validates: Requirements 3.4, 3.5**
    """
    # Buduj nagłówki: 5 znanych + N dodatkowych
    extra_headers = [f"extra_{i}" for i in range(extra_count)]
    headers = known_headers + extra_headers
    total_cols = len(headers)

    # Dopasuj wartości do liczby kolumn
    cell_values = values[:total_cols]
    while len(cell_values) < total_cols:
        cell_values.append("filler")

    # Mock wiersza tabeli
    row = MagicMock()
    cells = []
    for val in cell_values:
        cell_mock = MagicMock()
        cell_mock.text_content.return_value = val
        cells.append(cell_mock)

    locator_mock = MagicMock()
    locator_mock.all.return_value = cells
    row.locator.return_value = locator_mock

    # Parsuj
    result = parse_table_row(row, headers, "TestCharacter")

    assert result is not None
    assert result.character == "TestCharacter"

    # Pola dedykowane muszą być wypełnione
    assert result.item_name == cell_values[0]
    assert result.quantity == cell_values[1]
    assert result.price == cell_values[2]
    assert result.price_type == cell_values[3]
    assert result.date == cell_values[4]

    # Dodatkowe kolumny w extra_fields
    assert len(result.extra_fields) == extra_count
    for i, eh in enumerate(extra_headers):
        assert eh in result.extra_fields
        assert result.extra_fields[eh] == cell_values[5 + i]


def test_parse_table_row_empty_row_returns_none() -> None:
    """Pusty wiersz → None."""
    row = MagicMock()
    locator_mock = MagicMock()
    locator_mock.all.return_value = []
    row.locator.return_value = locator_mock

    result = parse_table_row(row, ["name", "count", "price", "price_type", "date"], "Test")
    assert result is None


def test_parse_table_row_no_data_returns_none() -> None:
    """Wiersz 'No data available' → None."""
    row = MagicMock()
    cell = MagicMock()
    cell.text_content.return_value = "No data available in table"
    locator_mock = MagicMock()
    locator_mock.all.return_value = [cell]
    row.locator.return_value = locator_mock

    result = parse_table_row(row, ["name"], "Test")
    assert result is None
