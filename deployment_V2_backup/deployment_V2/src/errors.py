"""Hierarchia wyjątków scrapera UCP.

Każdy wyjątek posiada pole `stage` identyfikujące etap przepływu,
na którym wystąpił błąd: "config", "login", "characters", "scraping", "export".
"""


class ScraperError(Exception):
    """Bazowy błąd scrapera z identyfikacją etapu."""

    stage: str = "unknown"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f"[{self.stage}] {message}")


class AuthError(ScraperError):
    """Błąd uwierzytelnienia w panelu UCP."""

    stage = "login"


class CharacterDetectionError(ScraperError):
    """Błąd wykrywania postaci na koncie."""

    stage = "characters"


class PaginationError(ScraperError):
    """Błąd nawigacji między stronami logów."""

    stage = "scraping"


class ParseError(ScraperError):
    """Błąd parsowania danych z tabeli lub strony."""

    stage = "scraping"


class SessionExpiredError(ScraperError):
    """Sesja UCP wygasła podczas pobierania danych."""

    stage = "scraping"


class ExportError(ScraperError):
    """Błąd eksportu danych do pliku CSV."""

    stage = "export"


class ConfigError(ScraperError):
    """Błąd konfiguracji programu."""

    stage = "config"
