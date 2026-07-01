@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD LOG - Informacje

cls
echo.
echo  ==========================================
echo         METIN HARD LOG
echo     Eksporter Logow Sprzedazy
echo               v1.0
echo  ==========================================
echo.
echo  Serwer:        projekt-hard.eu
echo  Panel:         https://projekt-hard.eu/ucp
echo.
echo  Pliki:         XLSX + CSV
echo  Nazwa:         POSTAC_DD_MM_RRRR_GG_MM
echo  Data:          HH:MM YYYY-MM-DD
echo  CSV:           separator ; / UTF-8 BOM
echo.
echo  Kolumny:
echo    1. Postac
echo    2. Nazwa przedmiotu
echo    3. Ilosc
echo    4. Cena
echo    5. Typ ceny
echo    6. Data i godzina
echo.
echo  ------------------------------------------
echo  Srodowisko:
echo.
python --version 2>nul
pip show playwright 2>nul | findstr "Version"
pip show openpyxl 2>nul | findstr "Version"
echo.
echo  ==========================================
echo.
pause