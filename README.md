# MECHREVO OSD for Linux

**简体中文** | [English](README.en.md)

为**机械革命无界 14X / 14X Pro** 等笔记本提供 Linux 按键状态提示。移植自 Windows 实现，保留原厂图标；按下快捷键，即可看到性能模式、键盘背光、Fn 锁定、触控板及 Caps Lock / Num Lock 状态。

当前适配板型：**MECHREVO WUJIE Series-T142-HPT-R**。其他板型可按[适配指南](docs/hardware-adaptation.md)测试适配。

## 让 AI 帮你安装（推荐）

在目标电脑上打开 Claude Code、Codex 等 AI 编程助手，发送：

> 阅读 https://github.com/wearzdk/mechrevo-osd-linux ，按照 AGENTS.md 检查我的机型、内核和桌面环境，安装并配置 OSD 与登录自动启动，验证按键状态提示。如果型号不同，请检查硬件接口并尝试适配；需要实体按键测试时告诉我。适配成功后提交 PR，帮助更多人使用。

AI 负责安装和配置，你按提示测试实体按键即可。以下说明也供 AI 安装时参考；无需自己逐项研究驱动配置。

## 快速安装（Arch Linux）

**先准备与你当前内核匹配的头文件。** 例如 Arch 标准 `linux` 内核需要 `linux-headers`，LTS 内核需要 `linux-lts-headers`。可用 `uname -r` 查看当前内核；定制内核的处理见[安装指南](docs/installation.md)。

在当前桌面的终端执行：

```sh
yay -S mechrevo-osd-linux &&
sudo systemctl enable --now mechrevo-osd-binding.service &&
mkdir -p ~/.config/autostart &&
cp /usr/share/applications/mechrevo-osd.desktop ~/.config/autostart/ &&
mechrevo-osd --check --check-display
```

也可以把 `yay` 换成 `paru`。这会安装程序和 DKMS 驱动、启用系统绑定服务，并配置以后登录时自动显示 OSD。

**立即试用：**运行 `mechrevo-osd`，按 **Fn+X**、键盘背光键或 **Caps Lock**，查看状态图标。程序在当前终端持续运行；退出后可在下次登录时自动启动。OSD 没有需要一直打开的控制面板。

已有用户服务或手动安装版本时，先让 AI 检查现有启动入口，避免重复配置。其他发行版或源码安装见[安装与维护](docs/installation.md)。

## 桌面兼容性

程序自动选择显示方式，不需要绑定某个桌面环境：

| 桌面会话 | 显示方式 |
| --- | --- |
| X11 | 屏幕下方显示原厂图标，约 1.5 秒后隐藏 |
| 支持 layer-shell 的 Wayland，例如 Plasma、Sway、Hyprland | 同样的悬浮图标，不抢焦点、不拦截点击 |
| 其他 Wayland，例如 GNOME | 通过桌面通知显示图标与状态，遵循桌面通知设置 |

Wayland 原生悬浮显示需要 `qt6-wayland`、`wayland-utils`、`layer-shell-qt`，安装方法见[指南](docs/installation.md)。Plasma Wayland 已在本机运行；其他环境的验证范围见[测试记录](docs/validation.md)。

Fn+X、键盘背光、Caps Lock / Num Lock 已通过实机按键测试；Fn 锁定和触控板提示已实现，仍待实机确认。

## 没有出现提示？

先运行：

```sh
mechrevo-osd --check --check-display
systemctl status mechrevo-osd-binding.service
journalctl -u mechrevo-osd-binding.service -b
```

检查图形进程是否正在运行，并在使用通知后端时检查勿扰模式。报告问题时附上机型、`uname -r`、桌面环境、X11 / Wayland 会话类型和上述输出。

## 更多说明

- [安装、更新、迁移与卸载](docs/installation.md)
- [新型号适配](docs/hardware-adaptation.md)与[贡献指南](CONTRIBUTING.md)
- [测试与兼容性记录](docs/validation.md)
- AI 工作入口：[AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md)

本项目由社区独立维护，与机械革命及相关厂商无隶属关系，未获官方认可或赞助。源码使用 [GPL-2.0-or-later](LICENSE)；原厂图标归其权利人所有，见 [NOTICE](NOTICE)。
