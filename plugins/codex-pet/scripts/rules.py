"""Local level progression shared by the pet and plant unlocks."""
import math
import growth

MAX_LEVEL=30

def progression(tokens):
    xp = tokens // 1000
    return progression_xp(xp)


def progress_for_db(db):
    return progression_xp(growth.total_units(db)//growth.UNIT)


def progression_xp(xp):
    level = min(MAX_LEVEL, (1 + math.isqrt(1 + 4 * (xp // 5))) // 2)
    spent = 5 * level * (level - 1)
    return dict(level=level, experience=xp, level_progress=xp-spent,
                next_level_cost=level*10 if level < MAX_LEVEL else None,
                level_cap=MAX_LEVEL, at_level_cap=level == MAX_LEVEL)

