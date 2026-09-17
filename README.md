# Sprout Pet · 小芽桌面花园

A quiet pixel garden that grows alongside your work in Codex.
一座陪你使用 Codex、随时间慢慢成长的像素桌面花园。

**Windows Beta · 0.1.0-beta.1**

[English](#english) · [简体中文](#简体中文)

## English

### What is Sprout Pet?

Sprout Pet is a local Codex plugin with a desktop garden and a round little companion, Xiaoya. Time helps your pet and plants grow; newly recorded Codex token usage replenishes your pet's energy for garden work. You do not need to make extra AI requests to keep it growing.

### Main features

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

### Requirements and installation

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

### Updates, saves and current limits

Refresh the marketplace with `codex plugin marketplace upgrade sprout-beta`, check for the plugin update in Codex, restart the garden and open a new Codex task. Right-click the garden to exit. Saves are kept in `.codex-pet` under your user home directory; close the garden before backing up that folder. Uninstalling the plugin leaves the save in place.

This is an early Windows beta. Python is not bundled. Token collection depends on the host's local transcript format and may vary by Codex version; time-based growth still works when usage cannot be read. Automatic gardening runs while the desktop garden is open, not during offline settlement. Harvest inventory currently records quantities only; there is no trading or currency system. Clean-machine installation and real host hook compatibility still need broader testing.

The hook reads local transcript records to extract session IDs and cumulative token counts. It does not copy conversation text into the garden save or upload it to a game server. See [privacy details](PRIVACY.md) and [release notes](RELEASE.md) (currently in Chinese).

Report bugs in [Issues](https://github.com/Jb-C-Lelouch/sprout-pet-beta/issues), including your plugin, Windows, Python and Codex versions, steps to reproduce, and any environment-check error. Please do not upload chat transcripts or full saves.

## 简体中文

### 小芽是什么？

小芽是一个本地运行的 Codex 插件，带有像素桌面花园和圆滚滚的宠物伙伴。陪伴时间让宠物和植物成长，Codex 新记录的 token 用量为宠物补充劳动精力。不需要为了养宠物额外调用 AI。

### 主要功能

- **连续的像素花园。** 观赏植物、菜畦和草地位于同一个二维场景中。小芽会走到植物旁，播放对应的劳动动作。
- **挂机与离线成长。** 桌面花园运行时每小时获得 6 经验，离线每小时获得 3 经验，每次离开最多结算 12 小时。目前等级上限为 30 级，拥有四阶段外观。
- **Token 补充劳动精力。** 每 1,000 个可靠新增 token 补充 1 精力，上限 100。小芽消耗精力播种、浇水、施肥和收获；没有精力时植物仍会自然成长，不会枯萎。
- **种下即固定的随机种子。** 自动播种从对应区域已解锁的植物中随机选择，种下后品种固定，查看或重启不会重新抽取。
- **10 种植物、五阶段生长。** 随解锁条件满足，逐步种植三叶草、薄荷、雏菊、樱花树、向日葵、金盏花、胡萝卜、番茄、小萝卜和生菜。
- **植物科普信息卡。** 点击植物查看中英文简介与生长信息，区分真实植物知识和游戏内压缩后的成长规则。
- **收获、收藏与补种循环。** 精力足够时，小芽会收获成熟作物并补种空菜畦。成熟观赏植物可收藏后再摆回，也可开启自动轮换；轮换默认关闭。
- **花园小访客。** 记录成熟植物种类，逐步解锁蝴蝶和麻雀访客。
- **外观与桌面交互。** 点击小芽查看属性，通过手记查看成长、收藏和外观；支持中英文界面、配色主题、自定义 PNG 形象、拖动和窗口置顶。
- **本地存档。** 花园进度保存在自己的电脑上，无需游戏服务器，不包含联机对战。

### 环境与安装

需要 Windows 桌面环境、支持插件的 Codex 客户端、Python 3.10+（含 Tcl/Tk 和 `pythonw`），并将 Python 加入 PATH。下列命令还需要 Codex CLI、Git 和访问 GitHub 的网络。花园运行无需安装第三方 Python 包。

在 PowerShell 中执行：

```powershell
codex plugin marketplace add Jb-C-Lelouch/sprout-pet-beta
codex plugin add codex-pet@sprout-beta
```

重启 Codex，按提示审核并信任插件钩子，新建任务说 **“打开小芽花园”**。首次用量事件建立基线，不补记历史 token。

如果使用下载的 ZIP，完整解压后，在能看到本 README 和 `plugins` 文件夹的仓库根目录打开 PowerShell：

```powershell
codex plugin marketplace add .
codex plugin add codex-pet@sprout-beta
```

双击 `plugins/codex-pet/Check-Environment.cmd` 检查 Python/Tk 环境。同目录的 `Open-Desktop-Pet.cmd` 可以独立打开花园，但单独打开窗口不会替你安装或授权 Codex 用量钩子。

### 更新、存档与当前限制

执行 `codex plugin marketplace upgrade sprout-beta` 刷新市场，再在 Codex 中检查插件更新，重启花园并新建 Codex 任务。右键花园可退出。存档位于用户主目录的 `.codex-pet` 文件夹，备份前请关闭花园；卸载插件默认保留存档。

当前是早期 Windows 测试版，尚未内置 Python。Token 读取依赖宿主的本地 transcript 格式，兼容性可能随 Codex 版本变化；无法读取用量时仍可按时间成长。自动劳动仅在桌面花园运行时进行，离线不模拟劳动。收获仓库目前只记录数量，没有交易或货币系统。干净电脑安装与真实宿主钩子连接仍需更多测试。

钩子会读取本地 transcript 记录以提取会话标识和累计 token 数，不把对话正文复制进花园存档，也不上传到游戏服务器。详情见[隐私说明](PRIVACY.md)和[发布说明](RELEASE.md)。

遇到问题请在 [Issues](https://github.com/Jb-C-Lelouch/sprout-pet-beta/issues) 中提供插件、Windows、Python、Codex 版本，复现步骤和环境检查报错。无需上传聊天记录或完整存档。
