# 小芽 · Windows 测试版

本地桌面花园：陪伴时间让小芽成长，Codex 新增 token 补充精力，小芽自动播种、浇水、施肥、收获。点击植物查看中英文植物科普卡。

## 环境

- Windows 桌面环境和支持插件的 Codex 客户端。
- Python 3.10 或更新版本，安装 Tcl/Tk 和 pythonw，并将 Python 加入 PATH。无需 pip 依赖。
- 使用下列命令安装时需要 Codex CLI、Git 和网络访问仓库。花园本身不需要服务器。

## 从仓库安装

仓库：[Jb-C-Lelouch/sprout-pet-beta](https://github.com/Jb-C-Lelouch/sprout-pet-beta)。在 PowerShell 中执行：

```powershell
codex plugin marketplace add Jb-C-Lelouch/sprout-pet-beta
codex plugin add codex-pet@sprout-beta
```

重启桌面应用，按提示审核并信任插件钩子，新建任务说“打开小芽花园”。仅打开窗口不代表 token 钩子已连接；首次事件建立基线，不补记历史 token。不同客户端提供的用量事件可能不同，用量不可读时自然成长仍可使用。

## 从下载包本地测试

完整解压 ZIP，打开解压目录里的 PowerShell（能看到本文件和 plugins 文件夹）：

```powershell
codex plugin marketplace add .
codex plugin add codex-pet@sprout-beta
```

双击 `plugins/codex-pet/Check-Environment.cmd` 检查环境；双击同目录 `Open-Desktop-Pet.cmd` 可以独立打开花园，但不会替你安装或信任用量钩子。

## 更新、退出与反馈

刷新市场：`codex plugin marketplace upgrade sprout-beta`。随后在插件界面检查更新，重启花园并新建 Codex 任务。

右键花园退出；在 Codex 插件界面卸载插件。存档默认保留在用户主目录的 `.codex-pet`，更新前建议在关闭花园后备份整个目录。测试请勿删除原存档。

问题请向[仓库 Issues](https://github.com/Jb-C-Lelouch/sprout-pet-beta/issues)反馈：版本 0.1.0-beta.1、Windows/Python/Codex 版本、复现步骤、环境检查报错。不需要上传聊天记录或完整存档。

隐私说明见 [PRIVACY.md](PRIVACY.md)，发布说明见 [RELEASE.md](RELEASE.md)。
