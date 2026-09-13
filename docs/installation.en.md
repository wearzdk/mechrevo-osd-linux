# Installation and maintenance

[Back to README](../README.en.md) · [简体中文](installation.md)

Reference instructions for AI assistants and users who need to install, update, or troubleshoot manually. Read [AGENTS.md](../AGENTS.md) first and identify the laptop model, kernel, and existing installation method.

## Arch Linux / AUR

Follow the [quick start](../README.en.md#quick-start-on-arch-linux) for initial installation and login startup. The `mechrevo-osd-linux` package automatically depends on the `mechrevo-osd-dkms` driver package.

Install headers matching the running kernel: `linux-headers` for Arch's `linux`, `linux-lts-headers` for `linux-lts`, and `linux-zen-headers` for `linux-zen`. Custom kernels need their corresponding header packages. Check `uname -r` before choosing a package.

For native Wayland overlays, also install:

```sh
sudo pacman -S --needed qt6-wayland wayland-utils layer-shell-qt
```

The default `--backend auto` selects a backend based on the session. You may explicitly select `layer-shell`, `x11`, or `notifications`; an unavailable explicitly selected backend produces an error. See [desktop compatibility](../README.en.md#desktop-compatibility).

### Updates

```sh
yay -S mechrevo-osd-linux
```

Restart the computer after updating to load the new driver and graphical process. To apply an update immediately, stop the graphical process, then reload the module:

```sh
sudo systemctl stop mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo systemctl start mechrevo-osd-binding.service
mechrevo-osd
```

If a user service manages the graphical process, stop it with `systemctl --user stop mechrevo-osd.service` before reloading the module and start it afterward with `systemctl --user start mechrevo-osd.service`.

### Disable and remove

Stop the graphical process and remove the startup method you enabled, then remove the packages:

```sh
rm -f ~/.config/autostart/mechrevo-osd.desktop
# Only if you enabled the user service:
systemctl --user disable --now mechrevo-osd.service
sudo systemctl disable --now mechrevo-osd-binding.service
sudo pacman -Rns mechrevo-osd-linux mechrevo-osd-dkms
```

Removing the DKMS package removes its module. Stopping the binding service restores the original event driver.

### Migrate from a source installation

Follow the source removal instructions below before installing the AUR packages. Files under `/usr/local/bin` and old custom systemd units can take precedence over the package files under `/usr`. Preserve your source checkout and configuration, and check `type -a mechrevo-osd` to confirm which version will start.

The AUR application package also includes a local reference at `/usr/share/doc/mechrevo-osd-linux/README.arch` (Chinese).

## Source installation requirements

- Linux kernel headers, DKMS, C build tools, make, and systemd/udev. The driver has build coverage for the 6.18 LTS and 7.2 kernel series; see the [validation record](validation.md).
- Python 3.10+ and PySide6 with Qt Quick / QML. Use matching packages from your distribution.
- Native Wayland overlays: `wayland-info` and the `layer-shell-qt` QML module, on a compositor supporting layer-shell.
- Desktop notifications: `dbus-python` (`python-dbus` on Arch) and a session service implementing `org.freedesktop.Notifications`.

On Arch, install the build and display dependencies, plus the appropriate kernel headers:

```sh
sudo pacman -S --needed base-devel dkms pyside6 qt6-declarative qt6-wayland python-dbus wayland-utils layer-shell-qt
```

## Install from source

Check the board and running kernel first:

```sh
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/board_name
uname -r
```

Clone the repository and enter its directory. The commands below match driver version `0.1.1`; check `driver/dkms.conf` when using a different revision.

```sh
git clone https://github.com/wearzdk/mechrevo-osd-linux.git
cd mechrevo-osd-linux
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

If Secure Boot is enabled, follow your distribution's instructions to configure module signing and trust for DKMS modules.

Start the OSD from a terminal in your desktop session:

```sh
mechrevo-osd
```

## Start at login after a source installation

Use XDG Autostart:

```sh
mkdir -p ~/.config/autostart
cp /usr/local/share/applications/mechrevo-osd.desktop ~/.config/autostart/
```

For a manually configured window manager, you can instead add `/usr/local/bin/mechrevo-osd` to its session startup configuration. Run the graphical process as the desktop user.

If your desktop manages `graphical-session.target`, the optional user service is another alternative. Use one startup method:

```sh
mkdir -p ~/.config/systemd/user
cp /usr/local/share/mechrevo-osd/mechrevo-osd.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now mechrevo-osd.service
```

## Update or reinstall a source installation

Stop the graphical process, stop the binding service, and remove the old DKMS registration before repeating the installation steps. Use the old version reported by `dkms status` in the removal command. If the graphical process is managed by the optional user service:

```sh
systemctl --user stop mechrevo-osd.service
sudo systemctl stop mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo dkms remove -m mechrevo-osd -v 0.1.1 --all
```

After installation, start the binding service and graphical process again to use the new version.

## Remove a source installation

Stop the graphical process and remove the startup entry you enabled:

```sh
rm -f ~/.config/autostart/mechrevo-osd.desktop
# Only if you enabled the optional user service:
systemctl --user disable --now mechrevo-osd.service
rm -f ~/.config/systemd/user/mechrevo-osd.service
systemctl --user daemon-reload
```

Then, from the source checkout:

```sh
sudo systemctl disable --now mechrevo-osd-binding.service
sudo modprobe -r mechrevo_osd_wmi
sudo dkms remove -m mechrevo-osd -v 0.1.1 --all
sudo make uninstall
sudo systemctl daemon-reload
sudo udevadm control --reload-rules
```

Stopping the binding service restores the original event driver.

## Diagnostics and tests

```sh
mechrevo-osd --check --check-display
systemctl status mechrevo-osd-binding.service
journalctl -u mechrevo-osd-binding.service -b
# If using the optional user service:
journalctl --user -u mechrevo-osd.service -b
# From the source checkout:
make test
```

`--check` verifies access to the event devices and icons; `--check-display` checks backend initialization. Physical-key testing is still needed to verify the full event-to-display path.
