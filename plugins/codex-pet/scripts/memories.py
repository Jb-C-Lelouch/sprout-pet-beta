"""Permanent first achievements, separate from the bounded recent event log."""
import time


def record(db,kind,subject,observed=None):
    db.execute('INSERT OR IGNORE INTO garden_memories(kind,subject,observed) VALUES(?,?,?)',
               (kind,subject,int(time.time()) if observed is None else observed))


def initialize(db):
    existed=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='garden_memories'").fetchone()
    db.execute("CREATE TABLE IF NOT EXISTS garden_memories(id INTEGER PRIMARY KEY,kind TEXT NOT NULL,subject TEXT NOT NULL,observed INTEGER,UNIQUE(kind,subject))")
    if existed:return
    # Legacy saves know the achievement but not when it happened.
    for kind,subject in db.execute('SELECT kind,item FROM garden_collection').fetchall():
        if kind in ('plant','visitor'):
            db.execute('INSERT OR IGNORE INTO garden_memories(kind,subject,observed) VALUES(?,?,NULL)',('mature' if kind=='plant' else kind,subject))
    for subject, in db.execute('SELECT species FROM garden_inventory WHERE amount>0').fetchall():
        db.execute("INSERT OR IGNORE INTO garden_memories(kind,subject,observed) VALUES('harvest',?,NULL)",(subject,))
    for kind,subject in db.execute("SELECT DISTINCT action,species FROM garden_events WHERE action IN ('harvest','feed')").fetchall():
        db.execute('INSERT OR IGNORE INTO garden_memories(kind,subject,observed) VALUES(?,?,NULL)',(kind,subject))


def entries(db):
    return [dict(id=i,kind=k,subject=s,observed=t) for i,k,s,t in db.execute(
        'SELECT id,kind,subject,observed FROM garden_memories ORDER BY observed IS NULL,observed DESC,id DESC')]
