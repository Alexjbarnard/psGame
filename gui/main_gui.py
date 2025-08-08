"""
Simple Tkinter GUI for Pit Stop.

Matches launcher signature:
    run_gui(game, settings, stop_event, lock)

- Uses the shared PitStopGame instance (already ticking in main.py)
- Reads state with a lock, updates UI every 250ms
- Buttons call engine methods inside the same lock
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Iterable

# Optional: small helper to flexibly call engine methods even if names differ
def _call_any(obj, names: Iterable[str], *args, **kwargs):
    for n in names:
        fn = getattr(obj, n, None)
        if callable(fn):
            return fn(*args, **kwargs)
    raise AttributeError(f"None of these methods exist on {type(obj).__name__}: {', '.join(names)}")

def run_gui(game, settings, stop_event, lock):
    # Lazy import to avoid circulars
    try:
        from core.save_manager import save_game
    except Exception:
        save_game = None

    backups_to_keep = int(settings.get("backups_to_keep", 10))

    root = tk.Tk()
    root.title("⛽ Pit Stop")

    # === Top: Stats ===
    stats_frame = ttk.Frame(root, padding=10)
    stats_frame.grid(row=0, column=0, sticky="nsew")

    lbl_cash_var = tk.StringVar()
    lbl_income_var = tk.StringVar()
    lbl_pumps_var = tk.StringVar()
    lbl_pump_lvl_var = tk.StringVar()
    lbl_store_lvl_var = tk.StringVar()
    lbl_status_var = tk.StringVar(value="Ready.")

    ttk.Label(stats_frame, text="Cash:").grid(row=0, column=0, sticky="w")
    ttk.Label(stats_frame, textvariable=lbl_cash_var).grid(row=0, column=1, sticky="w", padx=(4, 12))

    ttk.Label(stats_frame, text="Income/sec:").grid(row=0, column=2, sticky="w")
    ttk.Label(stats_frame, textvariable=lbl_income_var).grid(row=0, column=3, sticky="w", padx=(4, 12))

    ttk.Label(stats_frame, text="Pumps:").grid(row=1, column=0, sticky="w")
    ttk.Label(stats_frame, textvariable=lbl_pumps_var).grid(row=1, column=1, sticky="w", padx=(4, 12))

    ttk.Label(stats_frame, text="Pump Lvl:").grid(row=1, column=2, sticky="w")
    ttk.Label(stats_frame, textvariable=lbl_pump_lvl_var).grid(row=1, column=3, sticky="w", padx=(4, 12))

    ttk.Label(stats_frame, text="Store Lvl:").grid(row=1, column=4, sticky="w")
    ttk.Label(stats_frame, textvariable=lbl_store_lvl_var).grid(row=1, column=5, sticky="w", padx=(4, 12))

    # === Middle: Actions ===
    btns = ttk.Frame(root, padding=(10, 0, 10, 10))
    btns.grid(row=1, column=0, sticky="nsew")
    btns.columnconfigure((0,1,2), weight=1)

    def do(action_names):
        try:
            with lock:
                _call_any(game, action_names)
            lbl_status_var.set(f"✅ {action_names[0].replace('_',' ').title()} OK")
        except Exception as e:
            lbl_status_var.set(f"⚠️ {e}")

    ttk.Button(btns, text="Upgrade Pump",
               command=lambda: do(("upgrade_pump", "upgrade_gas_pump"))).grid(row=0, column=0, sticky="ew", padx=4, pady=4)

    ttk.Button(btns, text="Buy Pump",
               command=lambda: do(("buy_pump", "buy_new_pump", "purchase_pump"))).grid(row=0, column=1, sticky="ew", padx=4, pady=4)

    ttk.Button(btns, text="Upgrade Store",
               command=lambda: do(("upgrade_store",))).grid(row=0, column=2, sticky="ew", padx=4, pady=4)

    ttk.Button(btns, text="Remodel",
               command=lambda: do(("remodel",))).grid(row=1, column=0, sticky="ew", padx=4, pady=4)

    ttk.Button(btns, text="Prestige",
               command=lambda: do(("prestige",))).grid(row=1, column=1, sticky="ew", padx=4, pady=4)

    def do_save():
        if save_game is None:
            lbl_status_var.set("⚠️ save_game not available")
            return
        try:
            with lock:
                save_game(game.get_state(), backups_to_keep=backups_to_keep)
            lbl_status_var.set("💾 Saved.")
        except Exception as e:
            lbl_status_var.set(f"❌ Save failed: {e}")

    ttk.Button(btns, text="Save Now", command=do_save).grid(row=1, column=2, sticky="ew", padx=4, pady=4)

    # === Bottom: Status & Quit ===
    bottom = ttk.Frame(root, padding=10)
    bottom.grid(row=2, column=0, sticky="ew")
    bottom.columnconfigure(0, weight=1)

    ttk.Label(bottom, textvariable=lbl_status_var, anchor="w").grid(row=0, column=0, sticky="ew")
    ttk.Button(bottom, text="Quit", command=root.destroy).grid(row=0, column=1, sticky="e", padx=(10,0))

    # === Refresh loop ===
    def refresh_ui():
        with lock:
            try:
                state = game.get_state()
            except Exception:
                state = {}
        lbl_cash_var.set(f"{state.get('currency', 0):,.2f}")
        ips = state.get('income_per_second', 0)
        lbl_income_var.set(f"{ips:,.2f}")
        lbl_pumps_var.set(str(state.get('gas_pumps', 0)))
        lbl_pump_lvl_var.set(str(state.get('gas_pump_level', 0)))
        lbl_store_lvl_var.set(str(state.get('store_level', 0)))

        # Reschedule
        if not stop_event.is_set():
            root.after(250, refresh_ui)

    refresh_ui()

    def on_close():
        # Signal main.py to wind down threads; main will also do a final save
        try:
            stop_event.set()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Basic theming for readability
    try:
        root.tk.call("ttk::style", "theme", "use", "clam")
    except Exception:
        pass

    # Sensible minimum size
    root.minsize(560, 200)
    root.mainloop()

