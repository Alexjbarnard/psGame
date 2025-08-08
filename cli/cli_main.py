"""
CLI frontend that operates on the *shared* PitStopGame instance created by main.py.

It expects:
  start_cli_game(game, settings, lock)

- game: PitStopGame (already ticking in a background thread)
- settings: dict from settings.json
- lock: threading.Lock used by the main loop to guard game state
"""

from __future__ import annotations
import sys
from typing import Iterable

def _call_any(obj, names: Iterable[str], *args, **kwargs):
    """Try multiple method names to match your engine API, raise if none found."""
    for n in names:
        fn = getattr(obj, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise AttributeError(f"None of these methods exist on {type(obj).__name__}: {', '.join(names)}")

def _print_state(game, lock):
    with lock:
        try:
            state = game.get_state()  # safest way—engine controls the shape
        except Exception:
            print("⚠️  Unable to read state (no get_state?).", flush=True)
            return
    # Pretty, but generic—prints whatever your engine exposes.
    print("\n=== Current State ===")
    for k, v in state.items():
        print(f"{k}: {v}")
    print("=====================\n", flush=True)

def _help():
    print(
        """
Commands:
  status                 Show current game state
  upgrade_pump           Upgrade pump level
  buy_pump               Buy a new pump
  upgrade_store          Upgrade the store
  remodel                Perform a remodel (soft reset with multiplier)
  prestige               Perform prestige reset
  tick                   Force an immediate tick (debug)
  save                   Save the game now
  help                   Show this help
  quit / exit            Leave the CLI
""",
        flush=True,
    )

def start_cli_game(game, settings, lock):
    """Interactive REPL that manipulates the shared engine instance."""
    backups_to_keep = int(settings.get("backups_to_keep", 10))

    # Lazy import to avoid coupling if you ever split packages later
    try:
        from core.save_manager import save_game
    except Exception:
        save_game = None

    print("🛠️  Pit Stop CLI — type 'help' for commands.\n", flush=True)
    _print_state(game, lock)

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting…", flush=True)
            break

        if cmd in ("quit", "exit"):
            break
        elif cmd in ("help", "?"):
            _help()
        elif cmd == "status":
            _print_state(game, lock)
        elif cmd == "tick":
            with lock:
                game.tick()
            _print_state(game, lock)
        elif cmd == "upgrade_pump":
            with lock:
                _call_any(game, ("upgrade_pump", "upgrade_gas_pump"))
            _print_state(game, lock)
        elif cmd == "buy_pump":
            with lock:
                _call_any(game, ("buy_pump", "buy_new_pump", "purchase_pump"))
            _print_state(game, lock)
        elif cmd == "upgrade_store":
            with lock:
                _call_any(game, ("upgrade_store",))
            _print_state(game, lock)
        elif cmd == "remodel":
            with lock:
                _call_any(game, ("remodel",))
            _print_state(game, lock)
        elif cmd == "prestige":
            with lock:
                _call_any(game, ("prestige",))
            _print_state(game, lock)
        elif cmd == "save":
            if save_game is None:
                print("⚠️  save_game not available.", flush=True)
            else:
                with lock:
                    try:
                        save_game(game.get_state(), backups_to_keep=backups_to_keep)
                        print("💾 Saved.", flush=True)
                    except Exception as e:
                        print(f"❌ Save failed: {e}", flush=True)
        elif cmd == "":
            continue
        else:
            print("Unknown command. Type 'help' for options.", flush=True)

    print("Goodbye! 👋", flush=True)

