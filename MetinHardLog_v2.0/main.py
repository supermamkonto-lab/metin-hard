"""METIN HARD LOG -- Eksporter Logow Sprzedazy v2.0

Profesjonalny interfejs uzydkownika.
Wyswietla kazdy etap dzialania programu.
Kazde uruchomienie jest dokumentowane w pliku logu.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from src.config import load_config
from src.auth import login
from src.characters import detect_characters
from src.scraper import scrape_sales_logs
from src.errors import ScraperError
from src.export import export_xlsx, generate_filename, generate_combined_filename
from src.models import AppConfig, Character, SaleEntry

# Wywolywane po wykryciu postaci, zanim rozpocznie sie pobieranie logow.
# Otrzymuje pelna liste wykrytych postaci, zwraca:
#   - (wybrane_postacie, combined) - combined=True: jeden wspolny plik XLSX,
#     combined=False: osobny plik XLSX dla kazdej postaci,
#   - None - uzytkownik przerwal (wyjscie), program konczy sie bez pobierania.
# Gdy None (tryb CLI bez GUI), pobierane sa wszystkie wykryte postacie do
# jednego wspolnego pliku - zachowanie sprzed dodania wyboru w GUI.
CharacterSelector = Callable[[list[Character]], "tuple[list[Character], bool] | None"]

# Kod wyjscia gdy uzytkownik przerwal operacje wyborem "Wyjscie" w GUI.
EXIT_CODE_CANCELLED = 2

# Wywolywane po udanym eksporcie (jesli sa jakiekolwiek dane) z pelna lista
# pobranych wpisow i lista utworzonych plikow - np. do pokazania podsumowania
# sprzedazy w GUI. Opcjonalne, nieuzywane w trybie CLI.
ResultCallback = Callable[[list[SaleEntry], list[Path]], None]


class Logger:
    """Logger zapisujacy kazdy komunikat do pliku i na ekran."""

    def __init__(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.log_path = log_dir / f"log_{timestamp}.txt"
        self._file = open(self.log_path, "w", encoding="utf-8")
        self._write_header()

    def _write_header(self):
        self._file.write("=" * 60 + "\n")
        self._file.write("METIN HARD LOG - Log uruchomienia\n")
        self._file.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._file.write("=" * 60 + "\n\n")
        self._file.flush()

    def log(self, message: str):
        """Zapisuje komunikat do pliku z timestampem i wyswietla na ekranies."""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}"
        print(f" {message}")
        self._file.write(line + "\n")
        self._file.flush()

    def log_error(self, message: str, exc_info: str = ""):
        """Zapisuje blad do pliku i wyswietla na ekranies."""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] BLAD: {message}"
        print(f" BLAD: {message}")
        self._file.write(line + "\n")
        if exc_info:
            self._file.write(exc_info + "\n")
        self._file.flush()

    def log_separator(self):
        sep = "-" * 40
        print(f" {sep}")
        self._file.write(sep + "\n")
        self._file.flush()

    def close(self):
        self._file.write("\n" + "=" * 60 + "\n")
        self._file.write(f"Zakonczono: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self._file.write("=" * 60 + "\n")
        self._file.close()


def print_header():
    print()
    print(" ====================================")
    print(" METIN HARD LOG")
    print(" Eksporter Logow Sprzedazy")
    print(" v2.0")
    print(" ===================================")
    print()


def _group_entries_by_character(entries: list[SaleEntry]) -> dict[str, list[SaleEntry]]:
    """Grupuje wpisy sprzedazy wedlug nazwy postaci, zachowujac kolejnosc."""
    groups: dict[str, list[SaleEntry]] = {}
    for entry in entries:
        groups.setdefault(entry.character, []).append(entry)
    return groups


def main(
    character_selector: CharacterSelector | None = None,
    result_callback: ResultCallback | None = None,
) -> int:
    """Glowna funkcja programu.

    Zwraca kod wyjscia: 0 = sukces, 1 = blad, 2 = przerwano przez uzytkownika
    (wybor "Wyjscie" w oknie wyboru postaci).
    """
    print_header()

    # Uruchomienie logow
    logger = Logger()
    logger.log("Program uruchomiony.")

    # [1/9] Konfiguracja
    logger.log("[1/9] Wczytywanie konfiguracji...")
    try:
        config = load_config(Path("config.toml"))
        logger.log("Konfiguracja wczytana poprawnie.")
    except ScraperError as e:
        logger.log_error(f"Nie udalo sie wczytac konfiguracji: {e}")
        logger.close()
        return 1

    # [2/9] Uruchomienie przegladarki
    logger.log("[2/9] Uruchamianie przegladarki...")
    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=not config.show_browser)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        logger.log("Przegladarka uruchomiona.")
    except Exception as e:
        logger.log_error(f"Nie udalo sie uruchomic przegladarki: {e}", traceback.format_exc())
        logger.close()
        return 1

    try:
        # [3/9] Otwieranie strony
        logger.log("[3/9] Otwieranie strony logowania...")
        page.goto(config.ucp_url, timeout=config.timeout_ms)
        logger.log(f"Strona zaladowana: {page.title()}")

        # [4/9] Logowanie
        logger.log("[4/9] Logowanie do panelu UCP...")
        login(page, config)
        logger.log("Logowanie zakonczone pomyslnie.")

        # [5/9] Wykrywanie postaci
        logger.log("[5/9] Wyszukiwanie postaci...")
        all_characters = detect_characters(page)
        logger.log(f"Znaleziono {len(all_characters)} postaci:")
        for char in all_characters:
            logger.log(f"  * {char.name}")

        # Zapis postaci do config.toml
        from src.config_writer import update_characters_in_config
        detected_names = [char.name for char in all_characters]
        update_characters_in_config(Path("config.toml"), detected_names)
        logger.log(f"Zapisano {len(detected_names)} postaci do config.toml.")

        # [6/9] Wybor postaci do pobrania i trybu eksportu
        logger.log("[6/9] Wybor postaci do pobrania...")
        combined = True
        if character_selector is not None:
            # GUI: uzytkownik wybiera ktore postacie (1-4) pobrac zaznaczajac
            # je "ptaszkiem", albo przerywa cala operacje wyborem "Wyjscie".
            selection = character_selector(all_characters)
            if selection is None:
                logger.log("Uzytkownik przerwal operacje (Wyjscie).")
                logger.close()
                return EXIT_CODE_CANCELLED
            characters, combined = selection
            logger.log(
                f"Wybrano {len(characters)} z {len(all_characters)} postaci: "
                + ", ".join(c.name for c in characters)
            )
            logger.log(
                "Tryb eksportu: "
                + ("jeden wspolny plik XLSX" if combined else "osobny plik XLSX dla kazdej postaci")
            )
        else:
            # CLI bez GUI: zachowanie sprzed dodania interaktywnego wyboru -
            # pobierz wszystkie wykryte postacie (lub te z config.toml, jesli
            # sekcja [characters] zostala recznie skonfigurowana) do jednego
            # wspolnego pliku.
            characters = all_characters
            if config.characters_list:
                filtered = [c for c in characters if c.name in config.characters_list]
                if filtered:
                    characters = filtered

        if not characters:
            logger.log_error("Brak wybranych postaci do pobrania.")
            logger.close()
            return 1

        # [7/9] Pobieranie logow
        logger.log("[7/9] Pobieranie logow sprzedazy\x2e..")
        all_entries: list[SaleEntry] = []

        for char in characters:
            logger.log_separator()
            logger.log(f"Postac: {char.name}")
            try:
                entries = scrape_sales_logs(page, char, config)
                if entries:
                    logger.log(f"Pobrano {len(entries)} rekordow.")
                    all_entries.extend(entries)
                else:
                    logger.log(f"Brak logow sprzedazy dla {char.name}. Przechodze dalej.")
            except ScraperError as e:
                logger.log_error(f"Blad przy pobieraniu logow {char.name}: {e}")
                logger.log("Przechodze do nastepnej postaci.")
            except Exception as e:
                logger.log_error(f"Nieoczekiwany blad przy {char.name}: {e}", traceback.format_exc())
                logger.log("Przechodze do nastepnej postaci.")

        logger.log_separator()
        logger.log(f"Lacznie pobrano: {len(all_entries)} rekordow ze wszystkich postaci.")

        # [8/9] Eksport XLSX
        logger.log("[8/9] Tworzenie pliku/plikow XLSX...")
        created_files: list[Path] = []
        entries_by_character = _group_entries_by_character(all_entries)

        if not all_entries:
            logger.log("Brak danych do eksportu XLSX.")
        elif combined or len(entries_by_character) <= 1:
            # Jeden wspolny plik. Jesli po odsianiu pustych postaci zostaly
            # dane tylko od jednej postaci, plik nazywa sie jej imieniem
            # (czytelniej niz generyczna nazwa zbiorcza).
            if len(entries_by_character) == 1:
                base_name = generate_filename(next(iter(entries_by_character)))
            else:
                base_name = generate_combined_filename()
            xlsx_path = config.output_dir / f"{base_name}.xlsx"
            export_xlsx(all_entries, xlsx_path)
            created_files.append(xlsx_path)
            logger.log(f"Zapisano: {xlsx_path.name} ({len(all_entries)} rekordow)")
        else:
            # Osobny plik XLSX dla kazdej postaci, ktora ma jakiekolwiek dane.
            for char_name, group_entries in entries_by_character.items():
                base_name = generate_filename(char_name)
                xlsx_path = config.output_dir / f"{base_name}.xlsx"
                export_xlsx(group_entries, xlsx_path)
                created_files.append(xlsx_path)
                logger.log(f"Zapisano: {xlsx_path.name} ({len(group_entries)} rekordow)")

        if result_callback is not None:
            try:
                result_callback(all_entries, created_files)
            except Exception:  # noqa: BLE001 - podsumowanie w GUI nie moze wywrocic scrapera
                logger.log_error("Blad podczas generowania podsumowania (pomijam).", traceback.format_exc())

        # [9/9] Raport koncowy
        logger.log("[9/9] Generowanie raportu...")
        print()
        print(" ====================================")
        print(" Operacja zakonczona pomyslnie")
        print(" ====================================")
        print()
        print(f" Postaci: {len(characters)}")
        print(f" Lacznie rekordow: {len(all_entries)}")
        if created_files:
            print()
            print(" Utworzono pliki:")
            for created in created_files:
                print(f"   + {created.name}")
        print()
        print(f" Data eksportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(" Status: SUKCES")
        print(f" Log: {logger.log_path}")
        print(" ====================================")
        print()

        logger.log("Program zakonczony pomyslnie. Status: SUKCES.")
        logger.close()
        return 0

    except ScraperError as e:
        logger.log_error(f"Blad scrapera na etapie: {e.stage} - {e.message}", traceback.format_exc())
        print()
        print(" ====================================")
        print(f" BLAD na etapie: {e.stage}")
        print(f" {e.message}")
        print(f" Log: {logger.log_path}")
        print(" ====================================")
        logger.close()
        return 1

    except Exception as e:
        logger.log_error(f"Nieoczekiwany blad: {e}", traceback.format_exc())
        print()
        print(" ====================================")
        print(" NIEOCZEKIWANY BLAD:")
        print(f" {e}")
        print(f" Log: {logger.log_path}")
        print(" ====================================")
        logger.close()
        return 1

    finally:
        try:
            browser.close()
            pw.stop()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
