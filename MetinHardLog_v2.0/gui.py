"""METIN HARD LOG -- graficzny interfejs uzytkownika (Tkinter). v2.0

Zastepuje tekstowe menu !URUCHOM_PROGRAM.cmd oknem Windows. Przy starcie
sprawdza srodowisko (Python, Playwright, openpyxl, Chromium, config.toml)
i - jesli czegos brakuje - pyta uzytkownika, czy zainstalowac to od razu.
Pozwala skonfigurowac dane logowania, wybrac ktore postacie pobrac (i czy
do jednego pliku czy osobno), oraz pobrac logi sprzedazy z panelu UCP,
pokazujac postep na biezaco w oknie.
"""

from __future__ import annotations

import contextlib
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Uwaga: "main" (scraper) importuje playwright/openpyxl na poziomie modulu.
# Na swiezej maszynie (przed pierwsza instalacja) te pakiety moga nie
# istniec - import "main" jest wiec celowo odroczony do momentu klikniecia
# "Pobierz logi", zeby okno GUI dalo sie otworzyc i pokazac diagnostyke
# nawet gdy srodowisko jeszcze nie jest gotowe (pythonw.exe nie ma konsoli,
# wiec blad importu na starcie bylby caly czas niewidoczny dla uzytkownika).
from src.config_writer import save_credentials  # noqa: E402

APP_TITLE = "METIN HARD LOG"
APP_VERSION = "v2.0"
CONFIG_PATH = Path("config.toml")

# --- Paleta kolorow -- nawiazuje do klimatu projekt-hard.eu/ucp (ciemne tlo,
# bordowo-zlota gora, zielone przyciski) - kolory zmierzone na stronie logowania,
# BEZ kopiowania jakiejkolwiek grafiki/ilustracji z serwisu. ---
BG_DARK = "#141210"
BG_PANEL = "#1C1A18"
BG_ENTRY = "#242220"
BORDER_COLOR = "#3A3835"
TEXT_LIGHT = "#C9C2C2"
TEXT_MUTED = "#8A8480"
GOLD = "#D9A441"
GOLD_DARK = "#B8842E"
BRAND_GREEN = "#3A7A3E"
BRAND_GREEN_DARK = "#274F29"
HEADER_TOP = "#3A1210"
HEADER_BOTTOM = "#120806"
CONSOLE_BG = "#0B0D0A"
CONSOLE_FG = "#7CE28C"
OK_COLOR = "#59C15E"
BAD_COLOR = "#E4685D"
PENDING_COLOR = "#8A8480"


# --- Funkcje diagnostyczne (kazda zwraca (ok: bool, opis: str)) ---


def check_python_version() -> tuple[bool, str]:
    v = sys.version_info
    ok = v >= (3, 11)
    return ok, f"{v.major}.{v.minor}.{v.micro}" + ("" if ok else " (wymagane 3.11+)")


def check_module(module_name: str) -> tuple[bool, str]:
    try:
        __import__(module_name)
        return True, "zainstalowany"
    except ImportError:
        return False, "brak -- wymaga instalacji"


def check_chromium() -> tuple[bool, str]:
    try:
        from playwright.sync_api import sync_playwright

        p = sync_playwright().start()
        try:
            b = p.chromium.launch(headless=True)
            b.close()
        finally:
            p.stop()
        return True, "OK"
    except Exception as e:  # noqa: BLE001 - chcemy pokazac dowolny blad uzytkownikowi
        return False, str(e).splitlines()[0][:70]


def check_config() -> tuple[bool, str]:
    if not CONFIG_PATH.exists():
        return False, "brak pliku -- uzupelnij w Konfiguracji"
    try:
        from src.config import load_config

        load_config(CONFIG_PATH)
        return True, "poprawny"
    except Exception as e:  # noqa: BLE001
        return False, str(getattr(e, "message", e))[:70]


DIAGNOSTIC_CHECKS: list[tuple[str, object]] = [
    ("Python 3.11+", check_python_version),
    ("Playwright", lambda: check_module("playwright")),
    ("openpyxl", lambda: check_module("openpyxl")),
    ("Chromium", check_chromium),
    ("config.toml", check_config),
]

# Nazwy diagnostyk, ktore instalacja srodowiska (pip/playwright) potrafi
# naprawic automatycznie. "config.toml" nie jest tu wliczony - to naprawia
# formularz Konfiguracji, nie instalacja pakietow.
INSTALLABLE_CHECKS = {"Python 3.11+": False, "Playwright": True, "openpyxl": True, "Chromium": True}


