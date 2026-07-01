@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD LOG - Diagnostyka

cls
echo.
echo  ==========================================
echo  METIN HARD LOG - Diagnostyka
echo  ==========================================
echo.

set ALL_OK=1

:: Python
python --version >nul 2>&1
if %errorlevel%==0 (
    echo  Python ..................... OK
) else (
    echo  Python ..................... BLAD
    echo    ^>^> Zainstaluj Python 3.11+ : https://python.org/downloads/
    set ALL_OK=0
)

:: pip
pip --version >nul 2>&1
if %errorlevel%==0 (
    echo  pip ........................ OK
) else (
    echo  pip ........................ BLAD
    set ALL_OK=0
)

:: Playwright
python -c "import playwright" >nul 2>&1
if %errorlevel%==0 (
    echo  Playwright ................. OK
) else (
    echo  Playwright ................. BLAD
    echo    ^>^> Uruchom: Instalacja srodowiska
    set ALL_OK=0
)

:: openpyxl
python -c "import openpyxl" >nul 2>&1
if %errorlevel%==0 (
    echo  openpyxl ................... OK
) else (
    echo  openpyxl ................... BLAD
    echo    ^>^> Uruchom: Instalacja srodowiska
    set ALL_OK=0
)

:: Chromium
python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop()" >nul 2>&1
if %errorlevel%==0 (
    echo  Chromium ................... OK
) else (
    echo  Chromium ................... BLAD
    echo    ^>^> Uruchom: python -m playwright install chromium
    set ALL_OK=0
)

:: Moduly projektu
python -c "from src.config import load_config; from src.auth import login; from src.characters import detect_characters; from src.scraper import scrape_sales_logs" >nul 2>&1
if %errorlevel%==0 (
    echo  Moduly projektu ............ OK
) else (
    echo  Moduly projektu ............ BLAD
    echo    ^>^> Uruchom: Instalacja srodowiska
    set ALL_OK=0
)

:: config.toml
if exist config.toml (
    echo  config.toml ................ OK
) else (
    echo  config.toml ................ BLAD
    echo    ^>^> Uruchom: Konfiguracja programu
    set ALL_OK=0
)

:: Walidacja config
if exist config.toml (
    python -c "from src.config import load_config; from pathlib import Path; load_config(Path('config.toml'))" >nul 2>&1
    if %errorlevel%==0 (
        echo  config.toml poprawny ...... OK
    ) else (
        echo  config.toml poprawny ...... BLAD
        echo    ^>^> Sprawdz dane w config.toml
        set ALL_OK=0
    )
)

:: Folder output
if exist output (
    echo  Folder output .............. OK
) else (
    echo  Folder output .............. BLAD (zostanie utworzony automatycznie)
)

echo.
echo  ==========================================
if %ALL_OK%==1 (
    echo  STATUS: GOTOWY
) else (
    echo  STATUS: NIE GOTOWY
    echo  Napraw powyzsze problemy.
)
echo  ==========================================
echo.
pause
