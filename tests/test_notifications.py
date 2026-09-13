"""Notification update tests with an isolated in-process bus stub."""
import sys
import time
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QTimer

from display import Notifications


class NotificationUpdates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.calls = []
        self.bus_patch = patch("dbus.SessionBus")
        self.bus = self.bus_patch.start().return_value
        self.addCleanup(self.bus_patch.stop)

        def call(*args, **kwargs):
            if args[3] == "Notify":
                self.calls.append((time.monotonic(), args[5]))
                return 42
            return ("test server", "test", "1", "1.2")

        self.bus.call_blocking.side_effect = call
        self.display = Notifications()
        self.addCleanup(self.display.refresh.stop)

    def test_repeated_state_refreshes_after_server_interval(self):
        errors = []
        self.display.show("CapsLK_ON")
        for _ in range(10):
            self.display.show("CapsLK_ON")
        self.assertEqual(len(self.calls), 1)
        with patch.object(sys, "excepthook", lambda *exc: errors.append(exc)):
            QTimer.singleShot(1200, self.app.quit)
            self.app.exec()
        self.assertFalse(errors)
        self.assertEqual(len(self.calls), 2)
        self.assertGreaterEqual(self.calls[1][0] - self.calls[0][0], 1)
        self.assertEqual(int(self.calls[1][1][1]), 42)

    def test_new_state_cancels_queued_old_state(self):
        self.display.show("CapsLK_ON")
        self.display.show("CapsLK_ON")
        self.assertTrue(self.display.refresh.isActive())
        self.display.show("CapsLK_OFF")
        self.assertFalse(self.display.refresh.isActive())
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.calls[-1][1][3], "Caps Lock off")


if __name__ == "__main__":
    unittest.main()
