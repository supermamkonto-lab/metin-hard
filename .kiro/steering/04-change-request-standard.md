# Standard Change Request

## Kiedy tworzyć CR

- Rozbieżność między Design a rzeczywistością (np. wynik eksperymentu).
- Odkrycie brakującego wymagania.
- Konieczność zmiany zaimplementowanego modułu.

## Zakres CR

- CR dotyczy wyłącznie przywrócenia zgodności między dokumentacją a implementacją.
- CR nie zmienia architektury projektu.
- CR nie dodaje nowych funkcjonalności.

## 12 sekcji raportu CR

1. Cel CR
2. Zmodyfikowane pliki
3. Zakres zmian (dla każdego pliku: co dodane, usunięte, zmodyfikowane, dlaczego)
4. Wyniki testów
5. Wyniki importów
6. Macierz zgodności z Design (obowiązkowa tabela)
7. Ocena wpływu na architekturę
8. Odstępstwa od Design
9. Problemy napotkane podczas implementacji
10. Wpływ na kolejne Taski
11. Gotowość projektu
12. Zakończenie

## Macierz zgodności z Design

Obowiązkowa tabela w każdym CR:

| Element Design | Zweryfikowano | Wynik |
|----------------|---------------|-------|
| Model danych | ✓ | zgodny |
| Strategia logowania | ✓ | zgodna |
| Interfejs API | ✓ | zgodny |

## Formuła zamykająca

> „CR-XXX zakończony. Review zakończony. Oczekuję decyzji Master Admin dotyczącej dalszych prac."
