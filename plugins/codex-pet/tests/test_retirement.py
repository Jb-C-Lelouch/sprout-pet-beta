from test_pet import pet
from contextlib import closing
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class RetirementTests(unittest.TestCase):
    def test_old_combat_tables_removed_without_changing_garden_or_growth(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            with closing(pet.connect(path,now=1800000000)) as db:
                pet.garden.edit(db,'plant',1,'clover')
                with db:
                    db.execute('UPDATE growth_state SET xp=123456')
                    db.execute('UPDATE pet_energy SET units=34567')
                    for name in pet.RETIRED_TABLES:
                        db.execute('CREATE TABLE '+name+'(value TEXT)')
                        db.execute('INSERT INTO '+name+" VALUES('retired fixture')")
                kept=['pet','sessions','growth_state','pet_energy','garden_plots','garden_care','garden_collection','garden_inventory','garden_work','garden_autonomy']
                before={name:db.execute('SELECT * FROM '+name).fetchall() for name in kept}
            with closing(pet.connect(path,now=1800000000)) as db:
                self.assertEqual(before,{name:db.execute('SELECT * FROM '+name).fetchall() for name in kept})
                tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertFalse(tables & set(pet.RETIRED_TABLES))
                state=pet.status(db)
                for key in ('skills','equipment','stats','base_stats','slots','next_skill_level'):self.assertNotIn(key,state)

    def test_retired_cli_commands_are_not_available(self):
        result=subprocess.run([sys.executable,pet.__file__,'--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        for command in ('trial','friend-duel','equip','battle-log','card-export'):self.assertNotIn(command,result.stdout)
