# Dokument Wymagań

## Wprowadzenie

Program do automatycznego pobierania logów sprzedaży ze wszystkich postaci na koncie w panelu UCP serwera Metin2 (https://projekt-hard.eu/ucp) i zapisywania ich do pliku CSV. Program uruchamiany jest ręcznie lub przez Harmonogram Zadań Windows, wykonuje swoją pracę i kończy działanie.

## Słownik

- **UCP**: User Control Panel — panel zarządzania kontem na serwerze Metin2, dostępny pod adresem https://projekt-hard.eu/ucp
- **Log_Sprzedaży**: Pojedynczy wpis w historii transakcji sprzedaży widoczny w panelu UCP, zawierający informacje o sprzedanym przedmiocie
- **Postać**: Postać gracza przypisana do konta w panelu UCP; każda postać ma własne logi sprzedaży
- **Paginacja**: Mechanizm podziału logów na strony w panelu UCP, wyświetlający informację "Pozycje od X do Y z Z łącznie"
- **Raport_Zakończenia**: Podsumowanie wyświetlane po zakończeniu pracy programu, zawierające statystyki przebiegu operacji
- **PIN**: 5-cyfrowy kod zabezpieczający wymagany przez panel UCP podczas logowania, oprócz nazwy użytkownika i hasła

## Wymagania

### Wymaganie 1: Uwierzytelnienie w panelu UCP

**User Story:** Jako użytkownik, chcę aby program automatycznie logował się do panelu UCP, abym nie musiał ręcznie przeprowadzać procesu uwierzytelnienia.

#### Kryteria Akceptacji

1. WHEN użytkownik uruchomi program z poprawnymi danymi logowania (login, hasło oraz PIN), THE Program SHALL zalogować się do panelu UCP i uzyskać dostęp do danych konta
2. IF dane logowania są nieprawidłowe (odrzucone przez serwer), THEN THE Program SHALL poinformować użytkownika o nieprawidłowych danych uwierzytelniających i zakończyć działanie z błędem
3. IF panel UCP jest niedostępny, THEN THE Program SHALL poinformować użytkownika o problemie z połączeniem i zakończyć działanie z błędem
4. IF dane logowania (login, hasło, PIN) nie zostały podane w konfiguracji, THEN THE Program SHALL poinformować użytkownika o brakujących danych logowania i zakończyć działanie z błędem przed próbą połączenia

### Wymaganie 2: Automatyczne wykrywanie postaci

**User Story:** Jako użytkownik, chcę aby program automatycznie wykrywał wszystkie postacie na moim koncie, abym nie musiał ręcznie podawać ich nazw.

#### Kryteria Akceptacji

1. WHEN program zaloguje się do panelu UCP, THE Program SHALL automatycznie wykryć wszystkie Postacie przypisane do konta
2. THE Program SHALL obsługiwać dowolną liczbę Postaci na koncie (1, 2, 5 lub więcej)
3. THE Program SHALL pobrać logi sprzedaży dla każdej wykrytej Postaci
4. IF na koncie nie zostanie wykryta żadna Postać, THEN THE Program SHALL poinformować użytkownika o braku postaci i zakończyć działanie z błędem

### Wymaganie 3: Pobieranie kompletnych logów sprzedaży

**User Story:** Jako użytkownik, chcę aby program pobierał wszystkie logi sprzedaży bez wyjątku, abym miał pełną historię transakcji.

#### Kryteria Akceptacji

1. WHEN program przechodzi do logów sprzedaży danej Postaci, THE Program SHALL pobrać 100% wpisów Log_Sprzedaży dostępnych w panelu UCP dla tej Postaci
2. THE Program SHALL automatycznie obsługiwać Paginację, przechodząc przez wszystkie strony od pierwszej do ostatniej
3. THE Program SHALL rozpoznawać całkowitą liczbę wpisów na podstawie informacji "Pozycje od X do Y z Z łącznie" i kontynuować pobieranie aż do pobrania wszystkich Z wpisów
4. THE Program SHALL pobierać następujące dane z tabeli logów: Nazwa przedmiotu, Ilość, Cena, Typ ceny, Data
5. IF tabela logów w panelu UCP zawiera dodatkowe kolumny poza wymienionymi, THE Program SHALL pobrać również te dodatkowe dane
6. IF Postać nie posiada żadnych logów sprzedaży, THEN THE Program SHALL potraktować to jako poprawną sytuację i przejść do następnej Postaci

### Wymaganie 4: Eksport do pliku CSV

**User Story:** Jako użytkownik, chcę aby program tworzył plik CSV z logami sprzedaży, abym mógł analizować dane w arkuszu kalkulacyjnym.

#### Kryteria Akceptacji

1. WHEN program zakończy pobieranie logów ze wszystkich Postaci, THE Program SHALL utworzyć nowy plik CSV zawierający wszystkie pobrane wpisy Log_Sprzedaży
2. THE Program SHALL każdorazowo tworzyć nowy plik CSV z unikalną nazwą w formacie sales_log_YYYY-MM-DD_HH-MM-SS.csv (nigdy nie nadpisuje istniejących plików)
3. THE Program SHALL zapisywać plik CSV w kodowaniu UTF-8
4. THE Program SHALL zapisywać plik CSV w folderze wskazanym przez użytkownika w konfiguracji
5. THE Program SHALL zawierać w pliku CSV co najmniej kolumny: Character, Date, Buyer, Item, Quantity, Yang, Shop, Page
6. THE Program SHALL dodać kolumnę "Character" identyfikującą, do której Postaci należy dany wpis Log_Sprzedaży
7. IF panel UCP udostępnia dodatkowe informacje poza wymaganymi kolumnami, THE Program SHALL również je wyeksportować do pliku CSV
8. IF zapis pliku CSV nie powiedzie się, THEN THE Program SHALL poinformować użytkownika o przyczynie błędu zapisu

### Wymaganie 5: Model wykonania programu

**User Story:** Jako użytkownik, chcę aby program wykonywał swoje zadanie i kończył działanie, abym mógł uruchamiać go ręcznie lub przez Harmonogram Zadań Windows.

#### Kryteria Akceptacji

1. WHEN program zakończy pobieranie i eksport danych, THE Program SHALL zakończyć swoje działanie (nie działa jako usługa w tle)
2. THE Program SHALL być możliwy do uruchomienia ręcznie z wiersza poleceń
3. THE Program SHALL być możliwy do uruchomienia automatycznie przez Harmonogram Zadań Windows
4. THE Program SHALL zakończyć działanie z kodem wyjścia 0 w przypadku sukcesu oraz z kodem wyjścia różnym od 0 w przypadku błędu

### Wymaganie 6: Raport zakończenia

**User Story:** Jako użytkownik, chcę widzieć podsumowanie po zakończeniu pracy programu, abym wiedział czy operacja się powiodła i ile danych zostało pobranych.

#### Kryteria Akceptacji

1. WHEN program zakończy działanie (sukces lub błąd), THE Program SHALL wyświetlić Raport_Zakończenia
2. THE Raport_Zakończenia SHALL zawierać liczbę wykrytych Postaci
3. THE Raport_Zakończenia SHALL zawierać liczbę przetworzonych stron (łącznie dla wszystkich Postaci)
4. THE Raport_Zakończenia SHALL zawierać liczbę pobranych wpisów Log_Sprzedaży
5. THE Raport_Zakończenia SHALL zawierać nazwę utworzonego pliku CSV (lub informację o braku pliku w przypadku błędu)
6. THE Raport_Zakończenia SHALL zawierać status operacji: SUCCESS w przypadku pełnego powodzenia lub informację o błędzie w przypadku niepowodzenia

### Wymaganie 7: Informowanie o błędach

**User Story:** Jako użytkownik, chcę być informowany o błędach, abym wiedział co poszło nie tak i mógł podjąć działania naprawcze.

#### Kryteria Akceptacji

1. IF wystąpi błąd podczas logowania, wykrywania postaci, pobierania logów lub zapisu CSV, THEN THE Program SHALL poinformować użytkownika o typie błędu i etapie, na którym wystąpił
2. IF sesja wygaśnie podczas pobierania danych, THEN THE Program SHALL poinformować użytkownika o wygaśnięciu sesji
3. THE Program SHALL przedstawiać komunikaty błędów w sposób zrozumiały dla użytkownika (nie surowe wyjątki techniczne)

### Wymaganie 8: Konfiguracja programu

**User Story:** Jako użytkownik, chcę skonfigurować dane logowania i lokalizację zapisu plików, abym mógł dostosować program do swoich potrzeb.

#### Kryteria Akceptacji

1. THE Program SHALL umożliwiać użytkownikowi podanie nazwy użytkownika, hasła oraz 5-cyfrowego kodu PIN do panelu UCP
2. THE Program SHALL umożliwiać użytkownikowi wskazanie folderu docelowego do zapisu plików CSV
3. IF wymagane pola konfiguracyjne (login, hasło, PIN) nie są podane, THEN THE Program SHALL poinformować użytkownika o brakujących polach i zakończyć działanie z błędem
4. IF wskazany folder docelowy nie istnieje, THEN THE Program SHALL poinformować użytkownika o nieistniejącym folderze i zakończyć działanie z błędem

## Ograniczenia

1. System operacyjny: Windows 11
2. Język programowania: Python
3. Automatyzacja przeglądarki: Playwright
4. Docelowy panel: https://projekt-hard.eu/ucp (jeden panel, jedno konto)
