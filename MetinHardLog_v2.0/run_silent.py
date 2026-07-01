"""Uruchomienie METIN HARD LOG bez GUI - do Harmonogramu Zadan Windows.

Nie pokazuje zadnych okien wyboru postaci (character_selector=None), wiec
pobiera WSZYSTKIE wykryte postacie do jednego wspolnego pliku XLSX -
dokladnie tak jak dawny tryb CLI. Nie nadaje sie do uruchamiania w tle
bez zalogowanego uzytkownika: serwer UCP blokuje tryb headless
Playwright, wiec przegladarka i tak musi sie faktycznie wyswietlic
(patrz config.toml -> [ui] show_browser).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Wymuszamy katalog roboczy = folder programu, niezaleznie od tego skad
# Harmonogram Zadan faktycznie uruchamia ten skrypt - config.toml/logs/
# output sa odczytywane sciezkami wzglednymi.
os.chdir(Path(__file__).resolve().parent)

import main  # noqa: E402


if __name__ == "__main__":
    sys.exit(main.main())
