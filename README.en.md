# MECHREVO OSD for Linux

[简体中文](README.md) | **English**

On-screen keyboard and firmware status for **MECHREVO Wujie 14X / 14X Pro** laptops on Linux. Ported from the Windows implementation, with original OEM icons. See performance mode, keyboard backlight, Fn lock, touchpad, Caps Lock, and Num Lock status when you press the corresponding keys.

Currently supported board: **MECHREVO WUJIE Series-T142-HPT-R**. Other boards can be investigated using the [hardware adaptation guide](docs/hardware-adaptation.md) (Chinese).

## Recommended: let an AI assistant install it

Open Claude Code, Codex, or another AI coding assistant on the target laptop and send:

> Read https://github.com/wearzdk/mechrevo-osd-linux and follow AGENTS.md to check my laptop model, kernel, and desktop environment. Install the OSD, configure startup at login, and verify keyboard status notifications. If my model differs, inspect the hardware interfaces and try adapting it. Tell me when you need me to press physical keys for testing. Once an adaptation works, submit a pull request to help other users.

The assistant handles installation and configuration; you help test the physical keys. The instructions below also serve as a reference for the assistant.

## Quick start on Arch Linux

**Install the headers matching your running kernel first.** For example, the standard Arch `linux` kernel needs `linux-headers`, while `linux-lts` needs `linux-lts-headers`. Check your kernel with `uname -r`. For custom kernels, see the [installation guide](docs/installation.en.md).

Run these commands in a terminal in your desktop session:

```sh
yay -S mechrevo-osd-linux &&
sudo systemctl enable --now mechrevo-osd-binding.service &&
mkdir -p ~/.config/autostart &&
cp /usr/share/applications/mechrevo-osd.desktop ~/.config/autostart/ &&
mechrevo-osd --check --check-display
```

You can use `paru` instead of `yay`. This installs the application and DKMS driver, enables the system binding service, and configures the OSD to start at future logins.

**Try it now:** run `mechrevo-osd`, then press **Fn+X**, a keyboard backlight key, or **Caps Lock**. The program stays running in that terminal. After exiting, it will start automatically at your next login. There is no control panel you need to keep open.

If you already use a user service or a manual installation, have the assistant inspect your existing startup configuration before adding another entry. For other distributions and source installations, see [installation and maintenance](docs/installation.en.md).

## Desktop compatibility

The app automatically selects a display backend:

| Desktop session | Display |
| --- | --- |
| X11 | Original icons near the bottom of the screen, hidden after about 1.5 seconds |
| Wayland with layer-shell, such as Plasma, Sway, or Hyprland | The same overlay, without taking focus or intercepting clicks |
| Other Wayland sessions, such as GNOME | Icons and status text through desktop notifications, following your desktop's notification settings |

Native Wayland overlays require `qt6-wayland`, `wayland-utils`, and `layer-shell-qt`; see the [installation guide](docs/installation.en.md). Plasma Wayland has been tested on the development laptop. Standalone X11, GNOME, Sway, and Hyprland have not yet been tested on a full desktop session; the [validation record](docs/validation.md) documents the current coverage in Chinese.

Fn+X, keyboard backlight, Caps Lock, and Num Lock have passed physical-key tests. Fn lock and touchpad notifications are implemented but still await physical-key verification.

## No notification appears?

Run:

```sh
mechrevo-osd --check --check-display
systemctl status mechrevo-osd-binding.service
journalctl -u mechrevo-osd-binding.service -b
```

Check that the graphical process is running. When using the notifications backend, also check your desktop's Do Not Disturb setting. When reporting a problem, include your laptop model, `uname -r`, desktop environment, session type (X11 or Wayland), and the output above.

## Further reading

- [Installation, updates, migration, and removal](docs/installation.en.md)
- [Hardware adaptation](docs/hardware-adaptation.md) and [contribution guide](CONTRIBUTING.md) (Chinese)
- [Validation and compatibility record](docs/validation.md) (Chinese)
- Instructions for AI assistants: [AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md)

This is an independent community project, not affiliated with, endorsed by, or sponsored by MECHREVO or other hardware manufacturers. Source code is licensed under [GPL-2.0-or-later](LICENSE). Original icons belong to their respective rights holders; see [NOTICE](NOTICE).
