import test_garden
import unittest
from test_pet import pet
from contextlib import closing
from unittest.mock import patch
from garden_motion import Gardener
import desktop
import botany
from pixel_art import plant_pixels


class CycleTests(unittest.TestCase):
    setUp=test_garden.GardenTests.setUp
    tearDown=test_garden.GardenTests.tearDown
    xp=test_garden.GardenTests.xp
    def test_rotation_requires_opt_in_online_display_and_energy(self):
        self.xp(1000)
        for p in range(1,7):pet.garden.edit(self.db,'plant',p,'clover')
        self.xp(1006)
        with self.db:
            self.db.execute('UPDATE pet_energy SET units=100000')
            self.db.execute('UPDATE garden_autonomy SET next_xp=999999999')
        self.assertFalse(pet.garden.snapshot(self.db)['rotation'])
        pet.garden.set_rotation(self.db,True)
        self.assertNotEqual((pet.garden.work_plan(self.db,100) or {}).get('action'),'archive')
        with self.db:self.db.execute('UPDATE growth_state SET offline_seconds=999999')
        self.assertNotEqual((pet.garden.work_plan(self.db,100) or {}).get('action'),'archive')
        with self.db:self.db.execute('UPDATE growth_state SET online_seconds=3600')
        plan=pet.garden.work_plan(self.db,100)
        self.assertEqual(plan['action'],'archive')
        pet.garden.set_rotation(self.db,False)
        self.assertFalse(pet.garden.perform_work(self.db,plan,100))
        pet.garden.set_rotation(self.db,True)
        with self.db:self.db.execute('UPDATE pet_energy SET units=3000')
        self.assertFalse(pet.garden.perform_work(self.db,plan,100))
        with self.db:self.db.execute('UPDATE pet_energy SET units=100000')
        self.assertTrue(pet.garden.perform_work(self.db,plan,100))
        self.assertFalse(pet.garden.perform_work(self.db,plan,100))
        self.assertEqual(len(pet.garden.snapshot(self.db)['archive']),1)
        self.assertEqual(self.db.execute('SELECT units FROM pet_energy').fetchone()[0],96000)

    def test_manual_collect_restore_retains_age_care_and_is_once_only(self):
        self.xp(1000);pet.garden.edit(self.db,'plant',1,'mint')
        with self.db:self.db.execute('INSERT INTO garden_care VALUES(1,?,1)',(3*pet.growth.UNIT,))
        self.xp(1015);before=pet.garden.snapshot(self.db)
        pet.garden.archive_plant(self.db,1,before['revision'])
        with self.assertRaises(ValueError):pet.garden.archive_plant(self.db,1,before['revision'])
        identity=pet.garden.snapshot(self.db)['archive'][0]['id']
        self.xp(1100)
        with closing(pet.connect(self.path)) as other:
            self.assertEqual(pet.garden.restore_plant(other,identity),1)
            with self.assertRaises(ValueError):pet.garden.restore_plant(other,identity)
        restored=pet.garden.snapshot(self.db)['plots'][0]
        self.assertEqual(restored['earned_xp'],18)
        self.assertEqual(restored['species'],'mint')
        self.assertEqual(self.db.execute('SELECT pinned FROM garden_display WHERE plot=1').fetchone()[0],1)
        self.assertEqual(self.db.execute('SELECT units FROM pet_energy').fetchone()[0],0)
        self.assertEqual(pet.growth.total_units(self.db),1100*pet.growth.UNIT)

    def test_restore_full_garden_rolls_back_and_young_crop_cannot_collect(self):
        pet.garden.edit(self.db,'plant',1,'clover')
        with self.assertRaises(ValueError):pet.garden.archive_plant(self.db,1,1)
        self.xp(6);pet.garden.archive_plant(self.db,1,1)
        identity=pet.garden.snapshot(self.db)['archive'][0]['id']
        for p in range(1,7):pet.garden.edit(self.db,'plant',p,'clover')
        before=list(self.db.iterdump())
        with self.assertRaises(ValueError):pet.garden.restore_plant(self.db,identity)
        self.assertEqual(before,list(self.db.iterdump()))
        for p in (True,0,7,10):
            with self.assertRaises(ValueError):pet.garden.archive_plant(self.db,p,7)

    def test_harvest_reseed_draws_once_and_clears_old_care(self):
        pet.garden.edit(self.db,'plant',7,'radish');self.xp(12)
        with self.db:
            self.db.execute('INSERT INTO garden_care VALUES(7,0,1)')
            self.db.execute('UPDATE pet_energy SET units=100000')
            self.db.execute('UPDATE garden_autonomy SET next_xp=999999999')
        plan=pet.garden.work_plan(self.db,100);self.assertEqual(plan['action'],'harvest')
        self.assertTrue(pet.garden.perform_work(self.db,plan,100))
        self.assertFalse(pet.garden.perform_work(self.db,plan,100))
        self.assertEqual(pet.garden.snapshot(self.db)['inventory'],{'radish':1})
        self.assertIsNone(pet.garden.work_plan(self.db,159))
        with patch('garden.secrets.choice',return_value='lettuce') as draw:
            plan=pet.garden.work_plan(self.db,160);draw.assert_not_called()
            self.assertEqual(plan['plot'],7)
            self.assertTrue(pet.garden.perform_work(self.db,plan,160));draw.assert_called_once()
        self.assertEqual(pet.garden.snapshot(self.db)['plots'][6]['progress'],0)
        self.assertIsNone(self.db.execute('SELECT * FROM garden_care WHERE plot=7').fetchone())

    def test_archive_animation_commits_after_work(self):
        brain=Gardener();plan=dict(action='archive',plot=1,species='clover',revision=1)
        events=[];modes=set()
        for _ in range(200):
            event=brain.advance(.1,plan);modes.add(brain.mode)
            if event:events.append(event)
        self.assertEqual(events,[plan]);self.assertIn('archive',modes)

    def test_languages_preserve_save_and_all_ten_have_distinct_new_stages(self):
        before=list(self.db.iterdump())
        for lang in ('en','zh'):
            desktop.save_preferences(self.path,dict(desktop.DEFAULTS,language=lang))
            self.assertEqual(desktop.preferences(self.path)['language'],lang)
            for species in pet.garden.PLANTS:
                profile=botany.profile(species,lang)
                self.assertTrue(all(profile[k] for k in ('name','intro','observe','habitat','fact','url')))
        self.assertEqual(before,list(self.db.iterdump()))
        self.assertEqual(len(botany.EN),10)
        for species in ('sunflower','calendula','radish','lettuce'):
            stages={str(plant_pixels(species,i).rows) for i in range(5)}
            self.assertEqual(len(stages),5)
