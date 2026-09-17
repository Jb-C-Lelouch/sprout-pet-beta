from test_pet import pet
from contextlib import closing
from pathlib import Path
import concurrent.futures
import tempfile
import unittest


class EnergyWorkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.db=pet.connect(self.path,now=1800000000)

    def tearDown(self):self.db.close();self.tmp.cleanup()

    def fill(self):
        with self.db:self.db.execute('UPDATE pet_energy SET units=100000')

    def test_baseline_fraction_repeat_overflow_and_no_xp(self):
        pet.record(self.db,'s',100000)
        self.assertEqual(pet.energy.summary(self.db)['current'],0)
        pet.record(self.db,'s',100125);pet.record(self.db,'s',100125)
        self.assertEqual(pet.energy.summary(self.db)['current'],.125)
        pet.record(self.db,'s',400000)
        self.assertEqual(pet.energy.summary(self.db)['current'],100)
        with self.db:self.db.execute('UPDATE pet_energy SET units=0')
        pet.record(self.db,'s',400000)
        self.assertEqual(pet.energy.summary(self.db)['current'],0)
        pet.record(self.db,'s',399000);pet.record(self.db,'s',401000)
        self.assertEqual(pet.energy.summary(self.db)['current'],1)
        self.assertEqual(pet.growth.total_units(self.db),0)

    def test_empty_energy_blocks_work_but_not_natural_growth(self):
        pet.garden.edit(self.db,'plant',1,'clover')
        self.assertIsNone(pet.garden.work_plan(self.db,1800000000))
        pet.tick(self.db,now=1800007200)
        self.assertEqual(pet.garden.snapshot(self.db)['plots'][0]['progress'],1)
        self.assertEqual(pet.energy.summary(self.db)['current'],0)

    def test_atomic_plant_cooldown_stale_and_pause(self):
        self.fill();plan=pet.garden.work_plan(self.db,100)
        self.assertTrue(pet.garden.perform_work(self.db,plan,100))
        self.assertFalse(pet.garden.perform_work(self.db,plan,100))
        self.assertEqual(pet.energy.summary(self.db)['current'],94)
        self.assertIsNone(pet.garden.work_plan(self.db,159))
        next_plan=pet.garden.work_plan(self.db,160)
        self.assertGreater(next_plan['plot'],6)
        pet.garden.set_autonomy(self.db,False)
        self.assertFalse(pet.garden.perform_work(self.db,next_plan,160))
        self.assertEqual(pet.energy.summary(self.db)['current'],94)

    def test_care_cannot_replace_more_than_half_natural_growth(self):
        for n in range(1,10):pet.garden.edit(self.db,'plant',n,'clover' if n<=6 else 'carrot')
        actions=set()
        for t in range(100,20000,61):
            self.fill();plan=pet.garden.work_plan(self.db,t)
            if not plan:break
            actions.add(plan['action']);self.assertTrue(pet.garden.perform_work(self.db,plan,t))
        self.assertTrue({'water','fertilize'}<=actions)
        self.assertTrue(all(p['progress']==.5 for p in pet.garden.snapshot(self.db)['plots']))
        self.assertEqual(pet.growth.total_units(self.db),0)
        before=list(self.db.iterdump());pet.garden.snapshot(self.db)
        self.assertEqual(before,list(self.db.iterdump()))

    def test_harvest_inventory_and_replant_resets_care(self):
        self.fill();pet.garden.edit(self.db,'plant',7,'carrot')
        with self.db:
            self.db.execute('UPDATE growth_state SET xp=?',(18*pet.growth.UNIT,))
            self.db.execute('INSERT INTO garden_care VALUES(7,3600,1)')
        plan=pet.garden.work_plan(self.db,100);self.assertEqual(plan['action'],'harvest')
        self.assertTrue(pet.garden.perform_work(self.db,plan,100))
        self.assertEqual(pet.garden.snapshot(self.db)['inventory'],{'carrot':1})
        self.assertIsNone(self.db.execute('SELECT * FROM garden_care WHERE plot=7').fetchone())
        self.assertFalse(pet.garden.perform_work(self.db,plan,161))
        pet.garden.edit(self.db,'plant',7,'carrot')
        self.assertEqual(pet.garden.snapshot(self.db)['plots'][6]['progress'],0)

    def test_same_job_from_two_connections_commits_once(self):
        self.fill();plan=pet.garden.work_plan(self.db,100)
        def run(_):
            with closing(pet.connect(self.path)) as db:return pet.garden.perform_work(db,plan,100)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(run,range(2))),1)
        self.assertEqual(pet.energy.summary(self.db)['current'],94)

    def test_migration_preserves_old_growth_plants_and_excludes_old_tokens(self):
        with self.db:
            self.db.execute('DROP TABLE pet_energy')
            self.db.execute('UPDATE pet SET tokens=200000')
            self.db.execute('UPDATE growth_state SET xp=7654321')
            self.db.execute('DROP TABLE garden_plots')
            self.db.execute('CREATE TABLE garden_plots(plot INTEGER PRIMARY KEY CHECK(plot BETWEEN 1 AND 6),species TEXT NOT NULL,planted_xp INTEGER NOT NULL)')
            self.db.execute("INSERT INTO garden_plots VALUES(4,'clover',123456)")
        self.db.close();self.db=pet.connect(self.path)
        self.assertEqual(pet.growth.total_units(self.db),7654321)
        self.assertEqual(self.db.execute('SELECT * FROM garden_plots').fetchall(),[(4,'clover',123456)])
        self.assertEqual(pet.energy.summary(self.db)['current'],0)
        pet.garden.edit(self.db,'plant',7,'carrot')

    def test_moving_keeps_care_and_forbids_cross_zone(self):
        pet.garden.edit(self.db,'plant',1,'clover')
        with self.db:self.db.execute('INSERT INTO garden_care VALUES(1,3600,1)')
        pet.garden.edit(self.db,'move',1,destination=2)
        self.assertEqual(self.db.execute('SELECT * FROM garden_care').fetchall(),[(2,3600,1)])
        with self.assertRaises(ValueError):pet.garden.edit(self.db,'move',2,destination=7)
        pet.garden.edit(self.db,'remove',2)
        self.assertEqual(self.db.execute('SELECT * FROM garden_care').fetchall(),[])
