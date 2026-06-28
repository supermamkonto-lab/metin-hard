# Workflow implementacji

## Cykl życia Task

```
Task → Implementacja → Test → Raport → Review → Decyzja Master Admin → Kolejny Task
```

Każdy krok jest obowiązkowy. Nie wolno pomijać etapów.

## Zasady implementacji

1. Korzystaj wyłącznie z informacji zawartych w Design.
2. Nie wymyślaj selektorów CSS — używaj sekcji "Selektory UCP" z Design.
3. Nie dodawaj funkcjonalności spoza zakresu aktualnego Task.
4. Nie refaktoryzuj kodu spoza zakresu aktualnego Task.
5. Nie zmieniaj publicznych interfejsów modułów bez CR.

## Realizacja zadań

- Jeden Task naraz.
- Sekwencyjna realizacja zgodna z kolejnością w tasks.md.
- Po zakończeniu Task — raport + Review.
- Po Review — zatrzymanie i oczekiwanie na decyzję Master Admin.

## Kontrola jakości po każdym Task

1. Uruchom import wszystkich modułów.
2. Uruchom `python -m pytest tests/ -v`.
3. Zweryfikuj brak regresji.
4. Przygotuj raport implementacji.

## Czego nie robić

- Nie rozpoczynaj kolejnego Task bez akceptacji.
- Nie wykonuj refaktoryzacji niezwiązanej z aktualnym Task.
- Nie dodawaj bibliotek bez akceptacji.
- Nie zmieniaj architektury bez CR.
