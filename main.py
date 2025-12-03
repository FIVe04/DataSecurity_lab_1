import os
import sys
import winreg
from pathlib import Path

import customtkinter as ctk

from app.crud.user import get_user_by_username, add_user, get_all_users, block_user, restrict_password_user, add_admin
from app.database import get_db
from app.models.user import User
from app.services.crypto import verify_password, get_password_hash
from app.services.signature import verify_hardware_fingerprint
from app.utils.hwinfo import gather_hw_info
from app.state_manager.user import UserState

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

def _no_spaces_callback(new_value):
    if " " in new_value:
        return False
    return True

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_main, switch_to_register, **kwargs):
        super().__init__(master, **kwargs)

        self.validate_no_spaces = self.register(_no_spaces_callback)

        self.label = ctk.CTkLabel(self, text="Login Page")
        self.label.pack(pady=10)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username",
                                           validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*",
                                           validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.password_entry.pack(pady=10)

        self.label_info = ctk.CTkLabel(self, text="")
        self.label_info.pack(pady=0)

        self.login_button = ctk.CTkButton(self, text="Sign In", command=switch_to_main)
        self.login_button.pack(pady=5)

        self.label2 = ctk.CTkLabel(self, text="Don't have an account?")
        self.label2.pack(pady=4)
        self.register_button = ctk.CTkButton(self, text="Sign Up", command=switch_to_register)
        self.register_button.pack(pady=1)


