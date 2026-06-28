# Metin HARD Log Extractor — Instalacja środowiska (idempotentna)
# Uruchom jako Administrator w PowerShell.
# Bezpieczne do wielokrotnego uruchomienia — nie psuje istniejącej instalacji.

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Metin HARD Log Extractor"
Write-Host "  Instalacja srodowiska"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectDir

# --- PYTHON ---
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[!] Python nie jest zainstalowany." -ForegroundColor Red
    Write-Host ""
    Write-Host "    1. Pobierz Python 3.11+ ze strony:" -ForegroundColor Yellow
    Write-Host "       https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Write-Host "    2. Podczas instalacji ZAZNACZ:" -ForegroundColor Yellow
    Write-Host "       [x] Add Python to PATH" -ForegroundColor White
    Write-Host ""
    Write-Host "    3. Po zainstalowaniu uruchom ten skrypt ponownie." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

$pyVer = python --version 2>&1
$match = [regex]::Match($pyVer, "(\d+)\.(\d+)")
$major = [int]$match.Groups[1].Value
$minor = [int]$match.Groups[2].Value
if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
    Write-Host "[!] Wymagany Python 3.11+. Zainstalowano: $pyVer" -ForegroundColor Red
    Write-Host "    Pobierz nowsza wersje: https://python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] $pyVer" -ForegroundColor Green

# --- ZALEŻNOŚCI PROJEKTU ---
Write-Host ""
$depsOk = (python -c "from src.config import load_config; from src.scraper import scrape_sales_logs; import openpyxl; print('ok')" 2>&1) -eq "ok"
if ($depsOk) {
    Write-Host "[OK] Zaleznosci projektu juz zainstalowane" -ForegroundColor Green
} else {
    Write-Host "[*] Instalacja zaleznosci projektu..." -ForegroundColor Cyan
    pip install -e . 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Blad instalacji zaleznosci." -ForegroundColor Red
        pip install -e .
        exit 1
    }
    Write-Host "[OK] Zaleznosci zainstalowane" -ForegroundColor Green
}

# --- ZALEŻNOŚCI DEV (testy) ---
$devOk = (python -c "import pytest; import hypothesis; print('ok')" 2>&1) -eq "ok"
if ($devOk) {
    Write-Host "[OK] Zaleznosci deweloperskie juz zainstalowane" -ForegroundColor Green
} else {
    Write-Host "[*] Instalacja zaleznosci deweloperskich..." -ForegroundColor Cyan
    pip install -e ".[dev]" 2>&1 | Out-Null
    Write-Host "[OK] Zaleznosci deweloperskie zainstalowane" -ForegroundColor Green
}

# --- PLAYWRIGHT CHROMIUM ---
Write-Host ""
$crOk = (python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('ok')" 2>&1) -eq "ok"
if ($crOk) {
    Write-Host "[OK] Chromium (Playwright) juz zainstalowany" -ForegroundColor Green
} else {
    Write-Host "[*] Instalacja przegladarki Chromium..." -ForegroundColor Cyan
    python -m playwright install chromium 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Blad instalacji Chromium." -ForegroundColor Red
        python -m playwright install chromium
        exit 1
    }
    Write-Host "[OK] Chromium zainstalowany" -ForegroundColor Green
}

# --- CONFIG.TOML ---
Write-Host ""
if (Test-Path "config.toml") {
    Write-Host "[OK] config.toml istnieje" -ForegroundColor Green
} else {
    Write-Host "[!] Brak config.toml" -ForegroundColor Yellow
    Write-Host "    Wykonaj:" -ForegroundColor Yellow
    Write-Host "    copy config.toml.example config.toml" -ForegroundColor White
    Write-Host "    notepad config.toml" -ForegroundColor White
    Write-Host "    Uzupelnij login, haslo i PIN." -ForegroundColor Yellow
}

# --- GOTOWE ---
Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Instalacja zakonczona!"
Write-Host ""
Write-Host "  Nastepny krok:"
Write-Host "  .\deployment\metin_hard_doctor.ps1" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
