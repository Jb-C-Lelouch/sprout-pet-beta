from test_pet import pet
from contextlib import closing
from pathlib import Path
import tempfile
import unittest
from garden_motion import Gardener


class SceneTests(unittest.TestCase):
    def test_autoplant_is_atomic_and_costs_no_xp(self):
        with tempfile.TemporaryDirectory() as tmp,closing(pet.connect(Path(tmp))) as db:
            first=pet.garden.auto_plan(db);before=pet.growth.total_units(db)
            self.assertTrue(pet.garden.auto_plant(db,first))
            self.assertEqual(pet.growth.total_units(db),before)
            self.assertFalse(pet.garden.auto_plant(db,first))
            self.assertIsNone(pet.garden.auto_plan(db))
            with db:db.execute('UPDATE growth_state SET xp=xp+?',(6*pet.growth.UNIT,))
            second=pet.garden.auto_plan(db)
            self.assertEqual(second['plot'],2)
            self.assertIsNone(second['species'])

    def test_pause_and_stale_layout_cancel_pending_plant(self):
        with tempfile.TemporaryDirectory() as tmp,closing(pet.connect(Path(tmp))) as db:
            plan=pet.garden.auto_plan(db)
            pet.garden.set_autonomy(db,False)
            self.assertFalse(pet.garden.auto_plant(db,plan))
            pet.garden.set_autonomy(db,True)
            pet.garden.edit(db,'plant',1,'clover')
            self.assertFalse(pet.garden.auto_plant(db,plan))
            self.assertEqual(pet.garden.snapshot(db)['plots'][0]['species'],'clover')

    def test_full_garden_and_reopen_do_not_reset_seed_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            with closing(pet.connect(Path(tmp))) as db:
                pet.garden.auto_plant(db,pet.garden.auto_plan(db))
            with closing(pet.connect(Path(tmp))) as db:
                self.assertIsNone(pet.garden.auto_plan(db))
                for n in range(2,10):pet.garden.edit(db,'plant',n,'clover' if n<=6 else 'carrot')
                with db:db.execute('UPDATE growth_state SET xp=xp+?',(100*pet.growth.UNIT,))
                self.assertIsNone(pet.garden.auto_plan(db))

    def test_motion_walks_and_digs_before_commit(self):
        brain=Gardener();proposal=dict(plot=1,species='clover',revision=0)
        modes=set();event=None
        for i in range(200):
            event=brain.advance(.1,proposal);modes.add(brain.mode)
            if event:break
        self.assertEqual(event,proposal)
        self.assertTrue({'rest','walk','dig','water'}<=modes)
        self.assertGreater(i,70)
        self.assertEqual((brain.x,brain.y),(171,256))
        brain.cancel_work();self.assertIsNone(brain.plan)
