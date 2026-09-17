"""Local-only experimental Codex transcript adapter; Python standard library."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rules
import growth
import energy
import garden


def snapshot(path, session):
    latest = None
    identity = None
    with Path(path).open(encoding="utf-8") as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # A writer may not have finished its last line.
            if not isinstance(row, dict):
                continue
            payload = row.get("payload") or {}
            if not isinstance(payload, dict):
                continue
            if row.get("type") == "session_meta":
                identity = payload.get("id")
            if row.get("type") == "event_msg" and payload.get("type") == "token_count":
                info = payload.get("info")
                if isinstance(info, dict):
                    usage = info.get("total_token_usage")
                    if isinstance(usage, dict):
                        value = usage.get("total_tokens")
                        if type(value) is int and value >= 0:
                            latest = value
    if identity != session:
        raise ValueError("session identity mismatch")
    return latest


# These tables belong exclusively to the removed prototype. Never recreate them.
RETIRED_TABLES=('learned','loadout','rewards','battle_reports','card_identity','friendly_deck','friend_cards','friendly_reports')


def retire_combat(db):
    with db:
        db.execute('BEGIN IMMEDIATE')
        for table in RETIRED_TABLES:db.execute('DROP TABLE IF EXISTS '+table)


def connect(directory,now=None):
    directory.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(directory / "pet.sqlite3", timeout=5)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, high INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS pet(id INTEGER PRIMARY KEY CHECK(id=1), tokens INTEGER NOT NULL);
        INSERT OR IGNORE INTO pet VALUES(1,0);
        CREATE TABLE IF NOT EXISTS health(id INTEGER PRIMARY KEY CHECK(id=1), message TEXT, updated TEXT);
    """)
    growth.initialize(db,now)
    energy.initialize(db)
    retire_combat(db)
    garden.initialize(db)
    return db


def record(db, session, total, baseline=False,now=None):
    # The same transaction serializes callbacks from multiple Codex tasks.
    with db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute("SELECT high FROM sessions WHERE id=?", (session,)).fetchone()
        delta = 0
        if previous is None:
            db.execute("INSERT INTO sessions VALUES(?,?)", (session, total))
            message = "baseline established; historical tokens excluded"
        elif total < previous[0]:
            message = "counter decreased; credit paused until previous high-water mark"
        else:
            delta = 0 if baseline else total - previous[0]
            db.execute("UPDATE sessions SET high=? WHERE id=?", (total, session))
            db.execute("UPDATE pet SET tokens=tokens+? WHERE id=1", (delta,))
            message = "baseline refreshed" if baseline else "real transcript usage received"
        db.execute("INSERT OR REPLACE INTO health VALUES(1,?,datetime('now'))", (message,))
        growth.credit_tokens(db,now)
        garden.sync(db)
    return delta


def handle(db, event):
    kind = event.get("hook_event_name")
    if kind not in ("SessionStart", "UserPromptSubmit", "Stop"):
        return 0
    session = event.get("session_id")
    if not isinstance(session, str) or not session:
        raise ValueError("missing session_id")
    path = event.get("transcript_path")
    if not path:
        raise ValueError("transcript unavailable; no experience awarded")
    total = snapshot(path, session)
    if total is None:
        if kind in ("SessionStart", "UserPromptSubmit"):
            total = 0
        else:
            raise ValueError("no supported token counter; no experience awarded")
    # Prompt callbacks initialize new sessions only, preserving late Stop updates.
    if kind == "UserPromptSubmit" and db.execute("SELECT 1 FROM sessions WHERE id=?", (session,)).fetchone():
        return 0
    return record(db, session, total, baseline=kind == "SessionStart")


def tick(db,mode='observe',now=None):
    with db:
        db.execute('BEGIN IMMEDIATE')
        receipt=growth.settle(db,mode,now)
        growth.credit_tokens(db,now)
        garden.sync(db)
    return receipt


def status(db):
    tokens = db.execute("SELECT tokens FROM pet WHERE id=1").fetchone()[0]
    progress = rules.progress_for_db(db)
    level = progress["level"]
    health = db.execute("SELECT message,updated FROM health WHERE id=1").fetchone()
    return {"name": "小芽", **progress,
            "form": "幼芽" if level < 5 else "灵芽" if level < 15 else "灵木" if level < 30 else "星树",
            "credited_tokens": tokens, "source": "local-time-and-token-energy", "growth":growth.summary(db), "energy":energy.summary(db),
            "connection": health[0] if health else "waiting for first hook",
            "last_event_utc": health[1] if health else None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["hook", "status", "garden", "plant", "garden-move", "garden-remove"])
    parser.add_argument('--plot',type=int)
    parser.add_argument('--plant')
    parser.add_argument('--destination',type=int)
    parser.add_argument("--data", type=Path)
    args = parser.parse_args()
    directory = args.data or Path(os.environ.get("CODEX_PET_DATA") or
                                  str(Path.home() / ".codex-pet"))
    db = connect(directory)
    try:
        if args.command == "hook":
            try:
                handle(db, json.load(sys.stdin))
            except (OSError, ValueError, TypeError, AttributeError) as exc:
                with db:
                    db.execute("INSERT OR REPLACE INTO health VALUES(1,?,datetime('now'))",
                               ("collection unavailable: " + type(exc).__name__,))
            print("{}")  # Never ask Codex to continue just to feed the pet.
        elif args.command in ('garden','plant','garden-move','garden-remove'):
            tick(db)
            if args.command!='garden':
                action={'plant':'plant','garden-move':'move','garden-remove':'remove'}[args.command]
                garden.edit(db,action,args.plot,args.plant,args.destination)
            print(json.dumps(garden.snapshot(db),ensure_ascii=True,indent=2))
        else:
            tick(db)
            print(json.dumps(status(db),ensure_ascii=True,indent=2))
    except (ValueError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True))
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
