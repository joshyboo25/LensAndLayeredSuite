"""
Lens & Layered Suite v2 – Control Center
----------------------------------------
Stark‑inspired control room for Josh’s tools.

This one file is standalone:
    python lens_layered_control_center_full.py
"""

import os
import sys
import gc
import json
import shutil
import random
import socket
import getpass
import platform
import subprocess
import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser  # add this here


try:
    import psutil  # optional – for live CPU / RAM stats
except Exception:  # pragma: no cover
    psutil = None

try:
    from PIL import Image, ImageOps, ImageStat
    from PIL.PngImagePlugin import PngInfo
except Exception:
    Image = None
    ImageOps = None
    ImageStat = None
    PngInfo = None

# Close the PyInstaller splash screen if running as a bundled .exe
try:
    import pyi_splash
    pyi_splash.update_text("Launching Lens and Layered Suite…")
    pyi_splash.close()
except Exception:
    pass

# -----------------------------------------------------------------------------
# Branding and styling
# -----------------------------------------------------------------------------

BG_MAIN = "#050712"
BG_CARD = "#0b0f1a"
BG_STRIP = "#020617"

TEXT_PRIMARY = "#f9fafb"
TEXT_MUTED = "#9ca3af"

CYAN = "#22d3ee"
CYAN_SOFT = "#06b6d4"
ACCENT = CYAN

OK_GREEN = "#22c55e"
WARN_YELLOW = "#eab308"
ERR_RED = "#ef4444"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUB = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)

OUTPUT_DIR = (Path.home() / "LensAndLayered_output").expanduser()
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

FINANCE_DATA_FILE = Path.home() / "LensAndLayered_FinanceData.json"

from pathlib import Path
import sys

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
ASSETS_DIR = BASE_DIR / "assets"

WATERMARK_DIR = ASSETS_DIR / "watermark images"
WATERMARK_LIGHT = WATERMARK_DIR / "watermark_light.png"
WATERMARK_DARK = WATERMARK_DIR / "watermark_dark.png"



IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

WATERMARK_SCALE = 0.25
MARGIN_RATIO = 0.03
WATERMARK_OPACITY = 0.65

COPYRIGHT_TEXT = "© 2025 Lens & Layered Designs. All rights reserved."
ARTIST_TEXT = "Lens & Layered Designs"
WEBSITE_TEXT = "https://lenslayereddesigns.netlify.app/"


MESSAGES = [
    "Your next idea is about to go crazy, just wait.",
    "Systems online. Confidence at 110 percent.",
    "Reminder: you are actually kinda unstoppable.",
    "Lowkey you are entering your main character arc.",
    "You are cooking right now. Do not stop.",
    "Your future self is already proud of you.",
    "Your creativity stat just hit legendary tier.",
    "You are not trying to be seen. You are building something worth seeing.",
    "Your potential is not just high, it is disrespectful.",
    "Productivity has joined the server.",
    "You are one wild idea away from a serious bag.",
    "The version of you from last year would freak out at this growth.",
    "Grace would tell you to keep going. So keep going.",
]


# -----------------------------------------------------------------------------
# Helper functions – system / cleaner
# -----------------------------------------------------------------------------


def get_temp_paths():
    paths = set()
    temp_dir = Path(os.getenv("TEMP") or os.getenv("TMP") or Path.cwd())
    paths.add(temp_dir)
    paths.add(Path.home() / "AppData" / "Local" / "Temp")
    return [p for p in paths if p.exists()]


