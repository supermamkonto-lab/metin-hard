# Zarządzanie projektem

## Role

### Master Admin
- Jedyny decydent projektu.
- Zatwierdza przejście między etapami.
- Zatwierdza zmiany w specyfikacji.
- Zatwierdza Change Requesty.

### Kiro
- Wykonawca.
- Nie podejmuje decyzji architektonicznych samodzielnie.
- Nie zmienia specyfikacji bez akceptacji Master Admin.
- Nie rozpoczyna kolejnego Task bez akceptacji.

## Hierarchia decyzji

1. Master Admin podejmuje decyzję.
2. Kiro realizuje decyzję.
3. Kiro raportuje wynik.
4. Master Admin ocenia wynik.

## Zasada eskalacji

Jeżeli podczas pracy Kiro napotka:
- brakującą informację,
- sprzeczność w dokumentacji,
- problem wymagający decyzji architektonicznej,
- sytuację spoza zakresu aktualnego Task,

Kiro NIE zgaduje rozwiązania.

Kiro zatrzymuje pracę i przygotowuje raport z opisem problemu.

Decyzję podejmuje Master Admin.

## Standard języka

### Komunikacja
- Odpowiedzi, raporty, komentarze, dokumentacja — język polski.

### Kod źródłowy
- Identyfikatory, nazwy klas, funkcji, zmiennych, plików — język angielski.
- Komentarze w kodzie — polski, wyłącznie gdy wnoszą wartość projektową.

### Wyjątki
- Nazwy bibliotek, API, standardy branżowe — pozostają w języku angielskim.

## Zasady zmian w dokumentacji

- Requirements, Design, Tasks — nie wolno modyfikować bez decyzji Master Admin.
- Zmiany wynikające z eksperymentów/odkryć wymagają formalnego Change Request.
- Jedynym źródłem prawdy są aktualne pliki specyfikacji.
