# Metin HARD Log Extractor — Deployment Package

Kompletna dokumentacja umożliwiająca uruchomienie programu na czystym Windows 11.

## Nazwa programu

**Metin HARD Log Extractor** — automatyczny eksport logów sprzedaży z panelu UCP serwera Metin2 Projekt-Hard.eu.

## Typowy przebieg pracy

```
1. setup.ps1          → Instalacja środowiska
       ↓
2. metin_hard_doctor.ps1  → Weryfikacja gotowości
       ↓
3. config.toml        → Uzupełnienie danych logowania
       ↓
4. run.ps1            → Uruchomienie programu
       ↓
5. XLSX + CSV         → Pliki z logami sprzedaży
```

## Szybki start

1. Skopiuj cały katalog projektu na nowy komputer.
2. Uruchom PowerShell jako Administrator.
3. Wykonaj: `.\deployment\setup.ps1`
4. Wykonaj: `.\deployment\metin_hard_doctor.ps1`
5. Uzupełnij plik `config.toml` swoimi danymi logowania.
6. Wykonaj: `.\deployment\run.ps1`

## Dokumenty w tym katalogu

| Plik | Opis |
|------|------|
| README.md | Ten dokument |
| 01-wymagania-systemowe.md | Wymagania sprzętowe i programowe |
| 02-instalacja.md | Instrukcja instalacji krok po kroku |
| 03-konfiguracja.md | Konfiguracja programu (config.toml) |
| 04-uruchomienie.md | Jak uruchomić program |
| 05-rozwiazywanie-problemow.md | FAQ i diagnostyka |
| setup.ps1 | Automatyczna instalacja środowiska (idempotentna) |
| metin_hard_doctor.ps1 | Diagnostyka gotowości środowiska |
| run.ps1 | Uruchomienie programu (z pre-check) |

---

## Format eksportu: v1.0

### Pliki wynikowe

Program generuje **dwa pliki** przy każdym uruchomieniu:

| Format | Opis |
|--------|------|
| `.xlsx` | Plik Excel — sformatowany, auto-fit kolumn, filtry, freeze panes |
| `.csv` | Plik CSV — separator `;`, kodowanie UTF-8 z BOM |

### Kolumny (v1.0)

| # | Kolumna | Typ | Opis |
|---|---------|-----|------|
| 1 | Postać | tekst | Nazwa postaci na koncie |
| 2 | Nazwa przedmiotu | tekst | Nazwa sprzedanego przedmiotu |
| 3 | Ilość | liczba | Liczba sprzedanych sztuk |
| 4 | Cena | liczba | Kwota transakcji |
| 5 | Typ ceny | tekst | Waluta: Yang lub Gold Bar |
| 6 | Data i godzina | tekst | Format: HH:MM YYYY-MM-DD |

### Kodowanie

| Element | Wartość |
|---------|---------|
| Kodowanie pliku | UTF-8 z BOM |
| Separator CSV | `;` (średnik) |
| Format Excel | XLSX (openpyxl) |
| Format daty | HH:MM YYYY-MM-DD (ISO-8601) |

### Nazewnictwo plików

Format: `POSTAĆ_DD_MM_RRRR_GG_MM`

Przykład: `MiesoMielone_28_06_2026_11_18.xlsx`

Data i czas pobierane z zegara systemowego Windows w momencie eksportu.

### Historia wersji formatu

| Wersja | Data | Opis |
|--------|------|------|
| v1.0 | 2026-06-28 | Pierwsza wersja: 6 kolumn, XLSX + CSV, data ISO-8601, separator ; |
