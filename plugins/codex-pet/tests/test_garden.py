from test_pet import pet
from contextlib import closing
from pathlib import Path
import tempfile
import unittest

garden=pet.garden


class GardenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.db=pet.connect(self.path,now=1800000000)

    def tearDown(self):self.db.close();self.tmp.cleanup()

    def xp(self,value):
        with self.db:
            self.db.execute('UPDATE growth_state SET xp=? WHERE id=1',(value*pet.growth.UNIT,))
            garden.sync(self.db)

    def test_fresh_and_locked_plant(self):
        self.assertEqual(len(garden.snapshot(self.db)['plots']),9)
        with self.assertRaises(ValueError):garden.edit(self.db,'plant',1,'cherry')
        garden.edit(self.db,'plant',1,'clover')
        self.assertEqual(pet.growth.total_units(self.db),0)
        with self.assertRaises(ValueError):garden.edit(self.db,'plant',1,'clover')
        with self.assertRaises(ValueError):garden.edit(self.db,'plant',True,'clover')

    def test_legacy_xp_does_not_instantly_mature(self):
        self.xp(6000);garden.edit(self.db,'plant',1,'cherry')
        self.assertEqual(garden.snapshot(self.db)['plots'][0]['progress'],0)
        self.xp(6036)
        self.assertEqual(garden.snapshot(self.db)['plots'][0]['progress'],.5)

    def test_mature_collection_and_visitors_persist(self):
        self.xp(1000)
        for p,s in enumerate(['clover','mint','daisy'],1):garden.edit(self.db,'plant',p,s)
        self.xp(1036)
        state=garden.snapshot(self.db)
        self.assertTrue(all(v['discovered'] for v in state['visitors']))
        for p in range(1,4):garden.edit(self.db,'remove',p)
        self.assertTrue(all(v['discovered'] for v in garden.snapshot(self.db)['visitors']))
        self.assertEqual(pet.growth.total_units(self.db),1036*pet.growth.UNIT)

    def test_move_swap_preserves_start_and_rejects_stale(self):
        self.xp(1000);garden.edit(self.db,'plant',1,'clover')
        self.xp(1002);garden.edit(self.db,'plant',2,'mint')
        before=garden.snapshot(self.db);revision=before['revision']
        garden.edit(self.db,'move',1,destination=2,expected=revision)
        after=garden.snapshot(self.db)
        self.assertEqual(after['plots'][1]['earned_xp'],2)
        self.assertEqual(after['plots'][0]['earned_xp'],0)
        with self.assertRaises(ValueError):garden.edit(self.db,'remove',1,expected=revision)
        garden.edit(self.db,'move',2,destination=6)
        self.assertEqual(garden.snapshot(self.db)['plots'][5]['earned_xp'],2)

    def test_snapshot_read_only_and_reopen(self):
        garden.edit(self.db,'plant',1,'clover')
        before=list(self.db.iterdump());state=garden.snapshot(self.db)
        self.assertEqual(before,list(self.db.iterdump()))
        self.db.close();self.db=pet.connect(self.path)
        self.assertEqual(state,garden.snapshot(self.db))

    def test_offline_time_grows_plants_no_token_required(self):
        garden.edit(self.db,'plant',1,'clover')
        pet.tick(self.db,now=1800000000+7200)
        state=garden.snapshot(self.db)
        self.assertEqual(state['plots'][0]['stage'],'成熟')
        self.assertTrue(state['visitors'][0]['discovered'])
        self.assertEqual(pet.status(self.db)['credited_tokens'],0)
