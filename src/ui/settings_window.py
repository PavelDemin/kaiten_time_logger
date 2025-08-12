import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from PIL import ImageTk

from src.ai.constants import AiProvider
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
        self.geometry('450x600')

        window_width = 450
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        style = ttk.Style()
        style.configure('Settings.TLabel', padding=5)
        style.configure('Settings.TEntry', padding=5)
        style.configure('Settings.TButton', padding=5)
        style.configure('Settings.TCheckbutton', padding=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Таб основных настроек
        self.basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.basic_frame, text='Основные настройки')

        # Таб AI настроек
        self.ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_frame, text='AI генерация')

        self._create_basic_settings()
        self._create_ai_settings()
        self._create_buttons()

    def _create_basic_settings(self):
        """Создает содержимое таба основных настроек"""

        token_label = ttk.Label(self.basic_frame, text='Kaiten API токен:', style='Settings.TLabel')
        token_label.pack(padx=5, pady=5)
        self.token_var = tk.StringVar(value=config.kaiten_token)
        token_entry = ttk.Entry(
            self.basic_frame,
            textvariable=self.token_var,
            width=45,
            show='*',
            style='Settings.TEntry',
        )
        token_entry.pack(padx=5, pady=5)
        token_entry.bind('<FocusOut>', self._update_user_roles)

        url_label = ttk.Label(self.basic_frame, text='URL Kaiten:', style='Settings.TLabel')
        url_label.pack(padx=5, pady=5)
        self.url_var = tk.StringVar(value=config.kaiten_url)
        url_entry = ttk.Entry(
            self.basic_frame,
            textvariable=self.url_var,
            width=45,
            style='Settings.TEntry',
        )
        url_entry.pack(padx=5, pady=5)
        url_entry.bind('<FocusOut>', self._update_user_roles)

        repo_label = ttk.Label(self.basic_frame, text='Путь до git репозитория:', style='Settings.TLabel')
        repo_label.pack(padx=5, pady=5)
        self.repo_var = tk.StringVar(value=config.git_repo_path)
        repo_entry = ttk.Entry(
            self.basic_frame,
            textvariable=self.repo_var,
            width=45,
            style='Settings.TEntry',
        )
        repo_entry.pack(padx=5, pady=5)

        role_label = ttk.Label(self.basic_frame, text='Роль пользователя:', style='Settings.TLabel')
        role_label.pack(padx=5, pady=5)

        role_frame = ttk.Frame(self.basic_frame)
        role_frame.pack(padx=5, pady=5)

        self.role_var = tk.StringVar()
        self.role_combobox = ttk.Combobox(
            role_frame,
            textvariable=self.role_var,
            values=sorted(role for role in self.user_roles.values()),
            width=39,
        )
        self.role_combobox.pack(side=tk.LEFT, padx=(0, 2))
        self.role_var.set(self.user_roles.get(config.role_id, ''))

        reload_icon = safe_get_icon(get_resource_path('static\\reload.png'), size=14)
        self.reload_icon = ImageTk.PhotoImage(reload_icon)

        reload_button = ttk.Button(
            role_frame,
            image=self.reload_icon,
            command=self._update_user_roles,
        )
        reload_button.image = ImageTk.PhotoImage(reload_icon)
        reload_button.pack(side=tk.RIGHT)

        working_time_label = ttk.Label(self.basic_frame, text='Рабочее время (часы):', style='Settings.TLabel')
        working_time_label.pack(padx=5, pady=5)
        self.working_time_var = tk.DoubleVar(value=config.working_time)
        working_hours_entry = ttk.Entry(
            self.basic_frame,
            textvariable=self.working_time_var,
            width=10,
            style='Settings.TEntry',
        )
        working_hours_entry.pack(padx=5, pady=5)

        time_label = ttk.Label(self.basic_frame, text='Время уведомления (HH:MM):', style='Settings.TLabel')
        time_label.pack(padx=5, pady=5)
        self.time_var = tk.StringVar(value=config.notification_time)
        time_entry = ttk.Entry(
            self.basic_frame,
            textvariable=self.time_var,
            width=10,
            style='Settings.TEntry',
        )
        time_entry.pack(padx=5, pady=5)

    def _create_ai_settings(self):
        """Создает содержимое таба AI настроек"""

        title_label = ttk.Label(
            self.ai_frame, text='Настройки автоматической генерации описания', font=('Segoe UI', 11, 'bold')
        )
        title_label.pack(padx=10, pady=(10, 12))

        provider_row = ttk.Frame(self.ai_frame)
        provider_row.pack(fill='x', padx=10, pady=(0, 8))
        ttk.Label(provider_row, text='Провайдер:', style='Settings.TLabel').pack(side='left')
        self.ai_provider_var = tk.StringVar(value=getattr(config, 'ai_provider', AiProvider.yandex))
        provider_combo = ttk.Combobox(
            provider_row,
            textvariable=self.ai_provider_var,
            values=[member.value for member in AiProvider],
            state='readonly',
            width=12,
        )
        provider_combo.pack(side='left', padx=(8, 0))
        provider_combo.bind('<<ComboboxSelected>>', self._on_ai_provider_change)

        self.ai_enabled_var = tk.BooleanVar(value=config.ai_enabled)
        ai_checkbox = ttk.Checkbutton(
            self.ai_frame,
            text='Включить автоматическую генерацию описания',
            variable=self.ai_enabled_var,
            style='Settings.TCheckbutton',
        )
        ai_checkbox.pack(padx=10, pady=6)

        # Динамический контейнер под поля провайдера
        self.ai_provider_fields = ttk.Frame(self.ai_frame)
        self.ai_provider_fields.pack(fill='x', padx=10, pady=(8, 0))

        # Инициализируем поля для текущего провайдера
        self._render_ai_provider_fields(self.ai_provider_var.get())

        # Справочная информация
        self.ai_help_label = ttk.Label(self.ai_frame, text='', font=('Segoe UI', 8), foreground='blue')
        self.ai_help_label.pack(padx=10, pady=(12, 6))
        self._update_ai_help_text(self.ai_provider_var.get())

    def _on_ai_provider_change(self, event=None):
        provider = self.ai_provider_var.get()
        # Перерисовываем блок с полями под выбранного провайдера
        for child in self.ai_provider_fields.winfo_children():
            child.destroy()
        self._render_ai_provider_fields(provider)
        self._update_ai_help_text(provider)

    def _render_ai_provider_fields(self, provider: str):
        if provider == AiProvider.yandex:
            yandex_key_label = ttk.Label(self.ai_provider_fields, text='Yandex API ключ:', style='Settings.TLabel')
            yandex_key_label.pack(pady=(0, 4), anchor='w')
            self.yandex_api_key_var = tk.StringVar(value=config.ai_api_key)
            yandex_key_entry = ttk.Entry(
                self.ai_provider_fields,
                textvariable=self.yandex_api_key_var,
                width=45,
                show='*',
                style='Settings.TEntry',
            )
            yandex_key_entry.pack(pady=(0, 6))

            folder_id_label = ttk.Label(self.ai_provider_fields, text='Yandex Folder ID:', style='Settings.TLabel')
            folder_id_label.pack(pady=(2, 4), anchor='w')
            self.yandex_folder_id_var = tk.StringVar(value=config.ai_folder_id)
            folder_id_entry = ttk.Entry(
                self.ai_provider_fields,
                textvariable=self.yandex_folder_id_var,
                width=45,
                style='Settings.TEntry',
            )
            folder_id_entry.pack(pady=(0, 6))
        else:
            placeholder = ttk.Label(
                self.ai_provider_fields,
                text='Провайдер еще не настроен.',
                foreground='gray',
            )
            placeholder.pack(anchor='w')

    def _update_ai_help_text(self, provider: str):
        if provider == AiProvider.yandex:
            help_text = (
                'Получить API ключ можно в Yandex Cloud Console: console.cloud.yandex.ru → IAM → Сервисные аккаунты.'
            )
        else:
            help_text = ''
        self.ai_help_label.configure(text=help_text)

    def _create_buttons(self):
        button_frame = ttk.Frame(self)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        save_button = ttk.Button(
            button_frame,
            text='Сохранить',
            command=self.save_settings,
            style='Settings.TButton',
            width=12,
        )
        save_button.pack(side='right')

        cancel_button = ttk.Button(
            button_frame,
            text='Отмена',
            command=self.destroy,
            style='Settings.TButton',
            width=12,
        )
        cancel_button.pack(side='right', padx=(0, 10))

    def save_settings(self):
        validation_errors = []

        token = self.token_var.get().strip()
        if not token:
            validation_errors.append('• Kaiten API токен')

        url = self.url_var.get().strip()
        if not url:
            validation_errors.append('• URL Kaiten')

        repo_path = self.repo_var.get().strip()
        if not repo_path:
            validation_errors.append('• Путь до git репозитория')

        role_name = self.role_var.get().strip()
        if not role_name or role_name not in self.user_roles.values():
            validation_errors.append('• Роль пользователя')

        time_str = self.time_var.get().strip()
        if not self._validate_time_format(time_str):
            validation_errors.append('• Время уведомления (формат HH:MM)')

        try:
            working_time = self.working_time_var.get()
            if working_time <= 0 or working_time > 24:
                validation_errors.append('• Рабочее время (должно быть от 1 до 24 часов)')
        except tk.TclError:
            working_time = 8
            validation_errors.append('• Рабочее время (должно быть числом)')

        ai_provider = getattr(self, 'ai_provider_var', tk.StringVar(value=AiProvider.yandex)).get()
        ai_enabled = getattr(self, 'ai_enabled_var', tk.BooleanVar(value=False)).get()
        ai_api_key = None
        ai_folder_id = None
        if ai_enabled and ai_provider == AiProvider.yandex:
            ai_api_key = getattr(self, 'yandex_api_key_var', tk.StringVar(value='')).get().strip()
            ai_folder_id = getattr(self, 'yandex_folder_id_var', tk.StringVar(value='')).get().strip()
            if not ai_api_key:
                validation_errors.append('• Yandex API ключ (для AI)')
            if not ai_folder_id:
                validation_errors.append('• Yandex Folder ID (для AI)')

        if validation_errors:
            messagebox.showwarning(
                'Ошибка валидации', 'Необходимо заполнить следующие поля:\n\n' + '\n'.join(validation_errors)
            )
            return

        try:
            role_id = next(
                role_id for role_id, role_name in self.user_roles.items() if role_name == self.role_var.get()
            )
            Config.save_config(
                token=token,
                time=time_str,
                repo_path=repo_path,
                kaiten_url=url,
                role_id=role_id,
                working_time=working_time,
                ai_enabled=ai_enabled,
                ai_api_key=ai_api_key,
                ai_folder_id=ai_folder_id,
                ai_provider=ai_provider,
            )
            self.on_init_app()
            self.destroy()
        except StopIteration:
            messagebox.showerror('Ошибка', 'Выбранная роль пользователя недействительна')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Не удалось сохранить настройки: {e}')

    def _validate_time_format(self, time_str: str) -> bool:
        """Валидация формата времени HH:MM"""
        if not time_str:
            return False
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            hours = int(parts[0])
            minutes = int(parts[1])
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except ValueError:
            return False

    def _update_user_roles(self, event=None):
        if not (self.token_var.get() and self.url_var.get()):
            return
        kaiten_api = KaitenAPI.from_credentials(token=self.token_var.get(), base_url=self.url_var.get())
        self.user_roles = kaiten_api.get_list_of_user_roles()
        self.role_combobox['values'] = sorted(self.user_roles.values())
        role = self.user_roles.get(config.role_id)
        self.role_var.set(role if role else next(iter(self.role_combobox['values']), ''))
