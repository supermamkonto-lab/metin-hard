@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Instalacja srodowiska

cls
echo.
echo  ==========================================
echo  METIN HARD
echo  Instalacja srodowiska
echo  ==========================================
echo.

echo  [1/5] Sprawdzanie Python ...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo        BLAD: Python nie jest zainstalowany!
    echo.
    echo        Pobierz Python 3.11+ ze strony:
    echo        https://www.python.org/downloads/
    echo.
    echo        WAZNE: Zaznacz "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
python --version
echo        OK
echo.

echo  [2/5] Instalacja zaleznosci projektu ...
pip install -e . >nul 2>&1
if %errorlevel% neq 0 (
    echo        BLAD przy instalacji. Probuje ponownie...
    pip install -e .
    if %errorlevel% neq 0 (
        pause
        exit /b 1
    )
)
echo        OK
echo.

echo  [3/5] Instalacja narzedzi testowych ...
pip install -e ".[dev]" >nul 2>&1
echo        OK
echo.

echo  [4/5] Instalacja przegladarki Chromium ...
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if %errorlevel%==0 (
    echo        Juz zainstalowana.
) else (
    python -m playwright install chromium
    if %errorlevel% neq 0 (
        echo        BLAD instalacji Chromium.
        pause
        exit /b 1
    )
    echo        OK
)
echo.

echo  [5/5] Sprawdzanie konfiguracji ...
if exist config.toml (
    echo        config.toml istnieje - OK
) else (
    copy config.toml.example config.toml >nul
    echo        Utworzono config.toml z przykladu.
    echo        UZUPELNIJ DANE LOGOWANIA!
)
echo.

echo  ==========================================
echo  Instalacja zakonczona!
echo  ==========================================
echo.
pause
