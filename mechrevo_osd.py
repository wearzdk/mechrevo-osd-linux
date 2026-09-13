#!/usr/bin/env python3
"""Display real MECHREVO firmware and keyboard status on Linux."""
import argparse
import errno
import logging
import os
from pathlib import Path
import struct
import sys

from events import LABELS, firmware_resource, lock_resource

EVENT_NAME = "MECHREVO OSD firmware events"
INPUT_EVENT = struct.Struct("llHHi")
LOG = logging.getLogger("mechrevo-osd")
BASE = Path(__file__).resolve().parent


def event_device():
    for path in Path("/sys/class/input").glob("event*"):
        try:
            if (path / "device/name").read_text().strip() == EVENT_NAME:
                return Path("/dev/input") / path.name
        except FileNotFoundError:
            continue
    return None


def lock_paths():
    result = {}
    for name in ("capslock", "numlock"):
        paths = sorted(Path("/sys/class/leds").glob(f"*::{name}/brightness"))
        paths.sort(key=lambda p: "/i8042/" not in str(p.resolve()))
        if paths:
            result[name] = paths[0]
    return result


def validate_assets():
    from PySide6.QtGui import QImageReader
    for name in LABELS:
        asset = BASE / "assets" / (name + ".png")
        reader = QImageReader(str(asset))
        if reader.read().isNull():
            raise RuntimeError(f"Cannot read icon {asset}: {reader.errorString()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--backend", choices=["auto", "layer-shell", "x11", "notifications"], default="auto")
    parser.add_argument("--check-display", action="store_true", help="Check the selected display without showing an OSD")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.check:
        path = event_device()
        if path is None:
            parser.error("Firmware event transport is not bound")
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        os.close(fd)
        validate_assets()
        print(f"Read-only firmware transport: {path}; icons present")
        if not args.check_display:
            return

    from PySide6.QtCore import QObject, QTimer, QSocketNotifier, QLockFile
    from PySide6.QtGui import QGuiApplication
    from display import create_display

    app = QGuiApplication(sys.argv[:1])
    app.setApplicationName("mechrevo-osd")
    app.setDesktopFileName("mechrevo-osd")
    app.setQuitOnLastWindowClosed(False)
    validate_assets()
    display = create_display(app, args.backend)
    LOG.info("Display backend: %s", display.name)
    if args.check_display:
        print(f"Display ready: {display.name}")
        return
    runtime = Path(os.environ["XDG_RUNTIME_DIR"]) / "mechrevo-osd"
    runtime.mkdir(mode=0o700, exist_ok=True)
    lock = QLockFile(str(runtime / "daemon.lock"))
    if not lock.tryLock(0):
        parser.error("OSD is already running or its runtime directory is unavailable")

    def show_resource(name):
        if name is not None:
            display.show(name)
            LOG.info("state=%s", name)

    class Bindings(QObject):
        def __init__(self):
            super().__init__()
            self.fd = None
            self.notifier = None
            self.words = {}
            self.leds = lock_paths()
            self.previous = self.read_locks()
            self.discovery = QTimer(self)
            self.discovery.timeout.connect(self.discover)
            self.discovery.start(1000)
            self.led_timer = QTimer(self)
            self.led_timer.timeout.connect(self.poll_locks)
            self.led_timer.start(100)
            self.discover()

        def discover(self):
            self.leds = lock_paths()
            if self.fd is None:
                path = event_device()
                if path is not None:
                    self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                    self.notifier = QSocketNotifier(self.fd, QSocketNotifier.Read, self)
                    self.notifier.activated.connect(self.read_events)
                    LOG.info("Listening to firmware events: %s", path)

        def read_events(self):
            try:
                raw = os.read(self.fd, INPUT_EVENT.size * 64)
            except BlockingIOError:
                return
            except OSError as exc:
                if exc.errno != errno.ENODEV:
                    raise
                self.notifier.setEnabled(False)
                self.notifier.deleteLater()
                os.close(self.fd)
                self.fd = None
                self.words.clear()
                LOG.warning("Firmware device removed; waiting for device re-enumeration")
                return
            if not raw or len(raw) % INPUT_EVENT.size:
                raise RuntimeError("Truncated firmware transport record")
            for sec, usec, typ, code, value in INPUT_EVENT.iter_unpack(raw):
                if typ == 0 and code == 3:
                    raise RuntimeError("Firmware event queue overflow")
                if typ == 4 and code in (0, 3):
                    self.words[code] = value & 0xffffffff
                elif typ == 0 and code == 0:
                    if set(self.words) != {0, 3}:
                        raise RuntimeError("Incomplete Firmware event payload")
                    detail = struct.pack("<II", self.words[0], self.words[3])
                    self.words.clear()
                    LOG.info("firmware packet=%s time=%s.%06d", detail.hex(), sec, usec)
                    show_resource(firmware_resource(detail))

        def read_locks(self):
            states = {}
            for name, path in self.leds.items():
                try:
                    state = int(path.read_text())
                except FileNotFoundError:
                    continue
                if state not in (0, 1):
                    raise ValueError(f"Invalid kernel lock state: {path}: {state}")
                states[name] = state
            return states

        def poll_locks(self):
            # Kernel LEDs report the actual lock state, including external changes.
            current = self.read_locks()
            for name, state in current.items():
                if name in self.previous and self.previous[name] != state:
                    LOG.info("kernel lock state %s=%d", name, state)
                    show_resource(lock_resource(name, state))
            self.previous = current

    # Qt calls Python slots asynchronously: errors must stop the service visibly.
    def fail(exc_type, exc, traceback):
        LOG.critical("OSD binding failed", exc_info=(exc_type, exc, traceback))
        app.exit(1)
    sys.excepthook = fail
    bindings = Bindings()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
