"""Versioned local content; no executable code is loaded from content packs."""
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import struct
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / 'content'
PLANT_VARIANTS = {'clover', 'mint', 'daisy', 'cherry', 'carrot', 'tomato',
                  'sunflower', 'calendula', 'radish', 'lettuce'}
ACTIONS = {'rest', 'walk', 'dig', 'water', 'fertilize', 'harvest', 'archive', 'sleep'}
PROFILE_FIELDS = ('name', 'latin', 'family', 'life', 'intro', 'observe', 'habitat', 'fact', 'garden_name')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    try:
        require(path.stat().st_size <= 1024 * 1024, f'{path}: JSON exceeds 1 MB')
        def unique(pairs):
            result = {}
            for key, value in pairs:
                require(key not in result, f'{path}: duplicate key {key}')
                result[key] = value
            return result
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'{path}: {exc}') from exc


def resource(directory, name):
    require(isinstance(name, str) and name and '\\' not in name and ':' not in name,
            f'{directory}: resource must be a relative POSIX path')
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts,
            f'{directory}: resource escapes pack: {name}')
    path = (directory / relative).resolve()
    require(path.is_relative_to(directory.resolve()) and path.is_file(),
            f'{directory}: missing or external resource: {name}')
    return path


def positive_int(value, maximum=2048):
    return type(value) is int and 0 < value <= maximum


def pair(value, predicate):
    return isinstance(value, list) and len(value) == 2 and all(predicate(x) for x in value)


def validate_png(path, size):
    require(path.suffix.lower() == '.png' and path.stat().st_size <= 8 * 1024 * 1024,
            f'{path}: expected PNG, at most 8 MB')
    with path.open('rb') as stream:
        header = stream.read(24)
    require(len(header) == 24 and header[:8] == b'\x89PNG\r\n\x1a\n' and header[12:16] == b'IHDR',
            f'{path}: invalid PNG header')
    require(list(struct.unpack('>II', header[16:24])) == size,
            f'{path}: image dimensions must match {size}')


def validate_visual(directory, visual, kind):
    require(isinstance(visual, dict), f'{directory}: missing visual')
    size, anchor = visual.get('size'), visual.get('anchor')
    require(pair(size, positive_int), f'{directory}: invalid visual.size')
    require(pair(anchor, lambda n: type(n) is int and n >= 0) and
            all(a <= n for a, n in zip(anchor, size)), f'{directory}: anchor outside canvas')
    require(positive_int(visual.get('scale'), 4), f'{directory}: scale must be integer 1..4')
    backend = visual.get('kind')
    require(backend in ('procedural', 'png'), f'{directory}: unknown visual kind')
    if kind == 'plant':
        stages = visual.get('stages')
        require(isinstance(stages, list) and len(stages) == 5 and
                all(isinstance(s, str) and s for s in stages) and len(set(stages)) == 5,
                f'{directory}: five distinct ordered stage names required')
        if backend == 'procedural':
            require(visual.get('renderer') == 'botanical-v1' and visual.get('variant') in PLANT_VARIANTS,
                    f'{directory}: unregistered plant renderer or variant')
            require(size == [80, 96], f'{directory}: botanical-v1 canvas is 80x96')
        else:
            files = visual.get('files')
            require(isinstance(files, dict) and set(files) == set(stages), f'{directory}: missing stage files')
            for name in files.values():
                validate_png(resource(directory, name), size)
    else:
        if backend == 'procedural':
            require(visual.get('renderer') == 'sprout-v1' and size == [64, 64],
                    f'{directory}: unregistered pet renderer or canvas')
        actions = visual.get('actions')
        require(isinstance(actions, dict) and set(actions) == ACTIONS, f'{directory}: all eight actions required')
        for action, animation in actions.items():
            require(isinstance(animation, dict), f'{directory}: invalid action {action}')
            frames, ms = animation.get('frames'), animation.get('frame_ms')
            require(isinstance(frames, list) and 1 <= len(frames) <= 64, f'{directory}: invalid frames for {action}')
            require(type(ms) in (int, float) and math.isfinite(ms) and 10 <= ms <= 10000,
                    f'{directory}: frame_ms must be 10..10000')
            require(type(animation.get('loop')) is bool, f'{directory}: loop must be boolean')
            for frame in frames:
                if backend == 'procedural':
                    require(type(frame) is int and (8 <= frame < 16 if action == 'sleep' else 0 <= frame < 8),
                            f'{directory}: invalid procedural frame for {action}')
                else:
                    validate_png(resource(directory, frame), size)


