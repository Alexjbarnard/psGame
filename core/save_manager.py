# core/save_manager.py
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

SAVE_DIR = Path("data")
SAVE_PATH = SAVE_DIR / "savegame.json"
BACKUP_DIR = SAVE_DIR / "saves"
SCHEMA_VERSION = 1

def _write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def _trim_backups(limit: int) -> None:
    backups = sorted(BACKUP_DIR.glob("save_*.json"))
    while len(backups) > limit:
        old = backups.pop(0)
        try:
            old.unlink()
        except OSError:
            pass

def save_game(state: Dict[str, Any], backups_to_keep: int = 10) -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    to_write = {
        **state,
        "_schema_version": SCHEMA_VERSION,
        "_saved_at": time.time(),
    }
    text = json.dumps(to_write)

    # atomic main save
    _write_atomic(SAVE_PATH, text)

    # timestamped backup
    backup = BACKUP_DIR / f"save_{int(time.time())}.json"
    _write_atomic(backup, text)
    _trim_backups(backups_to_keep)

def load_game() -> Optional[Dict[str, Any]]:
    if SAVE_PATH.exists():
        return json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    return None

