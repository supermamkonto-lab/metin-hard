"""Modul ponawiania prob przy przejsciowych bledach sieci (np. timeout)."""

from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry_on_timeout(
    func: Callable[[], T],
    *,
    exceptions: tuple[type[BaseException], ...],
    attempts: int = 3,
    base_delay_s: float = 1.0,
    on_retry: Callable[[int, int, float], None] | None = None,
) -> T:
    """Wywoluje 'func', ponawiajac probe przy wyjatkach z 'exceptions'.

    Opoznienie miedzy probami rosnie wykladniczo (base_delay_s, *2, *4...).
    Jesli ostatnia proba tez zawiedzie, wyjatek jest przepuszczany dalej.

    Args:
        func: Funkcja bezargumentowa do wywolania (np. lambda).
        exceptions: Typy wyjatkow traktowane jako przejsciowe (do ponowienia).
        attempts: Maksymalna liczba prob (>=1).
        base_delay_s: Opoznienie przed druga proba, w sekundach.
        on_retry: Wywolywane przed kazdym ponowieniem z (nieudana_proba,
            wszystkie_proby, opoznienie_s) - np. do wypisania komunikatu.
    """
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except exceptions:
            if attempt == attempts:
                raise
            delay = base_delay_s * (2 ** (attempt - 1))
            if on_retry:
                on_retry(attempt, attempts, delay)
            time.sleep(delay)
    raise AssertionError("nieosiagalne")  # attempts >= 1 gwarantuje return/raise powyzej
