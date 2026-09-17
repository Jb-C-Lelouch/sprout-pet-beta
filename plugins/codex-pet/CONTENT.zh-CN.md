# 扩展小芽内容

[English](CONTENT.md)

内容统一放在 `content/` 下，每个进程启动时加载一次。安装更新后重启花园，并新建 Codex 任务。运行只需要 Python 3.10+，不增加第三方依赖。

```text
content/
  plants/<id>/manifest.json
  plants/<id>/locales/en.json
  plants/<id>/locales/zh-CN.json
  plants/<id>/sources.json
  plants/<id>/sprites/*.png          # 使用 PNG 时添加
  pets/sprout/manifest.json
  pets/sprout/locales/*.json
  scenery/garden/manifest.json
  scenery/garden/background.png
  locales/en.json
  locales/zh-CN.json
```

## ID 与版本

清单统一包含 `schema_version: 1`、`type`、`id`、`author` 和 `license`。ID 必须与文件夹名相同，用小写字母开头，可包含数字和连字符，同类内容中不能重复。旧存档直接保存植物 ID，因此不要改名或删除已有 ID；确需变更时必须做存档迁移。新增品种无需改数据库。内容缺失或格式错误时会明确指出文件并停止加载，不会悄悄替换原来的植物。

植物清单还包括目录排序 `order`、区域 `zone`（`garden` 或 `crops`）以及 `game` 中的解锁等级 `level`、成熟进度 `xp`、代表色 `color` 和兼容字段 `shape`。`xp` 是种下后需要新增的成长进度，不是购买价格。农作物的 `shape` 为 `crop`；播种与摆放按 `zone` 判断。新植物复用已有照料、收获与收藏规则。

## 不改 Python，增加一株普通植物

1. 复制一株已有植物的目录，例如复制到 `plants/test-flower/`。
2. 修改 ID、排序、区域和数值，不修改旧物种 ID。
3. 填写 `locales/en.json`：`garden_name`（游戏简称）、`name`（科普名称）、`latin`（学名）、`family`（科）、`life`（生活型）、`intro`（简介）、`observe`（观察线索）、`habitat`（习性）、`fact`（知识点）。在 `zh-CN.json` 填写对应中文字段。英文必填，中文缺项时逐字段回退英文。
4. 更新 `sources.json`，填写经过核对的科普来源。每条包括 `id`（必须有 `main`，可另有 `extra`）、HTTPS `url`、分语言的 `label` 和核对日期 `checked_at`。真实习性与游戏成长数值分开，当前信息卡最多显示两条来源。
5. 提供五阶段 PNG，或复用一个已注册绘图变体。发布前执行检查。

PNG 图像配置示例，替换清单中的 `visual`：

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

五阶段依次对应 0%、25%、50%、75%、100% 进度，阶段名称可自定，不要求成熟一定是开花。图片尺寸必须与 `size` 相符。`anchor` 使用原始画布坐标，表示植物接触地面的点；`scale` 为 1–4 的整数倍像素放大。透明部分不会挡住场景点击。图片必须位于本内容包内，单张不超过 8 MB，宽高不超过 2048。`--render` 会实际解码，而不只是检查 PNG 文件头。

现有绘图使用 `kind: procedural`、`renderer: botanical-v1` 和已注册的 `variant`（原物种 ID），固定原始画布为 80×96。复用变体不需要改代码，全新的程序绘图仍需写代码；PNG 不需要注册绘图函数。内容包不能动态导入或执行 Python。

## 宠物形态与动作

`pets/sprout/manifest.json` 的 `forms` 定义形态 ID、递增的解锁等级 `level` 和现有绘图等级 `rank`（0–3）。形态名称放在各语言的 `forms` 字典中。每个形态可用独立 `visual` 覆盖默认外观，适合逐形态配置 PNG 动作帧。当前桌面仍固定选择内置 `sprout`，添加第二个宠物包不会自动出现宠物选择界面。

宠物图像配置包含尺寸、落地锚点、放大倍数和八种动作：`rest`、`sleep`、`walk`、`dig`、`water`、`fertilize`、`harvest`、`archive`。每个动作指定 `frames`、单帧毫秒数 `frame_ms`、是否循环 `loop`。PNG 模式的帧为文件相对路径；`sprout-v1` 绘图器使用整数姿势帧 0–7，睡眠为 8–15。休息两秒后显示睡眠动作。PNG 原图朝左，朝右时自动镜像，锚点也同步镜像；不循环的动画停在最后一帧。

PNG 动作示例：`"water": {"frames": ["sprites/water-0.png", "sprites/water-1.png"], "frame_ms": 125, "loop": true}`。

动作清单只控制外观播放。劳动完成、扣精力和奖励仍由游戏逻辑结算，换皮肤不会改变收益或重复扣费；播放完动画本身不会触发结算。新增劳动类型或特殊玩法仍需要改代码。

## 场景与公共文案

`scenery/garden` 描述背景文件、原始尺寸、缩小倍数、位置以及菜畦绘图器和位置。菜畦仍由程序绘制。种植点布局、交互和装饰访客仍由代码控制，这次没有引入场景编辑器。

公共界面译文和游戏科普说明位于 `content/locales/`。公共界面仍兼容原有中文文本键及动态格式化，植物资料已改为具名字段，不再依赖英文元组的排列顺序。当前界面选择器提供中英文。

## 检查与发布

在插件根目录执行：

```powershell
python scripts/validate_content.py --strict
python scripts/validate_content.py --render --strict
python scripts/check_environment.py --smoke
```

检查范围包括版本、ID、资源路径、数值、英文必填字段、资料来源、图片尺寸、阶段、形态和动作。缺少中文字段会警告，`--strict` 将警告视为失败；运行时仍回退英文。实际绘制检查需要 Tk 和桌面环境。环境检查使用临时存档，不修改个人花园。

分发时带上整个 `content/` 和配套脚本，开发目录的发布脚本会自动收集 JSON、PNG 和 Markdown 内容。新增第三方素材时保留真实作者和适用许可证，不要将无权授权的素材标为 MIT。科普来源链接只是引用依据，不意味着可以复制来源网页。