def safe_clean_directory(path: Path, log):
    try:
        if not path.exists():
            log(f"Skip – folder not found: {path}")
            return
        for item in path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink(missing_ok=True)
                    log(f"Deleted file {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    log(f"Deleted folder {item.name}")
            except Exception as e:
                log(f"Could not delete {item.name}  {e}")
    except Exception as e:
        log(f"Error scanning {path}  {e}")


def quick_clean(log):
    log("Quick Clean started.")
    for p in get_temp_paths():
        log(f"Cleaning {p}")
        safe_clean_directory(p, log)
    log("Quick Clean finished.")


def deep_clean(log):
    log("Deep Clean started.")
    quick_clean(log)
    home = Path.home()
    extra = [
        home / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
        home / "AppData" / "Local" / "Microsoft" / "Windows" / "WebCache",
    ]
    for p in extra:
        if p.exists():
            log(f"Cleaning {p}")
            safe_clean_directory(p, log)
    log("Deep Clean finished.")


def ram_refresh(log):
    log("RAM refresh requested.")
    gc.collect()
    log("Python garbage collector run. Other apps keep their own usage.")
    log("RAM refresh finished.")


# -----------------------------------------------------------------------------
# Helper functions – branding / watermark
# -----------------------------------------------------------------------------


def open_image_fix_orientation(path: Path):
    if Image is None or ImageOps is None:
        raise RuntimeError("Pillow is required for watermarking. pip install pillow")
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def resize_watermark(base_img, wm_img):
    w, h = base_img.size
    shortest = min(w, h)
    target_w = int(shortest * WATERMARK_SCALE)

    wm_w, wm_h = wm_img.size
    scale = target_w / wm_w
    target_size = (target_w, int(wm_h * scale))
    return wm_img.resize(target_size, Image.LANCZOS)


def apply_opacity(wm_img, opacity: float):
    if wm_img.mode != "RGBA":
        wm_img = wm_img.convert("RGBA")
    alpha = wm_img.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    wm_img.putalpha(alpha)
    return wm_img


def region_brightness(img, box):
    if ImageStat is None:
        return 128.0
    region = img.crop(box).convert("L")
    stat = ImageStat.Stat(region)
    return stat.mean[0]


def choose_best_position(base_img, wm_size):
    w, h = base_img.size
    wm_w, wm_h = wm_size

    margin_x = int(w * MARGIN_RATIO)
    margin_y = int(h * MARGIN_RATIO)

    positions = {
        "bottom_right": (w - wm_w - margin_x, h - wm_h - margin_y),
        "bottom_left": (margin_x, h - wm_h - margin_y),
        "top_right": (w - wm_w - margin_x, margin_y),
        "top_left": (margin_x, margin_y),
    }

    target_brightness = 128
    best_pos = None
    best_score = None

    for _, (x, y) in positions.items():
        box = (x, y, x + wm_w, y + wm_h)
        bright = region_brightness(base_img, box)
        score = abs(bright - target_brightness)
        if best_score is None or score < best_score:
            best_score = score
            best_pos = (x, y, bright)

    return best_pos


def watermark_and_tag(path: Path) -> Path:
    img = open_image_fix_orientation(path)
    if not WATERMARK_LIGHT.exists() or not WATERMARK_DARK.exists():
        raise FileNotFoundError("watermark_light.png / watermark_dark.png not found next to the script.")

    wm_light = Image.open(WATERMARK_LIGHT).convert("RGBA")
    wm_dark = Image.open(WATERMARK_DARK).convert("RGBA")

    wm_light_resized = resize_watermark(img, wm_light)
    wm_dark_resized = resize_watermark(img, wm_dark)

    wm_w, wm_h = wm_light_resized.size
    x, y, brightness = choose_best_position(img, (wm_w, wm_h))
    wm_variant = wm_light_resized if brightness < 128 else wm_dark_resized
    wm_variant = apply_opacity(wm_variant, WATERMARK_OPACITY)

    watermarked = Image.new("RGBA", img.size)
    watermarked.paste(img, (0, 0))
    watermarked.paste(wm_variant, (x, y), wm_variant)

    suffix = path.suffix.lower()
    out_path = OUTPUT_DIR / f"{path.stem}_branded{suffix}"

    if suffix in {".jpg", ".jpeg"}:
        watermarked.convert("RGB").save(out_path, format="JPEG", quality=95)
    elif suffix == ".png":
        pnginfo = PngInfo() if PngInfo is not None else None
        if pnginfo is not None:
            pnginfo.add_text("Copyright", COPYRIGHT_TEXT)
            pnginfo.add_text("Author", ARTIST_TEXT)
            pnginfo.add_text("Website", WEBSITE_TEXT)
        watermarked.save(out_path, format="PNG", pnginfo=pnginfo)
    else:
        watermarked.convert("RGB").save(out_path)

    return out_path


def batch_rename_images(folder: Path, base_name: str, log):
    files = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=lambda p: p.stat().st_mtime,
    )
    if not files:
        log("No image files found to rename.")
        return
    width = len(str(len(files)))
    log(f"Found {len(files)} images. Renaming with base name '{base_name}'")
    for idx, f in enumerate(files, 1):
        new_name = f"{base_name}_{str(idx).zfill(width)}{f.suffix.lower()}"
        new_path = folder / new_name
        if new_path.exists():
            log(f"Skip – already exists: {new_name}")
            continue
        try:
            f.rename(new_path)
            log(f"{f.name}  →  {new_name}")
        except Exception as e:
            log(f"Error renaming {f.name}  {e}")
    log("Batch rename finished.")


def organize_images_by_date(folder: Path, log):
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    if not files:
        log("No image files found to organize.")
        return
    log(f"Found {len(files)} images. Organizing into year-month folders.")
    for f in files:
        try:
            ts = f.stat().st_mtime
            dt = datetime.datetime.fromtimestamp(ts)
            subfolder = f"{dt.year}-{str(dt.month).zfill(2)}"
            target_dir = folder / subfolder
            target_dir.mkdir(exist_ok=True)
            new_path = target_dir / f.name
            if new_path.exists():
                log(f"Skip – exists: {new_path}")
                continue
            shutil.move(str(f), str(new_path))
            log(f"Moved {f.name}  →  {subfolder}/")
        except Exception as e:
            log(f"Error moving {f.name}  {e}")
    log("Organize by date finished.")


# -----------------------------------------------------------------------------
# Helper – network + car audio + finance
# -----------------------------------------------------------------------------


def ping_host(host: str, count: int, log):
    host = host.strip()
    if not host:
        log("No host provided.")
        return False

    system_name = platform.system().lower()
    if system_name == "windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]

    log(f"Pinging {host} ({count} packets).")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception as e:
        log(f"Ping failed to start  {e}")
        return False

    if proc.stdout:
        for line in proc.stdout.splitlines():
            if line.strip():
                log(line.strip())
    if proc.stderr:
        for line in proc.stderr.splitlines():
            if line.strip():
                log("stderr  " + line.strip())

    log(f"Ping finished with code {proc.returncode}.")
    return proc.returncode == 0


def get_local_network_info(log):
    try:
        hostname = socket.gethostname()
        log(f"Hostname  {hostname}")
        try:
            local_ip = socket.gethostbyname(hostname)
            log(f"Local IP  {local_ip}")
        except Exception as e:
            log(f"Local IP lookup failed  {e}")
    except Exception as e:
        log(f"Local info error  {e}")


def get_public_ip(log):
    try:
        import requests

        log("Requesting public IP from api.ipify.org.")
        resp = requests.get("https://api.ipify.org", timeout=5)
        if resp.ok:
            log(f"Public IP  {resp.text.strip()}")
        else:
            log(f"Public IP request failed with status {resp.status_code}.")
    except Exception as e:
        log(f"Public IP lookup failed  {e}")


