from test_pet import pet
from pathlib import Path
import tempfile
import unittest

class CompanionTests(unittest.TestCase):
    def test_feed_consumes_once_without_growth_rewards_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            db=pet.connect(directory,now=1800000000)
            with db:db.execute("INSERT INTO garden_inventory VALUES('carrot',1)")
            xp=pet.growth.total_units(db);energy=pet.energy.summary(db)
            self.assertTrue(pet.garden.feed(db,'carrot'))
            self.assertFalse(pet.garden.feed(db,'carrot'))
            self.assertEqual(pet.growth.total_units(db),xp)
            self.assertEqual(pet.energy.summary(db),energy)
            db.close()
            db=pet.connect(directory,now=1800000000)
            self.assertEqual(db.execute("SELECT amount FROM garden_inventory WHERE species='carrot'").fetchone()[0],0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM garden_events WHERE action='feed'").fetchone()[0],1)
            db.close()

    def test_non_food_is_rejected_without_consumption(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=pet.connect(Path(tmp),now=1800000000)
            with db:db.execute("INSERT INTO garden_inventory VALUES('cherry',1)")
            with self.assertRaises(ValueError):pet.garden.feed(db,'cherry')
            self.assertEqual(db.execute("SELECT amount FROM garden_inventory WHERE species='cherry'").fetchone()[0],1)
            db.close()
