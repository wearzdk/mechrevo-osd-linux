# 安装与维护

[返回首页](../README.md) · [English](installation.en.md)

供 AI 助手和需要手动安装、升级或排查的用户参考。先阅读 [AGENTS.md](../AGENTS.md)，确认机型、内核和现有安装来源。

## Arch Linux / AUR

首次安装及登录启动见[首页快速安装](../README.md#快速安装arch-linux)。主程序包 `mechrevo-osd-linux` 自动依赖驱动包 `mechrevo-osd-dkms`。

安装当前内核对应的头文件。Arch 官方 `linux` 使用 `linux-headers`，`linux-lts` 使用 `linux-lts-headers`，`linux-zen` 使用 `linux-zen-headers`；其他内核需使用其对应的头文件包。用 `uname -r` 确认当前内核，不要给定制内核套用标准内核的头文件。

Wayland 原生悬浮显示还需安装：

```sh
sudo pacman -S --needed qt6-wayland wayland-utils layer-shell-qt
```

显示后端由会话能力决定，见[首页](../README.md#桌面兼容性)。默认 `--backend auto`；也可显式指定 `layer-shell`、`x11` 或 `notifications`。指定的后端不可用时会报告错误。

### 更新

```sh
yay -S mechrevo-osd-linux
```

更新后重启电脑，使驱动和图形进程加载新版本。需要立即生效时，先停止图形进程，再重新加载模块：

```sh
sudo systemctl stop mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo systemctl start mechrevo-osd-binding.service
mechrevo-osd
```

若使用用户服务管理图形进程，用 `systemctl --user stop mechrevo-osd.service` 停止，并在重新加载模块后用 `systemctl --user start mechrevo-osd.service` 启动。

### 停用和卸载

先关闭图形进程，移除已启用的登录启动入口，再移除软件包：

```sh
rm -f ~/.config/autostart/mechrevo-osd.desktop
# 仅在启用了用户服务时执行：
systemctl --user disable --now mechrevo-osd.service
sudo systemctl disable --now mechrevo-osd-binding.service
sudo pacman -Rns mechrevo-osd-linux mechrevo-osd-dkms
```

DKMS 包卸载时会移除模块。停止绑定服务会恢复原事件驱动。

### 现有源码安装迁移到 AUR

先按下方源码卸载步骤停止并移除旧安装，再安装 AUR 包。`/usr/local/bin/mechrevo-osd` 和旧的自定义 systemd 单元可能优先于 `/usr` 下的软件包文件；保留源码和已有配置，核对 `type -a mechrevo-osd` 确认启动的是目标版本。

AUR 包也附带本地参考文档：`/usr/share/doc/mechrevo-osd-linux/README.arch`。

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

## 从源码安装

首次安装前检查主板和内核：

```sh
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/board_name
uname -r
```

首次使用源码安装时，先获取仓库；已有工作区则进入原目录：

```sh
git clone https://github.com/wearzdk/mechrevo-osd-linux.git
cd mechrevo-osd-linux
```

在仓库目录执行（以下命令对应驱动版本 `0.1.1`，其他版本以 `driver/dkms.conf` 为准）：

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

