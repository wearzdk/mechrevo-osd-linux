# MECHREVO OSD for Linux

为机械革命笔记本提供 Linux 屏幕状态提示（OSD），移植自 Windows 实现，使用原厂图标。

可显示性能模式、键盘背光亮度、Fn 锁定、触控板开关，以及 Caps Lock / Num Lock 状态。

## 用 AI 安装（推荐）

在目标 Linux 电脑上打开 Claude Code、Codex 或其他能执行本机命令的 AI 编程助手，把下面这段话发给它：

```text
请阅读这个仓库，并帮我在当前 Linux 电脑上安装、配置和测试：
https://github.com/wearzdk/mechrevo-osd-linux

先读取仓库的 AGENTS.md，检查我的机型、内核、桌面环境和现有安装，
选择合适的安装方式，配置登录启动，并验证按键状态提示。

如果我的型号与已支持型号不完全一致，请按仓库的机型适配指南，
检测硬件接口、采集事件并尝试适配；需要我配合按键测试时告诉我。
如果产生了新的适配代码，测试通过后请提交 PR，帮助更多人使用。
最后告诉我哪些功能已验证，以及如何更新或卸载。
```

让 AI 负责检查环境、安装依赖和处理配置，你按提示完成实体按键测试即可。**其他型号也欢迎尝试适配**，成功后可以让 AI 把改动和测试结果整理成 PR。

仓库提供 [AGENTS.md](AGENTS.md) 作为 AI 工作入口，[CLAUDE.md](CLAUDE.md) 引用同一套指引。后面的依赖、安装和排查说明主要供 AI 执行时查阅，也可以用于手动安装。

## 兼容性

当前已适配机型：**MECHREVO WUJIE Series-T142-HPT-R**。型号不完全一致时，可让 AI 按 [机型适配指南](docs/hardware-adaptation.md) 检查接口并测试适配。提交新机型支持请参考 [贡献指南](CONTRIBUTING.md)。

程序根据当前会话自动选择显示方式：

| 会话能力 | 自动使用 | 显示方式 |
| --- | --- | --- |
| X11 | `x11` | 120×120 悬浮图标，主屏下方，1500 ms |
| Wayland + layer-shell，例如 Plasma、Sway、Hyprland | `layer-shell` | 同上，不抢焦点、不截获点击 |
| 其他 Wayland，例如 GNOME | `notifications` | 原厂图标和状态文本；位置、尺寸、时长受通知服务控制 |

系统通知方式也可手动启用，其显示效果受桌面通知设置和勿扰模式影响。

各环境的测试情况见 [测试与兼容性](docs/validation.md)。

## 依赖

- Linux：支持 6.18 LTS 和 7.2 系列内核。
- Python 3.10+、PySide6（Qt Quick / Qt QML）。推荐使用发行版提供的匹配版本。
- DKMS、当前内核对应的头文件、C 编译工具、make、systemd/udev。
- Wayland 悬浮显示：`wayland-info` 和 `layer-shell-qt` 的 QML 模块，适用于支持 layer-shell 的合成器。
- 系统通知：`dbus-python`（Arch 包名 `python-dbus`）和 `org.freedesktop.Notifications` 会话服务。

Arch Linux 示例（内核头文件请选与你的内核匹配的软件包）：

```sh
sudo pacman -S --needed base-devel dkms pyside6 qt6-declarative qt6-wayland python-dbus wayland-utils layer-shell-qt
```

## 安装

**AI 执行入口：**先阅读 [AGENTS.md](AGENTS.md)，再根据本机情况选择下面的安装路径；需要修改型号支持时，转到 [机型适配指南](docs/hardware-adaptation.md)。

### AUR

Arch Linux 用户可安装 [mechrevo-osd-linux](https://aur.archlinux.org/packages/mechrevo-osd-linux)，会自动依赖 [mechrevo-osd-dkms](https://aur.archlinux.org/packages/mechrevo-osd-dkms) 驱动包。请先安装当前内核对应的头文件包。

```sh
yay -S mechrevo-osd-linux
sudo systemctl enable --now mechrevo-osd-binding.service
mechrevo-osd --check --check-display
mechrevo-osd
```

AUR 版本的登录启动、升级和卸载步骤见 [Arch 使用说明](https://aur.archlinux.org/cgit/aur.git/tree/README.arch?h=mechrevo-osd-linux)，安装后也可在 `/usr/share/doc/mechrevo-osd-linux/README.arch` 查看。

### 从源码安装

首次安装前检查主板和内核：

```sh
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/board_name
uname -r
```

在仓库目录执行：

```sh
sudo make install
sudo dkms add -m mechrevo-osd -v 0.1.1
sudo dkms install -m mechrevo-osd -v 0.1.1
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=input
sudo udevadm settle
sudo systemctl daemon-reload
sudo systemctl enable --now mechrevo-osd-binding.service
mechrevo-osd --check --check-display
```

使用 Secure Boot 的系统，还需按发行版文档完成 DKMS 签名信任配置。

随后在当前桌面的终端运行：

```sh
mechrevo-osd
```

默认 `--backend auto`。也可使用 `--backend layer-shell`、`--backend x11`、`--backend notifications`；明确指定的后端不可用时会报错。

## 登录启动（源码安装）

使用 XDG Autostart 在登录时启动：

```sh
mkdir -p ~/.config/autostart
cp /usr/local/share/applications/mechrevo-osd.desktop ~/.config/autostart/
```

对于自行配置的窗口管理器，可在会话启动配置中加入 `/usr/local/bin/mechrevo-osd`。图形进程应以当前桌面用户运行。

如果桌面支持 `graphical-session.target`，也可以**代替**上述方式使用可选用户服务：

```sh
mkdir -p ~/.config/systemd/user
cp /usr/local/share/mechrevo-osd/mechrevo-osd.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now mechrevo-osd.service
```

## 升级或重新安装（源码安装）

先停止图形进程，再停止绑定服务，然后移除旧 DKMS 注册（版本号按 `dkms status` 的结果填写）；接着执行安装步骤。已有用户服务可用以下命令停止：

```sh
systemctl --user stop mechrevo-osd.service
sudo systemctl stop mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo dkms remove -m mechrevo-osd -v 0.1.1 --all
```

安装完成后重新启动绑定服务和图形进程，使新版本生效。

## 停用与卸载（源码安装）

先停止图形进程，移除你启用的登录启动项：

```sh
rm -f ~/.config/autostart/mechrevo-osd.desktop
# 如果启用了可选用户服务：
systemctl --user disable --now mechrevo-osd.service
rm -f ~/.config/systemd/user/mechrevo-osd.service
systemctl --user daemon-reload
```

随后在仓库目录执行：

```sh
sudo systemctl disable --now mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo dkms remove -m mechrevo-osd -v 0.1.1 --all
sudo make uninstall
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

停止绑定服务后，系统会恢复使用原事件驱动。

## 排查与测试

```sh
mechrevo-osd --check --check-display
systemctl status mechrevo-osd-binding.service
journalctl -u mechrevo-osd-binding.service -b
# 可选用户服务的日志：
journalctl --user -u mechrevo-osd.service -b
make test
```

报告问题时请提供主板型号、内核版本、桌面环境、会话类型（X11 / Wayland）和相关错误日志。

源码使用 GPL-2.0-or-later；图标版权说明见 [NOTICE](NOTICE)。
