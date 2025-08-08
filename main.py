# main.py
import sys
import json
import threading
import time
from pathlib import Path
from core import PitStopGame, save_game, load_game
from cli.cli_main import start_cli_game

# --- Load settings with fallbacks ---
SETTINGS_PATH = Path("data/configs/settings.json")
DEFAULTS = {"tick_interval": 1.0, "autosave_interval": 30.0, "backups_to_keep": 10}

def load_settings():
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        return {**DEFAULTS, **data}
    except Exception:
        return DEFAULTS.copy()

settings = load_settings()
TICK_INTERVAL = float(settings["tick_interval"])
AUTOSAVE_INTERVAL = float(settings["autosave_interval"])
BACKUPS_TO_KEEP = int(settings["backups_to_keep"])

# --- Init game ---
saved_data = load_game()
game = PitStopGame(saved_data)

# --- Concurrency primitives ---
stop_event = threading.Event()
lock = threading.Lock()

def passive_income_loop():
    """Manages the passive income generation in a separate thread."""
    next_tick = time.monotonic()
    while not stop_event.is_set():
        now = time.monotonic()
        if now >= next_tick:
            with lock:
                # one logical second per tick
                game.tick(1)
            next_tick += TICK_INTERVAL
        else:
            time.sleep(min(0.05, max(0.0, next_tick - now)))

def autosave_loop():
    """Manages periodic autosaving in a separate thread."""
    next_save = time.monotonic() + AUTOSAVE_INTERVAL
    while not stop_event.is_set():
        now = time.monotonic()
        if now >= next_save:
            with lock:
                save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)
            next_save += AUTOSAVE_INTERVAL
        else:
            time.sleep(0.25)

# Start background threads
threading.Thread(target=passive_income_loop, daemon=True).start()
threading.Thread(target=autosave_loop, daemon=True).start()

# --- Main entry point logic ---
if "--gui" in sys.argv:
    # We will import this only if we need it
    from gui.gui_main import start_gui_game
    try:
        start_gui_game(game, lock, stop_event)
    finally:
        stop_event.set()
        with lock:
            save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)
elif "--cli" in sys.argv:
    # Run the CLI version
    print("🚗 Welcome to Pit Stop (Terminal Edition with Real-Time Income)")
    try:
        start_cli_game(game, lock, save_game, stop_event, BACKUPS_TO_KEEP)
    finally:
        stop_event.set()
        with lock:
            save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)
else:
    print("Please specify a mode: 'python3 main.py --cli' or 'python3 main.py --gui'")
    stop_event.set()