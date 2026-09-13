# MECHREVO OSD for Linux

为机械革命笔记本提供 Linux 屏幕状态提示（OSD），移植自 Windows 实现，使用原厂图标。

可显示性能模式、键盘背光亮度、Fn 锁定、触控板开关，以及 Caps Lock / Num Lock 状态。

## 兼容性

当前适配机型：**MECHREVO WUJIE Series-T142-HPT-R**。其他型号有待适配。

程序根据当前会话自动选择显示方式：

| 会话能力 | 自动使用 | 显示方式 |
| --- | --- | --- |
| X11 | `x11` | 120×120 悬浮图标，主屏下方，1500 ms |
| Wayland + layer-shell，例如 Plasma、Sway、Hyprland | `layer-shell` | 同上，不抢焦点、不截获点击 |
| 其他 Wayland，例如 GNOME | `notifications` | 原厂图标和状态文本；位置、尺寸、时长受通知服务控制 |

系统通知方式也可手动启用，其显示效果受桌面通知设置和勿扰模式影响。

各环境的测试情况见 [测试与兼容性](docs/validation.md)。

## 依赖

- Linux：当前在 7.2.4 内核上验证；旧内核兼容性待适配。
- Python 3.10+、PySide6（Qt Quick / Qt QML）。推荐使用发行版提供的匹配版本。
- DKMS、当前内核对应的头文件、C 编译工具、make、systemd/udev。
- Wayland 悬浮显示：`wayland-info` 和 `layer-shell-qt` 的 QML 模块，适用于支持 layer-shell 的合成器。
- 系统通知：`dbus-python`（Arch 包名 `python-dbus`）和 `org.freedesktop.Notifications` 会话服务。

Arch Linux 示例（内核头文件请选与你的内核匹配的软件包）：

```sh
sudo pacman -S --needed base-devel dkms pyside6 qt6-declarative qt6-wayland python-dbus wayland-utils layer-shell-qt
```

## 安装

首次安装前检查主板和内核：

```sh
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/board_name
uname -r
```

在仓库目录执行：

```sh
sudo make install
sudo dkms add -m mechrevo-osd -v 0.1.0
sudo dkms install -m mechrevo-osd -v 0.1.0
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

## 登录启动

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

## 升级或重新安装

先停止图形进程，再停止绑定服务，然后移除旧 DKMS 注册；接着执行安装步骤。已有用户服务可用以下命令停止：

```sh
systemctl --user stop mechrevo-osd.service
sudo systemctl stop mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo dkms remove -m mechrevo-osd -v 0.1.0 --all
```

安装完成后重新启动绑定服务和图形进程，使新版本生效。

## 停用与卸载

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
sudo dkms remove -m mechrevo-osd -v 0.1.0 --all
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
