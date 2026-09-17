"""Local time growth with bounded offline storage and diminishing token bonus.

All mutations are called inside the caller's IMMEDIATE transaction. One XP is
3600 integer units, retaining fractions without tick-frequency rounding loss.
"""
import time

UNIT=3600
ONLINE_RATE=6
OFFLINE_RATE=3
OFFLINE_CAP=12*3600
LEASE=45
TOKEN_MAX=30*UNIT
TOKEN_SCALE=100000


def initialize(db, now=None):
    now=int(time.time() if now is None else now)
    db.executescript('''CREATE TABLE IF NOT EXISTS growth_state(
        id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL,
        xp INTEGER NOT NULL, legacy_xp INTEGER NOT NULL,
        last_wall INTEGER NOT NULL, lease_until INTEGER NOT NULL,
        offline_used INTEGER NOT NULL, online_seconds INTEGER NOT NULL,
        offline_seconds INTEGER NOT NULL, token_xp INTEGER NOT NULL,
        token_day INTEGER NOT NULL, day_tokens INTEGER NOT NULL,
        accounted_tokens INTEGER NOT NULL);
    ''')
    with db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT 1 FROM growth_state WHERE id=1').fetchone():return
        tokens=db.execute('SELECT tokens FROM pet WHERE id=1').fetchone()[0]
        legacy=tokens*UNIT//1000
        db.execute('INSERT INTO growth_state VALUES(1,1,?,?,?,0,0,0,0,0,?,0,?)',(legacy,legacy,now,now//86400,tokens))


def total_units(db):
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='growth_state'").fetchone():
        row=db.execute('SELECT xp FROM growth_state WHERE id=1').fetchone()
        if row:return row[0]
    return db.execute('SELECT tokens FROM pet WHERE id=1').fetchone()[0]*UNIT//1000


def bonus(tokens):
    return TOKEN_MAX*tokens//(TOKEN_SCALE+tokens)


def credit_tokens(db,now=None):
    import energy
    energy.credit(db)
    total=db.execute('SELECT tokens FROM pet WHERE id=1').fetchone()[0]
    db.execute('UPDATE growth_state SET accounted_tokens=max(accounted_tokens,?) WHERE id=1',(total,))
    return 0


def settle(db,mode='observe',now=None):
    if mode not in ('observe','heartbeat','close'):raise ValueError('Unknown time mode')
    now=int(time.time() if now is None else now)
    last,lease,used=db.execute('SELECT last_wall,lease_until,offline_used FROM growth_state WHERE id=1').fetchone()
    if now<last:
        return dict(online_xp=0,offline_xp=0,clock_paused=True,offline_capped=False)
    online=max(0,min(now,lease)-last)
    absent=now-last-online
    offline=min(absent,max(0,OFFLINE_CAP-used))
    used=min(OFFLINE_CAP,used+absent)
    earned=online*ONLINE_RATE+offline*OFFLINE_RATE
    if mode=='heartbeat':lease=now+LEASE;used=0
    elif mode=='close':lease=now
    db.execute('UPDATE growth_state SET xp=xp+?,last_wall=?,lease_until=?,offline_used=?,online_seconds=online_seconds+?,offline_seconds=offline_seconds+? WHERE id=1',
               (earned,now,lease,used,online,offline))
    return dict(online_xp=online*ONLINE_RATE/UNIT,offline_xp=offline*OFFLINE_RATE/UNIT,
                clock_paused=False,offline_capped=absent>offline)


def summary(db,now=None):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='growth_state'").fetchone():return None
    row=db.execute('SELECT xp,legacy_xp,online_seconds,offline_seconds,token_xp,token_day,day_tokens,last_wall FROM growth_state WHERE id=1').fetchone()
    if not row:return None
    xp,legacy,online,offline,token,day,count,last=row
    now=int(time.time() if now is None else now)
    return dict(version=1,total_xp=xp/UNIT,legacy_xp=legacy/UNIT,online_seconds=online,offline_seconds=offline,
                online_xp=online*ONLINE_RATE/UNIT,offline_xp=offline*OFFLINE_RATE/UNIT,token_bonus_xp=token/UNIT,
                today_token_bonus_xp=0,
                online_xp_per_hour=ONLINE_RATE,offline_xp_per_hour=OFFLINE_RATE,offline_cap_hours=12,
                token_bonus_daily_limit=0,token_mode='energy',day_boundary='UTC 00:00',clock_paused=now<last)
