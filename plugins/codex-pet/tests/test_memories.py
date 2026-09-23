from test_pet import pet
import memories
import tempfile
from pathlib import Path
import unittest

class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.db=pet.connect(self.path,now=1800000000)
    def tearDown(self):self.db.close();self.tmp.cleanup()
    def test_first_maturity_and_visitor_are_permanent_and_unique(self):
        pet.garden.edit(self.db,'plant',1,'clover')
        with self.db:
            self.db.execute('UPDATE growth_state SET xp=?',(100*pet.growth.UNIT,))
            pet.garden.sync(self.db);pet.garden.sync(self.db)
        rows=memories.entries(self.db)
        self.assertEqual({(r['kind'],r['subject']) for r in rows},{('mature','clover'),('visitor','butterfly')})
        self.assertTrue(all(r['observed'] is not None for r in rows))
        with self.db:
            for _ in range(30):pet.garden.log_event(self.db,'water','clover')
        self.assertEqual(memories.entries(self.db),rows)
    def test_legacy_migration_never_invents_dates(self):
        with self.db:
            self.db.execute('DROP TABLE garden_memories')
            self.db.execute("INSERT INTO garden_collection VALUES('plant','clover')")
            self.db.execute("INSERT INTO garden_inventory VALUES('carrot',2)")
            self.db.execute("INSERT INTO garden_events(action,species) VALUES('feed','carrot')")
        self.db.close();self.db=pet.connect(self.path,now=1800000000)
        rows=memories.entries(self.db)
        self.assertEqual(len(rows),3);self.assertTrue(all(r['observed'] is None for r in rows))
        with self.db:memories.record(self.db,'mature','clover')
        self.assertEqual(memories.entries(self.db),rows)
    def test_rollback_does_not_record_uncommitted_achievement(self):
        with self.assertRaises(RuntimeError):
            with self.db:
                pet.garden.log_event(self.db,'harvest','carrot')
                raise RuntimeError('abort')
        self.assertEqual(memories.entries(self.db),[])
