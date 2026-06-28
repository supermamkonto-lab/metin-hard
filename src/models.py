"""Modele danych scrapera UCP.

Zawiera dataklasy reprezentujące konfigurację, postacie,
wpisy sprzedaży, informacje o paginacji oraz statystyki wykonania.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
    """Konfiguracja aplikacji załadowana z pliku TOML.

    Przechowuje dane logowania, katalog wyjściowy oraz parametry
    sterujące zachowaniem scrapera (timeouty, opóźnienia).
    """

    username: str
    password: str
    pin: str
    output_dir: Path
    ucp_url: str = "https://projekt-hard.eu/ucp"
    timeout_ms: int = 30000
    page_load_delay_ms: int = 1000


@dataclass
class Character:
    """Reprezentacja postaci wykrytej na koncie UCP.

    Przechowuje nazwę postaci oraz selektor CSS do jej panelu,
    umożliwiający późniejszą interakcję z przeglądarką.
    """

    name: str
    panel_selector: str  # Selektor do panelu danej postaci


@dataclass
class SaleEntry:
    """Pojedynczy wpis z logów sprzedaży postaci.

    Zawiera standardowe pola transakcji (przedmiot, ilość, cena, data)
    oraz słownik extra_fields na dodatkowe kolumny obecne w tabeli UCP.
    """

    character: str
    item_name: str
    quantity: str
    price: str
    price_type: str
    date: str
    extra_fields: dict[str, str] = field(default_factory=dict)  # Dodatkowe kolumny


@dataclass
class PaginationInfo:
    """Informacja o paginacji wyekstrahowana z tekstu 'Pozycje od X do Y z Z łącznie'.

    Umożliwia śledzenie postępu przetwarzania stron i weryfikację
    kompletności pobranych danych.
    """

    start: int  # X w "Pozycje od X do Y z Z łącznie"
    end: int  # Y
    total: int  # Z


@dataclass
class ExecutionStats:
    """Statystyki wykonania programu wyświetlane w raporcie końcowym.

    Zbiera informacje o liczbie wykrytych postaci, przetworzonych stron,
    zebranych wpisów oraz statusie zakończenia (sukces lub błąd).
    """

    characters_found: int
    pages_processed: int
    entries_collected: int
    csv_filepath: str | None
    status: str  # "SUCCESS" lub opis błędu
    error_stage: str | None  # Etap na którym wystąpił błąd
