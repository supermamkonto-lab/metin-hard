# Metin HARD Log Extractor — Uruchomienie programu
# Przed uruchomieniem sprawdza gotowość środowiska.

$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectDir

# --- PRE-CHECK: Szybka weryfikacja środowiska ---
$ready = $true

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $ready = $false }

# Moduły projektu
if ($python) {
    $modsOk = (python -c "from src.config import load_config; print('ok')" 2>&1) -eq "ok"
    if (-not $modsOk) { $ready = $false }
}

# config.toml
if (-not (Test-Path "config.toml")) { $ready = $false }

# Walidacja config
if ($ready) {
    $cfgOk = (python -c "from src.config import load_config; from pathlib import Path; load_config(Path('config.toml')); print('ok')" 2>&1) -eq "ok"
    if (-not $cfgOk) { $ready = $false }
}

if (-not $ready) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host "  Srodowisko nie jest gotowe." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Uruchom diagnostyke:" -ForegroundColor Yellow
    Write-Host "  .\deployment\metin_hard_doctor.ps1" -ForegroundColor White
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# --- URUCHOMIENIE PROGRAMU ---
Write-Host ""
Write-Host "Metin HARD Log Extractor — Start" -ForegroundColor Cyan
Write-Host ""

python main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Program zakonczyl dzialanie pomyslnie." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Program zakonczyl dzialanie z bledem (kod: $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "Uruchom diagnostyke: .\deployment\metin_hard_doctor.ps1" -ForegroundColor Yellow
}
Write-Host ""
