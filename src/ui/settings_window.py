import tkinter as tk
from tkinter import ttk
from typing import Callable

from PIL import ImageTk

from src.core.config import Config, config
from src.core.kaiten_api import KaitenAPI
from src.utils.resources import get_resource_path, safe_get_icon


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, on_init_app: Callable, kaiten_api: KaitenAPI):
        super().__init__(parent)
        self.on_init_app = on_init_app
        self.kaiten_api = kaiten_api
        self.user_roles = kaiten_api.get_list_of_user_roles()

        self.title('Настройки')
        self.geometry('400x540')

        window_width = 400
        window_height = 540
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        style = ttk.Style()
        style.configure('Settings.TLabel', padding=5)
        style.configure('Settings.TEntry', padding=5)
        style.configure('Settings.TButton', padding=5)

        token_label = ttk.Label(self, text='Kaiten API токен:', style='Settings.TLabel')
        token_label.pack(padx=5, pady=5)
        self.token_var = tk.StringVar(value=config.kaiten_token)
        token_entry = ttk.Entry(
            self,
            textvariable=self.token_var,
            width=40,
            show='*',
            style='Settings.TEntry',
        )
        token_entry.pack(padx=5, pady=5)
        token_entry.bind('<FocusOut>', self._update_user_roles)

        url_label = ttk.Label(self, text='URL Kaiten:', style='Settings.TLabel')
        url_label.pack(padx=5, pady=5)
        self.url_var = tk.StringVar(value=config.kaiten_url)
        url_entry = ttk.Entry(
            self,
            textvariable=self.url_var,
            width=40,
            style='Settings.TEntry',
        )
        url_entry.pack(padx=5, pady=5)
        url_entry.bind('<FocusOut>', self._update_user_roles)

        repo_label = ttk.Label(self, text='Путь до git репозитория:', style='Settings.TLabel')
        repo_label.pack(padx=5, pady=5)
        self.repo_var = tk.StringVar(value=config.git_repo_path)
        repo_entry = ttk.Entry(
            self,
            textvariable=self.repo_var,
            width=40,
            style='Settings.TEntry',
        )
        repo_entry.pack(padx=5, pady=5)

        role_label = ttk.Label(self, text='Роль пользователя:', style='Settings.TLabel')
        role_label.pack(padx=5, pady=5)

        role_frame = ttk.Frame(self, width=40)
        role_frame.pack(padx=5, pady=5)

        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(
            role_frame,
            textvariable=self.role_var,
            values=sorted(role for role in self.user_roles.values()),
            width=34,
        )
        self.role_combobox.pack(side=tk.LEFT, padx=(0, 2))
        self.role_var.set(self.user_roles.get(config.role_id, ''))

        reload_icon = safe_get_icon(get_resource_path('static\\reload.png'), size=14)
        self.reload_icon = ImageTk.PhotoImage(reload_icon)  # self, чтобы сборщик мусора не стёр иконку

        reload_button = ttk.Button(
            role_frame,
            image=self.reload_icon,
            command=self._update_user_roles,
        )
        reload_button.image = ImageTk.PhotoImage(reload_icon)
        reload_button.pack(side=tk.RIGHT)

        working_time_label = ttk.Label(self, text='Рабочее время (часы):', style='Settings.TLabel')
        working_time_label.pack(padx=5, pady=5)
        self.working_time_var = tk.DoubleVar(value=config.working_time)
        working_hours_entry = ttk.Entry(
            self,
            textvariable=self.working_time_var,
            width=5,
            style='Settings.TEntry',
        )
        working_hours_entry.pack(padx=5, pady=5)

        time_label = ttk.Label(self, text='Время уведомления (HH:MM):', style='Settings.TLabel')
        time_label.pack(padx=5, pady=5)
        self.time_var = tk.StringVar(value=config.notification_time)
        time_entry = ttk.Entry(
            self,
            textvariable=self.time_var,
            width=5,
            style='Settings.TEntry',
        )
        time_entry.pack(padx=5, pady=5)

        save_button = ttk.Button(
            self,
            text='Сохранить',
            command=self.save_settings,
            style='Settings.TButton',
        )
        save_button.pack(padx=5, pady=20)

    def save_settings(self):
        Config.save_config(
            self.token_var.get(),
            self.time_var.get(),
            self.repo_var.get(),
            self.url_var.get(),
            next(role_id for role_id, role_name in self.user_roles.items() if role_name == self.role_var.get()),
            self.working_time_var.get(),
        )
        self.on_init_app()
        self.destroy()

    def _update_user_roles(self, event=None):
        if not (self.token_var.get() and self.url_var.get()):
            return
        kaiten_api = KaitenAPI.from_credentials(token=self.token_var.get(), base_url=self.url_var.get())
        self.user_roles = kaiten_api.get_list_of_user_roles()
        self.role_combobox['values'] = sorted(self.user_roles.values())
        role = self.user_roles.get(config.role_id)
        self.role_var.set(role if role else next(iter(self.role_combobox['values']), ''))
