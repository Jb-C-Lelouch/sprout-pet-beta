# Codex Pet · 小芽的桌面花园

一个本地运行的休闲桌面花园：小芽随陪伴时间成长，Codex新增token补充精力，用于播种、浇水、施肥和收获。

- 观赏花园、菜畦与自然草地构成同一场景。
- 同区域已解锁植物随机播种，种下后品种固定。
- 点击植物打开离线科普卡，点击小芽查看等级、精力和种植数量。
- 10种植物提供中英文科普和五阶段形象；菜畦收获后随机补种。
- 成熟观赏植物可收藏、摆回，或开启自动轮换；默认保留原花园。
- 成长足迹显示陪伴与精力，收藏页显示收获；花园装扮提供中英文切换、配色与PNG形象。
- 需要Python3.10+和Tk，不需要Node或服务器。打开Open-Desktop-Pet.cmd启动。

## 规则与使用

[GROWTH.md](GROWTH.md)：时间成长和精力。[GARDEN.md](GARDEN.md)：自动照料与种植。[BOTANY.md](BOTANY.md)：植物资料来源。[DESKTOP.md](DESKTOP.md)：窗口交互。

命令：status、garden、plant、garden-move、garden-remove；hook供宿主回调使用。可以指定--data使用独立本地存档。

用量来自SessionStart / UserPromptSubmit / Stop钩子与本地transcript计数。transcript不是稳定公共接口，不可读时不补精力，自然成长仍可使用。新会话首次记录建立基线，不补记历史token。状态waiting for first hook表示尚未收到可靠用量；安装更新后新开Codex任务以加载新版本。

默认存档在~/.codex-pet，测试只使用临时存档。清理旧原型时先备份正式存档。当前产品仅保留休闲养成和植物科普。
