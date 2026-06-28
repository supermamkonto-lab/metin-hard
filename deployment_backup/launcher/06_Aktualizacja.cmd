@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."
title METIN HARD - Aktualizacja

cls
echo.
echo  ==========================================
echo  METIN HARD - Aktualizacja srodowiska
echo  ==========================================
echo.

pip install -e . --upgrade >nul 2>&1
echo  Zaleznosci zaktualizowane.

pip install -e ".[dev]" --upgrade >nul 2>&1
echo  Narzedzia testowe zaktualizowane.

python -m playwright install chromium >nul 2>&1
echo  Chromium zaktualizowany.

echo.
echo  Aktualizacja zakonczona.
echo.
pause
