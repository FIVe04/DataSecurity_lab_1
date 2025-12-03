import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import winreg
from Crypto.PublicKey import RSA

from app.services.signature import sign_hardware_fingerprint
from app.utils.hwinfo import gather_hw_info

if getattr(sys, "frozen", False):
    RUN_DIR = Path(sys.executable).resolve().parent
else:
    RUN_DIR = Path(__file__).resolve().parent


def locate_source_exe() -> Path:
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", RUN_DIR))
        candidates.append(meipass / "payload" / "main.exe")
        candidates.append(meipass / "main.exe")

    candidates.append(RUN_DIR / "main.exe")
    candidates.append(RUN_DIR / "dist" / "main.exe")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("Не удалось найти main.exe. Убедитесь, что он добавлен как ресурс.")


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Инсталлятор (ЛР6)")
        self.geometry("480x240")
        self.resizable(False, False)

        try:
            self.source_exe = locate_source_exe()
        except FileNotFoundError:
            self.source_exe = None

        default_install = Path.home() / "Lab6App"
        self.folder_var = tk.StringVar(value=str(default_install))
        self.registry_var = tk.StringVar()
        self.program_var = tk.StringVar(value="main.exe")

        self._build_ui()

    def _build_ui(self):
        padding = {"padx": 10, "pady": 5}

        btn_choose = tk.Button(self, text="Выбрать папку", command=self.choose_folder)
        btn_choose.grid(row=0, column=0, sticky="w", **padding)

        tk.Entry(self, textvariable=self.folder_var, width=50).grid(row=0, column=1, **padding)

        tk.Label(self, text="Имя раздела реестра (фамилия):").grid(row=1, column=0, sticky="w", **padding)
        tk.Entry(self, textvariable=self.registry_var, width=30).grid(row=1, column=1, sticky="w", **padding)

        tk.Label(self, text="Имя программы:").grid(row=2, column=0, sticky="w", **padding)
        tk.Entry(self, textvariable=self.program_var, width=30).grid(row=2, column=1, sticky="w", **padding)

        install_btn = tk.Button(self, text="Установить программу", command=self.install_program)
        install_btn.grid(row=3, column=0, columnspan=2, pady=15)

    def choose_folder(self):
        selected = filedialog.askdirectory()
        if selected:
            self.folder_var.set(selected)

    def install_program(self):
        target_folder = Path(self.folder_var.get()).expanduser()
        registry_name = self.registry_var.get().strip()
        program_name = self.program_var.get().strip()

        if not registry_name:
            messagebox.showerror("Ошибка", "Укажите имя раздела реестра (фамилию).")
            return

        if not program_name:
            messagebox.showerror("Ошибка", "Укажите имя программы (например, main.exe).")
            return

        if not program_name.lower().endswith(".exe"):
            program_name = f"{program_name}.exe"

        source_exe = self.source_exe
        if source_exe is None or not source_exe.exists():
            try:
                source_exe = locate_source_exe()
                self.source_exe = source_exe
            except FileNotFoundError as exc:
                messagebox.showerror("Ошибка", str(exc))
                return

        target_folder.mkdir(parents=True, exist_ok=True)
        destination = target_folder / program_name

        try:
            shutil.copy2(source_exe, destination)
        except OSError as exc:
            messagebox.showerror("Ошибка копирования", str(exc))
            return

        try:
            keys = RSA.generate(2048)
            private_pem = keys.export_key("PEM")
            public_pem = keys.publickey().export_key("PEM")

            public_key_path = destination.parent / "public_key.pem"
            public_key_path.write_bytes(public_pem)

            hw_info = gather_hw_info(destination)
            signature = sign_hardware_fingerprint(private_pem, hw_info)
        except Exception as exc:
            messagebox.showerror("Ошибка формирования подписи", str(exc))
            destination.unlink(missing_ok=True)
            return

        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"Software\{registry_name}") as reg_key:
                winreg.SetValueEx(reg_key, "Signature", 0, winreg.REG_BINARY, signature)
                winreg.SetValueEx(reg_key, "ProgramPath", 0, winreg.REG_SZ, str(destination))
        except OSError as exc:
            messagebox.showerror("Ошибка записи в реестр", str(exc))
            destination.unlink(missing_ok=True)
            return

        messagebox.showinfo(
            "Готово",
            f"Программа скопирована в {destination}\nПодпись сохранена в HKCU\\Software\\{registry_name}",
        )


if __name__ == "__main__":
    if os.name != "nt":
        print("Установщик предназначен для Windows.", file=sys.stderr)
        sys.exit(1)

    app = InstallerApp()
    app.mainloop()
