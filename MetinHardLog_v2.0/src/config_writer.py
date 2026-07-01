from __future__ import annotations

import tomllib
from pathlib import Path


def _esc(value: str) -> str:
    """Escapuje znaki specjalne dla wartosci tekstowej TOML."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def save_credentials(
    config_path: Path,
    username: str,
    password: str,
    pin: str,
    output_dir: str,
    show_browser: bool,
) -> None:
    """Zapisuje pelny plik config.toml na podstawie danych z formularza GUI.

    Zachowuje juz wykryte postacie ([characters]) oraz parametry scrapera
    ([scraper]), jesli plik juz istnieje - formularz konfiguracji nie
    powinien ich kasowac.
    """
    postacie = ["null", "null", "null", "null"]
    timeout_ms = 30000
    page_load_delay_ms = 1000

    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                existing = tomllib.load(f)
            chars = existing.get("characters", {})
            postacie = [chars.get(f"postac_{i}", "null") for i in range(1, 5)]
            scraper = existing.get("scraper", {})
            timeout_ms = scraper.get("timeout_ms", timeout_ms)
            page_load_delay_ms = scraper.get("page_load_delay_ms", page_load_delay_ms)
        except (tomllib.TOMLDecodeError, OSError):
            pass

    lines = [
        "[credentials]",
        f'username = "{_esc(username)}"',
        f'password = "{_esc(password)}"',
        f'pin = "{_esc(pin)}"',
        "",
        "[characters]",
    ]
    for i, nazwa in enumerate(postacie, 1):
        lines.append(f'postac_{i} = "{_esc(nazwa)}"')
    lines += [
        "",
        "[output]",
        f'directory = "{_esc(output_dir)}"',
        "",
        "[scraper]",
        f"timeout_ms = {timeout_ms}",
        f"page_load_delay_ms = {page_load_delay_ms}",
        "",
        "[ui]",
        f"show_browser = {str(show_browser).lower()}",
        "",
    ]
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def update_characters_in_config(config_path: Path, detected_names: list) -> None:
    """Aktualizuje sekcje [characters] w config.toml."""
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    new_lines = []
    in_chars = False
    for line in content:
        s = line.strip()
        if s == '[characters]':
            in_chars = True
            new_lines.append(line)
            for i in range(4):
                nm = detected_names[i] if i < len(detected_names) else 'null'
                new_lines.append(f'postac_{i+1} = "{nm}"\n')
            continue
        if in_chars and s.startswith('postac_'):
            continue
        if in_chars and s.startswith('[') and s != '[characters]':
            in_chars = False
        new_lines.append(line)
    with open(config_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
