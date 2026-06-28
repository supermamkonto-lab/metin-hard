# Instalacja — krok po kroku

## Opcja A: Automatyczna (zalecana)

1. Otwórz PowerShell jako Administrator:
   - Kliknij prawym na Menu Start → "Terminal (Administrator)"
   
2. Przejdź do katalogu projektu:
   ```powershell
   cd C:\ścieżka\do\Metin_HARD
   ```

3. Zezwól na uruchamianie skryptów (jednorazowo):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. Uruchom instalację:
   ```powershell
   .\deployment\setup.ps1
   ```

5. Po zakończeniu uruchom diagnostykę:
   ```powershell
   .\deployment\metin_hard_doctor.ps1
   ```

---

## Opcja B: Ręczna

### Krok 1: Zainstaluj Python

1. Pobierz Python 3.11+ ze strony: https://www.python.org/downloads/
2. Uruchom instalator.
3. **WAŻNE:** Zaznacz opcję "Add Python to PATH".
4. Kliknij "Install Now".
5. Sprawdź: `python --version` (powinno wyświetlić 3.11+)

### Krok 2: Zainstaluj zależności projektu

```powershell
cd C:\ścieżka\do\Metin_HARD
pip install -e .
pip install -e ".[dev]"
```

### Krok 3: Zainstaluj przeglądarkę Playwright

```powershell
python -m playwright install chromium
```

### Krok 4: Sprawdź instalację

```powershell
.\deployment\metin_hard_doctor.ps1
```
