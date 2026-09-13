#!/usr/bin/env python3
"""Bind only HID_EVENT20 to the read-only transport; restore its previous owner."""
import json
from pathlib import Path
import subprocess
import sys

DRIVER = "mechrevo-osd-wmi"
STATE = Path("/run/mechrevo-osd-binding/previous.json")


def owner(device):
    return (device / "driver").resolve().name if (device / "driver").exists() else None


def restore(state):
    device = Path(state["device"])
    if not device.exists():
        return
    if owner(device) == DRIVER:
        (device / "driver/unbind").write_text(device.name)
    (device / "driver_override").write_text(state["override"] + "\n")
    if state["owner"] and owner(device) is None:
        (Path("/sys/bus/wmi/drivers") / state["owner"] / "bind").write_text(device.name)


def main():
    if sys.argv[1:] == ["restore"]:
        if STATE.exists():
            restore(json.loads(STATE.read_text()))
            STATE.unlink()
        return
    if sys.argv[1:] != ["bind"]:
        raise SystemExit("Usage: bind-events.py bind|restore")
    if Path("/sys/class/dmi/id/board_name").read_text().strip() != "WUJIE Series-T142-HPT-R":
        raise SystemExit("Unsupported board")
    devices = list(Path("/sys/bus/wmi/devices").glob("46C93E13-EE9B-4262-8488-563BCA757FEF-*"))
    if len(devices) != 1:
        raise SystemExit(f"Expected one HID_EVENT20 device, found {len(devices)}")
    device = devices[0]
    if STATE.exists():
        raise SystemExit("A previous binding transaction exists; restore it before rebinding")
    if owner(device) == DRIVER:
        raise SystemExit("Transport already bound outside this service; restore its original owner first")
    override = (device / "driver_override").read_text().strip()
    state = {"device": str(device), "owner": owner(device),
             "override": "" if override == "(null)" else override}
    STATE.write_text(json.dumps(state))
    try:
        (device / "driver_override").write_text(DRIVER + "\n")
        if owner(device):
            (device / "driver/unbind").write_text(device.name)
        subprocess.run(["modprobe", DRIVER], check=True)
        if owner(device) is None:
            (Path("/sys/bus/wmi/drivers") / DRIVER / "bind").write_text(device.name)
        if owner(device) != DRIVER:
            raise RuntimeError("HID_EVENT20 did not bind to the requested transport")
    except BaseException:
        restore(state)
        STATE.unlink()
        raise
    print(f"{device.name}: {state['owner']} -> {DRIVER}; firmware control device unchanged")


if __name__ == "__main__":
    main()