def _draw_vertical_gradient(canvas: tk.Canvas, width: int, height: int, top: str, bottom: str) -> None:
    """Rysuje pionowy gradient kolorow na Canvas (od 'top' do 'bottom')."""
    canvas.delete("gradient")
    if width <= 0 or height <= 0:
        return
    r1, g1, b1 = (c // 256 for c in canvas.winfo_rgb(top))
    r2, g2, b2 = (c // 256 for c in canvas.winfo_rgb(bottom))
    for i in range(height):
        t = i / max(height - 1, 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="gradient")
    canvas.tag_lower("gradient")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _blend_left_edge_into_gradient(
    img: tk.PhotoImage, top_color: str, bottom_color: str, fade_width: int
) -> None:
    """Wtapia lewa krawedz obrazu (in-place) w pionowy gradient tla, zeby
    grafika 'wchodzila' w tlo zamiast miec twarda, prostokatna ramke -
    profesjonalny uklad graficzny zamiast wycietego prostokata."""
    w, h = img.width(), img.height()
    fade_width = min(fade_width, w)
    if fade_width <= 0:
        return
    top_rgb = _hex_to_rgb(top_color)
    bottom_rgb = _hex_to_rgb(bottom_color)

    rows = []
    for y in range(h):
        t = y / max(h - 1, 1)
        bg_r = top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * t
        bg_g = top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * t
        bg_b = top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * t
        row = []
        for x in range(fade_width):
            r, g, b = img.get(x, y)
            blend = x / fade_width
            nr = int(bg_r + (r - bg_r) * blend)
            ng = int(bg_g + (g - bg_g) * blend)
            nb = int(bg_b + (b - bg_b) * blend)
            row.append(f"#{nr:02x}{ng:02x}{nb:02x}")
        rows.append(row)
    img.put(rows, to=(0, 0))


def _show_silent(
    parent: tk.Misc, title: str, message: str, image: tk.PhotoImage | None = None
) -> None:
    """Pokazuje komunikat informacyjny BEZ systemowego dzwieku Windows
    (w odroznieniu od messagebox.showinfo/showwarning, ktore zawsze pipia).
    Dzwiek jest celowo zarezerwowany tylko dla prawdziwych bledow
    (messagebox.showerror)."""
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.configure(bg=BG_DARK)
    dlg.resizable(False, False)
    frame = ttk.Frame(dlg, padding=20)
    frame.pack(fill="both", expand=True)
    if image is not None:
        ttk.Label(frame, image=image, background=BG_DARK).pack(pady=(0, 12))
    ttk.Label(frame, text=message, wraplength=380, justify="left").pack(anchor="w")
    ttk.Button(frame, text="OK", command=dlg.destroy, style="Accent.TButton").pack(pady=(16, 0), fill="x")
    dlg.transient(parent)
    dlg.grab_set()
    dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)
    parent.wait_window(dlg)


def _ask_silent_yesno(parent: tk.Misc, title: str, message: str) -> bool:
    """Pytanie Tak/Nie BEZ systemowego dzwieku Windows."""
    result = {"value": False}
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.configure(bg=BG_DARK)
    dlg.resizable(False, False)
    frame = ttk.Frame(dlg, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=message, wraplength=380, justify="left").pack(anchor="w")

    def _yes():
        result["value"] = True
        dlg.destroy()

    def _no():
        result["value"] = False
        dlg.destroy()

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(16, 0))
    ttk.Button(btns, text="Tak", command=_yes, style="Accent.TButton").pack(side="left", expand=True, fill="x", padx=(0, 4))
    ttk.Button(btns, text="Nie", command=_no, style="Secondary.TButton").pack(side="left", expand=True, fill="x", padx=(4, 0))

    dlg.transient(parent)
    dlg.grab_set()
    dlg.protocol("WM_DELETE_WINDOW", _no)
    parent.wait_window(dlg)
    return result["value"]


