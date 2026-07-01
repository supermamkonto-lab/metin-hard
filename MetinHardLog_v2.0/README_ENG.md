# METIN HARD LOG (v2.0)

Sales log exporter for the Metin2 UCP panel ([projekt-hard.eu/ucp](https://projekt-hard.eu/ucp)) to an Excel (XLSX) file.

*(Polska wersja: [README_PL.md](README_PL.md))*

### What's new in v2.0

- Choose which characters to fetch, and the export mode (one file / separate files)
- Progress bar and colored log during fetching (errors in red, success in gold)
- In-window sales summary after completion (total value, top 5 items) — no need to open the XLSX
- Automatic retry (up to 3x) on transient network timeouts
- Scheduled daily auto-fetch via Windows Task Scheduler (Advanced menu)
- The program makes no system sounds except for genuine errors

---

## How to run it?

**Double-click `!URUCHOM_PROGRAM.cmd`** in this folder.

That's it — the program window opens. Everything else happens in the window, not in a console.

---

## First run

The first time you run it (or whenever something is missing on the system), the program:

1. Automatically checks your computer's environment — Python, Playwright, openpyxl, Chromium, the config file.
2. If anything is missing, **it shows a window listing the missing pieces** and asks whether to install them automatically.
3. Clicking **Yes** runs the installation in the background, with live progress shown in the "Progress" panel.
4. After installation, fill in your login details via the **Configuration** button (username, password, PIN, output folder).

`!URUCHOM_PROGRAM.cmd` automatically finds an installed Python on the machine (it works across different Windows 10/11 setups and different pre-existing Python versions) — no manual configuration needed.

The one requirement the program cannot fix by itself: **Python 3.11 or newer must actually be installed**. If it isn't, `!URUCHOM_PROGRAM.cmd` shows a message with a download link (https://www.python.org/downloads/ — make sure to check "Add Python to PATH" during installation).

---

## Main window

| Element | Purpose |
|---|---|
| **Environment status** | Status indicators showing whether everything is ready |
| **Fetch sales logs** | Main button — logs into UCP, finds characters, lets you pick which ones to fetch, and saves the result as XLSX |
| **Configuration** | Form with login details and the output folder |
| **Repair / install environment** | Manually trigger installation/repair at any time |
| **Output folder** | Opens the folder containing generated XLSX files |
| **Progress** | Live console — shows exactly what the program is doing right now |

The **Advanced** menu (project tests, dependency update) and **Help** menu (about, documentation) are available from the top menu bar.

---

## What does the program do, step by step?

1. Logs into [https://projekt-hard.eu/ucp](https://projekt-hard.eu/ucp) using the credentials from Configuration.
2. Detects all characters on the account (1-4) and saves their names to `config.toml`.
3. **Shows a window listing the detected characters** — check the ones you want logs for, or choose **Exit** to cancel the whole operation without fetching anything.
4. If you checked **2 or more** characters, the program asks: **one combined XLSX file for everyone, or a separate file per character?**
5. For each selected character it fetches the sales logs (offline shop) — if a character has no logs, the program automatically moves on to the next one.
6. Saves the result to one or more **XLSX** files, depending on your choice in step 4.
7. File name: `CHARACTER_DD_MM_YYYY_HH_MM.xlsx` (fetch date and time), or `WSZYSTKIE_POSTACIE_DD_MM_YYYY_HH_MM.xlsx` for a combined file with multiple characters.

### XLSX columns

| Column | Description |
|---|---|
| Postać (Character) | Name of the character the entry belongs to |
| Nazwa przedmiotu (Item name) | Name of the sold item |
| Ilość (Quantity) | Number of units sold |
| Cena (Price) | Transaction price with thousands separators, e.g. `125.000.000,00` |
| Typ ceny (Price type) | Yang / Gold Bar |
| Data i godzina (Date and time) | Transaction date and time (`HH:MM YYYY-MM-DD` format) |

The Price column is stored as text with the separators baked in (`.` every three digits, `,` before the cents) — this keeps it looking identical on every computer regardless of regional settings (Excel renders a genuinely numeric cell's separator according to the local Windows settings, so it would otherwise look different from machine to machine).

---

## Folder structure

```
MetinHardLog/
├── !URUCHOM_PROGRAM.cmd   <- THIS FILE STARTS THE PROGRAM
├── gui.py                  program window (Tkinter)
├── main.py                  log-fetching logic (called by the GUI)
├── config.toml              your login details (do not share this file!)
├── config.toml.example     configuration template
├── src/                     source code (config, auth, scraper, export...)
├── tests/                   automated project tests
├── launcher/                helper scripts (advanced, optional)
├── output/                  generated XLSX files land here
├── logs/                    text log of every run
├── README_PL.md             Polish version
└── README_ENG.md            this file
```

---

## Troubleshooting

- **The program doesn't open when double-clicking `!URUCHOM_PROGRAM.cmd`** — usually means Python is missing. Install Python 3.11+ from python.org, checking "Add Python to PATH", and try again.
- **The "Environment status" section shows a red error** — click "Repair / install environment" in the program window.
- **Login error** — check your details in Configuration (username, password, PIN must be exactly 5 characters).
- **No logs for a character** — normal if that character never sold anything through the offline shop; the program skips it and continues.
- **I chose "separate file per character" but only got one file** — that's intentional: if only one of the selected characters actually had data, only that character's file is created.
- A detailed log of every run is available in the `logs/` folder.

---

## Requirements

- Windows 10 or 11
- Python 3.11 or newer (added to PATH automatically by the python.org installer)
- Internet connection (for login and for the one-time dependency install)

---

Powered by Lewsonik (c) 2026
Contact: supermamkonto@gmail.com
GitHub: https://github.com/supermamkonto-lab/metin-hard
