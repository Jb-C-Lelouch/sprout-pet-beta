from test_pet import pet
import desktop
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest


class DesktopTests(unittest.TestCase):
    def test_missing_save_is_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'missing'
            self.assertIsNone(desktop.read_status(folder))
            self.assertFalse(folder.exists())

    def test_live_snapshot_is_read_only_and_updates(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            with closing(pet.connect(folder)) as db:
                pet.record(db,'test',0,baseline=True)
                pet.record(db,'test',45000)
                expected=pet.status(db)
                before=list(db.iterdump())
                self.assertEqual(desktop.read_status(folder),expected)
                self.assertEqual(list(db.iterdump()),before)
                pet.record(db,'test',90000)
                self.assertEqual(desktop.read_status(folder)['credited_tokens'],90000)

    def test_corrupt_preferences_fallback_and_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'desktop.json'
            for value in ['{', '[]', '{"theme": [], "topmost": "false"}']:
                path.write_text(value)
                self.assertEqual(desktop.preferences(tmp),desktop.DEFAULTS)
            value=dict(desktop.DEFAULTS,theme='夜色',compact=True,x=200,y=300)
            desktop.save_preferences(tmp,value)
            self.assertEqual(desktop.preferences(tmp),value)
            self.assertFalse((Path(tmp)/'pet.sqlite3').exists())


if __name__=='__main__':unittest.main()
