# Uruchomienie programu

## Sposób 1: Skrypt run.ps1 (zalecany)

```powershell
cd C:\ścieżka\do\Metin_HARD
.\deployment\run.ps1
```

## Sposób 2: Bezpośrednie uruchomienie

```powershell
cd C:\ścieżka\do\Metin_HARD
python main.py
```

## Co robi program

1. Loguje się do panelu UCP (https://projekt-hard.eu/ucp)
2. Wykrywa wszystkie postacie na koncie
3. Pobiera logi sprzedaży z każdej postaci
4. Zapisuje wynik do DWÓCH plików w folderze skonfigurowanym w config.toml

## Pliki wynikowe

Program generuje **dwa pliki** przy każdym uruchomieniu:

| Typ | Opis |
|-----|------|
| `.xlsx` | Plik Excel — sformatowany, z auto-fit kolumn, filtrami, freeze panes |
| `.csv` | Plik CSV — separator `;`, kodowanie UTF-8 z BOM |

### Nazwa pliku

Format: `POSTAĆ_DD_MM_RRRR_GG_MM`

Przykład:
```
MiesoMielone_28_06_2026_11_18.xlsx
MiesoMielone_28_06_2026_11_18.csv
```

Data i czas pobierane z zegara systemowego Windows w momencie eksportu.

### Kolumny

| # | Kolumna | Opis |
|---|---------|------|
| 1 | Postać | Nazwa postaci |
| 2 | Nazwa przedmiotu | Co sprzedano |
| 3 | Ilość | Liczba sztuk |
| 4 | Cena | Kwota transakcji |
| 5 | Typ ceny | Waluta (Yang / Gold Bar) |
| 6 | Data i godzina | Format: HH:MM YYYY-MM-DD |

### Format XLSX (Excel)

- Nagłówki: pogrubione, białe na zielonym tle
- Kolumny: automatyczna szerokość (auto-fit)
- Cena: format liczbowy z separatorem tysięcy
- Nagłówki: zamrożone (freeze panes)
- Filtry: włączone na wszystkich kolumnach
- Obramowanie: cienkie linie

## Wynik

Po zakończeniu program wyświetla raport:

```
============================================================
  Metin HARD Log Extractor — Eksport zakończony
============================================================

  Postać:          MiesoMielone
  Rekordów:        145
  Data eksportu:   11:18 2026-06-28

  Pliki:
    ✓ MiesoMielone_28_06_2026_11_18.xlsx  (Excel — sformatowany)
    ✓ MiesoMielone_28_06_2026_11_18.csv   (CSV — separator ;)

  Format daty w plikach: HH:MM YYYY-MM-DD (ISO-8601)
  Kodowanie CSV: UTF-8 z BOM
============================================================
```

## Uruchomienie przez Harmonogram Zadań Windows

1. Otwórz "Harmonogram zadań" (Task Scheduler)
2. Utwórz nowe zadanie
3. Akcja: "Uruchom program"
4. Program: `powershell.exe`
5. Argumenty: `-File "C:\ścieżka\do\Metin_HARD\deployment\run.ps1"`
6. Ustaw harmonogram (np. raz dziennie)
