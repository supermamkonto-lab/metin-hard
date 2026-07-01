"""Testy property-based dla modułu konfiguracji.

Property 10: Walidacja konfiguracji wykrywa brakujące pola.
Generujemy losowe konfiguracje TOML z brakującymi wymaganymi polami
i weryfikujemy że load_config rzuca ConfigError ze wskazaniem brakującego elementu.

**Validates: Requirements 8.3**
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from src.config import load_config
from src.errors import ConfigError


# Strategia wyboru, które wymagane pole/sekcję usunąć
REMOVAL_CHOICES = st.sampled_from([
    "credentials_section",    # Cała sekcja [credentials]
    "output_section",         # Cała sekcja [output]
    "username_field",         # Pole username
    "password_field",         # Pole password
    "pin_field",              # Pole pin
    "directory_field",        # Pole directory
])

# Strategia generowania losowych wartości dla pól (nie-puste)
random_string = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P")),
    min_size=3,
    max_size=20,
)


def _build_toml_content(
    *,
    include_credentials: bool = True,
    include_output: bool = True,
    include_username: bool = True,
    include_password: bool = True,
    include_pin: bool = True,
    include_directory: bool = True,
    output_dir: str = ".",
) -> str:
    """Buduje zawartość pliku TOML z opcjonalnym usuwaniem pól/sekcji."""
    lines: list[str] = []

    if include_credentials:
        lines.append("[credentials]")
        if include_username:
            lines.append('username = "testuser"')
        if include_password:
            lines.append('password = "testpass"')
        if include_pin:
            lines.append('pin = "12345"')
        lines.append("")

    if include_output:
        lines.append("[output]")
        if include_directory:
            lines.append(f'directory = "{output_dir}"')
        lines.append("")

    return "\n".join(lines)


@given(removal=REMOVAL_CHOICES)
@settings(max_examples=100)
def test_missing_required_field_raises_config_error(removal: str) -> None:
    """Property 10: Walidacja konfiguracji wykrywa brakujące pola.

    Dla każdego wymaganego pola/sekcji — usunięcie go z konfiguracji
    musi spowodować rzucenie ConfigError z komunikatem wskazującym
    brakujący element.

    **Validates: Requirements 8.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)

        # Budujemy TOML z jednym brakującym elementem
        kwargs: dict = {
            "include_credentials": True,
            "include_output": True,
            "include_username": True,
            "include_password": True,
            "include_pin": True,
            "include_directory": True,
            "output_dir": str(output_dir).replace("\\", "/"),
        }

        # Oczekiwane fragmenty w komunikacie błędu
        expected_fragments: dict[str, list[str]] = {
            "credentials_section": ["credentials"],
            "output_section": ["output"],
            "username_field": ["username"],
            "password_field": ["password"],
            "pin_field": ["pin"],
            "directory_field": ["directory"],
        }

        if removal == "credentials_section":
            kwargs["include_credentials"] = False
        elif removal == "output_section":
            kwargs["include_output"] = False
        elif removal == "username_field":
            kwargs["include_username"] = False
        elif removal == "password_field":
            kwargs["include_password"] = False
        elif removal == "pin_field":
            kwargs["include_pin"] = False
        elif removal == "directory_field":
            kwargs["include_directory"] = False

        toml_content = _build_toml_content(**kwargs)

        # Zapisujemy do tymczasowego pliku
        config_file = output_dir / "config.toml"
        config_file.write_text(toml_content, encoding="utf-8")

        # Weryfikacja: load_config musi rzucić ConfigError
        with pytest.raises(ConfigError) as exc_info:
            load_config(config_file)

        # Komunikat błędu powinien wskazywać brakujący element
        error_msg = str(exc_info.value).lower()
        fragments = expected_fragments[removal]
        assert any(
            frag.lower() in error_msg for frag in fragments
        ), (
            f"ConfigError dla '{removal}' nie zawiera żadnego z oczekiwanych "
            f"fragmentów {fragments}. Otrzymano: {exc_info.value}"
        )