class QueueWriter:
    """Plik-podobny obiekt przekazujacy print()/logi do kolejki GUI."""

    def __init__(self, q: "queue.Queue"):
        self._q = q

    def write(self, text: str) -> None:
        if text:
            self._q.put(("log", text))

    def flush(self) -> None:
        pass


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry("780x660")
        self.minsize(700, 580)
        self.configure(bg=BG_DARK)

        self.events: "queue.Queue" = queue.Queue()
        self.diag_labels: dict[str, ttk.Label] = {}
        self.diag_ok = {name: None for name, _ in DIAGNOSTIC_CHECKS}
        self.scrape_running = False
        self._wizard_shown = False
        self._last_entries: list = []
        self._last_created_files: list = []
        self._about_logo_image: tk.PhotoImage | None = None

        self._build_style()
        self._build_menu()
        self._build_layout()

        self.after(100, self._poll_events)
        self.run_diagnostics()

    # --- styl / wyglad ---

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_DARK, foreground=TEXT_LIGHT)
        style.configure("TCheckbutton", background=BG_DARK, foreground=TEXT_LIGHT)
        style.map("TCheckbutton", background=[("active", BG_DARK)])
        style.configure("TRadiobutton", background=BG_DARK, foreground=TEXT_LIGHT)
        style.map("TRadiobutton", background=[("active", BG_DARK)])

        style.configure(
            "Card.TLabelframe", background=BG_PANEL, bordercolor=BORDER_COLOR, relief="solid",
        )
        style.configure(
            "Card.TLabelframe.Label", background=BG_PANEL, foreground=GOLD,
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("Card.TFrame", background=BG_PANEL)
        style.configure("Card.TLabel", background=BG_PANEL, foreground=TEXT_LIGHT)
        style.configure("CardBold.TLabel", background=BG_PANEL, foreground=TEXT_LIGHT, font=("Segoe UI", 9, "bold"))

        style.configure(
            "Accent.TButton", font=("Segoe UI", 13, "bold"), foreground="white",
            background=BRAND_GREEN, padding=12, borderwidth=0,
        )
        style.map(
            "Accent.TButton",
            background=[("disabled", "#4A5A4B"), ("active", BRAND_GREEN_DARK)],
            foreground=[("disabled", "#B9C2B9")],
        )

        style.configure(
            "Secondary.TButton", font=("Segoe UI", 9), padding=8,
            background=BG_ENTRY, foreground=TEXT_LIGHT, borderwidth=1,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#32302D")],
            bordercolor=[("!disabled", BORDER_COLOR)],
        )

        style.configure(
            "TEntry", fieldbackground=BG_ENTRY, foreground=TEXT_LIGHT, insertcolor=TEXT_LIGHT,
            bordercolor=BORDER_COLOR,
        )

        style.configure(
            "Accent.Horizontal.TProgressbar", background=BRAND_GREEN, troughcolor=BG_ENTRY,
            bordercolor=BORDER_COLOR, lightcolor=BRAND_GREEN, darkcolor=BRAND_GREEN,
        )

    # --- budowa interfejsu ---

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        plik_menu = tk.Menu(menubar, tearoff=0)
        plik_menu.add_command(label="Zakoncz", command=self.destroy)
        menubar.add_cascade(label="Plik", menu=plik_menu)

        zaawansowane = tk.Menu(menubar, tearoff=0)
        zaawansowane.add_command(label="Uruchom testy projektu (pytest)", command=self.run_tests)
        zaawansowane.add_command(label="Zaktualizuj zaleznosci", command=self.run_update)
        zaawansowane.add_separator()
        zaawansowane.add_command(
            label="Harmonogram automatycznych pobran...", command=self.open_schedule_dialog
        )
        menubar.add_cascade(label="Zaawansowane", menu=zaawansowane)

        pomoc = tk.Menu(menubar, tearoff=0)
        pomoc.add_command(label="Informacje o programie", command=self.show_info)
        pomoc.add_command(label="Dokumentacja", command=self.open_docs)
        menubar.add_cascade(label="Pomoc", menu=pomoc)

        self.config(menu=menubar)

    def _build_layout(self) -> None:
        # --- naglowek: gradient bordowo-czarny + zloty tytul, w klimacie
        # strony logowania UCP, z grafika postaci po prawej stronie ---
        self.header_char_image = self._load_image("ph1.png", subsample=2)
        if self.header_char_image is not None:
            _blend_left_edge_into_gradient(self.header_char_image, HEADER_TOP, HEADER_BOTTOM, fade_width=90)
        self.header_logo_image = self._load_image("ph2.png", subsample=4)

        self.header_canvas = tk.Canvas(self, height=140, highlightthickness=0, bd=0, bg=HEADER_BOTTOM)
        self.header_canvas.pack(fill="x", side="top")
        self.header_canvas.bind("<Configure>", self._redraw_header)

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        diag_frame = ttk.LabelFrame(body, text="Stan srodowiska", style="Card.TLabelframe", padding=14)
        diag_frame.pack(fill="x", pady=(0, 12))
        for name, _ in DIAGNOSTIC_CHECKS:
            row = ttk.Frame(diag_frame, style="Card.TFrame")
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=name, width=16, style="CardBold.TLabel").pack(side="left")
            lbl = ttk.Label(row, text="●  sprawdzam...", background=BG_PANEL, foreground=PENDING_COLOR)
            lbl.pack(side="left")
            self.diag_labels[name] = lbl

        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=(0, 12))

        self.btn_scrape = ttk.Button(
            actions,
            text="▶   Pobierz logi sprzedazy",
            command=self.run_scrape,
            state="disabled",
            style="Accent.TButton",
        )
        self.btn_scrape.pack(fill="x", pady=(0, 10), ipady=6)

        self.progress = ttk.Progressbar(
            actions, mode="indeterminate", style="Accent.Horizontal.TProgressbar"
        )
        # ukryty dopoki nie trwa pobieranie - patrz run_scrape()/_on_scrape_done()

        self.row2 = row2 = ttk.Frame(actions)
        row2.pack(fill="x")
        ttk.Button(
            row2, text="Konfiguracja", command=self.open_config_dialog, style="Secondary.TButton"
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_install = ttk.Button(
            row2, text="Napraw / zainstaluj srodowisko", command=self.run_install,
            style="Secondary.TButton",
        )
        self.btn_install.pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(
            row2, text="Folder wynikow", command=self.open_output_folder, style="Secondary.TButton"
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

        log_frame = ttk.LabelFrame(body, text="Przebieg", style="Card.TLabelframe", padding=8)
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            log_frame, height=12, state="disabled", wrap="word",
            background=CONSOLE_BG, foreground=CONSOLE_FG, insertbackground=CONSOLE_FG,
            font=("Consolas", 10), relief="flat", padx=10, pady=8,
        )
        self.log_text.tag_configure("error", foreground=BAD_COLOR)
        self.log_text.tag_configure("success", foreground=GOLD)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- stopka w tych samych barwach co naglowek ---
        footer = tk.Frame(self, bg=HEADER_BOTTOM, height=28)
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=GOLD_DARK, height=1).pack(fill="x", side="top")
        tk.Label(
            footer, text=f"{APP_TITLE} {APP_VERSION}  -  Powered by Lewsonik (c) 2026",
            bg=HEADER_BOTTOM, fg=GOLD_DARK, font=("Segoe UI", 8),
        ).pack(anchor="w", padx=16, pady=4)

    @staticmethod
    def _load_image(filename: str, subsample: int = 1) -> tk.PhotoImage | None:
        """Wczytuje PNG z src/ (natywnie, Tk 8.6+, bez zaleznosci od Pillow).
        Zwraca None jesli plik nie istnieje - dekoracja jest opcjonalna."""
        path = Path(__file__).resolve().parent / "src" / filename
        if not path.exists():
            return None
        try:
            img = tk.PhotoImage(file=str(path))
            if subsample > 1:
                img = img.subsample(subsample, subsample)
            return img
        except tk.TclError:
            return None

    def _redraw_header(self, event=None) -> None:
        width = event.width if event else self.header_canvas.winfo_width()
        height = event.height if event else self.header_canvas.winfo_height()
        _draw_vertical_gradient(self.header_canvas, width, height, HEADER_TOP, HEADER_BOTTOM)
        self.header_canvas.delete("headertext")
        if self.header_char_image is not None:
            self.header_canvas.create_image(
                width - 10, height // 2, anchor="e", image=self.header_char_image, tags="headertext"
            )
        self.header_canvas.create_text(
            20, 34, anchor="w", text=APP_TITLE, fill=GOLD,
            font=("Georgia", 22, "bold"), tags="headertext",
        )
        self.header_canvas.create_text(
            20, 68, anchor="w",
            text=f"Eksporter logow sprzedazy  {APP_VERSION}  -  projekt-hard.eu/ucp",
            fill=TEXT_LIGHT, font=("Segoe UI", 9), tags="headertext",
        )
        if self.header_logo_image is not None:
            self.header_canvas.create_image(
                20, 105, anchor="w", image=self.header_logo_image, tags="headertext"
            )
        self.header_canvas.create_line(
            0, height - 2, width, height - 2, fill=GOLD_DARK, width=2, tags="headertext",
        )

    # --- logowanie do panelu tekstowego ---

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        # Kolorowanie linii wedlug tresci: bledy na czerwono, sukces na
        # zloto, reszta domyslnym zielonym kolorem konsoli.
        for line in text.splitlines(keepends=True):
            lowered = line.lower()
            if "blad" in lowered:
                tag = "error"
            elif "sukces" in lowered or "zakonczona pomyslnie" in lowered or "pomyslnie" in lowered:
                tag = "success"
            else:
                tag = ""
            self.log_text.insert("end", line, tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _poll_events(self) -> None:
        try:
            while True:
                kind, *payload = self.events.get_nowait()
                if kind == "log":
                    self._append_log(payload[0])
                elif kind == "diag":
                    name, ok, detail = payload
                    self._set_diag(name, ok, detail)
                elif kind == "diag_done":
                    self._update_scrape_button_state()
                    self._maybe_show_first_run_wizard()
                elif kind == "scrape_done":
                    self._on_scrape_done(payload[0])
                elif kind == "task_done":
                    label, ok = payload
                    self._append_log(f"\n[{label}] zakonczono {'poprawnie' if ok else 'z bledem'}.\n")
                    self.run_diagnostics()
        except queue.Empty:
            pass
        self.after(100, self._poll_events)

    def _set_diag(self, name: str, ok: bool, detail: str) -> None:
        lbl = self.diag_labels[name]
        lbl.configure(
            text=("●  OK - " if ok else "●  BLAD - ") + detail,
            foreground=OK_COLOR if ok else BAD_COLOR,
        )
        self.diag_ok[name] = ok

    def _update_scrape_button_state(self) -> None:
        all_ok = all(self.diag_ok.values())
        if not self.scrape_running:
            self.btn_scrape.configure(state="normal" if all_ok else "disabled")

    # --- kreator pierwszego uruchomienia / naprawy srodowiska ---

    def _maybe_show_first_run_wizard(self) -> None:
        if self._wizard_shown:
            return
        self._wizard_shown = True

        missing = [name for name, ok in self.diag_ok.items() if ok is False]
        if not missing:
            return

        installable_missing = [m for m in missing if INSTALLABLE_CHECKS.get(m)]
        details = "\n".join(f"   x  {name}" for name in missing)

        if not installable_missing:
            # Brakuje np. wersji Pythona lub poprawnego config.toml - tego
            # instalacja pakietow nie naprawi, wiec tylko informujemy.
            _show_silent(
                self,
                APP_TITLE,
                "Program wykryl problemy ze srodowiskiem, ktorych nie da sie "
                "naprawic automatyczna instalacja:\n\n" + details + "\n\n"
                "Sprawdz szczegoly powyzej w sekcji 'Stan srodowiska' i popraw je "
                "recznie (np. zainstaluj nowszego Pythona albo uzupelnij Konfiguracje).",
            )
            return

        answer = _ask_silent_yesno(
            self,
            APP_TITLE,
            "To wyglada na pierwsze uruchomienie programu na tym komputerze.\n\n"
            "Wykryto brakujace elementy wymagane do dzialania:\n\n"
            + details
            + "\n\n"
            "Czy zainstalowac je teraz automatycznie? (wymaga internetu, "
            "moze potrwac kilka minut)",
        )
        if answer:
            self.run_install()

    # --- diagnostyka ---

    def run_diagnostics(self) -> None:
        for name, _ in DIAGNOSTIC_CHECKS:
            self.diag_labels[name].configure(text="●  sprawdzam...", foreground=PENDING_COLOR)
            self.diag_ok[name] = None
        threading.Thread(target=self._diagnostics_worker, daemon=True).start()

    def _diagnostics_worker(self) -> None:
        for name, func in DIAGNOSTIC_CHECKS:
            ok, detail = func()
            self.events.put(("diag", name, ok, detail))
        self.events.put(("diag_done",))

    # --- pobieranie logow ---

    def run_scrape(self) -> None:
        if self.scrape_running:
            return
        self.scrape_running = True
        self.btn_scrape.configure(state="disabled", text="Pobieranie w toku...")
        self.progress.pack(fill="x", pady=(0, 10), before=self.row2)
        self.progress.start(12)
        self._append_log("\n" + "=" * 50 + "\n")
        threading.Thread(target=self._scrape_worker, daemon=True).start()

    def _ask_on_main_thread(self, factory):
        """Uruchamia 'factory' (tworzy i pokazuje okno modalne) na watku
        glownym Tk i blokuje watek wywolujacy (roboczy) do czasu jej
        zamkniecia. Zwraca to, co zwrocilo 'factory'. Bezpieczne watkowo -
        Tkinter wolno obslugiwac tylko z watku glownego."""
        result_box: dict = {}
        done = threading.Event()

        def runner():
            try:
                result_box["value"] = factory()
            finally:
                done.set()

        self.after(0, runner)
        done.wait()
        return result_box.get("value")

    def _character_selector(self, characters):
        """Wywolywane z watku roboczego (przez main.main) po wykryciu
        postaci. Pokazuje uzytkownikowi okno wyboru postaci, a jesli
        wybrano 2+ postacie - dodatkowe pytanie o tryb eksportu."""

        def show_selection():
            dialog = CharacterSelectionDialog(self, characters)
            self.wait_window(dialog)
            return dialog.result

        selected = self._ask_on_main_thread(show_selection)
        if not selected:
            return None
        if len(selected) <= 1:
            return (selected, True)

        def show_mode():
            dialog = ExportModeDialog(self, len(selected))
            self.wait_window(dialog)
            return dialog.result

        combined = self._ask_on_main_thread(show_mode)
        if combined is None:
            return None
        return (selected, combined)

    def _on_scrape_result(self, entries, created_files) -> None:
        """Wywolywane z watku roboczego (main.main) po eksporcie - tylko
        zapisuje dane, bez dotykania widgetow Tk (bezpieczne watkowo)."""
        self._last_entries = entries
        self._last_created_files = created_files

    def _scrape_worker(self) -> None:
        writer = QueueWriter(self.events)
        self._last_entries = []
        self._last_created_files = []
        try:
            with contextlib.redirect_stdout(writer):
                import main as scraper_main  # import odroczony - patrz komentarz na gorze pliku

                code = scraper_main.main(
                    character_selector=self._character_selector,
                    result_callback=self._on_scrape_result,
                )
        except Exception as e:  # noqa: BLE001
            self.events.put(("log", f"\nNIEOCZEKIWANY BLAD GUI: {e}\n"))
            code = 1
        self.events.put(("scrape_done", code))

    def _on_scrape_done(self, code: int) -> None:
        self.scrape_running = False
        self.btn_scrape.configure(text="▶   Pobierz logi sprzedazy")
        self.progress.stop()
        self.progress.pack_forget()
        self._update_scrape_button_state()
        if code == 0:
            if self._last_entries:
                SummaryDialog(self, self._last_entries, self._last_created_files)
            else:
                _show_silent(self, APP_TITLE, "Pobieranie zakonczone pomyslnie. Brak danych do eksportu.")
        elif code == 2:
            _show_silent(self, APP_TITLE, "Operacja przerwana - nie wybrano zadnej postaci.")
        else:
            messagebox.showerror(APP_TITLE, "Wystapil blad podczas pobierania. Sprawdz przebieg w oknie.")

    # --- konfiguracja ---

    def open_config_dialog(self) -> None:
        ConfigDialog(self)

    def open_schedule_dialog(self) -> None:
        ScheduleDialog(self)

    # --- instalacja / aktualizacja / testy (subprocess w tle) ---

    def run_install(self) -> None:
        self._run_subprocess_sequence(
            "Instalacja srodowiska",
            [
                [sys.executable, "-m", "pip", "install", "-e", "."],
                [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
                [sys.executable, "-m", "playwright", "install", "chromium"],
            ],
        )

    def run_update(self) -> None:
        self._run_subprocess_sequence(
            "Aktualizacja zaleznosci",
            [
                [sys.executable, "-m", "pip", "install", "-e", ".", "--upgrade"],
                [sys.executable, "-m", "playwright", "install", "chromium"],
            ],
        )

    def run_tests(self) -> None:
        self._run_subprocess_sequence(
            "Testy projektu", [[sys.executable, "-m", "pytest", "tests/", "-v"]]
        )

    def _run_subprocess_sequence(self, label: str, commands: list[list[str]]) -> None:
        self._append_log(f"\n=== {label} ===\n")
        threading.Thread(target=self._subprocess_worker, args=(label, commands), daemon=True).start()

    def _subprocess_worker(self, label: str, commands: list[list[str]]) -> None:
        ok = True
        for cmd in commands:
            self.events.put(("log", f"$ {' '.join(cmd)}\n"))
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                for line in proc.stdout:  # type: ignore[union-attr]
                    self.events.put(("log", line))
                proc.wait()
                if proc.returncode != 0:
                    ok = False
            except Exception as e:  # noqa: BLE001
                self.events.put(("log", f"BLAD: {e}\n"))
                ok = False
        self.events.put(("task_done", label, ok))

    # --- pomocnicze ---

    def open_output_folder(self) -> None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        try:
            os.startfile(output_dir)  # noqa: S606 - aplikacja Windows-only
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(APP_TITLE, f"Nie udalo sie otworzyc folderu: {e}")

    def open_docs(self) -> None:
        readme = Path("README_PL.md")
        if not readme.exists():
            readme = Path("README.md")
        if not readme.exists():
            _show_silent(self, APP_TITLE, "Nie znaleziono pliku README.")
            return
        try:
            os.startfile(readme)  # noqa: S606
        except Exception as e:  # noqa: BLE001
            messagebox.showerror(APP_TITLE, f"Nie udalo sie otworzyc dokumentacji: {e}")

    def show_info(self) -> None:
        if self._about_logo_image is None:
            self._about_logo_image = self._load_image("ph2.png", subsample=2)
        _show_silent(
            self,
            APP_TITLE,
            f"METIN HARD LOG - Eksporter Logow Sprzedazy\n"
            f"{APP_VERSION}\n\n"
            "Serwer: projekt-hard.eu\n"
            "Panel: https://projekt-hard.eu/ucp\n\n"
            "Format eksportu: XLSX (kolumna Cena - tekst z separatorami tysiecy)\n"
            "Nazwa pliku: POSTAC_DD_MM_RRRR_GG_MM\n\n"
            "Kolumny: Postac, Nazwa przedmiotu, Ilosc, Cena, Typ ceny, Data i godzina\n\n"
            "Mozna wybrac ktore postacie pobrac (1-4) oraz czy zapisac je\n"
            "do jednego wspolnego pliku, czy osobno dla kazdej postaci.\n\n"
            "------------------------------------------\n"
            "Powered by Lewsonik (c) 2026\n"
            "Kontakt: supermamkonto@gmail.com\n"
            "GitHub: https://github.com/supermamkonto-lab/metin-hard",
            image=self._about_logo_image,
        )


class CharacterSelectionDialog(tk.Toplevel):
    """Okno wyboru postaci do pobrania (1-4 postacie, zaznaczane ptaszkiem)."""

    def __init__(self, parent: App, characters) -> None:
        super().__init__(parent)
        self.title("Wybor postaci")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.result: list | None = None
        self.characters = characters

        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text=f"Znaleziono {len(characters)} posta{'c' if len(characters) == 1 else 'ci'}(e) na koncie.",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 4))
        ttk.Label(frame, text="Zaznacz, dla ktorych pobrac logi sprzedazy:").pack(anchor="w", pady=(0, 10))

        self.vars: list[tk.BooleanVar] = []
        for char in characters:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(frame, text=char.name, variable=var).pack(anchor="w", pady=2)
            self.vars.append(var)

        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(16, 0))
        ttk.Button(btns, text="Pobierz zaznaczone", command=self._confirm, style="Accent.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(btns, text="Wyjscie (przerwij)", command=self._cancel, style="Secondary.TButton").pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.grab_set()

    def _confirm(self) -> None:
        selected = [c for c, v in zip(self.characters, self.vars) if v.get()]
        if not selected:
            _show_silent(self, "Wybor postaci", "Zaznacz przynajmniej jedna postac albo wybierz Wyjscie.")
            return
        self.result = selected
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()


class ExportModeDialog(tk.Toplevel):
    """Pytanie o tryb eksportu, gdy wybrano 2 lub wiecej postaci."""

    def __init__(self, parent: App, character_count: int) -> None:
        super().__init__(parent)
        self.title("Tryb eksportu")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.result: bool | None = None

        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text=f"Wybrano {character_count} postacie. Jak zapisac wyniki?",
            font=("Segoe UI", 10, "bold"), wraplength=340,
        ).pack(anchor="w", pady=(0, 14))

        self.mode_var = tk.StringVar(value="combined")
        ttk.Radiobutton(
            frame, text="Jeden wspolny plik XLSX dla wszystkich postaci",
            variable=self.mode_var, value="combined",
        ).pack(anchor="w", pady=4)
        ttk.Radiobutton(
            frame, text="Osobny plik XLSX dla kazdej postaci",
            variable=self.mode_var, value="separate",
        ).pack(anchor="w", pady=4)

        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(16, 0))
        ttk.Button(btns, text="Dalej", command=self._confirm, style="Accent.TButton").pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(btns, text="Anuluj", command=self._cancel, style="Secondary.TButton").pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.grab_set()

    def _confirm(self) -> None:
        self.result = self.mode_var.get() == "combined"
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()


