#!/usr/bin/env python3
"""
Pit Stop launcher with --gui / --cli modes.

Linux Mint + Python 3 friendly.
Default mode is GUI. Use --cli for terminal mode.

Examples:
  python3 main.py
  python3 main.py --gui
  python3 main.py --cli
"""

from __future__ import annotations
import argparse
import json
import threading
import time
from pathlib import Path

from core import PitStopGame
from core.save_manager import load_game, save_game

ROOT = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT / "data" / "configs" / "settings.json"

def load_settings() -> dict:
    """Load settings.json with safe defaults for beginners."""
    settings = {
        "tick_interval": 1.0,        # seconds
        "autosave_interval": 30.0,   # seconds
        "backups_to_keep": 10
    }
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            file_data = json.load(f) or {}
            settings.update(file_data)
    except Exception:
        # Missing or invalid file? No worries—defaults above are fine.
        pass
    return settings

def start_threads(game: PitStopGame, settings: dict, stop_event: threading.Event, lock: threading.Lock):
    """Spin up passive tick + autosave threads. Return them for joining on exit."""
    tick_interval = float(settings.get("tick_interval", 1.0))
    autosave_interval = float(settings.get("autosave_interval", 30.0))
    backups_to_keep = int(settings.get("backups_to_keep", 10))

    def tick_loop():
        while not stop_event.is_set():
            with lock:
                game.tick()
            time.sleep(tick_interval)

    def autosave_loop():
        while not stop_event.is_set():
            time.sleep(autosave_interval)
            with lock:
                # Your save_manager expects a dict, not the object
                save_game(game.get_state(), backups_to_keep=backups_to_keep)

    t1 = threading.Thread(target=tick_loop, name="tick-thread", daemon=True)
    t2 = threading.Thread(target=autosave_loop, name="autosave-thread", daemon=True)
    t1.start()
    t2.start()
    return t1, t2

def run_gui_mode(game: PitStopGame, settings: dict, stop_event: threading.Event, lock: threading.Lock):
    """Lazy import so CLI users don’t need Tk installed."""
    from gui import main_gui as mg
    if hasattr(mg, "run_gui"):
        mg.run_gui(game, settings, stop_event, lock)
    else:
        raise RuntimeError("Expected gui.main_gui.run_gui(game, settings, stop_event, lock)")

def run_cli_mode(game: PitStopGame, settings: dict, lock: threading.Lock):
    """Run the shared game instance through the CLI frontend."""
    from cli import cli_main as cc
    if hasattr(cc, "start_cli_game"):
        cc.start_cli_game(game, settings, lock)
    elif hasattr(cc, "start_cli"):
        # Back-compat: older CLI that manages its own game loop
        cc.start_cli()
    else:
        raise RuntimeError("cli.cli_main.start_cli_game(...) or start_cli() not found")

def main():
    parser = argparse.ArgumentParser(description="Pit Stop launcher")
    parser.add_argument("--gui", action="store_true", help="Launch GUI")
    parser.add_argument("--cli", action="store_true", help="Launch CLI")
    args = parser.parse_args()

    mode = "gui" if (args.gui or not args.cli) else "cli"  # default to GUI

    settings = load_settings()

    # Load save or start fresh. Your load_game() takes no args and returns a dict or None.
    saved_data = load_game()
    game = PitStopGame(saved_data) if saved_data else PitStopGame()

    stop_event = threading.Event()
    lock = threading.Lock()
    threads = start_threads(game, settings, stop_event, lock)

    try:
        if mode == "gui":
            run_gui_mode(game, settings, stop_event, lock)
        else:
            run_cli_mode(game, settings, lock)
    except KeyboardInterrupt:
        pass
    finally:
        # Graceful shutdown + final save
        stop_event.set()
        for t in threads:
            t.join(timeout=2)
        with lock:
            save_game(game.get_state(), backups_to_keep=int(settings.get("backups_to_keep", 10)))

if __name__ == "__main__":
    main()

