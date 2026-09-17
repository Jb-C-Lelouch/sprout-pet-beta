from test_pet import pet
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest
import botany


class SeedBoxTests(unittest.TestCase):
    def test_planning_never_draws_and_successful_plant_draws_once(self):
        with tempfile.TemporaryDirectory() as tmp,closing(pet.connect(Path(tmp))) as db:
            with db:
                db.execute('UPDATE growth_state SET xp=?',(1000*pet.growth.UNIT,))
                db.execute('UPDATE pet_energy SET units=100000')
            with patch('garden.secrets.choice',return_value='daisy') as draw:
                plan=pet.garden.work_plan(db,100)
                self.assertEqual(plan,pet.garden.work_plan(db,100));draw.assert_not_called()
                self.assertIsNone(plan['species'])
                self.assertTrue(pet.garden.perform_work(db,plan,100));draw.assert_called_once()
                self.assertFalse(pet.garden.perform_work(db,plan,100));draw.assert_called_once()
            species=db.execute('SELECT species FROM garden_plots WHERE plot=1').fetchone()[0]
            self.assertEqual(species,'daisy')
            with patch('garden.secrets.choice',side_effect=AssertionError('unexpected reroll')):
                pet.garden.snapshot(db);pet.tick(db,now=1)
                pet.garden.edit(db,'move',1,destination=2)
                with closing(pet.connect(Path(tmp))) as other:
                    self.assertEqual(pet.garden.snapshot(other)['plots'][1]['species'],'daisy')

    def test_zone_pools_unlocks_and_explicit_manual_plant(self):
        with tempfile.TemporaryDirectory() as tmp,closing(pet.connect(Path(tmp))) as db:
            self.assertEqual(pet.garden.seed_pool(db,1),['clover','calendula'])
            self.assertEqual(pet.garden.seed_pool(db,7),['carrot','radish','lettuce'])
            with db:db.execute('UPDATE growth_state SET xp=?',(1000*pet.growth.UNIT,))
            self.assertEqual(set(pet.garden.seed_pool(db,1)),{'clover','mint','daisy','cherry','sunflower','calendula'})
            self.assertEqual(set(pet.garden.seed_pool(db,7)),{'carrot','tomato','radish','lettuce'})
            with patch('garden.secrets.choice',return_value='tomato') as draw:
                pet.garden.edit(db,'plant',7,'random');draw.assert_called_once()
            with patch('garden.secrets.choice',side_effect=AssertionError('explicit selection rerolled')):
                pet.garden.edit(db,'plant',1,'mint')

    def test_every_game_species_has_offline_science_and_sources(self):
        self.assertEqual(set(botany.PROFILES),set(pet.garden.PLANTS))
        for profile in botany.PROFILES.values():
            for key in ('name','latin','family','life','intro','observe','habitat','fact','source','url'):
                self.assertTrue(profile[key])
            self.assertTrue(profile['url'].startswith('https://'))
