# Sprout Pet

![Actual desktop garden in beta.4](preview.png)

A quiet pixel garden that grows alongside your work in Codex.

**Windows Beta · 0.1.0-beta.5**

**English** · [简体中文](README.zh-CN.md)

## What is Sprout Pet?

Sprout Pet is a local Codex plugin with a desktop garden and a round little companion, Xiaoya. Time helps your pet and plants grow; newly recorded Codex token usage replenishes your pet's energy for garden work. You do not need to make extra AI requests to keep it growing.

## Main features

- **Companion interactions.** Pet Xiaoya, watch idle stretches and naps, and feed one harvested crop for a snack animation. Switch to a small draggable pet using the right-click menu; time growth continues while automatic gardening pauses.
- **A living pixel garden.** Ornamental plants, a vegetable patch and a meadow share one continuous 2D scene. Your pet walks to plants and animates its gardening actions.
- **Idle and offline growth.** Earn 6 XP per hour with the desktop garden running, or 3 XP per offline hour for up to 12 hours per absence. The current level cap is 30, with four visual stages.
- **Token-powered care.** Every 1,000 newly credited tokens adds 1 energy, up to 100. Energy lets Xiaoya sow, water, fertilize and harvest. Plants continue growing without energy and do not wither.
- **Random seeds with lasting identities.** Automatic sowing picks an unlocked species for its growing area. Once planted, that species stays fixed across inspections and restarts.
- **10 plants, five growth stages.** Discover clover, mint, daisy, cherry, sunflower, calendula, carrot, tomato, radish and lettuce as they become available.
- **Botanical learning cards.** Click a plant to read its introduction and growing information in Chinese or English. Real-world plant facts are distinguished from the game's compressed growth rules.
- **Harvest, collect and replant.** Xiaoya harvests mature crops and replants empty beds when it has enough energy. Collect mature ornamental plants and place them back later, or enable optional automatic rotation. Rotation is off by default.
- **Small discoveries.** Recording mature species in the collection unlocks butterfly and sparrow visitors.
- **Personal touches.** Click Xiaoya for its stats; use the journal for growth, collections and appearance. Switch interface language, choose a color theme, use a custom PNG avatar, drag the garden, or pin it above other windows.
- **Local saves.** Garden progress stays on your computer. The garden needs no game server and includes no online battles.

## Requirements and installation

Use a Windows desktop with a plugin-capable Codex client, Python 3.10+ with Tcl/Tk and `pythonw`, and Python on PATH. The commands below also require Codex CLI, Git and access to GitHub. No third-party Python packages are needed to run the garden.

Run in PowerShell:

```powershell
codex plugin marketplace add Jb-C-Lelouch/sprout-pet-beta
codex plugin add codex-pet@sprout-beta
```

Restart Codex, review and trust the plugin hooks when prompted, then start a new task and ask **“Open the Sprout garden.”** The first usage event establishes a baseline; historical tokens are not credited.

For a downloaded ZIP, fully extract it and open PowerShell in the repository root, where this README and `plugins` are located:

```powershell
codex plugin marketplace add .
codex plugin add codex-pet@sprout-beta
```

Double-click `plugins/codex-pet/Check-Environment.cmd` to check Python/Tk. `Open-Desktop-Pet.cmd` in the same folder opens the standalone garden; opening it alone does not install or authorize Codex hooks.

## Updates, saves and current limits

Refresh the marketplace with `codex plugin marketplace upgrade sprout-beta`, check for the plugin update in Codex, restart the garden and open a new Codex task. Right-click the garden to exit. Saves are kept in `.codex-pet` under your user home directory; close the garden before backing up that folder. Uninstalling the plugin leaves the save in place.

This is an early Windows beta. Python is not bundled. Token collection depends on the host's local transcript format and may vary by Codex version; time-based growth still works when usage cannot be read. Automatic gardening runs while the desktop garden is open, not during offline settlement. Harvested crops can be fed to Xiaoya; there is no trading or currency system. Clean-machine installation and real host hook compatibility still need broader testing.

The hook reads local transcript records to extract session IDs and cumulative token counts. It does not copy conversation text into the garden save or upload it to a game server. See [privacy details](PRIVACY.md) and [release notes](RELEASE.md) (currently in Chinese).

Report bugs in [Issues](https://github.com/Jb-C-Lelouch/sprout-pet-beta/issues), including your plugin, Windows, Python and Codex versions, steps to reproduce, and any environment-check error. Please do not upload chat transcripts or full saves.

## Extending plants and artwork

Plants, pet forms, animations, botanical profiles and scene resources use versioned content packs. Add a plant with JSON metadata, localized text and five PNG growth stages, without editing gameplay code. See the [content authoring guide](plugins/codex-pet/CONTENT.md).

## License

Released under the [MIT License](LICENSE). Commercial use, modification and redistribution are allowed, provided the copyright and license notice are retained. The software is provided without warranty. Unless separately noted, this applies to the project's code, documentation and bundled artwork, to the extent the copyright holder can license them. Referenced external sources retain their own terms.
