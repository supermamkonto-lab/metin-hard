@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title METIN HARD Log Extractor

:menu
cls
echo.
echo  ==========================================
echo               METIN HARD
echo        Log Extractor v1.0
echo  ==========================================
echo.
echo   1. Instalacja srodowiska
echo.
echo   2. Diagnostyka komputera
echo.
echo   3. Konfiguracja programu
echo.
echo   4. Pobierz logi sprzedazy
echo.
echo   5. Test projektu
echo.
echo   6. Aktualizacja srodowiska
echo.
echo   7. Informacje
echo.
echo   8. Otworz folder z wynikami
echo.
echo   9. Otworz dokumentacje
echo.
echo   0. Zakoncz
echo.
echo  ==========================================
echo.
set /p choice="  Wybierz opcje: "

if "%choice%"=="1" call "%~dp0launcher\01_Instalacja.cmd"
if "%choice%"=="2" call "%~dp0launcher\02_Diagnostyka.cmd"
if "%choice%"=="3" call "%~dp0launcher\03_Konfiguracja.cmd"
if "%choice%"=="4" call "%~dp0launcher\04_Pobierz_logi.cmd"
if "%choice%"=="5" call "%~dp0launcher\05_Test_projektu.cmd"
if "%choice%"=="6" call "%~dp0launcher\06_Aktualizacja.cmd"
if "%choice%"=="7" call "%~dp0launcher\07_Informacje.cmd"
if "%choice%"=="8" call "%~dp0launcher\08_Folder_wynikow.cmd"
if "%choice%"=="9" call "%~dp0launcher\09_Dokumentacja.cmd"
if "%choice%"=="0" exit

goto menu
