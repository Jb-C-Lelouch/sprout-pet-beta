"""Validate pack metadata; optionally decode and render all sprites with Tk."""
import argparse
from pathlib import Path
import sys
from content_catalog import ContentCatalog, ROOT


def validate(root=ROOT, render=False):
    content = ContentCatalog(root)
    warnings = []
    for pack in [*content.plants.values(), *content.pets.values()]:
        english = pack['locales']['en']
        translated = pack['locales'].get('zh-CN', {})
        missing = sorted(english.keys() - translated.keys())
        if missing:
            warnings.append(f"{pack['type']}/{pack['id']}: zh-CN falls back to English: {', '.join(missing)}")
        if pack['type'] == 'pet':
            missing_forms = english['forms'].keys() - translated.get('forms', {}).keys()
            if missing_forms:
                warnings.append(f"pets/{pack['id']}: zh-CN form names fall back to English: {', '.join(sorted(missing_forms))}")
    if render:
        import tkinter as tk
        from pixel_art import PixelArt
        window = tk.Tk()
        window.withdraw()
        try:
            art = PixelArt(window, content)
            for id in content.plants:
                for stage in range(5):
                    art.plant(id, stage / 4)
            for id, pack in content.pets.items():
                for form in pack['forms']:
                    visual = form.get('visual', pack['visual'])
                    for action, animation in visual['actions'].items():
                        for index, frame in enumerate(animation['frames']):
                            if visual['kind'] == 'png':
                                for flip in (False, True):
                                    art._png(pack, frame, visual, flip)
                            else:
                                from pixel_art import pet_pixels
                                for theme in ('苔绿', '樱粉', '夜色'):
                                    pet_pixels('rest' if action == 'sleep' else action, frame, theme, form['rank']).photo(window, scale=visual['scale'])
            print('PASS: Tk decoded PNG resources and rendered every stage/action/form')
        finally:
            window.destroy()
    for warning in warnings:
        print('WARNING: ' + warning)
    print(f'PASS: {len(content.plants)} plants, {len(content.pets)} pets, {len(content.scenery)} scenes')
    return warnings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--strict', action='store_true', help='Fail on translation fallback warnings')
    args = parser.parse_args()
    try:
        warnings = validate(args.root, args.render)
        if args.strict and warnings:
            sys.exit(1)
    except (ValueError, OSError) as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
