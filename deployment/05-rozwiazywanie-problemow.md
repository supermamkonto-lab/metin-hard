# Rozwiązywanie problemów

## Problem: "python nie jest rozpoznawane"

**Przyczyna:** Python nie został dodany do PATH.

**Rozwiązanie:**
1. Odinstaluj Python
2. Zainstaluj ponownie — zaznacz "Add Python to PATH"
3. Zamknij i otwórz PowerShell ponownie

---

## Problem: "Plik konfiguracyjny nie istnieje"

**Przyczyna:** Brak pliku `config.toml`.

**Rozwiązanie:**
```powershell
copy config.toml.example config.toml
notepad config.toml
```
Uzupełnij dane logowania.

---

## Problem: "Folder wyjściowy nie istnieje"

**Przyczyna:** Folder z pola `directory` w config.toml nie istnieje.

**Rozwiązanie:**
```powershell
mkdir "C:\Users\Hubert\Documents\metin_logs"
```

---

## Problem: "Pole 'pin' musi mieć dokładnie 5 znaków"

**Przyczyna:** PIN w config.toml ma nieprawidłową długość.

**Rozwiązanie:** Upewnij się że PIN ma dokładnie 5 cyfr, np. `pin = "12345"`

---

## Problem: "Panel UCP jest niedostępny"

**Przyczyna:** Serwer nie odpowiada lub brak Internetu.

**Rozwiązanie:**
1. Sprawdź połączenie z Internetem
2. Otwórz w przeglądarce: https://projekt-hard.eu/ucp
3. Jeśli strona nie działa — problem po stronie serwera

---

## Problem: "Nieprawidłowe dane logowania"

**Przyczyna:** Login, hasło lub PIN są nieprawidłowe.

**Rozwiązanie:**
1. Zaloguj się ręcznie w przeglądarce na https://projekt-hard.eu/ucp
2. Sprawdź czy dane w config.toml są identyczne
3. Popraw config.toml

---

## Diagnostyka

Uruchom pełną diagnostykę:
```powershell
.\deployment\metin_hard_doctor.ps1
```
