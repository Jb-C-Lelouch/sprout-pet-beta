"""Extension and compatibility checks for data-driven content."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
from content_catalog import ContentCatalog, ROOT, resource
import garden
import pet


def png_bytes(width=2, height=1):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    pixels = b'\x00' + b'\xff\x00\x00\xff' + b'\x00\x00\xff\xff'
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'content'
        shutil.copytree(ROOT, self.root)

    def tearDown(self):
        self.temp.cleanup()

    def change(self, path, update):
        file = self.root / path
        value = json.loads(file.read_text(encoding='utf-8'))
        update(value)
        file.write_text(json.dumps(value), encoding='utf-8')

    def new_plant(self):
        directory = self.root / 'plants/test-flower'
        shutil.copytree(self.root / 'plants/clover', directory)
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        manifest['id'] = 'test-flower'
        visual = manifest['visual']
        visual.update(kind='png', size=[2, 1], anchor=[1, 1], scale=2)
        visual.pop('renderer'); visual.pop('variant')
        visual['files'] = {stage: f'{stage}.png' for stage in visual['stages']}
        for name in visual['files'].values():
            (directory / name).write_bytes(png_bytes())
        (directory / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        return directory

    def test_new_png_species_can_be_planted_saved_and_restored_without_code(self):
        self.new_plant()
        content = ContentCatalog(self.root)
        with patch.object(garden, 'PLANTS', content.plant_rules()), patch.object(garden, 'catalog', return_value=content):
            data = Path(self.temp.name) / 'save'
            db = pet.connect(data)
            try:
                garden.edit(db, 'plant', 1, 'test-flower')
                self.assertEqual(db.execute('SELECT species FROM garden_plots WHERE plot=1').fetchone()[0], 'test-flower')
                self.assertIn('test-flower', garden.seed_pool(db, 1))
                self.assertEqual(garden.snapshot(db)['plots'][0]['species'], 'test-flower')
            finally:
                db.close()
            db = pet.connect(data)
            try:
                self.assertEqual(db.execute('SELECT species FROM garden_plots WHERE plot=1').fetchone()[0], 'test-flower')
            finally:
                db.close()

    def test_missing_translation_falls_back_to_named_english_fields(self):
        self.change('plants/clover/locales/zh-CN.json', lambda v: v.pop('intro'))
        content = ContentCatalog(self.root)
        self.assertEqual(content.profile('clover', 'zh')['intro'], content.profile('clover', 'en')['intro'])
        self.assertEqual(content.profile('clover', 'fr'), content.profile('clover', 'en'))

    def test_unknown_schema_and_renderer_are_rejected(self):
        self.change('plants/clover/manifest.json', lambda v: v.update(schema_version=2))
        with self.assertRaisesRegex(ValueError, 'schema_version'):
            ContentCatalog(self.root)
        self.change('plants/clover/manifest.json', lambda v: (v.update(schema_version=1), v['visual'].update(renderer='execute-python')))
        with self.assertRaisesRegex(ValueError, 'renderer'):
            ContentCatalog(self.root)

    def test_duplicate_ids_are_rejected(self):
        shutil.copytree(self.root / 'plants/clover', self.root / 'plants/duplicate')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            ContentCatalog(self.root)

    def test_missing_source_invalid_rules_and_missing_english_are_rejected(self):
        path = self.root / 'plants/clover/sources.json'
        original = path.read_bytes();path.write_text('[]')
        with self.assertRaisesRegex(ValueError, 'source'):
            ContentCatalog(self.root)
        path.write_bytes(original)
        self.change('plants/clover/manifest.json', lambda v: v['game'].update(xp=0))
        with self.assertRaisesRegex(ValueError, 'XP'):
            ContentCatalog(self.root)
        self.change('plants/clover/manifest.json', lambda v: v['game'].update(xp=6))
        (self.root / 'plants/clover/locales/en.json').unlink()
        with self.assertRaisesRegex(ValueError, 'English'):
            ContentCatalog(self.root)

    def test_bad_png_size_path_escape_and_missing_stage_are_rejected(self):
        directory = self.new_plant()
        self.change('plants/test-flower/manifest.json', lambda v: v['visual'].update(size=[3, 1]))
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            ContentCatalog(self.root)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            resource(directory, '../clover/manifest.json')
        self.change('plants/test-flower/manifest.json', lambda v: (v['visual'].update(size=[2, 1]), v['visual']['files'].pop('seed')))
        with self.assertRaisesRegex(ValueError, 'stage files'):
            ContentCatalog(self.root)

    def test_pet_forms_keep_existing_level_boundaries(self):
        content = ContentCatalog(self.root)
        self.assertEqual([content.pet_form(n)['rank'] for n in (1, 4, 5, 14, 15, 29, 30)], [0, 0, 1, 1, 2, 2, 3])

    def test_png_rendering_anchor_flip_and_animation(self):
        import tkinter as tk
        from pixel_art import PixelArt
        self.new_plant()
        directory = self.root / 'pets/sprout'
        (directory / 'frame.png').write_bytes(png_bytes())
        def change_pet(value):
            visual = value['visual']
            visual.update(kind='png', size=[2, 1], anchor=[0, 1], scale=2)
            for action in visual['actions'].values():
                action['frames'] = ['frame.png'];action['loop'] = False
        self.change('pets/sprout/manifest.json', change_pet)
        content = ContentCatalog(self.root)
        window = tk.Tk();window.withdraw()
        try:
            art = PixelArt(window, content)
            image = art.plant('test-flower', 1)
            self.assertEqual((image.width(), image.height()), (4, 2))
            self.assertEqual(art.plant_anchor('test-flower'), (2, 2))
            left, anchor = art.pet_frame('walk', 10, '苔绿', True, 1)
            right, mirrored_anchor = art.pet_frame('walk', 10, '苔绿', False, 1)
            self.assertEqual(left.get(0, 0), (255, 0, 0))
            self.assertEqual(right.get(0, 0), (0, 0, 255))
            self.assertEqual((anchor, mirrored_anchor), ((0, 2), (4, 2)))
        finally:
            window.destroy()


if __name__ == '__main__':
    unittest.main()
