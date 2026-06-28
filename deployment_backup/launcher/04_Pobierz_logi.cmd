@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Pobieranie logow

cls
echo.
echo  ==========================================
echo  METIN HARD - Pobieranie logow sprzedazy
echo  ==========================================
echo.

:: Upewnij sie ze output/ istnieje
if not exist output mkdir output

:: Pre-check
python -c "from src.config import load_config; from pathlib import Path; load_config(Path('config.toml'))" >nul 2>&1
if %errorlevel% neq 0 (
    echo  BLAD: Srodowisko nie jest gotowe.
    echo  Uruchom: Instalacja + Konfiguracja
    echo.
    pause
    exit /b 1
)

echo  Uruchamiam pobieranie logow...
echo  (Moze to potrwac kilka minut)
echo.

python main.py

echo.
if %errorlevel%==0 (
    echo  Zakonczono pomyslnie!
) else (
    echo  Wystapil blad. Uruchom Diagnostyke.
)
echo.
pause
