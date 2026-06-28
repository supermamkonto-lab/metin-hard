@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Konfiguracja

cls
echo.
echo  ==========================================
echo  METIN HARD - Konfiguracja
echo  ==========================================
echo.

if not exist config.toml (
    copy config.toml.example config.toml >nul
    echo  Utworzono nowy plik konfiguracyjny.
    echo.
)

echo  Otwieram config.toml w Notatniku...
echo.
echo  Uzupelnij pola:
echo    username = "TWOJ LOGIN"
echo    password = "TWOJE HASLO"
echo    pin      = "5-CYFROWY PIN"
echo    directory = "output"
echo.
echo  UWAGA: Mozesz zostawic directory = "output"
echo  Program uzyje folderu output/ wewnatrz programu.
echo.

notepad config.toml

echo  Sprawdzam konfiguracje...
python -c "from src.config import load_config; from pathlib import Path; load_config(Path('config.toml')); print('OK')" 2>nul
if %errorlevel%==0 (
    echo  Konfiguracja poprawna!
) else (
    echo  BLAD: Sprawdz dane w config.toml
)
echo.
pause
