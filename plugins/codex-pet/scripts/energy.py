"""Token-backed energy. Stored in token-sized units; callers own transactions."""
UNIT=1000
CAP=100*UNIT


def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS pet_energy(id INTEGER PRIMARY KEY CHECK(id=1),units INTEGER NOT NULL CHECK(units BETWEEN 0 AND 100000),accounted_tokens INTEGER NOT NULL)')
    with db:
        db.execute('INSERT OR IGNORE INTO pet_energy SELECT 1,0,tokens FROM pet WHERE id=1')


def credit(db):
    total=db.execute('SELECT tokens FROM pet WHERE id=1').fetchone()[0]
    old=db.execute('SELECT accounted_tokens FROM pet_energy WHERE id=1').fetchone()[0]
    delta=max(0,total-old)
    if delta:db.execute('UPDATE pet_energy SET units=min(?,units+?),accounted_tokens=? WHERE id=1',(CAP,delta,total))
    return delta/UNIT


def summary(db):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='pet_energy'").fetchone():return None
    row=db.execute('SELECT units FROM pet_energy WHERE id=1').fetchone()
    return dict(current=row[0]/UNIT,cap=100,tokens_per_point=UNIT) if row else None
