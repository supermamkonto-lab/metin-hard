@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0.."

if exist README.md (
    start "" README.md
) else (
    echo  Nie znaleziono dokumentacji.
    pause
)
