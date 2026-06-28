@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Testy

cls
echo.
echo  ==========================================
echo  METIN HARD - Test projektu
echo  ==========================================
echo.

python -m pytest tests/ -v

echo.
if %errorlevel%==0 (
    echo  Wszystkie testy PASSED.
) else (
    echo  Niektore testy nie przeszly.
)
echo.
pause
