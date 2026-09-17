from test_pet import pet
from contextlib import closing
import concurrent.futures
from pathlib import Path
import sqlite3
import tempfile
import unittest

g=pet.growth


class GrowthTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.start=1800000000
        self.db=pet.connect(self.path,now=self.start)

    def tearDown(self):
        self.db.close();self.tmp.cleanup()

    def test_online_tick_frequency_and_duplicate(self):
        pet.tick(self.db,'heartbeat',self.start)
        for offset in range(15,3601,15):pet.tick(self.db,'heartbeat',self.start+offset)
        self.assertEqual(g.total_units(self.db),6*g.UNIT)
        self.assertEqual(pet.tick(self.db,'heartbeat',self.start+3600)['online_xp'],0)
        self.assertEqual(g.total_units(self.db),6*g.UNIT)
        self.assertEqual(pet.status(self.db)['credited_tokens'],0)

    def test_offline_cap_not_reset_by_read_or_token(self):
        first=pet.tick(self.db,now=self.start+10*3600)
        self.assertEqual(first['offline_xp'],30)
        pet.record(self.db,'s',0,now=self.start+10*3600)
        pet.record(self.db,'s',1000,now=self.start+10*3600)
        second=pet.tick(self.db,now=self.start+20*3600)
        self.assertEqual(second['offline_xp'],6)
        self.assertTrue(second['offline_capped'])
        self.assertEqual(pet.tick(self.db,now=self.start+40*3600)['offline_xp'],0)

    def test_close_and_reopen_receipt_only_once(self):
        pet.tick(self.db,'heartbeat',self.start)
        pet.tick(self.db,'close',self.start+30)
        receipt=pet.tick(self.db,'heartbeat',self.start+3630)
        self.assertEqual(receipt['offline_xp'],3)
        self.assertEqual(pet.tick(self.db,'heartbeat',self.start+3630)['offline_xp'],0)
        self.assertEqual(pet.tick(self.db,'close',self.start+3660)['online_xp'],.05)
        self.assertEqual(pet.tick(self.db,'heartbeat',self.start+7260)['offline_xp'],3)

    def test_sleep_and_clock_rollback(self):
        pet.tick(self.db,'heartbeat',self.start)
        receipt=pet.tick(self.db,'heartbeat',self.start+86400)
        self.assertEqual(receipt['online_xp'],45*6/3600)
        self.assertEqual(receipt['offline_xp'],36)
        units=g.total_units(self.db)
        self.assertTrue(pet.tick(self.db,'heartbeat',self.start+1)['clock_paused'])
        self.assertEqual(g.total_units(self.db),units)

    def test_token_splitting_daily_reset_and_rollback(self):
        pet.record(self.db,'a',0,now=self.start)
        for n in range(1000,100001,1000):pet.record(self.db,'a',n,now=self.start)
        self.assertEqual(g.total_units(self.db),0)
        self.assertEqual(pet.record(self.db,'a',100000,now=self.start),0)
        tomorrow=(self.start//86400+1)*86400
        pet.record(self.db,'a',200000,now=tomorrow)
        self.assertEqual(g.total_units(self.db),0)
        pet.record(self.db,'a',300000,now=self.start)
        self.assertEqual(g.total_units(self.db),0)
        self.assertLess(g.bonus(10**12),30*g.UNIT)

    def test_concurrent_heartbeat_never_multiplies_time(self):
        def run(_):
            with closing(pet.connect(self.path,now=self.start)) as db:
                return pet.tick(db,'heartbeat',self.start+3600)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            values=list(pool.map(run,range(12)))
        self.assertEqual(sum(v['offline_xp'] for v in values),3)
        self.assertEqual(g.total_units(self.db),3*g.UNIT)

    def test_migration_preserves_legacy_and_no_time_backfill(self):
        old=self.path/'old';old.mkdir()
        with closing(sqlite3.connect(old/'pet.sqlite3')) as db:
            db.executescript('CREATE TABLE pet(id INTEGER PRIMARY KEY,tokens INTEGER NOT NULL); INSERT INTO pet VALUES(1,6062334);')
        with closing(pet.connect(old,now=self.start)) as db:
            state=pet.status(db)
            self.assertEqual(state['level'],30)
            self.assertEqual(state['experience'],6062)
            self.assertEqual(pet.tick(db,now=self.start)['offline_xp'],0)
            before=g.total_units(db)
        with closing(pet.connect(old,now=self.start+86400)) as db:
            self.assertEqual(g.total_units(db),before)
            self.assertEqual(pet.tick(db,now=self.start+86400)['offline_xp'],36)

    def test_time_alone_grows_level(self):
        pet.tick(self.db,now=self.start+12*3600)
        state=pet.status(self.db)
        self.assertEqual(state['level'],3)
        self.assertEqual(state['credited_tokens'],0)

    def test_old_hook_counter_is_reconciled_once(self):
        with self.db:self.db.execute('UPDATE pet SET tokens=100000 WHERE id=1')
        pet.tick(self.db,now=self.start)
        self.assertEqual(g.total_units(self.db),0)
        pet.tick(self.db,now=self.start)
        self.assertEqual(g.total_units(self.db),0)
