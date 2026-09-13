"""Offline checks using recorded firmware packets; no device access or writes."""
import unittest

from events import firmware_resource, lock_resource


class FirmwareEvents(unittest.TestCase):
    def test_recorded_backlight_cycle(self):
        packets = ["0105010000000000", "0105020000000000", "0105030000000000", "0105000000000000"]
        self.assertEqual([firmware_resource(bytes.fromhex(p)) for p in packets], [
            "RGBKeyboardBrightnessLevel_1", "RGBKeyboardBrightnessLevel_2",
            "RGBKeyboardBrightnessLevel_3", "RGBKeyboardBrightnessLevel_0",
        ])

    def test_recorded_profile_changes(self):
        self.assertEqual(firmware_resource(bytes.fromhex("010f010000000000")), "SystemPerfMode_1")
        self.assertEqual(firmware_resource(bytes.fromhex("010f020000000000")), "SystemPerfMode_0")

    def test_unknown_events_do_not_show_status(self):
        for packet in ["000f010000000000", "0205010000000000", "01ff010000000000",
                       "0105040000000000", "010f030000000000", "010a010000000000"]:
            with self.subTest(packet=packet):
                self.assertIsNone(firmware_resource(bytes.fromhex(packet)))

    def test_malformed_packets_fail(self):
        for length in (0, 3, 7, 9, 16):
            with self.subTest(length=length), self.assertRaises(ValueError):
                firmware_resource(bytes(length))

    def test_lock_states_are_not_toggled_internally(self):
        self.assertEqual([lock_resource("capslock", n) for n in (1, 1, 0, 0)],
                         ["CapsLK_ON", "CapsLK_ON", "CapsLK_OFF", "CapsLK_OFF"])
        self.assertEqual(lock_resource("numlock", 0), "NumLK_OFF")
        self.assertEqual(lock_resource("numlock", 1), "NumLK_ON")
        with self.assertRaises(ValueError):
            lock_resource("capslock", 2)


if __name__ == "__main__":
    unittest.main()
