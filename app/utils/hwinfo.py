import ctypes
import os
import platform
from pathlib import Path
from typing import Any, Dict, List

import psutil


def _get_keyboard_info() -> Dict[str, Any]:
    if os.name != "nt":
        return {"type": None, "subtype": None}

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    keyboard_type = user32.GetKeyboardType(0)
    keyboard_subtype = user32.GetKeyboardType(1)
    return {"type": int(keyboard_type), "subtype": int(keyboard_subtype)}


def _get_screen_height() -> int:
    if os.name != "nt":
        return 0

    SM_CYSCREEN = 1
    user32 = ctypes.windll.user32
    return int(user32.GetSystemMetrics(SM_CYSCREEN))


def _get_disk_devices() -> List[str]:
    devices = set()
    for part in psutil.disk_partitions(all=False):
        if part.device:
            devices.add(part.device)
        elif part.mountpoint:
            devices.add(part.mountpoint)
    return sorted(devices)


def _get_volume_label(target_path: Path) -> str:
    if os.name != "nt":
        return ""

    drive, _ = os.path.splitdrive(str(target_path))
    if not drive:
        drive = os.path.splitdrive(str(target_path.resolve()))[0]
    if not drive.endswith("\\"):
        drive = f"{drive}\\"

    volume_name_buffer = ctypes.create_unicode_buffer(1024)
    file_system_name_buffer = ctypes.create_unicode_buffer(1024)
    serial_number = ctypes.c_uint()
    max_component_length = ctypes.c_uint()
    file_system_flags = ctypes.c_uint()

    result = ctypes.windll.kernel32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive),
        volume_name_buffer,
        ctypes.sizeof(volume_name_buffer),
        ctypes.byref(serial_number),
        ctypes.byref(max_component_length),
        ctypes.byref(file_system_flags),
        file_system_name_buffer,
        ctypes.sizeof(file_system_name_buffer),
    )

    if result == 0:
        return ""

    return volume_name_buffer.value


def gather_hw_info(program_path: Path) -> Dict[str, Any]:
    """
    Собирает требуемые характеристики компьютера для варианта 15.
    """
    program_path = program_path.resolve()

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    computer_name = os.getenv("COMPUTERNAME") or platform.node()
    windir = os.getenv("WINDIR") or os.getenv("SystemRoot") or ""
    system_dir = os.path.join(windir, "System32") if windir else ""

    return {
        "username": username,
        "computer_name": computer_name,
        "windir": windir,
        "system_dir": system_dir,
        "keyboard": _get_keyboard_info(),
        "screen_height": _get_screen_height(),
        "disks": _get_disk_devices(),
        "program_volume_label": _get_volume_label(program_path),
    }
