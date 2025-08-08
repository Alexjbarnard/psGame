# main.py
import json
import threading
import time
from pathlib import Path
from core import PitStopGame, save_game, load_game

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
    next_tick = time.monotonic()
    while not stop_event.is_set():
        now = time.monotonic()
        if now >= next_tick:
            with lock:
                game.tick(1)  # one logical second per tick
            next_tick += TICK_INTERVAL
        else:
            time.sleep(min(0.05, max(0.0, next_tick - now)))

def autosave_loop():
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

print("🚗 Welcome to Pit Stop (Terminal Edition with Real-Time Income)")
print("Type 'help' for commands.")

try:
    while True:
        cmd = input("> ").strip().lower()

        with lock:
            if cmd == "help":
                print("""
Commands:
  upgrade_pump   - Upgrade a pump
  buy_pump       - Buy a new pump
  upgrade_store  - Upgrade the store
  remodel        - Soft reset with bonus
  prestige       - Full reset
  stats          - Show game state
  save           - Save game
  quit           - Save and exit
""")

            elif cmd == "upgrade_pump":
                print("✅ Pump upgraded!" if game.upgrade_gas_pump() else "❌ Not enough currency.")

            elif cmd == "buy_pump":
                print("✅ New pump purchased!" if game.buy_gas_pump() else "❌ Not enough currency.")

            elif cmd == "upgrade_store":
                print("✅ Store upgraded!" if game.upgrade_store() else "❌ Not enough currency.")

            elif cmd == "remodel":
                bonus = game.remodel()
                print(f"🏗 Remodel complete! Bonus multiplier now {bonus:.2f}x")

            elif cmd == "prestige":
                game.prestige()
                print("🌟 Prestige reset complete!")

            elif cmd == "stats":
                print(game.get_state())

            elif cmd == "save":
                save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)
                print("💾 Game saved.")

            elif cmd == "quit":
                save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)
                print("💾 Game saved. Goodbye!")
                break

            else:
                print("❓ Unknown command. Type 'help' for options.")
finally:
    stop_event.set()
    with lock:
        save_game(game.get_state(), backups_to_keep=BACKUPS_TO_KEEP)

