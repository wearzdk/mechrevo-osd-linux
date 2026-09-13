"""Display adapters selected by session capabilities, independent of desktop names."""
import logging
from pathlib import Path
import shutil
import subprocess
import time

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuick import QQuickWindow

from events import LABELS

BASE = Path(__file__).resolve().parent
LOG = logging.getLogger("mechrevo-osd")


def layer_shell_available():
    if shutil.which("wayland-info") is None:
        return False, "wayland-info is not installed"
    result = subprocess.run(["wayland-info"], capture_output=True, text=True, timeout=5)
    if result.returncode:
        raise RuntimeError(f"Cannot inspect Wayland protocols: {result.stderr.strip()}")
    if "interface: 'zwlr_layer_shell_v1'" not in result.stdout:
        return False, "compositor does not advertise layer-shell"
    return True, "layer-shell is available"


class Overlay:
    def __init__(self, app, layer):
        self.engine = QQmlApplicationEngine()
        source = BASE / ("LayerOverlay.qml" if layer else "Overlay.qml")
        component = QQmlComponent(self.engine, QUrl.fromLocalFile(str(source)))
        if component.isError():
            raise RuntimeError("; ".join(error.toString() for error in component.errors()))
        self.engine.load(str(source))
        if not self.engine.rootObjects():
            raise RuntimeError("Cannot create the OSD window")
        self.window = self.engine.rootObjects()[0]
        if not isinstance(self.window, QQuickWindow):
            raise RuntimeError("OSD root is not a Qt Quick window")
        self.window.setScreen(app.primaryScreen())
        app.primaryScreenChanged.connect(lambda screen: self.window.setScreen(screen))
        self.name = "layer-shell" if layer else "x11"

    def show(self, resource):
        self.window.showResource(QUrl.fromLocalFile(str(BASE / "assets" / (resource + ".png"))).toString())


class Notifications:
    name = "notifications"

    def __init__(self):
        import dbus
        self.dbus = dbus
        self.bus = dbus.SessionBus()
        self.call("GetServerInformation", "", ())
        self.notification_id = 0
        self.last_resource = None
        self.last_sent = 0
        self.pending = None
        self.refresh = QTimer()
        self.refresh.setSingleShot(True)
        self.refresh.setTimerType(Qt.PreciseTimer)
        self.refresh.timeout.connect(self.flush)

    def call(self, method, signature, arguments):
        # Keep one sender connection and use the well-known service name so a
        # notification daemon restart does not pin us to its old bus owner.
        return self.bus.call_blocking(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications",
            "org.freedesktop.Notifications", method, signature, arguments, timeout=2,
        )

    def show(self, resource):
        self.refresh.stop()
        self.pending = resource
        # Notification servers can reject identical updates within one second.
        # Coalesce only repeats of the same observed state; changed states are
        # published immediately, and cancel any queued repeat of the old state.
        remaining = 1000 - (time.monotonic() - self.last_sent) * 1000
        if resource == self.last_resource and remaining > 0:
            self.refresh.start(int(remaining) + 1)
        else:
            self.flush()

    def flush(self):
        resource = self.pending
        dbus = self.dbus
        uri = (BASE / "assets" / (resource + ".png")).as_uri()
        hints = dbus.Dictionary({
            "image-path": uri, "transient": dbus.Boolean(True),
            "suppress-sound": dbus.Boolean(True), "desktop-entry": "mechrevo-osd",
        }, signature="sv")
        self.notification_id = int(self.call("Notify", "susssasa{sv}i", (
            "MECHREVO OSD", dbus.UInt32(self.notification_id), uri,
            LABELS[resource], "", dbus.Array([], signature="s"), hints,
            dbus.Int32(1500),
        )))
        self.last_resource = resource
        self.last_sent = time.monotonic()


def create_display(app, backend):
    platform = app.platformName()
    if backend == "notifications":
        return Notifications()
    if backend == "x11":
        if platform != "xcb":
            raise RuntimeError("The x11 backend requires an X11 session (Qt xcb platform)")
        return Overlay(app, layer=False)
    if platform == "xcb" and backend == "auto":
        return Overlay(app, layer=False)
    if platform != "wayland":
        raise RuntimeError(f"Unsupported Qt platform: {platform}")
    available, reason = layer_shell_available()
    if available:
        # Only module availability may select the notification adapter. A broken
        # installed overlay must remain a visible error, not be silently ignored.
        engine = QQmlApplicationEngine()
        component = QQmlComponent(engine)
        component.setData(b'import QtQuick; import org.kde.layershell; QtObject {}', QUrl())
        if component.isError():
            available = False
            reason = "; ".join(error.toString() for error in component.errors())
    if available:
        return Overlay(app, layer=True)
    if backend == "layer-shell":
        raise RuntimeError(f"Layer-shell display unavailable: {reason}")
    LOG.info("Using desktop notifications: %s", reason)
    return Notifications()
