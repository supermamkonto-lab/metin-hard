# METIN HARD LOG (v2.0)

Eksporter logów sprzedaży z panelu UCP serwera Metin2 ([projekt-hard.eu/ucp](https://projekt-hard.eu/ucp)) do pliku Excel (XLSX).

*(English version: [README_ENG.md](README_ENG.md))*

### Co nowego w v2.0

- Wybór, które postacie pobrać, i tryb eksportu (jeden plik / osobno)
- Pasek postępu i kolorowany log podczas pobierania (błędy na czerwono, sukces na złoto)
- Podsumowanie sprzedaży w oknie po zakończeniu (łączna kwota, top 5 przedmiotów) — bez otwierania XLSX
- Automatyczne ponawianie próby (do 3x) przy przejściowych timeoutach sieci
- Harmonogram automatycznych, codziennych pobrań przez Harmonogram Zadań Windows (menu Zaawansowane)
- Program nie wydaje żadnych dźwięków systemowych poza prawdziwymi błędami

---

## Jak uruchomić?

**Kliknij dwukrotnie plik `!URUCHOM_PROGRAM.cmd`** w tym folderze.

To wszystko — otworzy się okno programu. Reszta dzieje się w oknie, nie w konsoli.

---

## Pierwsze uruchomienie

Za pierwszym razem (albo gdy czegoś brakuje w systemie) program:

1. Sam sprawdza środowisko komputera — Python, Playwright, openpyxl, Chromium, plik konfiguracyjny.
2. Jeśli czegoś brakuje, **pokazuje okno z listą brakujących elementów** i pyta, czy zainstalować je automatycznie.
3. Po kliknięciu **Tak** instalacja leci w tle, a jej przebieg widać na żywo w oknie "Przebieg".
4. Po instalacji uzupełnij dane logowania w przycisku **Konfiguracja** (login, hasło, PIN, folder na wyniki).

`!URUCHOM_PROGRAM.cmd` sam znajduje zainstalowanego Pythona na komputerze (obsługuje różne wersje Windows 10/11 i różne wcześniej zainstalowane wersje Pythona) — nie trzeba nic konfigurować ręcznie.

Jedyny wymóg, którego program nie potrafi sam spełnić: **Python w wersji 3.11 lub nowszej musi być w ogóle zainstalowany**. Jeśli go brakuje, `!URUCHOM_PROGRAM.cmd` pokaże komunikat z linkiem do pobrania (https://www.python.org/downloads/ — pamiętaj, żeby przy instalacji zaznaczyć "Add Python to PATH").

---

## Główne okno programu

| Element | Do czego służy |
|---|---|
| **Stan środowiska** | Statusy pokazujące czy wszystko jest gotowe do pracy |
| **Pobierz logi sprzedaży** | Główny przycisk — loguje się do UCP, znajduje postacie, pozwala wybrać które pobrać, i zapisuje wynik do XLSX |
| **Konfiguracja** | Formularz z danymi logowania i folderem na wyniki |
| **Napraw / zainstaluj środowisko** | Ręczne uruchomienie instalacji/naprawy w dowolnym momencie |
| **Folder wyników** | Otwiera folder z wygenerowanymi plikami XLSX |
| **Przebieg** | Konsola na żywo — widać dokładnie co program robi w danej chwili |

Menu **Zaawansowane** (testy projektu, aktualizacja zależności) i **Pomoc** (informacje, dokumentacja) są dostępne z górnego paska menu.

---

## Co robi program krok po kroku?

1. Loguje się na [https://projekt-hard.eu/ucp](https://projekt-hard.eu/ucp) danymi z Konfiguracji.
2. Wykrywa wszystkie postacie na koncie (1-4) i zapisuje ich nazwy do `config.toml`.
3. **Pokazuje okno z listą wykrytych postaci** — zaznaczasz ptaszkiem te, dla których chcesz pobrać logi, albo wybierasz **Wyjście**, żeby przerwać całą operację bez pobierania czegokolwiek.
4. Jeśli zaznaczyłeś **2 lub więcej** postaci, program pyta: **jeden wspólny plik XLSX dla wszystkich, czy osobny plik dla każdej postaci?**
5. Dla każdej wybranej postaci pobiera logi sprzedaży (offline shop) — jeśli dana postać nie ma żadnych logów, program automatycznie przechodzi do kolejnej.
6. Zapisuje wynik do jednego lub kilku plików **XLSX**, zależnie od wyboru w kroku 4.
7. Nazwa pliku: `POSTAC_DD_MM_RRRR_GG_MM.xlsx` (data i godzina pobrania), albo `WSZYSTKIE_POSTACIE_DD_MM_RRRR_GG_MM.xlsx` przy wspólnym pliku dla kilku postaci.

### Kolumny w pliku XLSX

| Kolumna | Opis |
|---|---|
| Postać | Nazwa postaci, z której konta pochodzi wpis |
| Nazwa przedmiotu | Nazwa sprzedanego przedmiotu |
| Ilość | Liczba sprzedanych sztuk |
| Cena | Cena transakcji z separatorami tysięcy, np. `125.000.000,00` |
| Typ ceny | Yang / Gold Bar |
| Data i godzina | Data i godzina transakcji (format `HH:MM YYYY-MM-DD`) |

Kolumna Cena jest zapisana jako tekst z separatorami wpisanymi na stałe (`.` co trzy cyfry, `,` przed groszami) — dzięki temu wygląda identycznie na każdym komputerze, niezależnie od jego ustawień regionalnych (Excel renderuje separator liczb według Windows, więc "prawdziwie liczbowa" komórka wyglądałaby różnie na różnych komputerach).

---

## Struktura folderu

```
MetinHardLog/
├── !URUCHOM_PROGRAM.cmd   <- TEN PLIK URUCHAMIA PROGRAM
├── gui.py                  okno programu (Tkinter)
├── main.py                 logika pobierania logów (wywoływana przez GUI)
├── config.toml              Twoje dane logowania (nie udostępniaj nikomu!)
├── config.toml.example     szablon konfiguracji
├── src/                     kod źródłowy (config, auth, scraper, export...)
├── tests/                   testy automatyczne projektu
├── launcher/                skrypty pomocnicze (zaawansowane, opcjonalne)
├── output/                  tutaj trafiają wygenerowane pliki XLSX
├── logs/                    log tekstowy z każdego uruchomienia
├── README_PL.md             ten plik
└── README_ENG.md            wersja angielska
```

---

## Rozwiązywanie problemów

- **Program się nie otwiera po dwukliku na `!URUCHOM_PROGRAM.cmd`** — najczęściej brak Pythona. Zainstaluj Python 3.11+ ze strony python.org, zaznaczając "Add Python to PATH", i spróbuj ponownie.
- **Sekcja "Stan środowiska" pokazuje czerwony błąd** — kliknij "Napraw / zainstaluj środowisko" w oknie programu.
- **Błąd logowania** — sprawdź dane w Konfiguracji (login, hasło, PIN musi mieć dokładnie 5 znaków).
- **Brak logów dla postaci** — to normalne, jeśli dana postać nie sprzedawała nic przez offline shop; program pomija ją i przechodzi dalej.
- **Wybrałem "osobny plik dla każdej postaci", ale powstał tylko jeden plik** — to celowe: jeśli tylko jedna z wybranych postaci miała jakiekolwiek dane, powstaje tylko jej plik (pozostałe nie miały czego eksportować).
- Szczegółowy log każdego uruchomienia znajdziesz w folderze `logs/`.

---

## Wymagania

- Windows 10 lub 11
- Python 3.11 lub nowszy (instaluje się automatycznie do PATH przez instalator z python.org)
- Połączenie z internetem (do logowania i do jednorazowej instalacji zależności)

---

Powered by Lewsonik (c) 2026
Kontakt: supermamkonto@gmail.com
GitHub: https://github.com/supermamkonto-lab/metin-hard
