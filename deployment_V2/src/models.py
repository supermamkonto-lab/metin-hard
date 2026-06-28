"""Modele danych scrapera UCP.
Zawiera dataklasy reprezentujace konfiguracje, postacie,
wpisy sprzedazy, informacje o paginacji oraz statystyki wykonania.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppConfig:
 """Konfiguracja aplikacji zaladowana z pliku TOML."""
 username: str
 password: str
 pin: str
 output_dir: Path
 ucp_url: str = "https://projekt-hard.eu/ucp"
 timeout_ms: int = 30000
 page_load_delay_ms: int = 1000
 show_browser: bool = True


@dataclass
class Character:
 """Reprezentacja postaci wykrytej na koncie UCP."""
 name: str
 panel_selector: str


@dataclass
class SaleEntry:
 """Pojedynczy wpis z logow sprzedazy postaci."""
 character: str
 item_name: str
 quantity: str
 price: str
 price_type: str
 date: str
 extra_fields: dict[str, str] = field(default_factory=dict)


@dataclass
class PaginationInfo:
 """Informacja o paginacji."""
 start: int
 end: int
 total: int


@dataclass
class ExecutionStats:
 """Statystyki wykonania programu."""
 characters_found: int
 pages_processed: int
 entries_collected: int
 csv_filepath: str | None
 status: str
 error_stage: str | None
