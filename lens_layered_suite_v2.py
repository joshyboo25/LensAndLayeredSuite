import json
from pathlib import Path
import random
import os
from pathlib import Path
import random
import os
import shutil
import tempfile
import platform
import gc
import datetime
import subprocess
import socket
import sys
import time
import webbrowser

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageOps, ImageStat
from PIL.PngImagePlugin import PngInfo
import piexif
import requests

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser

def resource_path(relative: str) -> str:
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return str(base_path / relative)



BG_MAIN = "#050712"
BG_CARD = "#0b0f1a"

TEXT_PRIMARY = "#f9fafb"   # main text color
TEXT_MUTED = "#9ca3af"     # subtitles / hints

CYAN = "#3ee7ff"
ACCENT = CYAN              # or a different accent if you want



MESSAGES = [
    "Your next idea is about to go crazy, just wait.",
    "Systems online. Confidence at 110 percent.",
    "Reminder: You are actually kinda unstoppable.",
    "Lowkey you are entering your main character arc.",
    "You are cooking right now. Do not stop.",
    "Your future self is already proud of you.",
    "Peak efficiency unlocked. Proceed.",
    "Your creativity stat just hit legendary tier.",
    "Something good is lining up for you.",
    "You are not trying to be seen. You are building something worth seeing.",
    "The universe is quietly leaning in your favor today.",
    "Someone is going to remember you for something good soon.",
    "You are in the pre glow up loading screen.",
    "Your potential is not just high, it is disrespectful.",
    "Your energy today is borderline dangerous in a good way.",
    "Productivity has joined the server.",
    "You are one wild idea away from a serious bag.",
    "Tiny steps count. You already know that.",
    "You underestimate yourself way more than anyone else ever could.",
    "You are accidentally inspiring someone right now.",
    "Your resilience stat is actually cracked.",
    "God has you on a harder difficulty because you are built different.",
    "Someone out there is rooting for you and you do not even know it.",
    "Your story is not finished. You are mid plot twist.",
    "There is a win coming. Do not dip before you catch it.",
    "Your vibe is evolving. Pokemon style.",
    "Your glow up is downloading. Please do not power off.",
    "You are inevitable. People just have not realized it yet.",
    "If today had achievements, you already unlocked a few.",
    "Future you is watching like that is my goat.",
    "Blessings are in queue. Stay online.",
    "You are allowed to take up space. Go crazy.",
    "Your talent is loud even when you are quiet.",
    "You are carrying potential like it is contraband.",
    "Whatever you are stressing about is smaller than it feels right now.",
    "You are being watched over. More than you realize.",
    "You are closer than you think. Uncomfortably close.",
    "Your heart is too real to lose in the long run.",
    "Someone needs you alive and thriving. Keep going.",
    "Your next chapter is going to hit different.",
    "You matter way more than you let yourself believe.",
    "You have survived worse. You can handle this too.",
    "The blessings you forgot about are still active.",
    "Your mind is sharper than you give it credit for.",
    "Quit doubting. You have sauce you have not even unlocked yet.",
    "You are not falling behind. You are loading.",
    "Your future wife is going to be proud you did not quit.",
    "The version of you from last year would freak out at this growth.",
    "Grace would tell you to keep going. So keep going.",
    "You are not losing time. You are learning timing.",
    "You are built for more than survival. You are built for legacy.",
    "Every day you show up is an act of strength.",
    "Your purpose is louder than your fear.",
    "You do not need permission to rise.",
    "Your comeback season is going to hit.",
    "Some doors close because you are not meant to settle there.",
    "God did not bring you this far just to drop you.",
    "Your drive is rare. Do not waste it doubting yourself.",
    "Pain is temporary. Motion is permanent.",
    "You have a good heart. That is your real superpower.",
    "You already outgrew things you once prayed for.",
    "Your peace is returning piece by piece.",
    "You are protected in more ways than you can see.",
    "There is strength in your quiet. Do not get it twisted.",
    "The days that feel the heaviest are usually right before breakthrough.",
    "Somebody would be lost without you. Do not vanish.",
    "You do not just survive storms. You build inside them.",
    "What you are building will make sense later.",
    "You are the hope someone else is holding onto.",
    "Your best days are not memories. They are blueprints.",
]

WATERMARK_LIGHT = Path("watermark_light.png")
WATERMARK_DARK = Path("watermark_dark.png")

def get_output_dir() -> Path:
    """Return a writable output directory, with a safe fallback."""
    base = Path.cwd()
    candidate = base / "output"
    try:
        candidate.mkdir(exist_ok=True)
        return candidate
    except PermissionError:
        # Fallback to a folder in the user's home directory
        fallback = Path.home() / "LensAndLayered_output"
        fallback.mkdir(exist_ok=True)
        return fallback


OUTPUT_DIR = get_output_dir()


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

WATERMARK_SCALE = 0.25
MARGIN_RATIO = 0.03
WATERMARK_OPACITY = 0.65

COPYRIGHT_TEXT = "© 2025 Lens & Layered Designs. All rights reserved."
ARTIST_TEXT = "Lens & Layered Designs"
WEBSITE_TEXT = "https://lenslayereddesigns.netlify.app/"

GTA_CORE_TOOLS = {
    "Script Hook V": "https://www.gta5-mods.com/tools/script-hook-v/download/20231",
    "Menyoo Trainer": "https://www.gta5-mods.com/scripts/menyoo-2-0/download/181848",
    "OpenIV": "https://www.gta5-mods.com/tools/openiv/download/62463",
}

HITMAN_CORE_TOOLS = {
    "Simple Mod Framework": "https://github.com/OrfeasZ/ZHMTools/releases/latest/download/SMF.zip",
    "RPKG Tool": "https://github.com/OrfeasZ/ZHMTools/releases/latest/download/rpkg.zip",
    "Peacock Offline Server": "https://github.com/EverythingIsTaken/peacock/releases/latest/download/peacock.zip",
}

DEFAULT_WEB_URL = "https://lenslayereddesigns.netlify.app"
LENS_LAYERED_CORE_PATHS = [
    "/",
    "/home",
    "/about",
    "/contact",
    "/shop",
    "/gallery",
    "/privacy",
]

FINANCE_DATA_FILE = Path.home() / "LensAndLayered_FinanceData.json"

CONFIG_FILE = Path.home() / "LensAndLayered_SuiteConfig.json"


def open_image_fix_orientation(path: Path) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img


def resize_watermark(base_img: Image.Image, wm_img: Image.Image) -> Image.Image:
    w, h = base_img.size
    shortest = min(w, h)
    target_w = int(shortest * WATERMARK_SCALE)

    wm_w, wm_h = wm_img.size
    scale = target_w / wm_w
    target_size = (target_w, int(wm_h * scale))
    return wm_img.resize(target_size, Image.LANCZOS)


def apply_opacity(wm_img: Image.Image, opacity: float) -> Image.Image:
    if wm_img.mode != "RGBA":
        wm_img = wm_img.convert("RGBA")
    alpha = wm_img.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    wm_img.putalpha(alpha)
    return wm_img


def region_brightness(img: Image.Image, box) -> float:
    region = img.crop(box).convert("L")
    stat = ImageStat.Stat(region)
    return stat.mean[0]


def choose_best_position(base_img: Image.Image, wm_size):
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


def choose_watermark_variant(brightness, wm_light, wm_dark):
    if brightness < 128:
        return wm_light
    return wm_dark


def embed_jpeg_metadata() -> bytes:
    """Build a clean EXIF block with Lens & Layered fields only."""
    exif_dict = {
        "0th": {},
        "Exif": {},
        "GPS": {},
        "1st": {},
        "Interop": {},
        "thumbnail": None,
    }

    # Use ascii so Windows Properties stays happy
    exif_dict["0th"][piexif.ImageIFD.Artist] = ARTIST_TEXT.encode("ascii", "ignore")
    exif_dict["0th"][piexif.ImageIFD.Copyright] = COPYRIGHT_TEXT.encode("ascii", "ignore")
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = WEBSITE_TEXT.encode("ascii", "ignore")

    return piexif.dump(exif_dict)


def embed_png_metadata() -> PngInfo:
    meta = PngInfo()
    meta.add_text("Copyright", COPYRIGHT_TEXT)
    meta.add_text("Author", ARTIST_TEXT)
    meta.add_text("Website", WEBSITE_TEXT)
    return meta



def watermark_and_tag(path: Path) -> Path:
    img = open_image_fix_orientation(path)

    wm_light = Image.open(WATERMARK_LIGHT).convert("RGBA")
    wm_dark = Image.open(WATERMARK_DARK).convert("RGBA")

    wm_light_resized = resize_watermark(img, wm_light)
    wm_dark_resized = resize_watermark(img, wm_dark)

    wm_w, wm_h = wm_light_resized.size
    x, y, brightness = choose_best_position(img, (wm_w, wm_h))

    wm_variant = choose_watermark_variant(
        brightness,
        wm_light_resized,
        wm_dark_resized,
    )
    wm_variant = apply_opacity(wm_variant, WATERMARK_OPACITY)

    watermarked = Image.new("RGBA", img.size)
    watermarked.paste(img, (0, 0))
    watermarked.paste(wm_variant, (x, y), wm_variant)

    suffix = path.suffix.lower()
    out_path = OUTPUT_DIR / f"{path.stem}_branded{suffix}"

    if suffix in {".jpg", ".jpeg"}:
        watermarked_rgb = watermarked.convert("RGB")
        exif_bytes = embed_jpeg_metadata()
        watermarked_rgb.save(out_path, format="JPEG", quality=95, exif=exif_bytes)
    elif suffix == ".png":
        png_meta = embed_png_metadata()
        watermarked.save(out_path, format="PNG", pnginfo=png_meta)
    else:
        watermarked_rgb = watermarked.convert("RGB")
        watermarked_rgb.save(out_path)

    return out_path



def get_temp_paths():
    paths = set()

    temp_dir = Path(tempfile.gettempdir())
    paths.add(temp_dir)

    if platform.system().lower() == "windows":
        for key in ("TEMP", "TMP"):
            val = os.environ.get(key)
            if val:
                paths.add(Path(val))

        user_temp = Path.home() / "AppData" / "Local" / "Temp"
        paths.add(user_temp)

    return [p for p in paths if p.exists()]