def locale(pack, language):
    tag = 'zh-CN' if language in ('zh', 'zh-CN') else language
    return {**pack['locales']['en'], **pack['locales'].get(tag, {})}


class ContentCatalog:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.plants = self._load('plants', 'plant')
        self.pets = self._load('pets', 'pet')
        self.scenery = self._load('scenery', 'scenery')
        require(bool(self.plants) and 'sprout' in self.pets and 'garden' in self.scenery,
                'Content requires plants, pets/sprout and scenery/garden')
        self.messages = {}
        for path in sorted((self.root / 'locales').glob('*.json')):
            value = read_json(path)
            require(isinstance(value, dict) and isinstance(value.get('ui'), dict) and
                    all(isinstance(k, str) and isinstance(v, str) for k, v in value['ui'].items()) and
                    isinstance(value.get('game_note'), str), f'{path}: invalid shared locale')
            self.messages[path.stem] = value
        require('en' in self.messages, 'Missing English shared locale')

    def _load(self, folder, kind):
        packs = {}
        for path in sorted((self.root / folder).glob('*/manifest.json')):
            try:
                require(path.resolve().is_relative_to(self.root.resolve()), 'Pack is outside content root')
                pack = read_json(path)
                require(isinstance(pack, dict) and type(pack.get('schema_version')) is int and
                        pack['schema_version'] == 1, 'Unsupported schema_version')
                id = pack.get('id')
                require(isinstance(id, str) and re.fullmatch(r'[a-z][a-z0-9-]*', id), 'Invalid stable id')
                require(id not in packs, f'Duplicate {kind} id: {id}')
                require(id == path.parent.name and pack.get('type') == kind, 'Folder/id/type mismatch')
                require(all(isinstance(pack.get(k), str) and pack[k] for k in ('author', 'license')),
                        'Missing author/license')
                require(type(pack.get('order', 0)) is int, 'order must be an integer')
                pack['directory'] = path.parent
                if kind != 'scenery':
                    pack['locales'] = {p.stem: read_json(resource(path.parent, p.relative_to(path.parent).as_posix()))
                                       for p in sorted((path.parent / 'locales').glob('*.json'))}
                    require('en' in pack['locales'], 'English locale is required for fallback')
                    for tag, values in pack['locales'].items():
                        require(isinstance(values, dict), f'Invalid locale {tag}')
                    validate_visual(path.parent, pack.get('visual'), kind)
                getattr(self, '_validate_' + kind)(pack)
                packs[id] = pack
            except (ValueError, KeyError, TypeError, OSError) as exc:
                raise ValueError(f'{path}: {exc}') from exc
        return dict(sorted(packs.items(), key=lambda item: (item[1].get('order', 0), item[0])))

    def _validate_plant(self, pack):
        require(type(pack.get('order', 0)) is int, 'order must be an integer')
        require(pack.get('zone') in ('garden', 'crops'), 'Invalid growing zone')
        game = pack.get('game')
        require(isinstance(game, dict) and positive_int(game.get('level'), 30) and
                positive_int(game.get('xp'), 100000), 'Invalid level or maturity XP')
        require(isinstance(game.get('color'), str) and re.fullmatch(r'#[0-9a-fA-F]{6}', game['color']), 'Invalid color')
        require(isinstance(game.get('shape'), str), 'Missing legacy shape')
        require((game['shape'] == 'crop') == (pack['zone'] == 'crops'), 'shape/zone mismatch')
        for tag, values in pack['locales'].items():
            require(all(isinstance(v, str) and v.strip() for v in values.values()), f'Invalid locale values: {tag}')
        require(all(isinstance(pack['locales']['en'].get(k), str) and pack['locales']['en'][k].strip()
                    for k in PROFILE_FIELDS), 'Incomplete English botanical profile')
        sources = read_json(resource(pack['directory'], 'sources.json'))
        require(isinstance(sources, list) and sources, 'At least one botanical source required')
        ids = set()
        for source in sources:
            require(isinstance(source, dict) and source.get('id') in ('main', 'extra') and source['id'] not in ids,
                    'Sources must have unique main/extra IDs')
            ids.add(source['id'])
            require(isinstance(source.get('url'), str), 'Source URL must be text')
            url = urlparse(source['url'])
            require(url.scheme == 'https' and bool(url.netloc), 'Source must be an HTTPS URL')
            require(isinstance(source.get('label'), dict) and bool(source['label'].get('en')) and
                    all(isinstance(v, str) and v for v in source['label'].values()),
                    'Source needs an English label')
            require(isinstance(source.get('checked_at'), str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', source['checked_at']),
                    'Source needs checked_at (YYYY-MM-DD)')
        require('main' in ids, 'Main source required')
        pack['sources'] = sources

    def _validate_pet(self, pack):
        forms = pack.get('forms')
        require(isinstance(forms, list) and forms, 'Pet forms required')
        previous, ids = 0, set()
        for form in forms:
            require(isinstance(form, dict) and isinstance(form.get('id'), str) and form['id'] not in ids,
                    'Invalid or duplicate form id')
            ids.add(form['id'])
            require(positive_int(form.get('level'), 30) and form['level'] > previous, 'Form levels must increase')
            previous = form['level']
            require(type(form.get('rank')) is int and 0 <= form['rank'] <= 3, 'Rank must be 0..3')
            if 'visual' in form:
                validate_visual(pack['directory'], form['visual'], 'pet')
        require(forms[0]['level'] == 1, 'First form must unlock at level 1')
        for tag, values in pack['locales'].items():
            require(isinstance(values.get('name', pack['locales']['en'].get('name')), str), 'Missing pet name')
            require(isinstance(values.get('forms', {}), dict) and all(isinstance(v, str) and v for v in values.get('forms', {}).values()),
                    f'Invalid form names in {tag}')
        require(ids <= pack['locales']['en'].get('forms', {}).keys(), 'Missing English form names')

    def _validate_scenery(self, pack):
        background = pack.get('background', {})
        require(isinstance(background, dict), 'Invalid background object')
        require(pair(background.get('size'), positive_int) and positive_int(background.get('subsample'), 8),
                'Invalid background size/subsample')
        require(pair(background.get('position'), lambda n: type(n) is int), 'Invalid background position')
        validate_png(resource(pack['directory'], background.get('file')), background['size'])
        field = pack.get('field', {})
        require(isinstance(field, dict), 'Invalid field object')
        require(field.get('renderer') == 'field-v1' and pair(field.get('position'), lambda n: type(n) is int),
                'Invalid field renderer/position')

    def profile(self, species, language='zh'):
        pack = self.plants[species]
        result = {k: v for k, v in locale(pack, language).items() if k != 'garden_name'}
        tag = 'zh-CN' if language == 'zh' else language
        for source in pack['sources']:
            prefix = '' if source['id'] == 'main' else 'extra_'
            result[prefix + 'url'] = source['url']
            result[prefix + 'source'] = source['label'].get(tag, source['label']['en'])
        return result

    def plant_rules(self):
        return {id: dict(name=locale(pack, 'zh')['garden_name'], **pack['game']) for id, pack in self.plants.items()}

    def pet_form(self, level, pet='sprout'):
        return next(form for form in reversed(self.pets[pet]['forms']) if level >= form['level'])

    def form_name(self, level, language='zh', pet='sprout'):
        pack = self.pets[pet]
        tag = 'zh-CN' if language == 'zh' else language
        names = {**pack['locales']['en']['forms'], **pack['locales'].get(tag, {}).get('forms', {})}
        return names[self.pet_form(level, pet)['id']]

    def game_note(self, language='zh'):
        tag = 'zh-CN' if language == 'zh' else language
        return self.messages.get(tag, self.messages['en'])['game_note']


@lru_cache(maxsize=1)
def catalog():
    return ContentCatalog()
