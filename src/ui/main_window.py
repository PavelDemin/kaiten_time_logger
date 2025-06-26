import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List

import pystray
import schedule
from PIL import Image

from src.core.config import config
from src.core.git_manager import GitManager
from src.core.kaiten_api import KaitenAPI
from src.core.work_calendar import WorkCalendar
from src.ui.components import BranchTimeEntry, ManualTimeEntry, ScrollableFrame
from src.ui.settings_window import SettingsWindow
from src.utils.logger import logger


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


LOGO_PATH = get_resource_path('static\\clock.png')


class Application:
    def __init__(self):
        self.window_visible = False
        self.root = None

        try:
            self.icon_image = Image.open(LOGO_PATH)
        except Exception as e:
            logger.warning(f'Не удалось загрузить иконку: {e}')
            self.icon_image = Image.new('RGB', (70, 70), color='blue')

        self.setup_window()
        self.setup_tray()
        self.setup_scheduler()
        self._init_app()
        self.branch_entries: List[BranchTimeEntry] = []

    def _init_app(self):
        try:
            self.work_calendar = WorkCalendar()
            self.git_manager = GitManager(config.git_repo_path)
            self.kaiten_api = KaitenAPI(config.kaiten_token, config.kaiten_url, config.role_id)
        except Exception as e:
            logger.error(f'Ошибка при инициализации менеджеров: {e}')
            messagebox.showerror('Ошибка', 'Не удалось инициализировать приложение. Проверьте настройки.')
            self.show_settings()

    def _setup_global_paste_shortcut(self):
        def _on_paste(event):
            try:
                content = event.widget.clipboard_get()
                if isinstance(event.widget, (tk.Entry, ttk.Entry, tk.Text)):
                    event.widget.insert(tk.INSERT, content)
                    return 'break'
            except tk.TclError:
                pass
            return None

        for widget_class in ('Entry', 'TEntry', 'Text'):
            self.root.bind_class(widget_class, '<Control-v>', _on_paste)
            self.root.bind_class(widget_class, '<Control-V>', _on_paste)

    def setup_window(self):
        self.root = tk.Tk()
        self._setup_global_paste_shortcut()
        self.root.title('Kaiten Time Logger')
        self.root.geometry('1000x600')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1000
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)

        style = ttk.Style()
        style.configure('Main.TFrame', padding=10)
        style.configure('Main.TButton', padding=5)
        style.configure('Main.TLabel', padding=5)
        try:
            icon_photo = tk.PhotoImage(file=LOGO_PATH)
            self.root.iconphoto(True, icon_photo)
        except Exception as e:
            logger.warning(f'Не удалось установить иконку окна: {e}')

        self.loading_frame = ttk.Frame(self.root)
        self.loading_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        center_frame = ttk.Frame(self.loading_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.spinner = ttk.Progressbar(center_frame, mode='indeterminate', length=300)
        self.spinner.pack(pady=20)

        self.loading_label = ttk.Label(center_frame, text='Загрузка коммитов...', style='Main.TLabel')
        self.loading_label.pack(pady=10)

        self.main_frame = ScrollableFrame(self.root)
        self.manual_entry = ManualTimeEntry(self.main_frame, on_add_entry=self._add_manual_branch_entry)

        self.buttons_frame = ttk.Frame(self.root, style='Main.TFrame')

        settings_button = ttk.Button(
            self.buttons_frame,
            text='Настройки',
            command=self.show_settings,
            style='Main.TButton',
        )
        settings_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(
            self.buttons_frame,
            text='Записать время',
            command=self.save_time_logs,
            style='Main.TButton',
        )
        save_button.pack(side=tk.RIGHT, padx=5)

    def setup_tray(self):
        menu = (
            pystray.MenuItem('Показать', self.show_window),
            pystray.MenuItem('Выход', self.quit_application),
        )
        self.tray_icon = pystray.Icon(
            'kaiten_logger',
            self.icon_image,
            'Kaiten Time Logger',
            menu,
        )

    def setup_scheduler(self):
        schedule.every(30).seconds.do(self.check_notification_time)
        scheduler_thread = threading.Thread(
            target=self.run_scheduler,
            daemon=True,
        )
        scheduler_thread.start()

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            threading.Event().wait(30)

    def _add_manual_branch_entry(self, card_id: int, time_spent: str, description: str):
        entry = BranchTimeEntry(
            self.main_frame,
            branch_name=str(card_id),
            card_id=card_id,
            commits=[description] if description else [],
        )
        entry.time_var.set(time_spent)
        self.branch_entries.append(entry)

    def check_notification_time(self):
        if not self.window_visible and self.work_calendar.should_show_notification(config.notification_time):
            self.show_window()

    def show_window(self):
        if not self.window_visible:
            self.window_visible = True
            self.root.deiconify()
            self.root.lift()

            self.loading_frame.pack(fill=tk.BOTH, expand=True)
            self.main_frame.pack_forget()
            self.buttons_frame.pack_forget()
            self.spinner.start(10)

            def load_commits():
                self.update_branch_entries()
                self.loading_frame.pack_forget()
                self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                self.buttons_frame.pack(fill=tk.X, padx=10, pady=5, side=tk.BOTTOM)
                self.root.focus_force()

            threading.Thread(target=load_commits, daemon=True).start()

    def hide_window(self):
        self.window_visible = False
        self.root.withdraw()

    def show_settings(self):
        SettingsWindow(self.root, self._init_app)

    def update_branch_entries(self):
        for entry in self.branch_entries:
            entry.frame.destroy()
        self.branch_entries.clear()

        try:
            branches_data = self.git_manager.get_branches_with_commits()
            for branch_name, card_id, commits in branches_data:
                entry = BranchTimeEntry(
                    self.main_frame,
                    branch_name,
                    card_id,
                    commits,
                )
                self.branch_entries.append(entry)
            logger.info(f'Найдено {len(self.branch_entries)} веток с коммитами')
        except Exception as e:
            logger.error(f'Ошибка при обновлении списка веток: {e}')
            messagebox.showerror('Ошибка', 'Не удалось получить список коммитов. Проверьте путь к репозиторию.')

    def save_time_logs(self):
        success_count = 0
        error_count = 0

        # Сохраняем записи из веток
        for entry in self.branch_entries:
            card_id, time_spent, description = entry.get_data()
            if time_spent and float(time_spent) > 0:
                try:
                    if self.kaiten_api.add_time_log(card_id, time_spent, description):
                        success_count += 1
                        logger.debug(f'Успешно сохранено время для карточки {card_id}')
                    else:
                        error_count += 1
                        logger.error(f'Не удалось сохранить время для карточки {card_id}')
                except Exception as e:
                    error_count += 1
                    logger.error(f'Ошибка при сохранении времени для карточки {card_id}: {e}')
        if success_count > 0:
            message = f'Время успешно записано для {success_count} задач.'
            if error_count > 0:
                message += f'\nОшибка записи времени для {error_count} задач'
            logger.info(message)
            messagebox.showinfo('Успешно', message)
            self.hide_window()
        else:
            error_message = 'Ошибка записи времени. Проверьте настройки и попробуйте снова'
            logger.error(error_message)
            messagebox.showerror('Ошибка', error_message)

    def quit_application(self):
        self.tray_icon.stop()
        self.root.quit()

    def run(self):
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.hide_window()
        self.root.mainloop()
