# Extending Sprout content

[简体中文](CONTENT.zh-CN.md)

Content is loaded from `content/` once per process. Restart the garden and start a new Codex task after installing changed content. Python 3.10+ is sufficient; no extra runtime libraries are required.

```text
content/
  plants/<id>/manifest.json
  plants/<id>/locales/en.json
  plants/<id>/locales/zh-CN.json
  plants/<id>/sources.json
  plants/<id>/sprites/*.png          # optional PNG stages
  pets/sprout/manifest.json
  pets/sprout/locales/*.json
  scenery/garden/manifest.json
  scenery/garden/background.png
  locales/en.json
  locales/zh-CN.json
```

## Stable identifiers and schema

Every manifest has `schema_version: 1`, `type`, `id`, `author` and `license`. Folder names must match IDs (`a-z`, digits and hyphens, starting with a letter). IDs are unique within a category. Existing saves store plant IDs: never rename or remove an existing ID without a save migration. Adding content does not require a database migration. Missing/invalid packs stop loading with the responsible file path; the loader does not silently replace saved species.

Plants include `order` (catalog order), `zone` (`garden` or `crops`) and `game` (`level`, `xp`, `color`, `shape`). XP is progress earned after planting, not an XP purchase price. `shape` is retained for compatibility; crops use `crop`, ornamental plants use another shape. The zone controls sowing and placement. The existing rules for care, harvest and collection apply to newly added plants.

## Add a plant without editing Python

1. Copy an existing plant directory to a new stable ID, for example `plants/test-flower/`.
2. Change the manifest ID, order, zone and game values. Keep existing IDs untouched.
3. Edit named fields in `locales/en.json`: `garden_name`, `name`, `latin`, `family`, `life`, `intro`, `observe`, `habitat`, `fact`. `garden_name` is the short in-game label; `name` can be a precise botanical name. Add corresponding Chinese fields in `zh-CN.json`. Missing translated fields fall back to English. English fields are required.
4. Replace `sources.json` with verified botanical references. Each source has a unique `id` (`main`, optionally `extra`), an HTTPS `url`, localized `label`, and `checked_at` date. Sources describe real biology; `game` describes compressed game progression. The current information card displays up to two sources.
5. Supply five PNG stages or reuse a registered procedural variant. Run the validator below before publishing.

Example replacement for the manifest's `visual` object:

```json
{
  "kind": "png",
  "size": [80, 96],
  "anchor": [40, 92],
  "scale": 2,
  "stages": ["seed", "sprout", "growing", "budding", "mature"],
  "files": {
    "seed": "sprites/seed.png",
    "sprout": "sprites/sprout.png",
    "growing": "sprites/growing.png",
    "budding": "sprites/budding.png",
    "mature": "sprites/mature.png"
  }
}
```

Stages are ordered and selected at 0%, 25%, 50%, 75% and 100% progress. Their labels need not imply flowering: mature lettuce is harvested for its leaves. All five images must match `size`. Coordinates use the original unscaled canvas: `anchor` marks where the plant touches the ground. Integer `scale` is 1–4 and uses nearest-neighbor scaling. Transparent pixels do not intercept scene clicks. PNG files must stay inside their own content directory, be at most 8 MB and have dimensions at most 2048 × 2048. Run `--render` to verify image decoding, not just the PNG header.

Existing plants use `kind: procedural`, `renderer: botanical-v1` and a registered `variant` (the original species ID). Their canvas stays 80 × 96. Reusing a variant needs no code changes; an entirely new procedural drawing does. Content cannot import Python or register arbitrary executable renderers. PNG stages need no renderer registration.

## Pet forms and animation

`pets/sprout/manifest.json` defines ordered `forms` with stable `id`, ascending unlock `level` and existing procedural `rank` (0–3). Names live in each locale's `forms` map. Each form can optionally override `visual`; otherwise it uses the pet's default visual. This supports different PNG sheets of individual frames for each form. The desktop currently selects the built-in `sprout` pet; adding a second pet does not automatically add a pet-selection UI.

Each pet visual declares its canvas, anchor, scale and all eight actions: `rest`, `sleep`, `walk`, `dig`, `water`, `fertilize`, `harvest`, `archive`. Each action supplies `frames`, `frame_ms` and `loop`. For `kind: png`, frames are relative PNG paths; for `kind: procedural` with `renderer: sprout-v1`, frames are integer poses (0–7, or 8–15 for sleep). Sleep is selected after two seconds of rest. PNG frames face left; right-facing display is mirrored automatically, including the anchor. A non-looping animation holds its final frame.

Example PNG action: `"water": {"frames": ["sprites/water-0.png", "sprites/water-1.png"], "frame_ms": 125, "loop": true}`.

Animation metadata only controls presentation. Work completion and energy debits remain in the game state machine, so changing a skin cannot change rewards or charge energy twice. Completing a sprite sequence does not trigger a gameplay event. New action types or new mechanics still require code.

## Scenery and shared text

`scenery/garden` describes the background file, source dimensions, subsampling and position, plus the registered crop-bed drawing and position. The crop bed remains a procedural drawing. Garden layout, interaction code and decorative visitors remain in Python; this is not a scene editor.

`content/locales/` contains shared interface translations and the botanical game disclaimer. Existing UI text keys and dynamic formatting remain compatible with the previous UI; botanical profiles use named fields rather than position-dependent translation tuples. The current UI language selector exposes English and Chinese.

## Validate and distribute

From the plugin directory:

```powershell
python scripts/validate_content.py --strict
python scripts/validate_content.py --render --strict
python scripts/check_environment.py --smoke
```

The validator checks schema versions, IDs, references, rules, required English fields, sources, image dimensions, stages, forms and animation configuration. Missing Chinese fields are warnings (errors with `--strict`); runtime still falls back to English. Rendering requires Tk and a desktop session. Environment smoke checks use a temporary save, never your personal garden.

Ship the entire `content/` directory and the matching scripts. The development release builder includes JSON, PNG and Markdown content automatically. Keep original authorship and applicable licenses when adding contributed assets; do not label third-party work MIT without permission. Botanical source links are references, not licenses to reproduce the source pages.
