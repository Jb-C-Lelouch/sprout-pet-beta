---
name: pet-status
description: 查看或打开休闲桌面花园，查看陪伴成长与token精力、自动照料、随机植物、收获、收藏轮换和中英文植物科普信息卡，更换宠物外观。
---

Run bundled ../../scripts/pet.py status using Python, resolving the absolute path relative to this skill. Use python on Windows, python3 elsewhere. Present name, level, form, current experience, energy.current /100 and connection in Chinese. At level cap show stored excess XP, not progress to an unavailable level.

Read GROWTH.md and GARDEN.md at the plugin root for rules. Desktop growth is6XP/hour, offline3XP/hour capped12hours per absence. Each1000 new credited tokens adds1energy, capped100. No tokens are required for natural growth. Never fabricate tokens, time, XP, energy, crops or random results. Preserve existing plants and experience. New Codex tasks load updated hook code.

Commands:
- status: settle accrued time once and report pet growth.
- garden: settle time and report saved plants, energy, visitors and harvest inventory.
- plant --plot N [--plant ID]: explicit manual planting. Omit species or use random for a seed box. Slots1–6 ornamental,7–9 crops; use only unlocked species. Manual planting is not an energy debit.
- garden-move --plot N --destination N: move/swap within a zone, preserving species and care.
- garden-remove --plot N: remove only on explicit user request; individual growth is lost, discoveries remain.

Random species is selected once when planting completes and stored. Reading, moving, watering, fertilizing and restarting do not reroll. Read BOTANY.md for offline sourced profiles; distinguish real biology from compressed game growth. Existing species are clover, mint, daisy, cherry, carrot, tomato, sunflower, calendula, radish, lettuce. The scene has a garden, crops and meadow; there is no pond system.

When asked to open the desktop pet, launch bundled ../../scripts/desktop.py with Python/Tk. On Windows use available pythonw.exe through Start-Process with an absolute path. This is the visible interactive window the user requested. Do not launch after unrelated work or a text-only status request. Per-save Windows singleton prevents duplicates. Do not kill unrelated Python processes.

The main scene is a continuous pixel garden. Click pet for energy, level and garden counts; click plants for botanical cards. Reading cards pauses actions. Garden journal contains growth, collection and appearance. Mature ornamentals can be collected from their cards and restored from Collection, for free. Rotation is opt-in: after 1 hour of online display, automatic collecting costs 4 energy; sowing costs 6. Restored favorites are protected from automatic rotation. Appearance has persistent Chinese/English language controls. Viewing the journal also pauses actions. Right-click pauses care, pins or exits; Escape closes the pet card. PNG customization, drag and themes persist locally. UI reads every3seconds, time heartbeat writes every15seconds. Reopen an information panel to refresh its snapshot. See DESKTOP.md.

Only report real command results. Missing Tk means the desktop window cannot run; do not claim it appeared. Do not invoke deleted prototype commands or restore old prototype files.
