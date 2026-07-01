"""Testy jednostkowe dla modułu scrapera (src/scraper.py).

Testuje parsowanie paginacji, nagłówków i wierszy tabeli
w izolacji od przeglądarki.

**Validates: Requirements 3.3, 3.4, 3.5**
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.scraper import parse_pagination_info, parse_table_row
from src.errors import ParseError
from src.models import PaginationInfo


class TestParsePaginationInfo:
    """Testy parsowania tekstu paginacji."""

    def test_english_format(self) -> None:
        """Format angielski: 'Showing 1 to 10 of 145 entries'."""
        result = parse_pagination_info("Showing 1 to 10 of 145 entries")
        assert result == PaginationInfo(start=1, end=10, total=145)

    def test_polish_format(self) -> None:
        """Format polski: 'Pozycje od 1 do 10 z 145 łącznie'."""
        result = parse_pagination_info("Pozycje od 1 do 10 z 145 łącznie")
        assert result == PaginationInfo(start=1, end=10, total=145)

    def test_middle_page(self) -> None:
        """Strona środkowa: 'Showing 11 to 20 of 145 entries'."""
        result = parse_pagination_info("Showing 11 to 20 of 145 entries")
        assert result == PaginationInfo(start=11, end=20, total=145)

    def test_last_page(self) -> None:
        """Ostatnia strona: 'Showing 141 to 145 of 145 entries'."""
        result = parse_pagination_info("Showing 141 to 145 of 145 entries")
        assert result == PaginationInfo(start=141, end=145, total=145)

    def test_zero_entries(self) -> None:
        """Brak danych: 'Showing 0 to 0 of 0 entries'."""
        result = parse_pagination_info("Showing 0 to 0 of 0 entries")
        assert result == PaginationInfo(start=0, end=0, total=0)

    def test_single_entry(self) -> None:
        """Jeden wpis: 'Showing 1 to 1 of 1 entries'."""
        result = parse_pagination_info("Showing 1 to 1 of 1 entries")
        assert result == PaginationInfo(start=1, end=1, total=1)

    def test_invalid_format_raises_parse_error(self) -> None:
        """Nierozpoznany format → ParseError."""
        with pytest.raises(ParseError):
            parse_pagination_info("Random text without numbers")

    def test_empty_string_raises_parse_error(self) -> None:
        """Pusty string → ParseError."""
        with pytest.raises(ParseError):
            parse_pagination_info("")

    def test_whitespace_handling(self) -> None:
        """Tekst z dodatkowymi spacjami."""
        result = parse_pagination_info("  Showing  1  to  10  of  50  entries  ")
        assert result == PaginationInfo(start=1, end=10, total=50)


class TestParseTableRow:
    """Testy parsowania wierszy tabeli."""

    def _make_row(self, values: list[str]) -> MagicMock:
        """Helper: tworzy mock wiersza tabeli z podanymi wartościami."""
        row = MagicMock()
        cells = []
        for val in values:
            cell = MagicMock()
            cell.text_content.return_value = val
            cells.append(cell)
        locator_mock = MagicMock()
        locator_mock.all.return_value = cells
        row.locator.return_value = locator_mock
        return row

    def test_standard_5_columns(self) -> None:
        """Standardowy wiersz z 5 kolumnami."""
        headers = ["item name", "quantity", "price", "price type", "date"]
        row = self._make_row(["Miecz", "3", "15000", "Yang", "2026-06-20 14:30"])

        result = parse_table_row(row, headers, "MiesoMielone")

        assert result is not None
        assert result.character == "MiesoMielone"
        assert result.item_name == "Miecz"
        assert result.quantity == "3"
        assert result.price == "15000"
        assert result.price_type == "Yang"
        assert result.date == "2026-06-20 14:30"
        assert result.extra_fields == {}

    def test_polish_headers(self) -> None:
        """Polskie nagłówki mapowane poprawnie."""
        headers = ["nazwa przedmiotu", "ilość", "cena", "typ ceny", "data"]
        row = self._make_row(["Płaszcz", "1", "5000", "Yang", "2026-06-15"])

        result = parse_table_row(row, headers, "awsuk")

        assert result is not None
        assert result.item_name == "Płaszcz"
        assert result.quantity == "1"
        assert result.price == "5000"

    def test_extra_columns(self) -> None:
        """Dodatkowe kolumny trafiają do extra_fields."""
        headers = ["item name", "quantity", "price", "price type", "date", "buyer"]
        row = self._make_row(["Miecz", "1", "1000", "Yang", "2026-06-20", "Gracz123"])

        result = parse_table_row(row, headers, "Test")

        assert result is not None
        assert result.extra_fields == {"buyer": "Gracz123"}

    def test_empty_cells_returns_none(self) -> None:
        """Wiersz z samymi pustymi komórkami → None."""
        row = self._make_row(["", "", "", "", ""])
        headers = ["item name", "quantity", "price", "price type", "date"]

        result = parse_table_row(row, headers, "Test")
        assert result is None

    def test_no_cells_returns_none(self) -> None:
        """Wiersz bez komórek → None."""
        row = MagicMock()
        locator_mock = MagicMock()
        locator_mock.all.return_value = []
        row.locator.return_value = locator_mock

        result = parse_table_row(row, ["name"], "Test")
        assert result is None
