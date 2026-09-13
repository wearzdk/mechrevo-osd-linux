"""Decode firmware status packets without controlling the device."""

LABELS = {
    "CapsLK_ON": "Caps Lock on", "CapsLK_OFF": "Caps Lock off",
    "NumLK_ON": "Num Lock on", "NumLK_OFF": "Num Lock off",
    "Fn_ON": "Fn Lock on", "Fn_OFF": "Fn Lock off",
    "TouchPad_ON": "Touchpad on", "TouchPad_OFF": "Touchpad off",
    "SystemPerfMode_0": "Quiet mode",
    "SystemPerfMode_1": "Balanced mode",
    "SystemPerfMode_2": "Performance mode",
    **{f"RGBKeyboardBrightnessLevel_{n}": f"Keyboard backlight: {n}/3" for n in range(4)},
}


def firmware_resource(packet):
    if len(packet) != 8:
        raise ValueError("Firmware status packet must contain 8 bytes")
    kind, event, value = packet[:3]
    if kind != 1:
        return None
    if event == 5 and value <= 3:
        return f"RGBKeyboardBrightnessLevel_{value}"
    if event == 6:
        return "TouchPad_OFF" if value == 1 else "TouchPad_ON"
    if event == 7:
        return "Fn_ON" if value == 1 else "Fn_OFF"
    if event == 15:
        return {0: "SystemPerfMode_2", 1: "SystemPerfMode_1", 2: "SystemPerfMode_0"}.get(value)
    return None


def lock_resource(name, state):
    if state not in (0, 1):
        raise ValueError(f"Invalid lock state: {state}")
    prefix = {"capslock": "CapsLK", "numlock": "NumLK"}[name]
    return f"{prefix}_{'ON' if state else 'OFF'}"