def _parse_price_int(price_str: str) -> int:
    """Parsuje cene z tabeli UCP na liczbe calkowita (do sumowania).
    Zwraca 0, jesli parsowanie sie nie powiedzie (nie przerywa podsumowania)."""
    cleaned = price_str.replace(" ", "").replace("\xa0", "").replace(",", ".")
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


class SummaryDialog(tk.Toplevel):
    """Podsumowanie sprzedazy pokazywane w GUI zaraz po udanym eksporcie -
    laczna kwota wg typu ceny oraz top 5 najlepiej sprzedajacych sie
    przedmiotow, bez potrzeby otwierania wygenerowanego pliku XLSX."""

    def __init__(self, parent: App, entries: list, created_files: list) -> None:
        super().__init__(parent)
        self.title("Podsumowanie sprzedazy")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        totals_by_type: dict[str, int] = {}
        qty_by_item: dict[str, int] = {}
        for entry in entries:
            totals_by_type[entry.price_type] = totals_by_type.get(entry.price_type, 0) + _parse_price_int(entry.price)
            qty = int(entry.quantity) if entry.quantity.isdigit() else 0
            qty_by_item[entry.item_name] = qty_by_item.get(entry.item_name, 0) + qty
        top_items = sorted(qty_by_item.items(), key=lambda kv: kv[1], reverse=True)[:5]

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text=f"Pobrano {len(entries)} rekordow sprzedazy.",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        if totals_by_type:
            ttk.Label(frame, text="Laczna wartosc sprzedazy:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            for price_type, total in totals_by_type.items():
                ttk.Label(frame, text=f"   {price_type}:  {total:,}".replace(",", " ")).pack(anchor="w")
            ttk.Frame(frame, height=10).pack()

        if top_items:
            ttk.Label(frame, text="Najlepiej sprzedajace sie przedmioty (ilosc):", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            for name, qty in top_items:
                ttk.Label(frame, text=f"   {qty:>5}  x  {name}").pack(anchor="w")
            ttk.Frame(frame, height=10).pack()

        if created_files:
            ttk.Label(frame, text="Utworzone pliki:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            for f in created_files:
                ttk.Label(frame, text=f"   {f.name}").pack(anchor="w")

        ttk.Button(frame, text="OK", command=self.destroy, style="Accent.TButton").pack(
            fill="x", pady=(16, 0)
        )
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)


class ConfigDialog(tk.Toplevel):
    def __init__(self, parent: App) -> None:
        super().__init__(parent)
        self.parent = parent
        self.title("Konfiguracja")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        self.grab_set()

        existing = self._read_existing()

        pad = {"padx": 12, "pady": 6}
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Login:").grid(row=0, column=0, sticky="w", **pad)
        self.username_var = tk.StringVar(value=existing.get("username", ""))
        ttk.Entry(frame, textvariable=self.username_var, width=32).grid(row=0, column=1, **pad)

        ttk.Label(frame, text="Haslo:").grid(row=1, column=0, sticky="w", **pad)
        self.password_var = tk.StringVar(value=existing.get("password", ""))
        self.password_entry = ttk.Entry(frame, textvariable=self.password_var, width=32, show="*")
        self.password_entry.grid(row=1, column=1, **pad)

        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, text="Pokaz haslo", variable=self.show_password_var, command=self._toggle_password
        ).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="PIN (5 znakow):").grid(row=3, column=0, sticky="w", **pad)
        self.pin_var = tk.StringVar(value=existing.get("pin", ""))
        ttk.Entry(frame, textvariable=self.pin_var, width=32).grid(row=3, column=1, **pad)

        ttk.Label(frame, text="Folder wynikow:").grid(row=4, column=0, sticky="w", **pad)
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=4, column=1, sticky="we", **pad)
        self.output_dir_var = tk.StringVar(value=existing.get("directory", "output"))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=24).pack(side="left")
        ttk.Button(dir_frame, text="Przegladaj...", command=self._browse_dir).pack(side="left", padx=(4, 0))

        self.show_browser_var = tk.BooleanVar(value=existing.get("show_browser", True))
        ttk.Checkbutton(
            frame, text="Pokazuj przegladarke podczas pobierania", variable=self.show_browser_var
        ).grid(row=5, column=0, columnspan=2, sticky="w", **pad)

        btns = ttk.Frame(frame)
        btns.grid(row=6, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btns, text="Zapisz", command=self._save, style="Accent.TButton").pack(
            side="left", padx=4
        )
        ttk.Button(btns, text="Anuluj", command=self.destroy, style="Secondary.TButton").pack(
            side="left", padx=4
        )

    def _toggle_password(self) -> None:
        self.password_entry.configure(show="" if self.show_password_var.get() else "*")

    def _browse_dir(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.output_dir_var.get() or ".")
        if chosen:
            self.output_dir_var.set(chosen)

    def _read_existing(self) -> dict:
        if not CONFIG_PATH.exists():
            return {}
        try:
            import tomllib

            with open(CONFIG_PATH, "rb") as f:
                data = tomllib.load(f)
            credentials = data.get("credentials", {})
            output = data.get("output", {})
            ui = data.get("ui", {})
            return {
                "username": credentials.get("username", ""),
                "password": credentials.get("password", ""),
                "pin": credentials.get("pin", ""),
                "directory": output.get("directory", "output"),
                "show_browser": ui.get("show_browser", True),
            }
        except Exception:  # noqa: BLE001
            return {}

    def _save(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()
        pin = self.pin_var.get().strip()
        output_dir = self.output_dir_var.get().strip() or "output"

        if not username:
            messagebox.showerror("Konfiguracja", "Podaj login.")
            return
        if not password:
            messagebox.showerror("Konfiguracja", "Podaj haslo.")
            return
        if len(pin) != 5:
            messagebox.showerror("Konfiguracja", "PIN musi miec dokladnie 5 znakow.")
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        save_credentials(
            CONFIG_PATH, username, password, pin, output_dir, self.show_browser_var.get()
        )
        self.destroy()
        self.parent.run_diagnostics()
        _show_silent(self.parent, "Konfiguracja", "Zapisano konfiguracje.")


TASK_NAME = "MetinHardLogAutoFetch"


class ScheduleDialog(tk.Toplevel):
    """Konfiguracja automatycznego, codziennego pobierania przez Harmonogram
    Zadan Windows (uruchamia run_silent.py bez okien wyboru postaci)."""

    def __init__(self, parent: App) -> None:
        super().__init__(parent)
        self.title("Harmonogram automatycznych pobran")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Automatyczne, codzienne pobieranie logow o wybranej porze.",
            font=("Segoe UI", 10, "bold"), wraplength=380,
        ).pack(anchor="w", pady=(0, 6))
        ttk.Label(
            frame,
            text="UWAGA: serwer UCP blokuje ukryty tryb przegladarki, wiec "
            "komputer musi byc wtedy wlaczony i zalogowany (sesja aktywna, "
            "nie zablokowana) - zaplanowane pobieranie zawsze zapisuje "
            "wszystkie postacie do jednego pliku (bez okien wyboru).",
            wraplength=380, foreground=GOLD,
        ).pack(anchor="w", pady=(0, 14))

        time_frame = ttk.Frame(frame)
        time_frame.pack(anchor="w", pady=(0, 10))
        ttk.Label(time_frame, text="Godzina uruchomienia:").pack(side="left")
        self.hour_var = tk.StringVar(value="08")
        self.minute_var = tk.StringVar(value="00")
        ttk.Spinbox(
            time_frame, from_=0, to=23, width=3, textvariable=self.hour_var, format="%02.0f"
        ).pack(side="left", padx=(8, 2))
        ttk.Label(time_frame, text=":").pack(side="left")
        ttk.Spinbox(
            time_frame, from_=0, to=59, width=3, textvariable=self.minute_var, format="%02.0f"
        ).pack(side="left", padx=(2, 0))

        self.status_var = tk.StringVar(value="Sprawdzam biezacy stan...")
        ttk.Label(frame, textvariable=self.status_var, wraplength=380).pack(anchor="w", pady=(0, 14))

        btns = ttk.Frame(frame)
        btns.pack(fill="x")
        ttk.Button(
            btns, text="Zapisz harmonogram", command=self._create_task, style="Accent.TButton"
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))
        ttk.Button(
            btns, text="Usun harmonogram", command=self._delete_task, style="Secondary.TButton"
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

        ttk.Button(frame, text="Zamknij", command=self.destroy, style="Secondary.TButton").pack(
            fill="x", pady=(10, 0)
        )

        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._refresh_status()

    def _refresh_status(self) -> None:
        try:
            result = subprocess.run(
                ["schtasks", "/query", "/tn", TASK_NAME, "/fo", "list"],
                capture_output=True, text=True, encoding="oem", errors="replace", timeout=10,
            )
            if result.returncode == 0:
                next_run = "?"
                for line in result.stdout.splitlines():
                    if line.lower().startswith("next run time"):
                        next_run = line.split(":", 1)[1].strip()
                self.status_var.set(f"Zaplanowane zadanie istnieje. Nastepne uruchomienie: {next_run}")
            else:
                self.status_var.set("Brak zaplanowanego zadania.")
        except Exception as e:  # noqa: BLE001
            self.status_var.set(f"Nie udalo sie sprawdzic stanu: {e}")

    def _create_task(self) -> None:
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
        except ValueError:
            _show_silent(self, "Harmonogram", "Podaj poprawna godzine i minute.")
            return

        python_exe = Path(sys.executable)
        pythonw_exe = python_exe.with_name("pythonw.exe")
        if not pythonw_exe.exists():
            pythonw_exe = python_exe
        script_path = Path(__file__).resolve().parent / "run_silent.py"
        tr_value = f'"{pythonw_exe}" "{script_path}"'

        try:
            result = subprocess.run(
                [
                    "schtasks", "/create", "/tn", TASK_NAME,
                    "/tr", tr_value, "/sc", "daily",
                    "/st", f"{hour:02d}:{minute:02d}", "/it", "/f",
                ],
                capture_output=True, text=True, encoding="oem", errors="replace", timeout=15,
            )
            if result.returncode == 0:
                _show_silent(
                    self, "Harmonogram",
                    f"Zapisano. Program bedzie probowal pobierac logi codziennie o {hour:02d}:{minute:02d}.",
                )
            else:
                messagebox.showerror(
                    "Harmonogram", f"Nie udalo sie utworzyc zadania:\n{result.stderr or result.stdout}"
                )
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Harmonogram", f"Blad: {e}")
        self._refresh_status()

    def _delete_task(self) -> None:
        try:
            result = subprocess.run(
                ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
                capture_output=True, text=True, encoding="oem", errors="replace", timeout=15,
            )
            if result.returncode == 0:
                _show_silent(self, "Harmonogram", "Zaplanowane zadanie zostalo usuniete.")
            else:
                messagebox.showerror(
                    "Harmonogram", f"Nie udalo sie usunac zadania:\n{result.stderr or result.stdout}"
                )
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Harmonogram", f"Blad: {e}")
        self._refresh_status()


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
