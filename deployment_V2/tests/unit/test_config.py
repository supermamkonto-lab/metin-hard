"""Testy jednostkowe dla modułu konfiguracji (src/config.py).

Testuje poprawne ładowanie konfiguracji, wartości domyślne
oraz wszystkie scenariusze błędów walidacji.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import load_config
from src.errors import ConfigError


def _write_config(tmp_path: Path, content: str) -> Path:
    """Pomocnik: zapisuje zawartość TOML do pliku w tmp_path."""
    config_file = tmp_path / "config.toml"
    config_file.write_text(content, encoding="utf-8")
    return config_file


def _valid_toml(tmp_path: Path) -> str:
    """Zwraca poprawną zawartość TOML z istniejącym folderem wyjściowym."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return (
        "[credentials]\n"
        'username = "testuser"\n'
        'password = "testpass"\n'
        'pin = "12345"\n'
        "\n"
        "[output]\n"
        f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
    )


class TestLoadConfigSuccess:
    """Testy poprawnego ładowania konfiguracji."""

    def test_full_config_loads_correctly(self, tmp_path: Path) -> None:
        """Poprawne ładowanie pełnej konfiguracji z istniejącym folderem."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "myuser"\n'
            'password = "mypass"\n'
            'pin = "99999"\n'
            'ucp_url = "https://example.com/ucp"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
            "\n"
            "[scraper]\n"
            "timeout_ms = 5000\n"
            "page_load_delay_ms = 500\n"
        )
        config_file = _write_config(tmp_path, content)

        result = load_config(config_file)

        assert result.username == "myuser"
        assert result.password == "mypass"
        assert result.pin == "99999"
        assert result.output_dir == output_dir
        assert result.ucp_url == "https://example.com/ucp"
        assert result.timeout_ms == 5000
        assert result.page_load_delay_ms == 500

    def test_default_values_when_scraper_section_omitted(self, tmp_path: Path) -> None:
        """Wartości domyślne gdy sekcja [scraper] jest pominięta."""
        content = _valid_toml(tmp_path)
        config_file = _write_config(tmp_path, content)

        result = load_config(config_file)

        assert result.timeout_ms == 30000
        assert result.page_load_delay_ms == 1000
        assert result.ucp_url == "https://projekt-hard.eu/ucp"


class TestLoadConfigErrors:
    """Testy scenariuszy błędów konfiguracji."""

    def test_missing_config_file_raises_config_error(self, tmp_path: Path) -> None:
        """Brak pliku config.toml → ConfigError."""
        non_existent = tmp_path / "nonexistent.toml"

        with pytest.raises(ConfigError) as exc_info:
            load_config(non_existent)

        assert "nie istnieje" in str(exc_info.value).lower() or "not" in str(exc_info.value).lower()

    def test_empty_username_raises_config_error(self, tmp_path: Path) -> None:
        """Puste pole username → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "   "\n'
            'password = "testpass"\n'
            'pin = "12345"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "username" in str(exc_info.value).lower()

    def test_empty_password_raises_config_error(self, tmp_path: Path) -> None:
        """Puste pole password → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "  "\n'
            'pin = "12345"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "password" in str(exc_info.value).lower()

    def test_missing_username_field_raises_config_error(self, tmp_path: Path) -> None:
        """Brak pola username → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'password = "testpass"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "username" in str(exc_info.value).lower()

    def test_missing_password_field_raises_config_error(self, tmp_path: Path) -> None:
        """Brak pola password → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "password" in str(exc_info.value).lower()

    def test_missing_credentials_section_raises_config_error(self, tmp_path: Path) -> None:
        """Brak sekcji [credentials] → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "credentials" in str(exc_info.value).lower()

    def test_missing_output_section_raises_config_error(self, tmp_path: Path) -> None:
        """Brak sekcji [output] → ConfigError."""
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "12345"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "output" in str(exc_info.value).lower()

    def test_missing_directory_field_raises_config_error(self, tmp_path: Path) -> None:
        """Brak pola directory → ConfigError."""
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "12345"\n'
            "\n"
            "[output]\n"
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "directory" in str(exc_info.value).lower()

    def test_nonexistent_output_dir_is_created_automatically(self, tmp_path: Path) -> None:
        """Nieistniejący folder wyjściowy → tworzony automatycznie."""
        non_existent_dir = tmp_path / "does_not_exist"
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "12345"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(non_existent_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        result = load_config(config_file)

        assert result.output_dir == non_existent_dir
        assert non_existent_dir.exists()

    def test_invalid_toml_format_raises_config_error(self, tmp_path: Path) -> None:
        """Niepoprawny format TOML → ConfigError."""
        content = "this is not [valid toml ===\n[broken"
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "toml" in str(exc_info.value).lower() or "parsowania" in str(exc_info.value).lower()

    def test_missing_pin_field_raises_config_error(self, tmp_path: Path) -> None:
        """Brak pola pin → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "pin" in str(exc_info.value).lower()

    def test_empty_pin_raises_config_error(self, tmp_path: Path) -> None:
        """Pusty PIN → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "   "\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "pin" in str(exc_info.value).lower()

    def test_pin_too_short_raises_config_error(self, tmp_path: Path) -> None:
        """PIN < 5 znaków → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "123"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "pin" in str(exc_info.value).lower()
        assert "5" in str(exc_info.value)

    def test_pin_too_long_raises_config_error(self, tmp_path: Path) -> None:
        """PIN > 5 znaków → ConfigError."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "1234567"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        assert "pin" in str(exc_info.value).lower()
        assert "5" in str(exc_info.value)

    def test_valid_pin_passes(self, tmp_path: Path) -> None:
        """Poprawny 5-znakowy PIN → brak błędu."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        content = (
            "[credentials]\n"
            'username = "testuser"\n'
            'password = "testpass"\n'
            'pin = "54321"\n'
            "\n"
            "[output]\n"
            f'directory = "{str(output_dir).replace(chr(92), "/")}"\n'
        )
        config_file = _write_config(tmp_path, content)

        result = load_config(config_file)

        assert result.pin == "54321"