def safe_clean_directory(path: Path, log_callback):
    try:
        if not path.exists():
            log_callback(f"Skipped, not found  {path}")
            return

        for item in path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink(missing_ok=True)
                    log_callback(f"Deleted file  {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    log_callback(f"Deleted folder  {item.name}")
            except Exception as e:
                log_callback(f"Could not delete  {item.name}  {e}")
    except Exception as e:
        log_callback(f"Error scanning  {path}  {e}")


def quick_clean(log_callback):
    log_callback("Quick Clean started (system temp only).")
    paths = get_temp_paths()
    for p in paths:
        log_callback(f"Cleaning  {p}")
        safe_clean_directory(p, log_callback)
    log_callback("Quick Clean finished.")


def deep_clean(log_callback):
    log_callback("Deep Clean started (temp plus extra locations).")
    quick_clean(log_callback)

    if platform.system().lower() == "windows":
        home = Path.home()
        extra = [
            home / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
            home / "AppData" / "Local" / "Microsoft" / "Windows" / "WebCache",
        ]
        for p in extra:
            if p.exists():
                log_callback(f"Cleaning  {p}")
                safe_clean_directory(p, log_callback)

    log_callback("Deep Clean finished.")


def ram_refresh(log_callback):
    log_callback("RAM Refresh requested.")
    gc.collect()
    log_callback("Garbage collector run completed. Processes holding memory will still keep their own usage.")
    log_callback("RAM Refresh finished.")


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def batch_rename_images(folder: Path, base_name: str, log_callback):
    files = sorted(
        [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=lambda p: p.stat().st_mtime,
    )
    if not files:
        log_callback("No image files found to rename.")
        return

    width = len(str(len(files)))
    log_callback(f"Found {len(files)} image files. Renaming with base name '{base_name}'.")
    for idx, f in enumerate(files, start=1):
        new_name = f"{base_name}_{str(idx).zfill(width)}{f.suffix.lower()}"
        new_path = folder / new_name
        try:
            if new_path.exists():
                log_callback(f"Skipped (exists)  {new_name}")
                continue
            f.rename(new_path)
            log_callback(f"Renamed  {f.name}  →  {new_name}")
        except Exception as e:
            log_callback(f"Error renaming {f.name}  {e}")
    log_callback("Batch rename finished.")


def organize_images_by_date(folder: Path, log_callback):
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    if not files:
        log_callback("No image files found to organize.")
        return

    log_callback(f"Found {len(files)} image files. Organizing into year month folders.")
    for f in files:
        try:
            ts = f.stat().st_mtime
            dt = datetime.datetime.fromtimestamp(ts)
            subfolder_name = f"{dt.year}-{str(dt.month).zfill(2)}"
            target_dir = folder / subfolder_name
            target_dir.mkdir(exist_ok=True)
            new_path = target_dir / f.name
            if new_path.exists():
                log_callback(f"Skipped (exists)  {new_path}")
                continue
            shutil.move(str(f), str(new_path))
            log_callback(f"Moved  {f.name}  →  {subfolder_name}/")
        except Exception as e:
            log_callback(f"Error moving {f.name}  {e}")
    log_callback("Organize by date finished.")


def ping_host(host: str, count: int, log_callback):
    host = host.strip()
    if not host:
        log_callback("No host provided to ping.")
        return False

    system_name = platform.system().lower()
    if system_name == "windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]

    log_callback(f"Pinging {host} ({count} packets).")

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as e:
        log_callback(f"Ping failed to start  {e}")
        return False

    if proc.stdout:
        for line in proc.stdout.splitlines():
            if line.strip():
                log_callback(line.strip())

    if proc.stderr:
        for line in proc.stderr.splitlines():
            if line.strip():
                log_callback(f"stderr  {line.strip()}")

    log_callback(f"Ping finished with code {proc.returncode}.")
    return proc.returncode == 0


def get_local_network_info(log_callback):
    try:
        hostname = socket.gethostname()
        log_callback(f"Hostname  {hostname}")
        try:
            local_ip = socket.gethostbyname(hostname)
            log_callback(f"Local IP  {local_ip}")
        except Exception as e:
            log_callback(f"Local IP lookup failed  {e}")
    except Exception as e:
        log_callback(f"Local info error  {e}")


def get_public_ip(log_callback):
    log_callback("Requesting public IP from api.ipify.org.")
    try:
        resp = requests.get("https://api.ipify.org", timeout=5)
        if resp.ok:
            log_callback(f"Public IP  {resp.text.strip()}")
        else:
            log_callback(f"Public IP request failed with status {resp.status_code}.")
    except Exception as e:
        log_callback(f"Public IP lookup failed  {e}")


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
    

class LinkImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.images = set()

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "a":
            href = attrs_dict.get("href")
            if href:
                self.links.add(href)
        elif tag == "img":
            src = attrs_dict.get("src")
            if src:
                self.images.add(src)



class LensLayeredSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("Lens & Layered Suite v2.0")
        self.root.geometry("1200x650")
        self.root.configure(bg=BG_MAIN)

        try:
            icon_file = resource_path("assets/icons/lens_layered_32.png")
            if Path(icon_file).exists():
                icon_img = tk.PhotoImage(file=icon_file)
                # keep a reference so it doesn't get garbage collected
                self.app_icon = icon_img
                self.root.iconphoto(True, icon_img)
            else:
                print(f"Icon not found at {icon_file}")
        except Exception as e:
            print(f"Failed to set window icon  {e}")



        
        self.views = {}
        self.nav_buttons = {}

        self.mot_message_label = None
        self.current_text = ""
        self.typing_index = 0

        self.brand_status_box = None
        self.brand_btn = None
        self.output_label = None
        
        self.brand_output_box = None
        self.brand_output_path_label = None


        self.sys_status_box = None

        self.media_status_box = None
        self.media_folder_label = None
        self.media_current_folder = None

        self.net_status_box = None
        self.net_host_entry = None
        self.net_indicator_label = None

        self.car_status_box = None
        self.car_imp_entry = None
        self.car_count_entry = None
        self.car_mode_var = None
        self.car_result_label = None
        self.car_power_entry = None
        self.car_voltage_entry = None
        self.car_eff_entry = None

        self.build_ui()
        self.switch_view("motivation")

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG_MAIN)
        header.pack(fill="x", pady=(16, 8), padx=24)

        title = tk.Label(
            header,
            text="Lens & Layered Suite",
            font=("Segoe UI", 22, "bold"),
            fg=CYAN,
            bg=BG_MAIN,
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Unified creator environment  Lens & Layered Tools Ecosystem",
            font=("Segoe UI", 11),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
        )
        subtitle.pack(anchor="w")

        nav = tk.Frame(self.root, bg=BG_MAIN)
        nav.pack(fill="x", padx=24, pady=(6, 10))

        def add_tab(name, key):
            btn = tk.Button(
                nav,
                text=name,
                command=lambda k=key: self.switch_view(k),
                font=("Segoe UI", 10),
                fg=TEXT_MUTED,
                bg=BG_MAIN,
                activeforeground=CYAN,
                activebackground=BG_MAIN,
                bd=0,
                padx=6,
                pady=2,
            )
            btn.pack(side="left", padx=10)
            self.nav_buttons[key] = btn

        add_tab("Motivation", "motivation")
        add_tab("Branding", "branding")
        add_tab("Brand Output", "brandoutput")
        add_tab("System Tools", "systemtools")
        add_tab("Media", "media")
        add_tab("Network", "network")
        add_tab("Car Tools", "car")
        add_tab("Developer", "dev")
        add_tab("Game Tools", "game")
        add_tab("Web Tools", "web")
        add_tab("Finance", "finance")
        add_tab("Settings", "settings")
        add_tab("About", "about")
        
        self.card = tk.Frame(self.root, bg=BG_CARD, highlightthickness=1)
        self.card.config(highlightbackground=CYAN)
        self.card.pack(fill="both", expand=True, padx=24, pady=(4, 16))

        self.build_motivation_view()
        self.build_branding_view()
        self.build_brand_output_view()
        self.build_systemtools_view()
        self.build_media_view()
        self.build_network_view()
        self.build_car_view()
        self.build_dev_view()
        self.build_game_view()
        self.build_web_view()
        self.build_finance_view(self.card)
        self.build_settings_view()
        self.build_about_view()

        footer = tk.Label(
            self.root,
            text="Lens & Layered Suite v2.0  Core modules online",
            font=("Segoe UI", 10),
            fg=TEXT_MUTED,
            bg=BG_MAIN,
        )
        footer.pack(pady=(0, 10))

    def clear_card(self):
        for w in self.card.winfo_children():
            w.pack_forget()

    def switch_view(self, key):
        for k, btn in self.nav_buttons.items():
            btn.config(fg=TEXT_MUTED)
        self.nav_buttons[key].config(fg=CYAN)

        self.clear_card()
        view = self.views.get(key)
        if not view:
            return

        view.pack(fill="both", expand=True)

        if key == "motivation":
            self.show_new_message(animated=True)
        elif key == "brandoutput":
            self.refresh_brand_output()



    def create_view(self, key, title_text, body_text):
        frame = tk.Frame(self.card, bg=BG_CARD)
        title = tk.Label(
            frame,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        body = tk.Label(
            frame,
            text=body_text,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
        )
        body.pack(anchor="w", padx=24, pady=(4, 20))

        self.views[key] = frame

    def build_motivation_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Layered Motivation",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Tap New Layer whenever your mental battery dips. The system will serve you one line at a time.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24)

        self.mot_message_label = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 13),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=950,
            justify="left",
        )
        self.mot_message_label.pack(anchor="w", padx=24, pady=(18, 4))

        hint = tk.Label(
            frame,
            text="New Layer pulls another quote. Use it like a mental checkpoint.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 16))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(0, 10))

        new_btn = tk.Button(
            btn_row,
            text="New Layer",
            command=lambda: self.show_new_message(animated=True),
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=18,
            pady=6,
        )
        new_btn.pack(side="left")

        self.views["motivation"] = frame

    def show_new_message(self, animated=True):
        msg = random.choice(MESSAGES)
        self.current_text = "→ " + msg
        self.typing_index = 0

        if not self.mot_message_label:
            return

        if not animated:
            self.mot_message_label.config(text=self.current_text)
        else:
            self.mot_message_label.config(text="")
            self.type_next_char()

    def type_next_char(self):
        if self.typing_index <= len(self.current_text):
            partial = self.current_text[: self.typing_index]
            if self.mot_message_label:
                self.mot_message_label.config(text=partial)
            self.typing_index += 1
            self.root.after(15, self.type_next_char)

    def build_branding_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Branding Tool",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Drop in your final shots and export watermarked, tagged images.\n"
                "Outputs are saved into the output folder next to this suite."
            ),
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 12))

        path_row = tk.Frame(frame, bg=BG_CARD)
        path_row.pack(anchor="w", fill="x", padx=24, pady=(4, 10))

        label = tk.Label(
            path_row,
            text="Output directory",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        label.pack(anchor="w")

        self.output_label = tk.Label(
            path_row,
            text=str(OUTPUT_DIR.resolve()),
            font=("Segoe UI", 9),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        self.output_label.pack(anchor="w", pady=(2, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(8, 6))

        self.brand_btn = tk.Button(
            btn_row,
            text="Select images to brand",
            command=self.select_brand_files,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=18,
            pady=6,
        )
        self.brand_btn.pack(side="left")

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(8, 2))

        self.brand_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=14,
        )
        self.brand_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 6))

        hint = tk.Label(
            frame,
            text="Supported formats  jpg  jpeg  png  webp",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(0, 10))

        self.views["branding"] = frame

    def build_brand_output_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Branding Output",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Quick view of the latest branded files. This reads from the suite output folder.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        path_row = tk.Frame(frame, bg=BG_CARD)
        path_row.pack(anchor="w", fill="x", padx=24, pady=(4, 6))

        path_label = tk.Label(
            path_row,
            text="Active output folder",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        path_label.pack(anchor="w")

        self.brand_output_path_label = tk.Label(
            path_row,
            text=str(OUTPUT_DIR.resolve()),
            font=("Segoe UI", 9),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            wraplength=900,
            justify="left",
        )
        self.brand_output_path_label.pack(anchor="w", pady=(2, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(6, 6))

        refresh_btn = tk.Button(
            btn_row,
            text="Refresh list",
            command=self.refresh_brand_output,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        refresh_btn.pack(side="left")

        open_btn = tk.Button(
            btn_row,
            text="Open folder",
            command=self.open_brand_output_folder,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            activebackground="#1d2238",
            activeforeground=TEXT_PRIMARY,
            bd=0,
            padx=16,
            pady=6,
        )
        open_btn.pack(side="left", padx=(10, 0))

        log_label = tk.Label(
            frame,
            text="Branded files",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(8, 2))

        self.brand_output_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=18,
        )
        self.brand_output_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["brandoutput"] = frame


    def add_brand_status(self, text: str):
        if self.brand_status_box is None:
            return
        self.brand_status_box.insert(tk.END, text)
        self.brand_status_box.yview_moveto(1.0)

    def select_brand_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select images to brand",
            filetypes=(
                ("Images", "*.jpg *.jpeg *.png *.webp"),
                ("All files", "*.*"),
            ),
        )
        if not file_paths:
            return

        paths = []
        bad = []
        for p in file_paths:
            path = Path(p)
            if path.suffix.lower() in ALLOWED_EXTENSIONS:
                paths.append(path)
            else:
                bad.append(path.name)

        if bad:
            messagebox.showwarning(
                "Unsupported files",
                "These files were skipped due to unsupported extensions:\n"
                + "\n".join(bad),
            )

        if paths:
            self.process_brand_files(paths)

    def process_brand_files(self, file_paths):
        if not WATERMARK_LIGHT.exists() or not WATERMARK_DARK.exists():
            messagebox.showerror(
                "Missing watermark",
                "watermark_light.png or watermark_dark.png is missing.\n"
                "Place them next to this script and try again.",
            )
            return

        self.brand_btn.config(state="disabled")
        self.add_brand_status("Starting batch...")

        self.root.update_idletasks()

        for path in file_paths:
            try:
                out_path = watermark_and_tag(path)
                self.add_brand_status(f"[OK] {path.name}  →  {out_path.name}")
            except Exception as e:
                self.add_brand_status(f"[ERR] {path.name}  •  {e}")

        self.add_brand_status("Batch complete.")
        self.brand_btn.config(state="normal")

        # optional: auto update the Brand Output view after a run
        if self.brand_output_box:
            self.refresh_brand_output()

    def refresh_brand_output(self):
        if not self.brand_output_box:
            return

        self.brand_output_box.delete(0, tk.END)

        try:
            files = sorted(
                OUTPUT_DIR.iterdir(),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except Exception as e:
            self.brand_output_box.insert(tk.END, f"Error reading output folder  {e}")
            return

        if not files:
            self.brand_output_box.insert(tk.END, "No branded files found yet.")
            return

        for f in files:
            if f.is_file():
                size_kb = f.stat().st_size / 1024
                self.brand_output_box.insert(
                    tk.END,
                    f"{f.name}  ({size_kb:.1f} KB)",
                )

    def open_brand_output_folder(self):
        try:
            path = OUTPUT_DIR.resolve()
            if os.name == "nt":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.call(["open", str(path)])
            else:
                subprocess.call(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror(
                "Open folder failed",
                f"Could not open output folder.\n{e}",
            )

        

    def build_systemtools_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="System Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Lightweight cleanup and maintenance tasks. Built to be safe by default.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 8))

        quick_btn = tk.Button(
            btn_row,
            text="Quick Clean",
            command=self.run_quick_clean,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        quick_btn.pack(side="left")

        deep_btn = tk.Button(
            btn_row,
            text="Deep Clean",
            command=self.run_deep_clean,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            activebackground="#2fe7ff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        deep_btn.pack(side="left", padx=(10, 0))

        ram_btn = tk.Button(
            btn_row,
            text="RAM Refresh",
            command=self.run_ram_refresh,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            activebackground="#1c2238",
            activeforeground=TEXT_PRIMARY,
            bd=0,
            padx=16,
            pady=6,
        )
        ram_btn.pack(side="left", padx=(10, 0))

        hint = tk.Label(
            frame,
            text="Note   this focuses on temp style folders, not system critical paths.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.sys_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=16,
        )
        self.sys_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["systemtools"] = frame

    def add_sys_status(self, text: str):
        if not self.sys_status_box:
            return
        self.sys_status_box.insert(tk.END, text)
        self.sys_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def run_quick_clean(self):
        self.add_sys_status("==== Quick Clean triggered ====")
        quick_clean(self.add_sys_status)
        self.add_sys_status("")

    def run_deep_clean(self):
        confirm = messagebox.askyesno(
            "Confirm Deep Clean",
            "Deep Clean will remove more cached files.\nIt will not touch system critical paths, but it might log out some sessions.\nContinue",
        )
        if not confirm:
            self.add_sys_status("Deep Clean cancelled by user.")
            return
        self.add_sys_status("==== Deep Clean triggered ====")
        deep_clean(self.add_sys_status)
        self.add_sys_status("")

    def run_ram_refresh(self):
        self.add_sys_status("==== RAM Refresh triggered ====")
        ram_refresh(self.add_sys_status)
        self.add_sys_status("")

    def build_media_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Media Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Batch rename and organize your image folders before branding or export.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        folder_row = tk.Frame(frame, bg=BG_CARD)
        folder_row.pack(anchor="w", fill="x", padx=24, pady=(4, 6))

        choose_btn = tk.Button(
            folder_row,
            text="Select media folder",
            command=self.select_media_folder,
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=12,
            pady=4,
        )
        choose_btn.pack(side="left")

        self.media_folder_label = tk.Label(
            frame,
            text="No folder selected.",
            font=("Segoe UI", 9),
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
            text="Batch Rename",
            command=self.media_batch_rename,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            activebackground="#2fe7ff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        rename_btn.pack(side="left")

        organize_btn = tk.Button(
            btn_row,
            text="Organize by Date",
            command=self.media_organize_by_date,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            activebackground="#1d2238",
            activeforeground=TEXT_PRIMARY,
            bd=0,
            padx=16,
            pady=6,
        )
        organize_btn.pack(side="left", padx=(10, 0))

        hint = tk.Label(
            frame,
            text="Tip   point this at a raw export folder from Lightroom or camera dumps before branding.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.media_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=16,
        )
        self.media_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["media"] = frame

    def add_media_status(self, text: str):
        if not self.media_status_box:
            return
        self.media_status_box.insert(tk.END, text)
        self.media_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def select_media_folder(self):
        folder_path = filedialog.askdirectory(title="Select media folder")
        if not folder_path:
            return
        self.media_current_folder = Path(folder_path)
        self.media_folder_label.config(text=str(self.media_current_folder.resolve()))
        self.add_media_status(f"Selected folder  {self.media_current_folder}")

    def media_batch_rename(self):
        if not hasattr(self, "media_current_folder") or not self.media_current_folder:
            messagebox.showwarning("No folder", "Select a media folder first.")
            return
        base_name = "lens_layered"
        self.add_media_status("==== Batch Rename triggered ====")
        batch_rename_images(self.media_current_folder, base_name, self.add_media_status)
        self.add_media_status("")

    def media_organize_by_date(self):
        if not hasattr(self, "media_current_folder") or not self.media_current_folder:
            messagebox.showwarning("No folder", "Select a media folder first.")
            return
        self.add_media_status("==== Organize by Date triggered ====")
        organize_images_by_date(self.media_current_folder, self.add_media_status)
        self.add_media_status("")

    def build_network_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Network Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Simple diagnostics for when WiFi feels cursed. Ping, local info, and public IP checks.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        host_row = tk.Frame(frame, bg=BG_CARD)
        host_row.pack(anchor="w", fill="x", padx=24, pady=(4, 6))

        host_label = tk.Label(
            host_row,
            text="Host to ping",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        host_label.pack(side="left")

        self.net_host_entry = tk.Entry(
            host_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=30,
        )
        self.net_host_entry.pack(side="left", padx=(8, 0))
        self.net_host_entry.insert(0, "8.8.8.8")

        indicator_row = tk.Frame(frame, bg=BG_CARD)
        indicator_row.pack(anchor="w", padx=24, pady=(4, 8))

        indicator_text = tk.Label(
            indicator_row,
            text="Ping status",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        indicator_text.pack(side="left")

        self.net_indicator_label = tk.Label(
            indicator_row,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_PRIMARY,
            bg="#374151",
            padx=10,
            pady=3,
        )
        self.net_indicator_label.pack(side="left", padx=(8, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 8))

        ping_btn = tk.Button(
            btn_row,
            text="Ping host",
            command=self.net_ping_host,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        ping_btn.pack(side="left")

        local_btn = tk.Button(
            btn_row,
            text="Local info",
            command=self.net_local_info,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            activebackground="#2fe7ff",
            activeforeground=BG_MAIN,
            bd=0,
            padx=16,
            pady=6,
        )
        local_btn.pack(side="left", padx=(10, 0))

        public_btn = tk.Button(
            btn_row,
            text="Public IP",
            command=self.net_public_ip,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            activebackground="#1d2238",
            activeforeground=TEXT_PRIMARY,
            bd=0,
            padx=16,
            pady=6,
        )
        public_btn.pack(side="left", padx=(10, 0))

        hint = tk.Label(
            frame,
            text="Use this before blaming the router. If ping fails to everything, WiFi might be down.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.net_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=16,
        )
        self.net_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["network"] = frame

    def add_net_status(self, text: str):
        if not self.net_status_box:
            return
        self.net_status_box.insert(tk.END, text)
        self.net_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def update_net_indicator(self, success):
        if not self.net_indicator_label:
            return
        if success is True:
            self.net_indicator_label.config(
                text="OK",
                bg="#16a34a",
                fg=BG_MAIN,
            )
        elif success is False:
            self.net_indicator_label.config(
                text="Drop",
                bg="#dc2626",
                fg="#f9fafb",
            )
        else:
            self.net_indicator_label.config(
                text="Idle",
                bg="#374151",
                fg=TEXT_PRIMARY,
            )

    def net_ping_host(self):
        host = self.net_host_entry.get().strip() if self.net_host_entry else ""
        if not host:
            messagebox.showwarning("No host", "Enter a host or IP to ping.")
            return
        self.add_net_status(f"==== Ping {host} requested ====")
        self.update_net_indicator(None)
        success = ping_host(host, count=4, log_callback=self.add_net_status)
        self.update_net_indicator(success)
        self.add_net_status("")

    def net_local_info(self):
        self.add_net_status("==== Local info requested ====")
        get_local_network_info(self.add_net_status)
        self.add_net_status("")

    def net_public_ip(self):
        self.add_net_status("==== Public IP lookup requested ====")
        get_public_ip(self.add_net_status)
        self.add_net_status("")

    def build_car_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Car Audio Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Quick checks for sub wiring and amp draw. Use this before you melt something.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        top_row = tk.Frame(frame, bg=BG_CARD)
        top_row.pack(anchor="w", fill="x", padx=24, pady=(6, 4))

        imp_label = tk.Label(
            top_row,
            text="Driver impedance (Ω)",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        imp_label.pack(side="left")

        self.car_imp_entry = tk.Entry(
            top_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=6,
        )
        self.car_imp_entry.pack(side="left", padx=(6, 12))
        self.car_imp_entry.insert(0, "4")

        count_label = tk.Label(
            top_row,
            text="Number of drivers",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        count_label.pack(side="left")

        self.car_count_entry = tk.Entry(
            top_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=4,
        )
        self.car_count_entry.pack(side="left", padx=(6, 12))
        self.car_count_entry.insert(0, "1")

        mode_label = tk.Label(
            top_row,
            text="Wiring",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        mode_label.pack(side="left")

        self.car_mode_var = tk.StringVar(value="series")
        mode_menu = ttk.Combobox(
            top_row,
            textvariable=self.car_mode_var,
            values=["series", "parallel"],
            width=9,
            state="readonly",
        )
        mode_menu.pack(side="left", padx=(6, 0))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 4))

        calc_btn = tk.Button(
            btn_row,
            text="Calculate load",
            command=self.car_calc_load,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            activebackground="#33ecff",
            activeforeground=BG_MAIN,
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

        amp_label = tk.Label(
            amp_row,
            text="Amp RMS (W)",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        amp_label.pack(side="left")

        self.car_power_entry = tk.Entry(
            amp_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=8,
        )
        self.car_power_entry.pack(side="left", padx=(6, 12))
        self.car_power_entry.insert(0, "2000")

        volt_label = tk.Label(
            amp_row,
            text="System voltage (V)",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        volt_label.pack(side="left")

        self.car_voltage_entry = tk.Entry(
            amp_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=6,
        )
        self.car_voltage_entry.pack(side="left", padx=(6, 12))
        self.car_voltage_entry.insert(0, "13.8")

        eff_label = tk.Label(
            amp_row,
            text="Efficiency (0–1)",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        eff_label.pack(side="left")

        self.car_eff_entry = tk.Entry(
            amp_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=5,
        )
        self.car_eff_entry.pack(side="left", padx=(6, 12))
        self.car_eff_entry.insert(0, "0.8")

        amp_btn_row = tk.Frame(frame, bg=BG_CARD)
        amp_btn_row.pack(anchor="w", padx=24, pady=(2, 4))

        draw_btn = tk.Button(
            amp_btn_row,
            text="Estimate current draw",
            command=self.car_calc_current,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            activebackground="#1d2238",
            activeforeground=TEXT_PRIMARY,
            bd=0,
            padx=16,
            pady=6,
        )
        draw_btn.pack(side="left")

        hint = tk.Label(
            frame,
            text="Note   this is a simplified calc. Real world will spike higher, especially on bass hits.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint.pack(anchor="w", padx=24, pady=(4, 4))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.car_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=10,
        )
        self.car_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["car"] = frame

    def add_car_status(self, text: str):
        if not self.car_status_box:
            return
        self.car_status_box.insert(tk.END, text)
        self.car_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def car_calc_load(self):
        try:
            imp = float(self.car_imp_entry.get())
            count = int(self.car_count_entry.get())
        except Exception:
            messagebox.showwarning("Bad input", "Enter valid numbers for impedance and driver count.")
            return

        mode = self.car_mode_var.get() if self.car_mode_var else "series"
        self.add_car_status(f"==== Load calc  {count}×{imp}Ω in {mode} ====")

        if mode == "series":
            result = calc_series_load(imp, count)
        else:
            result = calc_parallel_load(imp, count)

        if result is None:
            self.add_car_status("Invalid values, could not compute load.")
            self.car_result_label.config(text="Resulting load  –")
            return

        self.car_result_label.config(text=f"Resulting load  ≈ {result:.2f} Ω")
        self.add_car_status(f"Resulting load ≈ {result:.2f} Ω  your amp sees this at the terminals.")
        self.add_car_status("")

    def car_calc_current(self):
        try:
            power = float(self.car_power_entry.get())
            voltage = float(self.car_voltage_entry.get())
            eff = float(self.car_eff_entry.get())
        except Exception:
            messagebox.showwarning("Bad input", "Enter valid numbers for power, voltage, and efficiency.")
            return

        self.add_car_status(f"==== Amp draw estimate  {power} W @ {voltage} V, eff={eff} ====")
        current = estimate_current_draw(power, voltage, eff)
        if current is None:
            self.add_car_status("Invalid values, could not compute current.")
            return

        self.add_car_status(f"Estimated current ≈ {current:.1f} A  expect peaks above this on heavy hits.")
        self.add_car_status("")

    def build_dev_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Developer Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text="Proxy rotation, request sandbox, response analyzer. Use responsibly.",
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        # URL entry
        url_row = tk.Frame(frame, bg=BG_CARD)
        url_row.pack(anchor="w", padx=24, pady=(6, 4))

        url_label = tk.Label(
            url_row,
            text="Target URL",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        url_label.pack(side="left")

        self.dev_url_entry = tk.Entry(
            url_row,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=45
        )
        self.dev_url_entry.pack(side="left", padx=(8, 0))
        self.dev_url_entry.insert(0, "https://httpbin.org/get")

        # Proxy list selector
        proxy_row = tk.Frame(frame, bg=BG_CARD)
        proxy_row.pack(anchor="w", padx=24, pady=(2, 4))

        proxy_btn = tk.Button(
            proxy_row,
            text="Load proxy list (.txt)",
            command=self.dev_load_proxies,
            font=("Segoe UI", 10),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=10,
            pady=4
        )
        proxy_btn.pack(side="left")

        self.dev_proxy_label = tk.Label(
            proxy_row,
            text="No proxy list loaded.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            wraplength=600,
            justify="left"
        )
        self.dev_proxy_label.pack(side="left", padx=(10, 0))

        # Action buttons
        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(8, 4))

        send_btn = tk.Button(
            btn_row,
            text="Send test request",
            command=self.dev_test_request,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            bd=0,
            padx=16,
            pady=6
        )
        send_btn.pack(side="left")

        proxy_test_btn = tk.Button(
            btn_row,
            text="Test proxies",
            command=self.dev_test_proxies,
            font=("Segoe UI", 11, "bold"),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            bd=0,
            padx=16,
            pady=6
        )
        proxy_test_btn.pack(side="left", padx=(10, 0))

        # Log label
        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(8, 2))

        # Log window
        self.dev_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            height=16,
        )
        self.dev_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.dev_proxy_list = []

        self.views["dev"] = frame

    def add_dev_status(self, text: str):
        if not hasattr(self, "dev_status_box") or self.dev_status_box is None:
            return
        self.dev_status_box.insert(tk.END, text)
        self.dev_status_box.yview_moveto(1.0)
        self.root.update_idletasks()
        
    def dev_load_proxies(self):
        file_path = filedialog.askopenfilename(
            title="Select a proxy list (.txt)",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            self.dev_proxy_list = proxies
            self.dev_proxy_label.config(text=f"Loaded {len(proxies)} proxies.")
            self.add_dev_status(f"Loaded {len(proxies)} proxies from file.")
        except Exception as e:
            self.add_dev_status(f"Error loading proxy list  {e}")


    def dev_test_request(self):
        url = self.dev_url_entry.get().strip()
        if not url:
            self.add_dev_status("No URL entered.")
            return

        ua = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X)",
        ])

        proxy = None
        if self.dev_proxy_list:
            proxy_pick = random.choice(self.dev_proxy_list)
            proxy = {
                "http": f"http://{proxy_pick}",
                "https": f"http://{proxy_pick}",
            }
            self.add_dev_status(f"Using proxy  {proxy_pick}")
        else:
            self.add_dev_status("No proxy used.")

        headers = {"User-Agent": ua}
        self.add_dev_status(f"User-Agent  {ua}")

        t0 = time.time()
        try:
            r = requests.get(url, headers=headers, proxies=proxy, timeout=6)
            latency = (time.time() - t0) * 1000
            self.add_dev_status(f"Status  {r.status_code}  |  Latency  {latency:.1f} ms")
            self.add_dev_status(f"Response length  {len(r.text)}")
        except Exception as e:
            self.add_dev_status(f"Request failed  {e}")

        self.add_dev_status("")

    def dev_test_proxies(self):
        if not self.dev_proxy_list:
            self.add_dev_status("No proxies loaded.")
            return

        self.add_dev_status(f"==== Testing {len(self.dev_proxy_list)} proxies ====")

        test_url = "https://httpbin.org/ip"

        for px in self.dev_proxy_list:
            self.add_dev_status(f"Testing  {px}")

            proxy = {
                "http": f"http://{px}",
                "https": f"http://{px}",
            }

            try:
                r = requests.get(test_url, proxies=proxy, timeout=4)
                if r.ok:
                    self.add_dev_status(f"[OK]  Proxy works  → {r.text.strip()}")
                else:
                    self.add_dev_status(f"[BAD]  Status {r.status_code}")
            except Exception as e:
                self.add_dev_status(f"[FAIL] {e}")

        self.add_dev_status("Proxy test complete.\n")


    def build_game_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Game Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Game profiles and setup helpers for single player modding.\n"
                "Start with GTA V core tools, then expand into Hitman and Cyberpunk later."
            ),
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        game_row = tk.Frame(frame, bg=BG_CARD)
        game_row.pack(anchor="w", padx=24, pady=(4, 6))

        game_label = tk.Label(
            game_row,
            text="Game profile",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        game_label.pack(side="left")

        self.game_profile_var = tk.StringVar(value="GTA V single player")
        game_menu = ttk.Combobox(
            game_row,
            textvariable=self.game_profile_var,
            values=[
                "GTA V single player",
                "Hitman 3 (future)",
                "Cyberpunk 2077 (future)",
            ],
            state="readonly",
            width=24,
        )
        game_menu.pack(side="left", padx=(8, 0))

        path_row = tk.Frame(frame, bg=BG_CARD)
        path_row.pack(anchor="w", fill="x", padx=24, pady=(6, 4))

        path_label = tk.Label(
            path_row,
            text="GTA V folder",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        path_label.pack(side="left")

        self.gta_path_var = tk.StringVar()
        self.gta_path_entry = tk.Entry(
            path_row,
            textvariable=self.gta_path_var,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=50,
        )
        self.gta_path_entry.pack(side="left", padx=(8, 0))

        browse_btn = tk.Button(
            path_row,
            text="Browse",
            command=self.game_browse_gta_folder,
            font=("Segoe UI", 9, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=10,
            pady=4,
        )
        browse_btn.pack(side="left", padx=(8, 0))

        hint_path = tk.Label(
            frame,
            text="Point this at the folder with GTA5.exe so tools know where to work.",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        hint_path.pack(anchor="w", padx=24, pady=(2, 8))

        btn_row = tk.Frame(frame, bg=BG_CARD)
        btn_row.pack(anchor="w", padx=24, pady=(4, 6))

        open_gta_btn = tk.Button(
            btn_row,
            text="Open GTA folder",
            command=self.game_open_gta_folder,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=16,
            pady=6,
        )
        open_gta_btn.pack(side="left")

        open_mods_btn = tk.Button(
            btn_row,
            text="Open mods folder",
            command=self.game_open_mods_folder,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            bd=0,
            padx=16,
            pady=6,
        )
        open_mods_btn.pack(side="left", padx=(10, 0))

        core_tools_btn = tk.Button(
            btn_row,
            text="Open core tool sites",
            command=self.game_download_core_tools,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            bd=0,
            padx=16,
            pady=6,
        )
        core_tools_btn.pack(side="left", padx=(10, 0))

        download_btn = tk.Button(
            btn_row,
            text="Download core tools",
            command=self.game_download_core_tools,
            font=("Segoe UI", 11, "bold"),
            fg=BG_MAIN,
            bg="#00ffbb",
            bd=0,
            padx=16,
            pady=6,
        )
        download_btn.pack(side="left", padx=(10, 0))


        hint_core = tk.Label(
            frame,
            text=(
                "Core pack gets them in the door   Script Hook V, Menyoo, OpenIV and more.\n"
                "Single player only  never use mod setups in online modes."
            ),
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            justify="left",
        )
        hint_core.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.game_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=14,
        )
        self.game_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["game"] = frame

    def add_game_status(self, text: str):
        if not hasattr(self, "game_status_box") or self.game_status_box is None:
            return
        self.game_status_box.insert(tk.END, text)
        self.game_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def game_browse_gta_folder(self):
        folder = filedialog.askdirectory(
            title="Select GTA V install folder"
        )
        if not folder:
            return
        self.gta_path_var.set(folder)
        self.add_game_status(f"GTA V folder set to  {folder}")

    def game_open_gta_folder(self):
        path_text = self.gta_path_var.get().strip()
        if not path_text:
            messagebox.showwarning("No folder", "Set the GTA V folder first.")
            return

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror("Not found", f"Folder does not exist  {path}")
            self.add_game_status(f"GTA path not found  {path}")
            return

        self.add_game_status(f"Opening GTA folder  {path}")
        try:
            if platform.system().lower() == "windows":
                os.startfile(str(path))
            elif platform.system().lower() == "darwin":
                subprocess.run(["open", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            self.add_game_status(f"Failed to open folder  {e}")

    def game_open_mods_folder(self):
        path_text = self.gta_path_var.get().strip()
        if not path_text:
            messagebox.showwarning("No folder", "Set the GTA V folder first.")
            return

        base = Path(path_text)
        mods = base / "mods"
        if not mods.exists():
            self.add_game_status("No mods folder found   creating one now.")
            try:
                mods.mkdir(exist_ok=True)
            except Exception as e:
                self.add_game_status(f"Failed to create mods folder  {e}")
                return

        self.add_game_status(f"Opening mods folder  {mods}")
        try:
            if platform.system().lower() == "windows":
                os.startfile(str(mods))
            elif platform.system().lower() == "darwin":
                subprocess.run(["open", str(mods)])
            else:
                subprocess.run(["xdg-open", str(mods)])
        except Exception as e:
            self.add_game_status(f"Failed to open mods folder  {e}")

    def game_open_core_sites(self):
        profile = self.game_profile_var.get() if hasattr(self, "game_profile_var") else "GTA V single player"
        if profile != "GTA V single player":
            self.add_game_status("Core pack is only wired for GTA V profile right now.")
            return

        if not GTA_CORE_TOOLS:
            self.add_game_status("No core tools configured yet. Add URLs in GTA_CORE_TOOLS.")
            return

        self.add_game_status("Opening core tool sites in your browser  Script Hook V, Menyoo, OpenIV etc.")
        for name, url in GTA_CORE_TOOLS.items():
            self.add_game_status(f"Opening  {name}  →  {url}")
            try:
                webbrowser.open(url)
            except Exception as e:
                self.add_game_status(f"Failed to open {name}  {e}")
        self.add_game_status("")


    def game_download_core_tools(self):
        self.add_game_status("Starting GTA V core pack download.")

        download_folder = Path("game_tools")
        download_folder.mkdir(exist_ok=True)

        for name, url in GTA_CORE_TOOLS.items():
            self.add_game_status(f"Fetching {name}…")

            try:
                response = requests.get(url, timeout=30, stream=True)
                response.raise_for_status()

                file_name = url.split("/")[-1]
                save_path = download_folder / file_name

                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=4096):
                        if chunk:
                            f.write(chunk)

                self.add_game_status(f"{name} saved as {file_name}")
            except Exception as e:
                self.add_game_status(f"Failed downloading {name}: {e}")

        self.add_game_status

    def game_download_core_tools(self):
        tools_dir = Path("game_tools")
        tools_dir.mkdir(exist_ok=True)

        self.add_game_status("Downloading GTA V core tools...")

        for name, url in GTA_CORE_TOOLS.items():
            safe_name = name.replace(" ", "_").lower()
            out_path = tools_dir / f"{safe_name}.zip"

            self.add_game_status(f"Fetching {name}...")
            try:
                r = requests.get(url, stream=True, timeout=20)

                if r.status_code != 200:
                    self.add_game_status(f"[ERROR] Failed to download {name}  status {r.status_code}")
                    continue

                total = int(r.headers.get("content-length", 0))

                with open(out_path, "wb") as f:
                    if total > 0:
                        dl = 0
                        for chunk in r.iter_content(chunk_size=4096):
                            if chunk:
                                f.write(chunk)
                                dl += len(chunk)
                        self.add_game_status(f"[OK] {name} saved as {out_path.name} ({dl/1024:.1f} KB)")
                    else:
                        # No content length, just write raw
                        f.write(r.content)
                        self.add_game_status(f"[OK] {name} downloaded (size unknown)")
            except Exception as e:
                self.add_game_status(f"[EXCEPTION] {name}: {e}")

        self.add_game_status("Download batch complete.\n")


    def build_web_view(self):
        frame = tk.Frame(self.card, bg=BG_CARD)

        title = tk.Label(
            frame,
            text="Web Tools",
            font=("Segoe UI", 16, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title.pack(anchor="w", padx=24, pady=(20, 4))

        desc = tk.Label(
            frame,
            text=(
                "Site health scanner with a dedicated Lens and Layered profile.\n"
                "Check status, broken links and missing images for any URL."
            ),
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg=BG_CARD,
            justify="left",
        )
        desc.pack(anchor="w", padx=24, pady=(0, 10))

        url_row = tk.Frame(frame, bg=BG_CARD)
        url_row.pack(anchor="w", padx=24, pady=(4, 4))

        url_label = tk.Label(
            url_row,
            text="Target URL",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        url_label.pack(side="left")

        self.web_url_var = tk.StringVar(value=DEFAULT_WEB_URL)
        self.web_url_entry = tk.Entry(
            url_row,
            textvariable=self.web_url_var,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#111526",
            bd=0,
            insertbackground=TEXT_PRIMARY,
            width=60,
        )
        self.web_url_entry.pack(side="left", padx=(8, 0))
        

        profile_row = tk.Frame(frame, bg=BG_CARD)
        profile_row.pack(anchor="w", padx=24, pady=(10, 6))

        profile_label = tk.Label(
            profile_row,
            text="Lens and Layered profile",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        profile_label.pack(side="left")

        profile_scan_btn = tk.Button(
            profile_row,
            text="Scan core pages",
            command=self.web_scan_lens_profile,
            font=("Segoe UI", 10, "bold"),
            fg=BG_MAIN,
            bg="#00c5dd",
            bd=0,
            padx=12,
            pady=4,
        )
        profile_scan_btn.pack(side="left", padx=(8, 0))

        open_site_btn = tk.Button(
            profile_row,
            text="Open live site",
            command=self.web_open_lens_site,
            font=("Segoe UI", 10),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            bd=0,
            padx=12,
            pady=4,
        )
        open_site_btn.pack(side="left", padx=(8, 0))
        
        quick_btn = tk.Button(
            url_row,
            text="Quick scan",
            command=self.web_quick_scan,
            font=("Segoe UI", 9, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=10,
            pady=4,
        )
        quick_btn.pack(side="left", padx=(8, 0))

        deep_btn = tk.Button(
            url_row,
            text="Deep scan",
            command=self.web_deep_scan,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            bd=0,
            padx=10,
            pady=4,
        )
        deep_btn.pack(side="left", padx=(8, 0))
        
        view_html_btn = tk.Button(
            url_row,
            text="View HTML",
            command=self.web_view_raw_html,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_PRIMARY,
            bg="#14192b",
            bd=0,
            padx=10,
            pady=4,
        )
        view_html_btn.pack(side="left", padx=(8, 0))



        hint = tk.Label(
            frame,
            text=(
                "Quick scan checks status and response time for a single page.\n"
                "Deep scan walks internal links and images up to a safe limit."
            ),
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            justify="left",
        )
        hint.pack(anchor="w", padx=24, pady=(4, 8))

        log_label = tk.Label(
            frame,
            text="Session log",
            font=("Segoe UI", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD,
        )
        log_label.pack(anchor="w", padx=24, pady=(4, 2))

        self.web_status_box = tk.Listbox(
            frame,
            font=("Segoe UI", 11),
            fg=TEXT_PRIMARY,
            bg="#050816",
            selectbackground="#1d2440",
            relief="flat",
            borderwidth=0,
            height=16,
        )
        self.web_status_box.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        self.views["web"] = frame

    def add_web_status(self, text: str):
        if not hasattr(self, "web_status_box") or self.web_status_box is None:
            return
        self.web_status_box.insert(tk.END, text)
        self.web_status_box.yview_moveto(1.0)
        self.root.update_idletasks()

    def web_normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url:
            return ""
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
        return url

    def web_quick_scan(self):
        url = self.web_normalize_url(self.web_url_var.get())
        if not url:
            messagebox.showwarning("No URL", "Enter a URL to scan.")
            return
        self.add_web_status(f"Quick scan for  {url}")
        self.web_scan_single_page(url, check_links=False)

    def web_deep_scan(self):
        url = self.web_normalize_url(self.web_url_var.get())
        if not url:
            messagebox.showwarning("No URL", "Enter a URL to scan.")
            return
        self.add_web_status(f"Deep scan for  {url}")
        self.web_scan_single_page(url, check_links=True)

    def web_scan_single_page(self, url: str, check_links: bool):
        try:
            t0 = time.time()
            resp = requests.get(url, timeout=10)
            dt = (time.time() - t0) * 1000
        except Exception as e:
            self.add_web_status(f"[ERROR] Request failed  {e}")
            self.add_web_status("")
            return

        self.add_web_status(f"Status  {resp.status_code}  |  Time  {dt:.1f} ms")
        self.add_web_status(f"Content length  {len(resp.content)} bytes")

        if not check_links or not resp.ok:
            self.add_web_status("")
            return

        parsed_base = urlparse(url)
        base_root = f"{parsed_base.scheme}://{parsed_base.netloc}"

        parser = LinkImageParser()
        try:
            parser.feed(resp.text)
        except Exception as e:
            self.add_web_status(f"[WARN] HTML parse issue  {e}")

        links = set()
        for href in parser.links:
            full = urljoin(base_root, href)
            p = urlparse(full)
            if p.netloc == parsed_base.netloc:
                links.add(full)

        images = set()
        for src in parser.images:
            full = urljoin(base_root, src)
            p = urlparse(full)
            if p.netloc == parsed_base.netloc:
                images.add(full)

        max_links = 40
        max_images = 40

        self.add_web_status(f"Internal links discovered  {len(links)}  (capped at {max_links})")
        self.add_web_status(f"Internal images discovered  {len(images)}  (capped at {max_images})")

        for idx, link in enumerate(sorted(links)):
            if idx >= max_links:
                self.add_web_status("Link cap reached, skipping remaining.")
                break
            try:
                r = requests.head(link, timeout=6, allow_redirects=True)
                code = r.status_code
                if 200 <= code < 300:
                    self.add_web_status(f"[OK]  {code}  {link}")
                elif 300 <= code < 400:
                    self.add_web_status(f"[REDIR]  {code}  {link}")
                elif 400 <= code < 500:
                    self.add_web_status(f"[CLIENT]  {code}  {link}")
                else:
                    self.add_web_status(f"[SERVER]  {code}  {link}")
            except Exception as e:
                self.add_web_status(f"[FAIL]  {link}  {e}")

        for idx, img in enumerate(sorted(images)):
            if idx >= max_images:
                self.add_web_status("Image cap reached, skipping remaining.")
                break
            try:
                r = requests.head(img, timeout=6, allow_redirects=True)
                code = r.status_code
                if 200 <= code < 300:
                    self.add_web_status(f"[IMG OK]   {code}  {img}")
                else:
                    self.add_web_status(f"[IMG BAD]  {code}  {img}")
            except Exception as e:
                self.add_web_status(f"[IMG FAIL] {img}  {e}")

        self.add_web_status("Deep scan complete.")
        self.add_web_status("")

    def web_scan_lens_profile(self):
        base = DEFAULT_WEB_URL.rstrip("/")
        self.add_web_status(f"Lens and Layered profile scan  base  {base}")
        for path in LENS_LAYERED_CORE_PATHS:
            url = base + path
            self.add_web_status(f"Checking  {url}")
            try:
                r = requests.get(url, timeout=8)
                code = r.status_code
                if 200 <= code < 300:
                    self.add_web_status(f"[OK]  {code}  {url}")
                elif code == 404:
                    self.add_web_status(f"[MISSING]  {code}  {url}")
                else:
                    self.add_web_status(f"[WARN]  {code}  {url}")
            except Exception as e:
                self.add_web_status(f"[ERROR] {url}  {e}")
        self.add_web_status("Lens and Layered profile scan complete.")
        self.add_web_status("")

    def web_open_lens_site(self):
        try:
            webbrowser.open(DEFAULT_WEB_URL)
            self.add_web_status(f"Opened live site in browser  {DEFAULT_WEB_URL}")
        except Exception as e:
            self.add_web_status(f"Failed to open browser  {e}")

    def web_view_raw_html(self):
        url = self.web_normalize_url(self.web_url_var.get())
        if not url:
            messagebox.showwarning("No URL", "Enter a URL to fetch.")
            return

        self.add_web_status(f"Fetching raw HTML for  {url}")

        try:
            t0 = time.time()
            resp = requests.get(url, timeout=10)
            latency = (time.time() - t0) * 1000
        except Exception as e:
            self.add_web_status(f"[ERROR] HTML fetch failed  {e}")
            self.add_web_status("")
            return

        self.add_web_status(f"Status  {resp.status_code}  |  Time  {latency:.1f} ms")
        self.add_web_status(f"Content length  {len(resp.content)} bytes")
        self.add_web_status("Opening HTML viewer window.")
        self.add_web_status("")

        self.web_open_html_window(
            html_text=resp.text,
            url=url,
            latency_ms=latency,
            size_bytes=len(resp.content),
            status_code=resp.status_code,
        )

    def web_open_html_window(self, html_text: str, url: str, latency_ms: float, size_bytes: int, status_code: int):
        # Close existing viewer if it is still open
        if hasattr(self, "web_html_window") and self.web_html_window is not None:
            try:
                self.web_html_window.destroy()
            except Exception:
                pass

        win = tk.Toplevel(self.root)
        self.web_html_window = win
        win.title("Raw HTML viewer")
        win.configure(bg=BG_CARD)

        header_frame = tk.Frame(win, bg=BG_CARD)
        header_frame.pack(fill="x", padx=16, pady=(12, 4))

        title_label = tk.Label(
            header_frame,
            text="Raw HTML viewer",
            font=("Segoe UI", 12, "bold"),
            fg=CYAN,
            bg=BG_CARD,
        )
        title_label.pack(anchor="w")

        info_label = tk.Label(
            header_frame,
            text=f"URL  {url}\nStatus  {status_code}    Time  {latency_ms:.1f} ms    Size  {size_bytes} bytes",
            font=("Segoe UI", 9),
            fg=TEXT_MUTED,
            bg=BG_CARD,
            justify="left",
        )
        info_label.pack(anchor="w", pady=(2, 4))

        text_frame = tk.Frame(win, bg=BG_CARD)
        text_frame.pack(fill="both", expand=True, padx=16, pady=(4, 10))

        scroll = tk.Scrollbar(text_frame)
        scroll.pack(side="right", fill="y")

        text_widget = tk.Text(
            text_frame,
            font=("Consolas", 9),
            fg=TEXT_PRIMARY,
            bg="#050816",
            insertbackground=TEXT_PRIMARY,
            wrap="none",
            relief="flat",
        )
        text_widget.pack(side="left", fill="both", expand=True)

        text_widget.config(yscrollcommand=scroll.set)
        scroll.config(command=text_widget.yview)

        text_widget.insert("1.0", html_text)
        text_widget.config(state="disabled")

        btn_frame = tk.Frame(win, bg=BG_CARD)
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        close_btn = tk.Button(
            btn_frame,
            text="Close",
            command=win.destroy,
            font=("Segoe UI", 9, "bold"),
            fg=BG_MAIN,
            bg=CYAN,
            bd=0,
            padx=12,
            pady=4,
        )
        close_btn.pack(anchor="e")


    def build_finance_view(self, parent):
        """
        Finance dashboard view
        Local JSON save and reload of entries
        """
        frame = tk.Frame(parent, bg=BG_MAIN)
        self.views["finance"] = frame

        header = tk.Label(
            frame,
            text="Lens and Layered Finance Dashboard",
            bg=BG_MAIN,
            fg="white",
            font=("Segoe UI Semibold", 18),
        )
        header.pack(anchor="w", padx=20, pady=(15, 5))

        subtitle = tk.Label(
            frame,
            text="Track debts, payments, and progress. Entries are saved locally on this machine.",
            bg=BG_MAIN,
            fg="#c0c7d0",
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        # Summary strip
        summary_frame = tk.Frame(frame, bg=BG_MAIN)
        summary_frame.pack(fill="x", padx=20, pady=(0, 10))

        def build_metric(parent, label_text):
            card = tk.Frame(parent, bg="#141820", bd=0, relief="flat")
            card.pack(side="left", padx=6, fill="x", expand=True)

            label = tk.Label(
                card,
                text=label_text,
                bg="#141820",
                fg="#9ca3af",
                font=("Segoe UI", 9),
            )
            label.pack(anchor="w", padx=10, pady=(8, 0))

            value = tk.Label(
                card,
                text="0.00",
                bg="#141820",
                fg=ACCENT,
                font=("Segoe UI Semibold", 14),
            )
            value.pack(anchor="w", padx=10, pady=(0, 8))
            return value

        self.finance_total_debt_label = build_metric(summary_frame, "Total debt")
        self.finance_total_paid_label = build_metric(summary_frame, "Total paid")
        self.finance_remaining_label = build_metric(summary_frame, "Remaining")
        self.finance_entries_label = build_metric(summary_frame, "Entries")

        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=(5, 10))

        content_frame = tk.Frame(frame, bg=BG_MAIN)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left side: form
        form_frame = tk.Frame(content_frame, bg=BG_MAIN)
        form_frame.pack(side="left", fill="y", padx=(0, 15))

        form_title = tk.Label(
            form_frame,
            text="New or existing entry",
            bg=BG_MAIN,
            fg="white",
            font=("Segoe UI Semibold", 12),
        )
        form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        def add_labeled_entry(row, label_text, placeholder=""):
            label = tk.Label(
                form_frame,
                text=label_text,
                bg=BG_MAIN,
                fg="#cbd5f5",
                font=("Segoe UI", 9),
            )
            label.grid(row=row, column=0, sticky="w", pady=3)

            entry = ttk.Entry(form_frame, width=26)
            entry.grid(row=row, column=1, sticky="we", pady=3)
            entry.insert(0, placeholder)
            return entry

        self.finance_name_entry = add_labeled_entry(1, "Label or account")
        self.finance_start_entry = add_labeled_entry(2, "Starting amount", "0.00")
        self.finance_paid_entry = add_labeled_entry(3, "Paid so far", "0.00")
        self.finance_monthly_entry = add_labeled_entry(4, "Monthly payment", "0.00")

        note = tk.Label(
            form_frame,
            text="Tip: treat interest as baked into the numbers. This v1 is simple total vs paid math.",
            bg=BG_MAIN,
            fg="#9ca3af",
            font=("Segoe UI", 8),
            wraplength=260,
            justify="left",
        )
        note.grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 10))

        button_row = tk.Frame(form_frame, bg=BG_MAIN)
        button_row.grid(row=6, column=0, columnspan=2, sticky="we", pady=(5, 0))

        self.finance_add_btn = ttk.Button(
            button_row, text="Add or update entry", command=self.finance_add_or_update
        )
        self.finance_add_btn.pack(side="left", padx=(0, 6))

        self.finance_delete_btn = ttk.Button(
            button_row, text="Delete selected", command=self.finance_delete_selected
        )
        self.finance_delete_btn.pack(side="left", padx=(0, 6))

        self.finance_clear_btn = ttk.Button(
            button_row, text="Clear form", command=self.finance_clear_form
        )
        self.finance_clear_btn.pack(side="left")

        save_status_frame = tk.Frame(form_frame, bg=BG_MAIN)
        save_status_frame.grid(row=7, column=0, columnspan=2, sticky="we", pady=(10, 0))

        self.finance_status_label = tk.Label(
            save_status_frame,
            text="Entries auto save after changes.",
            bg=BG_MAIN,
            fg="#9ca3af",
            font=("Segoe UI", 8),
        )
        self.finance_status_label.pack(anchor="w")

        # Right side: table
        table_frame = tk.Frame(content_frame, bg=BG_MAIN)
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("name", "start", "paid", "remaining", "monthly", "created")

        self.finance_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=12,
        )

        self.finance_tree.heading("name", text="Label")
        self.finance_tree.heading("start", text="Start")
        self.finance_tree.heading("paid", text="Paid")
        self.finance_tree.heading("remaining", text="Remaining")
        self.finance_tree.heading("monthly", text="Monthly")
        self.finance_tree.heading("created", text="Created")

        self.finance_tree.column("name", width=130, anchor="w")
        self.finance_tree.column("start", width=80, anchor="e")
        self.finance_tree.column("paid", width=80, anchor="e")
        self.finance_tree.column("remaining", width=90, anchor="e")
        self.finance_tree.column("monthly", width=80, anchor="e")
        self.finance_tree.column("created", width=120, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.finance_tree.yview)
        self.finance_tree.configure(yscrollcommand=vsb.set)

        self.finance_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.finance_tree.bind("<<TreeviewSelect>>", self.finance_on_select)

        # Load existing data and refresh metrics
        self.finance_load_data()
        self.finance_update_summary()

        return frame

    # -------------------- Finance helpers --------------------

    def finance_parse_float(self, value):
        try:
            return float(str(value).replace(",", "").strip())
        except Exception:
            return 0.0

    def finance_collect_rows(self):
        rows = []
        for item_id in self.finance_tree.get_children():
            vals = self.finance_tree.item(item_id, "values")
            if not vals:
                continue
            rows.append(
                {
                    "name": vals[0],
                    "start": self.finance_parse_float(vals[1]),
                    "paid": self.finance_parse_float(vals[2]),
                    "remaining": self.finance_parse_float(vals[3]),
                    "monthly": self.finance_parse_float(vals[4]),
                    "created": vals[5],
                }
            )
        return rows

    def finance_save_data(self):
        try:
            rows = self.finance_collect_rows()
            FINANCE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with FINANCE_DATA_FILE.open("w", encoding="utf8") as f:
                json.dump(rows, f, indent=2)
            self.finance_status_label.config(text="Saved", fg=ACCENT)
        except Exception as e:
            self.finance_status_label.config(text=f"Save failed: {e}", fg="#f97373")

    def finance_load_data(self):
        self.finance_tree.delete(*self.finance_tree.get_children())
        if not FINANCE_DATA_FILE.exists():
            self.finance_status_label.config(text="No saved entries yet.", fg="#9ca3af")
            return

        try:
            with FINANCE_DATA_FILE.open("r", encoding="utf8") as f:
                rows = json.load(f)
        except Exception as e:
            self.finance_status_label.config(
                text=f"Load failed: {e}", fg="#f97373"
            )
            return

        from datetime import datetime

        for row in rows:
            name = row.get("name", "")
            start = row.get("start", 0)
            paid = row.get("paid", 0)
            remaining = row.get("remaining", start - paid)
            monthly = row.get("monthly", 0)
            created = row.get("created")
            if not created:
                created = datetime.now().strftime("%Y-%m-%d %H:%M")

            self.finance_tree.insert(
                "", "end",
                values=(
                    name,
                    f"{start:,.2f}",
                    f"{paid:,.2f}",
                    f"{remaining:,.2f}",
                    f"{monthly:,.2f}",
                    created,
                ),
            )

        self.finance_status_label.config(text="Entries loaded.", fg="#9ca3af")

    def finance_update_summary(self):
        rows = self.finance_collect_rows()
        total_start = sum(r["start"] for r in rows)
        total_paid = sum(r["paid"] for r in rows)
        remaining = sum(r["remaining"] for r in rows)

        self.finance_total_debt_label.config(text=f"{total_start:,.2f}")
        self.finance_total_paid_label.config(text=f"{total_paid:,.2f}")
        self.finance_remaining_label.config(text=f"{remaining:,.2f}")
        self.finance_entries_label.config(text=str(len(rows)))

    def finance_clear_form(self):
        self.finance_name_entry.delete(0, tk.END)
        self.finance_start_entry.delete(0, tk.END)
        self.finance_paid_entry.delete(0, tk.END)
        self.finance_monthly_entry.delete(0, tk.END)
        self.finance_status_label.config(
            text="Form cleared. Select a row or enter a new one.",
            fg="#9ca3af",
        )

    def finance_on_select(self, event):
        sel = self.finance_tree.selection()
        if not sel:
            return
        item_id = sel[0]
        vals = self.finance_tree.item(item_id, "values")
        if not vals:
            return

        self.finance_name_entry.delete(0, tk.END)
        self.finance_name_entry.insert(0, vals[0])

        self.finance_start_entry.delete(0, tk.END)
        self.finance_start_entry.insert(0, vals[1])

        self.finance_paid_entry.delete(0, tk.END)
        self.finance_paid_entry.insert(0, vals[2])

        self.finance_monthly_entry.delete(0, tk.END)
        self.finance_monthly_entry.insert(0, vals[4])

        self.finance_status_label.config(
            text="Loaded entry into form. Edit and press “Add or update”.",
            fg="#9ca3af",
        )

    def finance_add_or_update(self):
        from datetime import datetime

        name = self.finance_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing label", "Give this entry a label or name.")
            return

        start = self.finance_parse_float(self.finance_start_entry.get())
        paid = self.finance_parse_float(self.finance_paid_entry.get())
        monthly = self.finance_parse_float(self.finance_monthly_entry.get())
        remaining = max(start - paid, 0)

        # Check if an item with this label is selected or present
        sel = self.finance_tree.selection()
        target_id = sel[0] if sel else None

        if not target_id:
            # Try to match by name
            for item in self.finance_tree.get_children():
                vals = self.finance_tree.item(item, "values")
                if vals and vals[0] == name:
                    target_id = item
                    break

        if target_id:
            created = self.finance_tree.item(target_id, "values")[5]
            self.finance_tree.item(
                target_id,
                values=(
                    name,
                    f"{start:,.2f}",
                    f"{paid:,.2f}",
                    f"{remaining:,.2f}",
                    f"{monthly:,.2f}",
                    created,
                ),
            )
            self.finance_status_label.config(
                text="Entry updated and saved.",
                fg=ACCENT,
            )
        else:
            created = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.finance_tree.insert(
                "",
                "end",
                values=(
                    name,
                    f"{start:,.2f}",
                    f"{paid:,.2f}",
                    f"{remaining:,.2f}",
                    f"{monthly:,.2f}",
                    created,
                ),
            )
            self.finance_status_label.config(
                text="New entry added and saved.",
                fg=ACCENT,
            )

        self.finance_update_summary()
        self.finance_save_data()

    def finance_delete_selected(self):
        sel = self.finance_tree.selection()
        if not sel:
            messagebox.showinfo("Nothing selected", "Select an entry to delete.")
            return

        item_id = sel[0]
        vals = self.finance_tree.item(item_id, "values")
        label = vals[0] if vals else "this entry"

        if not messagebox.askyesno(
            "Delete entry",
            f"Remove {label} from your finance tracker?",
        ):
            return

        self.finance_tree.delete(item_id)
        self.finance_update_summary()
        self.finance_save_data()
        self.finance_status_label.config(
            text="Entry deleted.",
            fg="#f97373",
        )

    def build_settings_view(self):
        frame = tk.Frame(self.card, bg=BG_MAIN)
        self.views["settings"] = frame

        header = tk.Label(
            frame,
            text="Suite Settings",
            bg=BG_MAIN,
            fg=CYAN,
            font=("Segoe UI Semibold", 18),
        )
        header.pack(anchor="w", padx=24, pady=(18, 4))

        subtitle = tk.Label(
            frame,
            text="Theme, behavior, config paths and global options.",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 16))

        outer = tk.Frame(frame, bg=BG_MAIN)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        left = tk.Frame(outer, bg=BG_MAIN)
        left.pack(side="left", fill="y", padx=(0, 18))

        right = tk.Frame(outer, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True)

        section1 = tk.Label(
            left,
            text="General options",
            bg=BG_MAIN,
            fg="white",
            font=("Segoe UI Semibold", 12),
        )
        section1.pack(anchor="w", pady=(0, 6))

        card_general = tk.Frame(left, bg=BG_CARD, highlightthickness=1)
        card_general.config(highlightbackground=CYAN)
        card_general.pack(fill="x", pady=(0, 16))

        self.settings_show_mot_var = tk.BooleanVar(value=True)
        self.settings_confirm_exit_var = tk.BooleanVar(value=True)
        self.settings_auto_save_brand_var = tk.BooleanVar(value=True)

        cb1 = ttk.Checkbutton(
            card_general,
            text="Show Motivation view on startup",
            variable=self.settings_show_mot_var
        )
        cb1.pack(anchor="w", padx=14, pady=(10, 2))

        cb2 = ttk.Checkbutton(
            card_general,
            text="Ask before closing the Suite",
            variable=self.settings_confirm_exit_var
        )
        cb2.pack(anchor="w", padx=14, pady=2)

        cb3 = ttk.Checkbutton(
            card_general,
            text="Auto save branding output",
            variable=self.settings_auto_save_brand_var
        )
        cb3.pack(anchor="w", padx=14, pady=(2, 10))

        section2 = tk.Label(
            left,
            text="Theme",
            bg=BG_MAIN,
            fg="white",
            font=("Segoe UI Semibold", 12),
        )
        section2.pack(anchor="w", pady=(0, 6))

        card_theme = tk.Frame(left, bg=BG_CARD, highlightthickness=1)
        card_theme.config(highlightbackground=CYAN)
        card_theme.pack(fill="x")

        tk.Label(
            card_theme,
            text="Color mode",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=(10, 2))

        self.settings_theme_var = tk.StringVar(value="Dark")

        theme_box = ttk.Combobox(
            card_theme,
            textvariable=self.settings_theme_var,
            values=["Dark", "Dim", "Light"],
            state="readonly",
            width=18,
        )
        theme_box.pack(anchor="w", padx=14, pady=(0, 10))

        tk.Label(
            card_theme,
            text="Theme selection is stored for future sessions. Actual live theme switching can be wired later.",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8),
            wraplength=220,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        section3 = tk.Label(
            right,
            text="Paths and storage",
            bg=BG_MAIN,
            fg="white",
            font=("Segoe UI Semibold", 12),
        )
        section3.pack(anchor="w", pady=(0, 6))

        card_paths = tk.Frame(right, bg=BG_CARD, highlightthickness=1)
        card_paths.config(highlightbackground=CYAN)
        card_paths.pack(fill="x")

        inner = tk.Frame(card_paths, bg=BG_CARD)
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(
            inner,
            text="Default media folder",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w")

        self.settings_media_path_var = tk.StringVar()

        media_entry = ttk.Entry(inner, textvariable=self.settings_media_path_var, width=40)
        media_entry.grid(row=1, column=0, sticky="we", pady=(2, 6))

        media_btn = ttk.Button(
            inner,
            text="Browse",
            command=self.settings_browse_media_folder,
            width=10,
        )
        media_btn.grid(row=1, column=1, sticky="w", padx=(6, 0))

        tk.Label(
            inner,
            text="Config file location",
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
        ).grid(row=2, column=0, sticky="w", pady=(10, 2))

        self.settings_config_path_label = tk.Label(
            inner,
            text=str(CONFIG_FILE),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        self.settings_config_path_label.grid(row=3, column=0, columnspan=2, sticky="w")

        inner.columnconfigure(0, weight=1)

        button_row = tk.Frame(right, bg=BG_MAIN)
        button_row.pack(anchor="e", pady=(14, 0))

        self.settings_status_label = tk.Label(
            right,
            text="Settings are saved per user profile.",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8),
        )
        self.settings_status_label.pack(anchor="w", pady=(8, 0))

        save_btn = ttk.Button(
            button_row,
            text="Save settings",
            command=self.settings_save,
        )
        save_btn.pack(side="right", padx=(6, 0))

        reset_btn = ttk.Button(
            button_row,
            text="Reset to defaults",
            command=self.settings_reset_to_defaults,
        )
        reset_btn.pack(side="right")

        self.settings_load()

    def settings_default_values(self):
        return {
            "show_motivation_on_start": True,
            "confirm_on_exit": True,
            "auto_save_brand_output": True,
            "theme": "Dark",
            "media_folder": "",
        }

    def settings_browse_media_folder(self):
        folder = filedialog.askdirectory(title="Select default media folder")
        if not folder:
            return
        self.settings_media_path_var.set(folder)

    def settings_load(self):
        data = self.settings_default_values()
        if CONFIG_FILE.exists():
            try:
                with CONFIG_FILE.open("r", encoding="utf8") as f:
                    stored = json.load(f)
                data.update(stored)
            except Exception:
                pass

        self.settings_show_mot_var.set(data.get("show_motivation_on_start", True))
        self.settings_confirm_exit_var.set(data.get("confirm_on_exit", True))
        self.settings_auto_save_brand_var.set(data.get("auto_save_brand_output", True))
        self.settings_theme_var.set(data.get("theme", "Dark"))
        self.settings_media_path_var.set(data.get("media_folder", ""))

        self.settings_status_label.config(text="Settings loaded.", fg=TEXT_MUTED)

    def settings_save(self):
        data = {
            "show_motivation_on_start": bool(self.settings_show_mot_var.get()),
            "confirm_on_exit": bool(self.settings_confirm_exit_var.get()),
            "auto_save_brand_output": bool(self.settings_auto_save_brand_var.get()),
            "theme": self.settings_theme_var.get(),
            "media_folder": self.settings_media_path_var.get(),
        }
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with CONFIG_FILE.open("w", encoding="utf8") as f:
                json.dump(data, f, indent=2)
            self.settings_status_label.config(text="Settings saved.", fg=CYAN)
        except Exception as e:
            self.settings_status_label.config(
                text=f"Save failed: {e}",
                fg="#f97373",
            )

    def settings_reset_to_defaults(self):
        defaults = self.settings_default_values()
        self.settings_show_mot_var.set(defaults["show_motivation_on_start"])
        self.settings_confirm_exit_var.set(defaults["confirm_on_exit"])
        self.settings_auto_save_brand_var.set(defaults["auto_save_brand_output"])
        self.settings_theme_var.set(defaults["theme"])
        self.settings_media_path_var.set(defaults["media_folder"])
        self.settings_status_label.config(
            text="Defaults restored, remember to save.",
            fg=TEXT_MUTED,
        )


    def build_about_view(self):
        frame = tk.Frame(self.card, bg=BG_MAIN)
        self.views["about"] = frame

        header = tk.Label(
            frame,
            text="About Lens & Layered Suite",
            bg=BG_MAIN,
            fg=CYAN,
            font=("Segoe UI Semibold", 18),
        )
        header.pack(anchor="w", padx=24, pady=(18, 4))

        subtitle = tk.Label(
            frame,
            text="Built as a personal creator control room for the Lens & Layered Designs ecosystem.",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 16))

        outer = tk.Frame(frame, bg=BG_MAIN)
        outer.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        left = tk.Frame(outer, bg=BG_MAIN)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = tk.Frame(outer, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # Suite overview card
        card_overview = tk.Frame(left, bg=BG_CARD, highlightthickness=1)
        card_overview.config(highlightbackground=CYAN)
        card_overview.pack(fill="both", expand=True)

        tk.Label(
            card_overview,
            text="What this Suite is for",
            bg=BG_CARD,
            fg="white",
            font=("Segoe UI Semibold", 13),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        overview_text = (
            "Lens & Layered Suite v2.0 is a custom toolkit for real world projects "
            "and creative chaos. It pulls together motivation, system tools, media, "
            "branding and car audio helpers into one place so you do not have twenty "
            "random scripts and windows open while you work."
        )

        tk.Label(
            card_overview,
            text=overview_text,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            wraplength=440,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 12))

        tk.Label(
            card_overview,
            text="Core modules",
            bg=BG_CARD,
            fg=CYAN,
            font=("Segoe UI Semibold", 10),
        ).pack(anchor="w", padx=16, pady=(4, 2))

        core_text = (
            "Motivation feed for mindset, branding automation for photos, system tools for "
            "cleanups and checks, media helpers, network utilities, car tools for builds, "
            "developer and game tools, finance tracking and suite settings."
        )

        tk.Label(
            card_overview,
            text=core_text,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            wraplength=440,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 16))

        # Creator card
        card_creator = tk.Frame(right, bg=BG_CARD, highlightthickness=1)
        card_creator.config(highlightbackground=CYAN)
        card_creator.pack(fill="both", expand=True)

        tk.Label(
            card_creator,
            text="Created by",
            bg=BG_CARD,
        )
    def open_url(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            messagebox.showerror("Open link", "Could not open the link in your browser.")


def main():
    root = tk.Tk()

    if pyi_splash is not None:
       pyi_splash.close()

    app = LensLayeredSuite(root)
    root.mainloop()


if __name__ == "__main__":
    main()







