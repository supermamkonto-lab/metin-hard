# Metin HARD Log Extractor — Environment Doctor
# Diagnostyka gotowości środowiska do uruchomienia programu.
# Użycie: .\deployment\metin_hard_doctor.ps1

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Metin HARD Doctor"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true
$projectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectDir

function Check($name, $condition, $fixMessage) {
    $dots = "." * (30 - $name.Length)
    if ($condition) {
        Write-Host "  $name $dots OK" -ForegroundColor Green
    } else {
        Write-Host "  $name $dots FAIL" -ForegroundColor Red
        if ($fixMessage) {
            Write-Host "    >> $fixMessage" -ForegroundColor Yellow
            Write-Host ""
        }
        $script:allOk = $false
    }
}

# --- SYSTEM ---
$winVer = [System.Environment]::OSVersion.Version
Check "Windows" ($winVer.Build -ge 22000) "Wymagany Windows 11 (build 22000+). Zainstaluj Windows 11."

# --- PYTHON ---
$python = Get-Command python -ErrorAction SilentlyContinue
Check "Python" ($null -ne $python) "Zainstaluj Python 3.11+ ze strony: https://python.org/downloads/ (zaznacz 'Add to PATH')"

$pyVersionOk = $false
if ($python) {
    $pyVer = python --version 2>&1
    $match = [regex]::Match($pyVer, "(\d+)\.(\d+)")
    if ($match.Success) {
        $pyVersionOk = ([int]$match.Groups[1].Value -ge 3) -and ([int]$match.Groups[2].Value -ge 11)
    }
}
if ($python) {
    Check "Python 3.11+" $pyVersionOk "Wymagany Python 3.11+. Obecna wersja: $pyVer. Pobierz nowsza: https://python.org/downloads/"
}

$pip = Get-Command pip -ErrorAction SilentlyContinue
Check "pip" ($null -ne $pip) "pip powinien byc zainstalowany razem z Python. Reinstaluj Python z zaznaczonym 'pip'."

# --- BIBLIOTEKI ---
$pwOk = $false
if ($python) { $pwOk = (python -c "import playwright; print('ok')" 2>&1) -eq "ok" }
Check "Playwright" $pwOk "Uruchom: pip install -e .   (w katalogu projektu)"

$oxOk = $false
if ($python) { $oxOk = (python -c "import openpyxl; print('ok')" 2>&1) -eq "ok" }
Check "openpyxl" $oxOk "Uruchom: pip install -e .   (w katalogu projektu)"

$crOk = $false
if ($python -and $pwOk) {
    $crOk = (python -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('ok')" 2>&1) -eq "ok"
}
Check "Chromium" $crOk "Uruchom: python -m playwright install chromium"

# --- PROJEKT ---
$modsOk = $false
if ($python) {
    $modsOk = (python -c "from src.config import load_config; from src.auth import login; from src.characters import detect_characters; from src.scraper import scrape_sales_logs; print('ok')" 2>&1) -eq "ok"
}
Check "Moduly projektu" $modsOk "Uruchom: pip install -e .   (w katalogu projektu)"

# --- KONFIGURACJA ---
$configExists = Test-Path "config.toml"
Check "config.toml" $configExists "Skopiuj: copy config.toml.example config.toml   Nastepnie uzupelnij dane logowania."

$configValid = $false
if ($configExists -and $python) {
    $configValid = (python -c "from src.config import load_config; from pathlib import Path; load_config(Path('config.toml')); print('ok')" 2>&1) -eq "ok"
}
if ($configExists) {
    Check "config.toml poprawny" $configValid "Sprawdz config.toml: czy login, haslo, pin i folder sa wypelnione poprawnie."
}

# --- FOLDER WYJŚCIOWY ---
$folderOk = $false
$writeOk = $false
if ($configExists -and $configValid -and $python) {
    $outDir = python -c "from src.config import load_config; from pathlib import Path; c=load_config(Path('config.toml')); print(c.output_dir)" 2>&1
    $folderOk = Test-Path $outDir
    if ($folderOk) {
        $testFile = Join-Path $outDir "_doctor_test.tmp"
        try {
            "test" | Out-File $testFile -ErrorAction Stop
            Remove-Item $testFile -ErrorAction SilentlyContinue
            $writeOk = $true
        } catch {}
    }
}
Check "Folder wynikowy" $folderOk "Utworz folder wskazany w config.toml: mkdir `"$outDir`""
if ($folderOk) {
    Check "Test zapisu" $writeOk "Brak uprawnien zapisu do folderu: $outDir. Sprawdz uprawnienia."
}

# --- SIEĆ ---
$internetOk = $false
try {
    $resp = Invoke-WebRequest -Uri "https://www.google.com" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    $internetOk = ($resp.StatusCode -eq 200)
} catch {}
Check "Internet" $internetOk "Brak dostepu do Internetu. Sprawdz polaczenie sieciowe."

$ucpOk = $false
try {
    $resp = Invoke-WebRequest -Uri "https://projekt-hard.eu/ucp" -UseBasicParsing -TimeoutSec 15 -ErrorAction Stop
    $ucpOk = ($resp.StatusCode -eq 200)
} catch {}
Check "UCP" $ucpOk "Strona https://projekt-hard.eu/ucp jest niedostepna. Sprobuj ponownie pozniej."

# --- WYNIK ---
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "  STATUS: READY" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Srodowisko gotowe. Mozesz uruchomic program:" -ForegroundColor Green
    Write-Host "  .\deployment\run.ps1" -ForegroundColor White
} else {
    Write-Host "  STATUS: NOT READY" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Napraw powyzsze problemy i uruchom ponownie:" -ForegroundColor Yellow
    Write-Host "  .\deployment\metin_hard_doctor.ps1" -ForegroundColor White
}
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
