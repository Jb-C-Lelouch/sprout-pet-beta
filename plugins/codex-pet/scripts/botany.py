"""Compatibility API backed by versioned botanical content packs."""
from content_catalog import catalog


def profile(species, language='zh'):
    return catalog().profile(species, language)


def name(species, language='zh'):
    return profile(species, language)['name']


PROFILES = {id: profile(id) for id in catalog().plants}
EN = {id: profile(id, 'en') for id in catalog().plants}
GAME_NOTE = catalog().game_note('zh')
