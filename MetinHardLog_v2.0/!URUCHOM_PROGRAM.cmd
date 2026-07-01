@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title METIN HARD LOG

rem Szukamy Pythona niezaleznie od tego, jak jest skonfigurowany na tym
rem komputerze. Kolejnosc prob (dziala na roznych instalacjach W10/W11):
rem   1) Python Launcher (py.exe)  -- wybiera automatycznie najnowsza
rem      zainstalowana wersje Pythona 3.x, niezaleznie od PATH
rem   2) "pythonw" bezposrednio w PATH
rem Wlasciwa wersja (3.11+) jest potem weryfikowana w oknie programu.

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 --version >nul 2>&1
    if %errorlevel%==0 (
        start "" pyw -3 gui.py
        exit /b 0
    )
)

pythonw --version >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw gui.py
    exit /b 0
)

echo.
echo  ==========================================
echo  METIN HARD LOG
echo  ==========================================
echo.
echo  BLAD: Nie znaleziono Pythona na tym komputerze.
echo.
echo  Pobierz i zainstaluj Python 3.11 lub nowszy ze strony:
echo  https://www.python.org/downloads/
echo.
echo  WAZNE: Podczas instalacji ZAZNACZ "Add Python to PATH".
echo  Bez tego program nie wystartuje.
echo.
pause
exit /b 1
