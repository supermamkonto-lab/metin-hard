@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Informacje

cls
echo.
echo  ==========================================
echo  METIN HARD Log Extractor
echo  ==========================================
echo.
echo  Wersja:        1.0
echo  Format:        v1.0
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
echo  ==========================================
echo.
python --version 2>nul
echo.
pause
