# CZYM JEST PROJEKT METIN HARD

## Cel projektu

Metin Hard jest aplikacją desktopową dla systemu Windows, której zadaniem jest automatyzacja pobierania oraz przetwarzania logów sprzedaży z serwera Metin2.

Program powstał w celu wyeliminowania ręcznego kopiowania danych oraz przygotowywania raportów sprzedaży.

Głównym rezultatem działania programu jest wygenerowanie profesjonalnego raportu XLSX zawierającego historię sprzedaży przedmiotów.

Projekt jest rozwijany jako narzędzie produkcyjne wykorzystywane na rzeczywistych danych.

---

# ŚRODOWISKO PRACY

Program współpracuje z panelem użytkownika serwera Metin2.

Adres panelu:

https://projekt-hard.eu/ucp

Do działania wymagane jest konto użytkownika posiadające dostęp do logów sprzedaży.

Program wykorzystuje przeglądarkę internetową do automatyzacji procesu.

---

# GŁÓWNY PRZEPŁYW PRACY

Cały proces wygląda następująco.

## Krok 1

Uruchomienie programu.

↓

## Krok 2

Automatyczne otwarcie strony:

https://projekt-hard.eu/ucp

↓

## Krok 3

Logowanie użytkownika.

Program loguje się przy użyciu danych przekazanych przez użytkownika.

Jeżeli sesja jest nadal aktywna, program powinien wykorzystywać istniejącą sesję.

↓

## Krok 4

Przejście do modułu logów sprzedaży.

Program automatycznie odnajduje odpowiednią sekcję panelu użytkownika.

↓

## Krok 5

Pobranie logów sprzedaży.

Program pobiera wszystkie rekordy spełniające zadane kryteria.

Nie powinien pomijać żadnego rekordu.

↓

## Krok 6

Analiza pobranych danych.

Program odczytuje między innymi:

- nazwę przedmiotu,
- ilość,
- cenę,
- datę sprzedaży,
- kupującego (jeżeli dostępny),
- pozostałe informacje znajdujące się w logach.

↓

## Krok 7

Normalizacja danych.

Na tym etapie dane są czyszczone i przygotowywane do eksportu.

Między innymi:

- konwersja wartości liczbowych,
- ujednolicenie formatów,
- walidacja rekordów,
- usuwanie niepoprawnych danych.

↓

## Krok 8

Generowanie raportu.

Program tworzy raport w formacie Microsoft Excel (*.xlsx).

Raport powinien zawierać wyłącznie poprawne dane.

↓

## Krok 9

Formatowanie raportu.

Program przygotowuje arkusz do dalszej pracy użytkownika.

Między innymi:

- nagłówki,
- szerokości kolumn,
- formatowanie liczb,
- poprawny zapis cen,
- możliwość sortowania,
- możliwość filtrowania,
- możliwość wykonywania obliczeń.

↓

## Krok 10

Zapis raportu.

Program zapisuje końcowy plik XLSX we wskazanej lokalizacji.

Na obecnym etapie projekt nie generuje już plików CSV.

Jedynym oficjalnym formatem eksportu jest XLSX.

---

# CEL RAPORTU

Raport XLSX ma umożliwiać użytkownikowi dalszą analizę sprzedaży.

Plik powinien być w pełni zgodny z Microsoft Excel.

Użytkownik powinien mieć możliwość:

- sortowania danych,
- filtrowania,
- wykonywania obliczeń,
- tworzenia tabel przestawnych,
- importowania danych do Power Query,
- dalszej analizy bez dodatkowych konwersji.

---

# ARCHITEKTURA PROJEKTU

Projekt można podzielić na kilka głównych modułów.

• konfiguracja programu

↓

• logowanie do panelu użytkownika

↓

• automatyzacja przeglądarki

↓

• pobieranie logów sprzedaży

↓

• analiza danych

↓

• przetwarzanie danych

↓

• eksport XLSX

↓

• zapis raportu

Claude powinien samodzielnie odnaleźć odpowiadające tym etapom moduły w kodzie źródłowym.

Nie należy zakładać nazw plików wyłącznie na podstawie ich nazw.

Źródłem prawdy jest implementacja.

---

# FILOZOFIA PROJEKTU

Projekt nie jest jednorazowym skryptem.

Projekt ma być rozwijany przez wiele lat.

Kod powinien być:

- prosty,
- czytelny,
- dobrze udokumentowany,
- łatwy do testowania,
- łatwy do utrzymania,
- łatwy do dalszej rozbudowy.

Każda zmiana powinna zwiększać wartość całego projektu.

---

# ZASADA NAJWYŻSZEGO PRIORYTETU

Najważniejszym celem nie jest dopisanie kolejnej funkcji.

Najważniejszym celem jest utrzymanie stabilnego, profesjonalnego i łatwego w rozwoju projektu.

Każdy kolejny programista lub model AI powinien być w stanie zrozumieć działanie programu na podstawie dokumentacji oraz kodu źródłowego, bez konieczności analizowania historii rozmów.