def calc_series_load(impedance: float, count: int):
    if count <= 0 or impedance <= 0:
        return None
    return impedance * count


def calc_parallel_load(impedance: float, count: int):
    if count <= 0 or impedance <= 0:
        return None
    return impedance / count


def estimate_current_draw(power_w: float, voltage_v: float, efficiency: float):
    if voltage_v <= 0 or efficiency <= 0:
        return None
    return power_w / (voltage_v * efficiency)


def load_finance_data():
    if not FINANCE_DATA_FILE.exists():
        return []
    try:
        with FINANCE_DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_finance_data(rows):
    try:
        with FINANCE_DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
    except Exception as e:
        print("Failed to save finance data:", e)


# -----------------------------------------------------------------------------
# GUI helpers
# -----------------------------------------------------------------------------


def create_vertical_scrolled_frame(parent, bg):
    container = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    vscroll = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)

    canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_config(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner.bind("<Configure>", _on_config)
    canvas.configure(yscrollcommand=vscroll.set)

    canvas.pack(side="left", fill="both", expand=True)
    vscroll.pack(side="right", fill="y")
    return container, inner


# -----------------------------------------------------------------------------
# Main control center class
# -----------------------------------------------------------------------------


class LensLayeredSuiteControlCenter:
    """
    One-window control room for the Lens & Layered Suite.

    Left side  nav buttons.
    Right side  main content card that swaps views.
    Bottom  status strip with user, machine, CPU and RAM.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Lens & Layered Suite v2 – Control Center")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 600)
        self.root.configure(bg=BG_MAIN)

        self.views = {}
        self.nav_buttons = {}

        # Finance table state
        self.finance_rows = load_finance_data()
        self.finance_selected = None

        self._build_layout()
        self._start_status_updater()
        self.switch_view("about")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BG_STRIP, height=56)
        header.pack(fill="x", side="top")

        title = tk.Label(
            header,
            text="Lens & Layered Suite v2",
            font=("Segoe UI", 18, "bold"),
            fg=CYAN,
            bg=BG_STRIP,
        )
        title.pack(anchor="w", padx=20, pady=(8, 0))

        subtitle = tk.Label(
            header,
            text="Control center for creators  System, Branding, Media, Dev, Finance, Car and more.",
            font=("Segoe UI", 10),
            fg=TEXT_MUTED,
            bg=BG_STRIP,
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 8))

        body = tk.Frame(self.root, bg=BG_MAIN)
        body.pack(fill="both", expand=True)

        # Left nav
        nav = tk.Frame(body, bg=BG_MAIN, width=170)
        nav.pack(side="left", fill="y", padx=(12, 4), pady=(12, 12))

        nav_title = tk.Label(
            nav,
            text="Suites",
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
            anchor="w",
        )
        nav_title.pack(anchor="w", pady=(0, 6), padx=4)

        def add_nav_button(key, label):
            btn = tk.Button(
                nav,
                text=label,
                font=("Segoe UI", 10),
                bg=BG_MAIN,
                fg=TEXT_MUTED,
                activebackground="#020617",
                activeforeground=CYAN,
                relief="flat",
                bd=0,
                padx=10,
                pady=4,
                anchor="w",
                command=lambda k=key: self.switch_view(k),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        add_nav_button("system", "System")
        add_nav_button("branding", "Branding")
        add_nav_button("media", "Media")
        add_nav_button("dev", "Dev tools")
        add_nav_button("finance", "Finance")
        add_nav_button("motivation", "Motivation")
        add_nav_button("car", "Car tools")
        add_nav_button("misc", "Misc / Future")
        add_nav_button("about", "About")

        # Right main card
        self.card = tk.Frame(body, bg=BG_CARD, highlightthickness=1)
        self.card.config(highlightbackground=CYAN_SOFT)
        self.card.pack(side="left", fill="both", expand=True, padx=(4, 12), pady=(12, 12))

        # Build all views
        self._build_system_view()
        self._build_branding_view()
        self._build_media_view()
        self._build_dev_view()
        self._build_finance_view()
        self._build_motivation_view()
        self._build_car_view()
        self._build_misc_view()
        self._build_about_view()

        # Footer status strip
        self.status_strip = tk.Frame(self.root, bg=BG_STRIP, height=24)
        self.status_strip.pack(fill="x", side="bottom")

        self.status_user = tk.Label(
            self.status_strip,
            text="",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_STRIP,
        )
        self.status_user.pack(side="left", padx=12)

        self.status_machine = tk.Label(
            self.status_strip,
            text="",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_STRIP,
        )
        self.status_machine.pack(side="left", padx=12)

        self.status_usage = tk.Label(
            self.status_strip,
            text="",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_STRIP,
        )
        self.status_usage.pack(side="right", padx=12)

    # ------------------------------------------------------------------
    # Nav
    # ------------------------------------------------------------------

    def clear_card(self):
        for child in self.card.winfo_children():
            child.pack_forget()

    def switch_view(self, key: str):
        for k, btn in self.nav_buttons.items():
            btn.config(fg=TEXT_MUTED, bg=BG_MAIN)
        if key in self.nav_buttons:
            self.nav_buttons[key].config(fg=CYAN, bg="#020617")

        self.clear_card()
        frame = self.views.get(key)
        if frame is not None:
            frame.pack(fill="both", expand=True)

        # Special behaviours
        if key == "motivation":
            self._show_new_message(animated=True)
        if key == "finance":
            self._refresh_finance_table()

    # ------------------------------------------------------------------
    # Status strip updater
    # ------------------------------------------------------------------

    def _start_status_updater(self):
        try:
            user = getpass.getuser()
        except Exception:
            user = "unknown"
        machine = platform.node() or platform.system()
        self.status_user.config(text=f"User  {user}")
        self.status_machine.config(text=f"Machine  {machine}")

        def tick():
            if psutil is not None:
                try:
                    cpu = psutil.cpu_percent(interval=None)
                    mem = psutil.virtual_memory()
                    self.status_usage.config(
                        text=f"CPU  {cpu:.0f}%   RAM  {mem.percent:.0f}% of {mem.total / (1024**3):.1f} GB"
                    )
                except Exception:
                    self.status_usage.config(text="CPU / RAM  unavailable")
            else:
                self.status_usage.config(text="psutil not installed  pip install psutil")
            self.root.after(1500, tick)

        tick()

    # ------------------------------------------------------------------
    # System view
    # ------------------------------------------------------------------

    def _build_system_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="System tools", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Safe cleanup and RAM refresh. Built to avoid touching critical folders.",
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 12))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(0, 8))

        quick_btn = tk.Button(
            btn_row,
            text="Quick Clean",
            command=self._run_quick_clean,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=16,
            pady=6,
        )
        quick_btn.pack(side="left")

        deep_btn = tk.Button(
            btn_row,
            text="Deep Clean",
            command=self._run_deep_clean,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN_SOFT,
            bd=0,
            padx=16,
            pady=6,
        )
        deep_btn.pack(side="left", padx=(10, 0))

        ram_btn = tk.Button(
            btn_row,
            text="RAM refresh",
            command=self._run_ram_refresh,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        ram_btn.pack(side="left", padx=(10, 0))

        hint = tk.Label(
            frame,
            text="Uses temp style folders only. It will not delete documents or project folders.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.sys_status = tk.Listbox(
            frame,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            selectbackground="#1d283a",
            relief="flat",
            height=14,
        )
        self.sys_status.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.views["system"] = frame

    def _add_sys_status(self, text: str):
        self.sys_status.insert(tk.END, text)
        self.sys_status.yview_moveto(1.0)
        self.root.update_idletasks()

    def _run_quick_clean(self):
        self._add_sys_status("==== Quick Clean triggered ====")
        quick_clean(self._add_sys_status)
        self._add_sys_status("")

    def _run_deep_clean(self):
        ok = messagebox.askyesno(
            "Confirm Deep Clean",
            "Deep Clean removes extra cached files and browser leftovers.\n"
            "It should not touch system critical paths, but may sign you out of some apps.\n\nContinue",
        )
        if not ok:
            self._add_sys_status("Deep Clean cancelled.")
            return
        self._add_sys_status("==== Deep Clean triggered ====")
        deep_clean(self._add_sys_status)
        self._add_sys_status("")

    def _run_ram_refresh(self):
        self._add_sys_status("==== RAM refresh triggered ====")
        ram_refresh(self._add_sys_status)
        self._add_sys_status("")

    # ------------------------------------------------------------------
    # Branding view
    # ------------------------------------------------------------------

    def _build_branding_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Branding tool", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Drop in finished shots and export watermarked images.\n"
                "Outputs are saved into a shared output folder so you can swap the watermark later."
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=900,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 12))

        out_row = tk.Frame(frame, bg=BG_CARD)
        out_row.pack(anchor="w", fill="x", padx=24, pady=(0, 6))

        label = tk.Label(out_row, text="Output folder", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        label.pack(anchor="w")

        self.brand_output_label = tk.Label(
            out_row,
            text=str(OUTPUT_DIR),
            font=FONT_SMALL,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        self.brand_output_label.pack(anchor="w", pady=(2, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(6, 6))

        self.brand_btn = tk.Button(
            btn_row,
            text="Select images to brand",
            command=self._select_brand_files,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=18,
            pady=6,
        )
        self.brand_btn.pack(side="left")

        open_btn = tk.Button(
            btn_row,
            text="Open output folder",
            command=self._open_output_folder,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        open_btn.pack(side="left", padx=(10, 0))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(8, 2))

        self.brand_status = tk.Listbox(
            frame,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            selectbackground="#1d283a",
            relief="flat",
            height=14,
        )
        self.brand_status.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        hint = tk.Label(
            frame,
            text="Supported formats  jpg  jpeg  png  webp",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(0, 10))

        self.views["branding"] = frame

    def _add_brand_status(self, text: str):
        self.brand_status.insert(tk.END, text)
        self.brand_status.yview_moveto(1.0)
        self.root.update_idletasks()

    def _select_brand_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select images to brand",
            filetypes=(("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")),
        )
        if not file_paths:
            return
        paths = []
        bad = []
        for p in file_paths:
            path = Path(p)
            if path.suffix.lower() in IMAGE_EXTS:
                paths.append(path)
            else:
                bad.append(path.name)
        if bad:
            messagebox.showwarning(
                "Unsupported files",
                "These files were skipped due to unsupported extensions:\n" + "\n".join(bad),
            )
        if paths:
            self._process_brand_files(paths)

    def _process_brand_files(self, paths):
        try:
            if Image is None:
                raise RuntimeError("Pillow is required for watermarking. pip install pillow")
            if not WATERMARK_LIGHT.exists() or not WATERMARK_DARK.exists():
                raise FileNotFoundError(
                    "watermark_light.png or watermark_dark.png is missing.\n"
                    "Place them next to this script and try again."
                )
        except Exception as e:
            messagebox.showerror("Branding setup error", str(e))
            return

        self.brand_btn.config(state="disabled")
        self._add_brand_status("Starting batch...")
        self.root.update_idletasks()

        for path in paths:
            try:
                out_path = watermark_and_tag(path)
                self._add_brand_status(f"[OK] {path.name}  →  {out_path.name}")
            except Exception as e:
                self._add_brand_status(f"[ERR] {path.name}  •  {e}")

        self._add_brand_status("Batch complete.")
        self.brand_btn.config(state="normal")

    def _open_output_folder(self):
        path = OUTPUT_DIR
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.call(["open", str(path)])
            else:
                subprocess.call(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Open failed", f"Could not open output folder.\n{e}")

    # ------------------------------------------------------------------
    # Media view
    # ------------------------------------------------------------------

    def _build_media_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Media tools", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Clean up image folders before branding  rename and group by month.",
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        folder_row = tk.Frame(frame, bg=BG_CARD)
        folder_row.pack(anchor="w", fill="x", padx=24, pady=(4, 6))

        choose_btn = tk.Button(
            folder_row,
            text="Select media folder",
            command=self._select_media_folder,
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=12,
            pady=4,
        )
        choose_btn.pack(side="left")

        self.media_folder_label = tk.Label(
            frame,
            text="No folder selected.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        self.media_folder_label.pack(anchor="w", padx=24, pady=(4, 10))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(0, 8))

        rename_btn = tk.Button(
            btn_row,
            text="Batch rename",
            command=self._media_batch_rename,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN_SOFT,
            bd=0,
            padx=16,
            pady=6,
        )
        rename_btn.pack(side="left")

        org_btn = tk.Button(
            btn_row,
            text="Organize by date",
            command=self._media_organize,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        org_btn.pack(side="left", padx=(10, 0))

        hint = tk.Label(
            frame,
            text="Tip  run this on raw export folders from Lightroom / camera dumps before branding.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.media_status = tk.Listbox(
            frame,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            selectbackground="#1d283a",
            relief="flat",
            height=14,
        )
        self.media_status.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.media_current_folder = None
        self.views["media"] = frame

    def _add_media_status(self, text: str):
        self.media_status.insert(tk.END, text)
        self.media_status.yview_moveto(1.0)
        self.root.update_idletasks()

    def _select_media_folder(self):
        folder = filedialog.askdirectory(title="Select media folder")
        if not folder:
            return
        self.media_current_folder = Path(folder)
        self.media_folder_label.config(text=str(self.media_current_folder))
        self._add_media_status(f"Selected folder  {self.media_current_folder}")

    def _media_batch_rename(self):
        if not self.media_current_folder:
            messagebox.showwarning("No folder", "Select a media folder first.")
            return
        self._add_media_status("==== Batch rename triggered ====")
        batch_rename_images(self.media_current_folder, "lens_layered", self._add_media_status)
        self._add_media_status("")

    def _media_organize(self):
        if not self.media_current_folder:
            messagebox.showwarning("No folder", "Select a media folder first.")
            return
        self._add_media_status("==== Organize by date triggered ====")
        organize_images_by_date(self.media_current_folder, self._add_media_status)
        self._add_media_status("")

    # ------------------------------------------------------------------
    # Dev tools – mini network sandbox (ping + IP helpers)
    # ------------------------------------------------------------------

    def _build_dev_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Dev / Net helpers", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Quick ping, local info and public IP checks for debugging cursed WiFi.",
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        host_row = tk.Frame(frame, bg=BG_CARD)
        host_row.pack(anchor="w", fill="x", padx=24, pady=(4, 6))

        host_label = tk.Label(host_row, text="Host to ping", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        host_label.pack(side="left")

        self.net_host_entry = tk.Entry(
            host_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=28,
        )
        self.net_host_entry.pack(side="left", padx=(8, 0))
        self.net_host_entry.insert(0, "8.8.8.8")

        self.net_indicator = tk.Label(
            host_row,
            text="Idle",
            font=FONT_SMALL,
            fg=TEXT_PRIMARY,
            bg="#374151",
            padx=10,
            pady=3,
        )
        self.net_indicator.pack(side="left", padx=(12, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 8))

        ping_btn = tk.Button(
            btn_row,
            text="Ping host",
            command=self._net_ping,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=16,
            pady=6,
        )
        ping_btn.pack(side="left")

        local_btn = tk.Button(
            btn_row,
            text="Local info",
            command=self._net_local,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        local_btn.pack(side="left", padx=(10, 0))

        public_btn = tk.Button(
            btn_row,
            text="Public IP",
            command=self._net_public,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        public_btn.pack(side="left", padx=(10, 0))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(8, 2))

        self.net_status = tk.Listbox(
            frame,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            selectbackground="#1d283a",
            relief="flat",
            height=14,
        )
        self.net_status.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.views["dev"] = frame

    def _add_net_status(self, text: str):
        self.net_status.insert(tk.END, text)
        self.net_status.yview_moveto(1.0)
        self.root.update_idletasks()

    def _set_net_indicator(self, state):
        if state is True:
            self.net_indicator.config(text="OK", bg=OK_GREEN, fg=BG_MAIN)
        elif state is False:
            self.net_indicator.config(text="Drop", bg=ERR_RED, fg="#f9fafb")
        else:
            self.net_indicator.config(text="Idle", bg="#374151", fg=TEXT_PRIMARY)

    def _net_ping(self):
        host = self.net_host_entry.get().strip()
        if not host:
            messagebox.showwarning("No host", "Enter a host or IP to ping.")
            return
        self._add_net_status(f"==== Ping {host} requested ====")
        self._set_net_indicator(None)
        success = ping_host(host, 4, self._add_net_status)
        self._set_net_indicator(success)
        self._add_net_status("")

    def _net_local(self):
        self._add_net_status("==== Local info requested ====")
        get_local_network_info(self._add_net_status)
        self._add_net_status("")

    def _net_public(self):
        self._add_net_status("==== Public IP lookup requested ====")
        get_public_ip(self._add_net_status)
        self._add_net_status("")

    # ------------------------------------------------------------------
    # Finance view – simple local debt tracker
    # ------------------------------------------------------------------

    def _build_finance_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Finance – debt tracker", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Track debts with starting balance, amount paid, and monthly payment.\n"
                "Data is stored locally in your home folder so it stays on your machine."
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        form = tk.Frame(frame, bg=BG_CARD)
        form.pack(anchor="w", padx=24, pady=(4, 6))

        # Inputs
        self.finance_label_var = tk.StringVar()
        self.finance_start_var = tk.StringVar(value="0.00")
        self.finance_paid_var = tk.StringVar(value="0.00")
        self.finance_monthly_var = tk.StringVar(value="0.00")

        def add_field(row, label_text, var):
            lbl = tk.Label(form, text=label_text, font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
            lbl.grid(row=row, column=0, sticky="w", pady=2)
            entry = tk.Entry(
                form, textvariable=var, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=18
            )
            entry.grid(row=row, column=1, sticky="w", pady=2, padx=(8, 16))

        add_field(0, "Label", self.finance_label_var)
        add_field(1, "Starting balance", self.finance_start_var)
        add_field(2, "Paid so far", self.finance_paid_var)
        add_field(3, "Monthly payment", self.finance_monthly_var)

        btn_col = tk.Frame(form, bg=BG_CARD)
        btn_col.grid(row=0, column=2, rowspan=4, padx=(12, 0))

        add_btn = tk.Button(
            btn_col,
            text="Save / update",
            command=self._finance_save_row,
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=14,
            pady=4,
        )
        add_btn.pack(fill="x", pady=(0, 4))

        clear_btn = tk.Button(
            btn_col,
            text="Clear form",
            command=self._finance_clear_form,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=14,
            pady=4,
        )
        clear_btn.pack(fill="x")

        # Table
        table_frame = tk.Frame(frame, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(8, 4))

        columns = ("label", "start", "paid", "monthly", "remaining", "months")
        self.finance_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8,
        )
        headings = {
            "label": "Label",
            "start": "Start",
            "paid": "Paid",
            "monthly": "Monthly",
            "remaining": "Remaining",
            "months": "Months left",
        }
        for key, text in headings.items():
            self.finance_tree.heading(key, text=text)
            self.finance_tree.column(key, anchor="w", stretch=True, width=110)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.finance_tree.yview)
        self.finance_tree.configure(yscrollcommand=vsb.set)

        self.finance_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.finance_tree.bind("<<TreeviewSelect>>", self._finance_on_select)

        self.finance_status_label = tk.Label(
            frame,
            text="Select a row to edit, or enter a new one.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        self.finance_status_label.pack(anchor="w", padx=24, pady=(4, 10))

        self.views["finance"] = frame

    def _refresh_finance_table(self):
        # Clear
        for item in self.finance_tree.get_children():
            self.finance_tree.delete(item)

        for idx, row in enumerate(self.finance_rows):
            label = row.get("label", "")
            start = float(row.get("start", 0))
            paid = float(row.get("paid", 0))
            monthly = float(row.get("monthly", 0))

            remaining = max(start - paid, 0)
            months = remaining / monthly if monthly > 0 else 0
            months = round(months, 1) if months > 0 else 0

            self.finance_tree.insert(
                "", "end", iid=str(idx), values=(label, f"{start:.2f}", f"{paid:.2f}", f"{monthly:.2f}", f"{remaining:.2f}", months)
            )

    def _finance_clear_form(self):
        self.finance_selected = None
        self.finance_label_var.set("")
        self.finance_start_var.set("0.00")
        self.finance_paid_var.set("0.00")
        self.finance_monthly_var.set("0.00")
        self.finance_status_label.config(
            text="Form cleared. Select a row or enter a new one.",
            fg=TEXT_MUTED,
        )

    def _finance_save_row(self):
        label = self.finance_label_var.get().strip() or "Untitled"
        try:
            start = float(self.finance_start_var.get())
            paid = float(self.finance_paid_var.get())
            monthly = float(self.finance_monthly_var.get())
        except Exception:
            messagebox.showwarning("Bad values", "Use numbers for balances and monthly payment.")
            return

        data = {"label": label, "start": start, "paid": paid, "monthly": monthly}

        if self.finance_selected is None:
            self.finance_rows.append(data)
        else:
            self.finance_rows[self.finance_selected] = data

        save_finance_data(self.finance_rows)
        self._refresh_finance_table()
        self.finance_status_label.config(text="Saved.", fg=OK_GREEN)

    def _finance_on_select(self, event):
        sel = self.finance_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.finance_selected = idx
        row = self.finance_rows[idx]

        self.finance_label_var.set(row.get("label", ""))
        self.finance_start_var.set(str(row.get("start", 0)))
        self.finance_paid_var.set(str(row.get("paid", 0)))
        self.finance_monthly_var.set(str(row.get("monthly", 0)))
        self.finance_status_label.config(text="Loaded into form. Edit and press Save / update.", fg=TEXT_MUTED)

    # ------------------------------------------------------------------
    # Motivation view
    # ------------------------------------------------------------------

    def _build_motivation_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Layered motivation", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Tap New layer whenever your mental battery dips. One line at a time.",
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        self.mot_label = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 13),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        self.mot_label.pack(anchor="w", padx=24, pady=(16, 8))

        hint = tk.Label(
            frame,
            text="Use this like a checkpoint, not a to do list.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(0, 10))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(0, 8))

        btn = tk.Button(
            btn_row,
            text="New layer",
            command=lambda: self._show_new_message(animated=True),
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=18,
            pady=6,
        )
        btn.pack(side="left")

        self.views["motivation"] = frame

    def _show_new_message(self, animated=True):
        msg = random.choice(MESSAGES)
        self._current_msg = "→ " + msg
        self._typing_index = 0

        if not animated:
            self.mot_label.config(text=self._current_msg)
            return

        self.mot_label.config(text="")
        self._type_next_char()

    def _type_next_char(self):
        if self._typing_index <= len(self._current_msg):
            partial = self._current_msg[: self._typing_index]
            self.mot_label.config(text=partial)
            self._typing_index += 1
            self.root.after(15, self._type_next_char)

    # ------------------------------------------------------------------
    # Car audio view
    # ------------------------------------------------------------------

    def _build_car_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Car audio tools", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Estimate sub wiring load and current draw before you melt an alternator.",
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        top_row = tk.Frame(frame, bg=BG_CARD)
        top_row.pack(anchor="w", fill="x", padx=24, pady=(6, 4))

        lbl_imp = tk.Label(top_row, text="Driver impedance (Ω)", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_imp.pack(side="left")
        self.car_imp_entry = tk.Entry(
            top_row, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=6, insertbackground=TEXT_PRIMARY
        )
        self.car_imp_entry.pack(side="left", padx=(6, 12))
        self.car_imp_entry.insert(0, "4")

        lbl_count = tk.Label(top_row, text="Number of drivers", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_count.pack(side="left")
        self.car_count_entry = tk.Entry(
            top_row, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=4, insertbackground=TEXT_PRIMARY
        )
        self.car_count_entry.pack(side="left", padx=(6, 12))
        self.car_count_entry.insert(0, "1")

        lbl_mode = tk.Label(top_row, text="Wiring", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_mode.pack(side="left")
        self.car_mode_var = tk.StringVar(value="series")
        mode_menu = ttk.Combobox(
            top_row, textvariable=self.car_mode_var, values=["series", "parallel"], state="readonly", width=10
        )
        mode_menu.pack(side="left", padx=(6, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 4))

        calc_btn = tk.Button(
            btn_row,
            text="Calculate load",
            command=self._car_calc_load,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=16,
            pady=6,
        )
        calc_btn.pack(side="left")

        self.car_result_label = tk.Label(
            frame,
            text="Resulting load  –",
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        self.car_result_label.pack(anchor="w", padx=24, pady=(4, 4))

        amp_row = tk.Frame(frame, bg=BG_CARD)
        amp_row.pack(anchor="w", fill="x", padx=24, pady=(10, 4))

        lbl_power = tk.Label(amp_row, text="Amp RMS (W)", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_power.pack(side="left")
        self.car_power_entry = tk.Entry(
            amp_row, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=8, insertbackground=TEXT_PRIMARY
        )
        self.car_power_entry.pack(side="left", padx=(6, 12))
        self.car_power_entry.insert(0, "2000")

        lbl_volt = tk.Label(amp_row, text="System voltage (V)", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_volt.pack(side="left")
        self.car_voltage_entry = tk.Entry(
            amp_row, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=6, insertbackground=TEXT_PRIMARY
        )
        self.car_voltage_entry.pack(side="left", padx=(6, 12))
        self.car_voltage_entry.insert(0, "13.8")

        lbl_eff = tk.Label(amp_row, text="Efficiency (0–1)", font=FONT_SMALL, fg=TEXT_MUTED, bg=BG_CARD)
        lbl_eff.pack(side="left")
        self.car_eff_entry = tk.Entry(
            amp_row, font=("Segoe UI", 10), fg=TEXT_PRIMARY, bg="#111827", bd=0, width=5, insertbackground=TEXT_PRIMARY
        )
        self.car_eff_entry.pack(side="left", padx=(6, 12))
        self.car_eff_entry.insert(0, "0.8")

        draw_row = tk.Frame(frame, bg=BG_CARD)
        draw_row.pack(anchor="w", padx=24, pady=(2, 4))

        draw_btn = tk.Button(
            draw_row,
            text="Estimate current draw",
            command=self._car_calc_current,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=16,
            pady=6,
        )
        draw_btn.pack(side="left")

        hint = tk.Label(
            frame,
            text="Simplified math. Real world peaks will be higher, especially on heavy bass.",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 6))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=FONT_SMALL,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.car_status = tk.Listbox(
            frame,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            selectbackground="#1d283a",
            relief="flat",
            height=10,
        )
        self.car_status.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.views["car"] = frame

    def _add_car_status(self, text: str):
        self.car_status.insert(tk.END, text)
        self.car_status.yview_moveto(1.0)
        self.root.update_idletasks()

    def _car_calc_load(self):
        try:
            imp = float(self.car_imp_entry.get())
            count = int(self.car_count_entry.get())
        except Exception:
            messagebox.showwarning("Bad input", "Use numbers for impedance and driver count.")
            return

        mode = self.car_mode_var.get()
        self._add_car_status(f"==== Load calc  {count}×{imp}Ω in {mode} ====")
        if mode == "series":
            result = calc_series_load(imp, count)
        else:
            result = calc_parallel_load(imp, count)
        if result is None:
            self._add_car_status("Invalid values.")
            self.car_result_label.config(text="Resulting load  –")
            return
        self.car_result_label.config(text=f"Resulting load  ≈ {result:.2f} Ω")
        self._add_car_status(f"Resulting load ≈ {result:.2f} Ω  (what the amp sees).")
        self._add_car_status("")

    def _car_calc_current(self):
        try:
            power = float(self.car_power_entry.get())
            voltage = float(self.car_voltage_entry.get())
            eff = float(self.car_eff_entry.get())
        except Exception:
            messagebox.showwarning("Bad input", "Use numbers for power, voltage and efficiency.")
            return

        self._add_car_status(f"==== Amp draw estimate  {power} W @ {voltage} V, eff={eff} ====")
        current = estimate_current_draw(power, voltage, eff)
        if current is None:
            self._add_car_status("Invalid values.")
            return
        self._add_car_status(f"Estimated current ≈ {current:.1f} A (real peaks will be higher).")
        self._add_car_status("")

    # ------------------------------------------------------------------
    # Misc / Future view – placeholder for new modules
    # ------------------------------------------------------------------

    def _build_misc_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(frame, text="Misc / Future", font=FONT_TITLE, fg=CYAN, bg=BG_CARD)
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Parking spot for future modules  GPU tools, LLM helpers, car build planner, etc.\n"
                "Use this as a scratch pad until the feature is ready to graduate into its own tab."
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 12))

        container, inner = create_vertical_scrolled_frame(frame, bg=BG_CARD)
        container.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        note = tk.Label(
            inner,
            text=(
                "- Drop ideas here as labels or notes.\n"
                "- When something becomes repeatable, break it into its own function.\n"
                "- Then we wire it into the nav on the left."
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=900,
        )
        note.pack(anchor="w", pady=(4, 8))

        self.misc_text = tk.Text(
            inner,
            font=("Consolas", 10),
            fg=TEXT_PRIMARY,
            bg="#020617",
            relief="flat",
            height=10,
            wrap="word",
        )
        self.misc_text.pack(fill="both", expand=True)

        self.views["misc"] = frame

    # ------------------------------------------------------------------
    # About view – Stark style story panel
    # ------------------------------------------------------------------

    def _build_about_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="About Lens & Layered Suite",
            font=FONT_TITLE,
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        subtitle = tk.Label(
            frame,
            text="Unified creator environment  Lens & Layered Designs",
            font=FONT_SUB,
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 14))

        grid = tk.Frame(frame, bg=BG_CARD)
        grid.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # --- Left card ---
        card_left = tk.Frame(
            grid,
            bg=BG_CARD,
            highlightbackground=CYAN_SOFT,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        card_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lbl1 = tk.Label(
            card_left,
            text="What this suite is for",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        lbl1.pack(anchor="w", pady=(0, 6))

        desc = (
            "Started as personal tools and grew into a control room for:\n"
            "• System cleanup and RAM refresh utilities\n"
            "• Automated watermarking for photos\n"
            "• Network and dev helpers\n"
            "• Car audio calculators and build utilities\n"
            "• A small finance dashboard with local storage\n"
        )

        text1 = tk.Label(
            card_left,
            text=desc,
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=420,
        )
        text1.pack(anchor="w")

        # --- Right card ---
        card_right = tk.Frame(
            grid,
            bg=BG_CARD,
            highlightbackground=CYAN_SOFT,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        card_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl2 = tk.Label(
            card_right,
            text="Created by",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        lbl2.pack(anchor="w", pady=(0, 6))

        text2 = tk.Label(
            card_right,
            text=(
                "Designed and coded by Josh for Lens & Layered Designs.\n"
                "Built to unify utilities into a clean, creator-friendly dashboard."
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=420,
        )
        text2.pack(anchor="w", pady=(0, 10))

        lbl3 = tk.Label(
            card_right,
            text="Tech stack",
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        lbl3.pack(anchor="w", pady=(4, 4))

        text3 = tk.Label(
            card_right,
            text=(
                "• Python 3 with Tkinter UI\n"
                "• Local JSON and file based storage\n"
                "• Optional psutil + Pillow\n"
                "• Packaged into EXE builds\n"
                "• Custom Lens & Layered theme\n"
            ),
            font=FONT_SUB,
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
            wraplength=420,
        )
        text3.pack(anchor="w")

        # quick links
        btn_row = tk.Frame(card_right, bg=BG_CARD)
        btn_row.pack(anchor="w", pady=(10, 0))

        def open_github():
            webbrowser.open("https://github.com/joshyboo25")

        def open_repo():
            webbrowser.open("https://github.com/joshyboo25/LensAndLayeredSuite")

        def open_site():
            webbrowser.open("https://lenslayereddesigns.netlify.app/home#gallery")

        tk.Button(
            btn_row,
            text="GitHub Profile",
            command=open_github,
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=12,
            pady=4,
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Suite Repository",
            command=open_repo,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111827",
            bd=0,
            padx=12,
            pady=4,
        ).pack(side="left", padx=(10, 0))

        tk.Button(
            btn_row,
            text="Lens & Layered Website",
            command=open_site,
            font=("Segoe UI", 10),
            fg=BG_MAIN,
            bg="#111827",
            bd=0,
            padx=12,
            pady=4,
        ).pack(side="left", padx=(10, 0))

        frame.pack(fill="both", expand=True)
        self.views["about"] = frame





# -----------------------------------------------------------------------------
# Main entry
# -----------------------------------------------------------------------------


def main():
    root = tk.Tk()
    app = LensLayeredSuiteControlCenter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
