"""Moduł ładowania i walidacji konfiguracji z pliku TOML.

Odpowiada za odczyt pliku config.toml, walidację wymaganych pól
oraz zwrócenie obiektu AppConfig gotowego do użycia przez resztę aplikacji.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from src.errors import ConfigError
from src.models import AppConfig


def load_config(config_path: Path = Path("config.toml")) -> AppConfig:
    """Ładuje i waliduje konfigurację z pliku TOML.

    Args:
        config_path: Ścieżka do pliku konfiguracyjnego. Domyślnie "config.toml".

    Returns:
        AppConfig: Zwalidowany obiekt konfiguracji.

    Raises:
        ConfigError: gdy plik nie istnieje, brakuje pól lub folder wyjściowy nie istnieje.
    """
    if not config_path.exists():
        raise ConfigError(f"Plik konfiguracyjny nie istnieje: {config_path}")

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Błąd parsowania pliku TOML: {e}") from e

    # Walidacja sekcji [credentials]
    credentials = data.get("credentials")
    if credentials is None:
        raise ConfigError("Brak wymaganej sekcji [credentials] w pliku konfiguracyjnym.")

    username = credentials.get("username")
    if username is None:
        raise ConfigError("Brak wymaganego pola 'username' w sekcji [credentials].")
    if not username.strip():
        raise ConfigError("Pole 'username' nie może być puste.")

    password = credentials.get("password")
    if password is None:
        raise ConfigError("Brak wymaganego pola 'password' w sekcji [credentials].")
    if not password.strip():
        raise ConfigError("Pole 'password' nie może być puste.")

    pin = credentials.get("pin")
    if pin is None:
        raise ConfigError("Brak wymaganego pola 'pin' w sekcji [credentials].")
    if not pin.strip():
        raise ConfigError("Pole 'pin' nie może być puste.")
    if len(pin.strip()) != 5:
        raise ConfigError("Pole 'pin' musi mieć dokładnie 5 znaków.")

    # Walidacja sekcji [output]
    output = data.get("output")
    if output is None:
        raise ConfigError("Brak wymaganej sekcji [output] w pliku konfiguracyjnym.")

    directory = output.get("directory")
    if directory is None:
        raise ConfigError("Brak wymaganego pola 'directory' w sekcji [output].")

    output_dir = Path(directory)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # Odczyt sekcji [scraper] z wartościami domyślnymi
    scraper = data.get("scraper", {})
    timeout_ms = scraper.get("timeout_ms", 30000)
    page_load_delay_ms = scraper.get("page_load_delay_ms", 1000)

    ucp_url = credentials.get("ucp_url", "https://projekt-hard.eu/ucp")

    return AppConfig(
        username=username,
        password=password,
        pin=pin.strip(),
        output_dir=output_dir,
        ucp_url=ucp_url,
        timeout_ms=timeout_ms,
        page_load_delay_ms=page_load_delay_ms,
    )