class RegisterFrame(ctk.CTkFrame):
    def __init__(self, master, switch_to_login, register_user_protected, **kwargs):
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(self, text="Sign Up Page")
        self.label.pack(pady=10)

        self.validate_no_spaces = self.register(_no_spaces_callback)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username",
                                           validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*",
                                           validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.password_entry.pack(pady=10)

        self.password_repeat_entry = ctk.CTkEntry(self, placeholder_text="Repeat_password", show="*",
                                                  validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.password_repeat_entry.pack(pady=10)

        self.label_info = ctk.CTkLabel(self, text="")
        self.label_info.pack(pady=0)

        self.login_button = ctk.CTkButton(self, text="Sign Up", command=register_user_protected)
        self.login_button.pack(pady=5)

        self.label2 = ctk.CTkLabel(self, text="Already have an account?")
        self.label2.pack(pady=4)
        self.register_button = ctk.CTkButton(self, text="Sign In", command=switch_to_login)
        self.register_button.pack(pady=1)


import customtkinter as ctk


class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, master, change_password_callback):
        super().__init__(master)
        self.title("Change Password")
        self.geometry("300x250")
        self.resizable(False, False)

        self.change_password_callback = change_password_callback

        self.label = ctk.CTkLabel(self, text="Change password", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=(20, 5))

        self.validate_no_spaces = self.register(_no_spaces_callback)

        self.old_password = ctk.CTkEntry(self, placeholder_text="Enter_old_password", show="*",
                                         validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.old_password.pack(pady=5)

        self.new_password = ctk.CTkEntry(self, placeholder_text="Enter_new_password", show="*",
                                         validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.new_password.pack(pady=5)

        self.new_password_repeat = ctk.CTkEntry(self, placeholder_text="Repeat_new_password", show="*",
                                                validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        self.new_password_repeat.pack(pady=5)

        self.label_info = ctk.CTkLabel(self, text="")
        self.label_info.pack(pady=5)

        self.change_password_button = ctk.CTkButton(
            self, text="Change password", command=self.on_change_password
        )
        self.change_password_button.pack(pady=10)

    def on_change_password(self):
        old_pwd = self.old_password.get()
        new_pwd = self.new_password.get()
        new_pwd_repeat = self.new_password_repeat.get()

        if new_pwd != new_pwd_repeat:
            self.label_info.configure(text="Passwords do not match!", text_color="red")
            return

        response = self.change_password_callback()

        if response:
            self.label_info.configure(text="Password changed successfully!")
            self.destroy()
        else:
            return


class UserMainFrame(ctk.CTkFrame):
    def __init__(self, master, logout, change_password_callback, **kwargs):
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(self, text="User Page", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=10)



        self.change_password_button = ctk.CTkButton(
            self, text="Change password",
            command=self.open_change_password
        )
        self.change_password_button.pack(pady=20)

        self.logout_button = ctk.CTkButton(self, text="Logout", command=logout)
        self.logout_button.pack(pady=30)

        self.about_button = ctk.CTkButton(self, text="About", command=self.open_about_dialog)
        self.about_button.pack(pady=5)

        self.dialog = None
        self.change_password_callback = change_password_callback

    def open_about_dialog(self):
        AboutDialog(self)

    def open_change_password(self):
        self.dialog = ChangePasswordDialog(self, self.change_password_callback)

class AboutDialog(ctk.CTkToplevel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title("О программе")
        self.geometry("300x200")
        self.resizable(False, False)

        # Делаем окно модальным
        self.grab_set()

        label = ctk.CTkLabel(
            self,
            text="Выполнил:\nФролов Иван\nСтудент группы А-05-22\nПрограмма: Лабораторная 4",
            justify="center"
        )
        label.pack(pady=20, padx=10)

        close_button = ctk.CTkButton(self, text="Закрыть", command=self.destroy)
        close_button.pack(pady=10)

class AdminMainFrame(ctk.CTkFrame):
    def __init__(self, master, logout, change_password, **kwargs):
        super().__init__(master, **kwargs)

        self.label = ctk.CTkLabel(self, text="Admin Page")
        self.label.pack(pady=10)

        self.change_password_button = ctk.CTkButton(
            self, text="Change password",
            command=self.open_change_password
        )
        self.change_password_button.pack(pady=20)

        self.manage_users_button = ctk.CTkButton(self, text="User management", command=self.open_users_dialog)
        self.manage_users_button.pack(pady=5)


        self.logout_button = ctk.CTkButton(self, text="Logout", command=logout)
        self.logout_button.pack(pady=5)

        self.about_button = ctk.CTkButton(self, text="About", command=self.open_about_dialog)
        self.about_button.pack(pady=5)

        self.users = []

        self.scroll_frame = None
        self.users_dialog = None

        self.dialog = None

        self.change_password_callback = change_password

    def open_about_dialog(self):
        AboutDialog(self)

    def open_change_password(self):
        self.dialog = ChangePasswordDialog(self, self.change_password_callback)

    def refresh_user_table(self):
        with get_db() as db:
            db_users = get_all_users(db)
            self.users = [{"id": user.id, "username": user.username, "role": user.role,
                           'blocked': user.is_locked, 'restricted': user.password_restrictions_enabled}
                          for user in db_users]

    def draw_user_table(self):
        self.refresh_user_table()

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.scroll_frame)
        header.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(header, text='username', width=120, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text='role', width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text='blocked', width=100, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text='restricted', width=120, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)

        # строки пользователей
        for u in self.users:
            if u['role'] == "admin":
                continue

            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=5, padx=5)

            ctk.CTkLabel(row, text=u["username"], width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=u["role"], width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(u['blocked']), width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(u['restricted']), width=120, anchor="w").pack(side="left", padx=5)

            ctk.CTkButton(row, text='Unlock' if u['blocked'] else 'Lock', width=100,
                          command=lambda usr=u: self.block_user(usr)).pack(side="left", padx=5)
            ctk.CTkButton(row, text='Disable restriction' if u['restricted'] else 'Restrict', width=150,
                          command=lambda usr=u: self.limit_user(usr)).pack(side="left", padx=5)

    def open_users_dialog(self):
        if self.users_dialog and self.users_dialog.winfo_exists():
            self.users_dialog.focus()
            return

        self.users_dialog = ctk.CTkToplevel(self)
        self.users_dialog.title("User management")
        self.users_dialog.geometry("900x700")

        self.scroll_frame = ctk.CTkScrollableFrame(self.users_dialog, width=880, height=600)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.draw_user_table()

        add_button = ctk.CTkButton(
            self.users_dialog, text="Add user", command=self.add_user
        )
        add_button.pack(pady=10)

    def block_user(self, user):
        with get_db() as db:
            block_user(db, user['id'])
        self.refresh_user_table()
        self.draw_user_table()

    def limit_user(self, user):
        with get_db() as db:
            restrict_password_user(db, user['id'])
        self.refresh_user_table()
        self.draw_user_table()

    def add_user(self):
        add_window = ctk.CTkToplevel(self)
        add_window.title("Add user")
        add_window.geometry("400x250")
        add_window.grab_set()

        lbl_name = ctk.CTkLabel(add_window, text="Username: ")
        lbl_name.pack(pady=(15, 5))

        self.validate_no_spaces = self.register(_no_spaces_callback)

        entry_name = ctk.CTkEntry(add_window, width=250, placeholder_text="Username",
                                  validate="key", validatecommand=(self.validate_no_spaces, "%P"))
        entry_name.pack(pady=5)

        chk_block_var = ctk.BooleanVar()
        chk_block = ctk.CTkCheckBox(add_window, text="Lock?", variable=chk_block_var)
        chk_block.pack(pady=5)

        chk_limit_var = ctk.BooleanVar(value=True)
        chk_limit = ctk.CTkCheckBox(add_window, text="Enable password restrictions?",
                                    variable=chk_limit_var)
        chk_limit.pack(pady=5)

        self.info_label = ctk.CTkLabel(add_window, text="")
        self.info_label.pack(pady=(15, 5))


        btn_frame = ctk.CTkFrame(add_window)
        btn_frame.pack(pady=15)


        def save_user():
            username = entry_name.get()
            blocked = chk_block_var.get()
            password_limit = chk_limit_var.get()

            response = userState.add_user_from_admin(username.lower(), blocked, password_limit)
            if response['message'] == 'OK':
                self.refresh_user_table()
                self.draw_user_table()
                add_window.destroy()
            else:
                self.info_label.configure(text=response['message'])

        btn_save = ctk.CTkButton(btn_frame, text="Save", command=save_user)
        btn_save.pack(side="left", padx=10)

        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray",
                                   hover_color="darkgray", command=add_window.destroy)
        btn_cancel.pack(side="left", padx=10)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            with get_db() as db:
                add_admin(db)
        except Exception as e:
            print(e)

        self.title("Lab_1")
        self.geometry("600x400")

        self.login_frame = LoginFrame(self, self.login_protected, self.show_register)
        self.register_frame = RegisterFrame(self, self.show_login, self.register_user_protected)
        self.main_frame = None
        self.show_login()

    def creat_main_frame(self):
        if self.main_frame:
            self.main_frame.destroy()

        if userState.is_admin:
            self.main_frame = AdminMainFrame(self, self.logout, self.change_password)
        else:
            self.main_frame = UserMainFrame(self, self.logout, self.change_password)

    def logout(self):
        userState.logout()
        self.clear_frames()
        self.login_frame.pack(fill="both", expand=True)
        return

    def change_password(self):
        old_password = self.main_frame.dialog.old_password.get()
        new_password = self.main_frame.dialog.new_password.get()
        new_password_repeat = self.main_frame.dialog.new_password_repeat.get()

        if not old_password:
            self.main_frame.dialog.label_info.configure(text="Old password is mandatory")
            return

        if not new_password:
            self.main_frame.dialog.label_info.configure(text="New password is mandatory")
            return

        if not new_password_repeat:
            self.main_frame.dialog.label_info.configure(text="Repeat new password is mandatory")
            return

        if new_password_repeat == old_password:
            self.main_frame.dialog.label_info.configure(text="New password and repeat new password should be equal")
            return

        if new_password == old_password:
            self.main_frame.dialog.label_info.configure(text="Old and new password should not be equal")
            return

        response = userState.change_password(old_password, new_password)

        if response['message'] == 'OK':
            self.main_frame.dialog.label_info.configure(text="Successfully changed password!")
            return True

        self.main_frame.dialog.label_info.configure(text=response['message'])
        return

    def register_user_protected(self):
        username = self.register_frame.username_entry.get()
        password = self.register_frame.password_entry.get()
        repeat_password = self.register_frame.password_repeat_entry.get()

        if not username:
            self.register_frame.label_info.configure(text="Username is mandatory!")
            return

        if not password:
            self.register_frame.label_info.configure(text="Password is mandatory!")
            return

        if not repeat_password:
            self.register_frame.label_info.configure(text="Repeat password is mandatory!")
            return

        if password != repeat_password:
            print('2')
            self.register_frame.label_info.configure(text="New password and repeat new password should be equal")
            return

        response = userState.register(username.lower(), password)

        if response['message'] == 'OK':
            self.register_frame.username_entry.delete(0, "end")
            self.register_frame.password_entry.delete(0, "end")
            self.register_frame.password_repeat_entry.delete(0, "end")
            self.creat_main_frame()
            self.show_main()
            return

        self.register_frame.label_info.configure(text=response['message'])
        return

    def clear_frames(self):
        for frame in (self.login_frame, self.register_frame, self.main_frame):
            if frame is not None:
                frame.pack_forget()

    def show_login(self):
        self.clear_frames()
        self.login_frame.pack(fill="both", expand=True)

    def show_register(self):
        self.clear_frames()
        self.register_frame.pack(fill="both", expand=True)

    def login_protected(self):
        username = self.login_frame.username_entry.get()
        password = self.login_frame.password_entry.get()

        if not username:
            self.login_frame.label_info.configure(text="Username is mandatory!")
            return

        if not password:
            self.login_frame.label_info.configure(text="Password is mandatory!")
            return

        response = userState.login(username.lower(), password)

        if response['message'] == 'You have exceeded maximum login attempts':
            self.destroy()
            sys.exit()

        if response['message'] == 'OK':
            self.login_frame.username_entry.delete(0, "end")
            self.login_frame.password_entry.delete(0, "end")
            self.creat_main_frame()
            self.show_main()
            return

        self.login_frame.label_info.configure(text=response['message'])
        return

    def show_main(self):
        self.clear_frames()
        self.main_frame.pack(fill="both", expand=True)


def perform_license_check():
    import tkinter.simpledialog as sd
    import tkinter.messagebox as mb

    registry_name = sd.askstring("Проверка подписи", "Введите фамилию (имя раздела реестра):")
    if not registry_name:
        mb.showerror("Ошибка", "Имя раздела реестра не указано.")
        sys.exit()

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, fr"Software\{registry_name}") as reg_key:
            signature, _ = winreg.QueryValueEx(reg_key, "Signature")
    except FileNotFoundError:
        mb.showerror("Ошибка", f"Ветка Software\\{registry_name} или значение Signature не найдены.")
        sys.exit()
    except OSError as exc:
        mb.showerror("Ошибка", f"Не удалось прочитать реестр: {exc}")
        sys.exit()

    program_path = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    hw_info = gather_hw_info(program_path)

    public_key_path = program_path.parent / "public_key.pem"
    if not public_key_path.exists():
        mb.showerror("Ошибка", f"Не найден публичный ключ: {public_key_path}")
        sys.exit()

    try:
        public_key_pem = public_key_path.read_bytes()
    except OSError as exc:
        mb.showerror("Ошибка", f"Не удалось прочитать публичный ключ: {exc}")
        sys.exit()

    if not verify_hardware_fingerprint(public_key_pem, hw_info, signature):
        mb.showerror("Ошибка", "Проверка подписи не пройдена.")
        sys.exit()


if __name__ == "__main__":
    import tkinter.simpledialog as sd
    import tkinter.messagebox as mb

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()

    if os.name != "nt":
        mb.showerror("Ошибка", "Проверка подписи доступна только на Windows.")
        sys.exit()

    perform_license_check()
    passphrase = sd.askstring("Парольная фраза", "Введите пароль:", show="*")
    if not passphrase:
        mb.showerror("Ошибка", "Пароль не введён!")
        sys.exit()

    try:
        from app.database import init_encrypted_db
        init_encrypted_db(passphrase)
    except Exception as e:
        mb.showerror("Ошибка", 'Неверная парольная фраза!')
        sys.exit()

    userState = UserState()
    app = App()

    def on_close():
        from app.database import save_encrypted_db
        save_encrypted_db(passphrase)
        app.destroy()
        sys.exit()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()
