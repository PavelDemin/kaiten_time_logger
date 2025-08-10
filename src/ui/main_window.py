import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Tuple

import pystray
import schedule

from src.ai.summary_generator import SummaryGenerator
from src.core.config import config
from src.core.git_manager import GitManager
from src.core.kaiten_api import KaitenAPI
from src.core.work_calendar import WorkCalendar
from src.ui.components import BranchTimeEntry, LoadingOverlay, ManualTimeEntry, ScrollableFrame
from src.ui.settings_window import SettingsWindow
from src.utils.logger import logger
from src.utils.resources import get_resource_path, safe_get_icon

LOGO_PATH = get_resource_path('static\\clock.png')


class Application:
    def __init__(self):
        self.window_visible = False
        self.root = None
        self.icon_image = safe_get_icon(LOGO_PATH, size=70)
        self.summary_generator = SummaryGenerator()
        self.setup_window()
        self.setup_tray()
        self.setup_scheduler()
        self._init_app()
        self.branch_entries: List[BranchTimeEntry] = []
        self._check_config()

    def _check_config(self):
        if not config.is_configured():
            result = messagebox.askokcancel(
                'Инициализация приложения',
                'Для работы приложения необходимо настроить:\n'
                '• Токен Kaiten API\n'
                '• URL сервера Kaiten\n'
                '• Путь к Git репозиторию\n'
                '• Роль пользователя\n\n'
                'Открыть окно настроек?',
                icon='question',
            )
            if result:
                self.show_settings()

    def _init_app(self):
        try:
            self.work_calendar = WorkCalendar()
            self.git_manager = GitManager(config.git_repo_path)
            self.kaiten_api = KaitenAPI.from_credentials(config.kaiten_token, config.kaiten_url, config.role_id)
            self.summary_generator.reinitialize()

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
            self.root.bind_class(
                widget_class, '<Control-KeyPress>', lambda e: _on_paste(e) if e.keycode == 86 else None
            )

    def setup_window(self):
        self.root = tk.Tk()
        self._setup_global_paste_shortcut()
        self.root.title('Kaiten Time Logger')

        window_width = 1000
        window_height = 800

        self.root.geometry(f'{window_width}x{window_height}')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
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

        # Универсальный оверлей загрузки
        self.loading_container = ttk.Frame(self.root)
        self.loading_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.loading_overlay = LoadingOverlay(self.loading_container, text='Загрузка коммитов...')

        self.main_frame = ScrollableFrame(self.root)
        self.manual_entry = ManualTimeEntry(
            self.main_frame, on_add_entry=self._add_manual_branch_entry, on_time_change=self._update_total_time
        )

        self.buttons_frame = ttk.Frame(self.root, style='Main.TFrame')

        settings_button = ttk.Button(
            self.buttons_frame,
            text='Настройки',
            command=self.show_settings,
            style='Main.TButton',
        )
        settings_button.pack(side=tk.LEFT, padx=5)

        # Добавляем отображение общего времени
        self.total_time_label = ttk.Label(
            self.buttons_frame, text='Общее время: 0ч 0м', font=('Segoe UI', 10, 'bold'), foreground='black'
        )
        self.total_time_label.pack(side=tk.LEFT, padx=10)

        save_button = ttk.Button(
            self.buttons_frame,
            text='Записать время',
            command=self.save_time_logs,
            style='Main.TButton',
        )
        save_button.pack(side=tk.RIGHT, padx=5)

    def setup_tray(self):
        menu = (
            pystray.MenuItem('Учет времени', self.show_window),
            pystray.MenuItem('Настройки', self.show_settings),
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
            on_time_change=self._update_total_time,
        )
        entry.time_var.set(time_spent)
        self.branch_entries.append(entry)
        self._update_total_time()

    def _update_total_time(self):
        total_minutes = 0
        for entry in self.branch_entries:
            total_minutes += entry.get_time_minutes()
        total_minutes += self.manual_entry.get_time_minutes()
        hours = total_minutes // 60
        minutes = total_minutes % 60
        time_text = f'Общее время: {hours}ч {minutes}м'
        working_minutes = int(config.working_time * 60)
        if total_minutes == working_minutes:
            color = 'green'
        elif total_minutes < working_minutes or total_minutes > working_minutes:
            color = 'red'
        else:
            color = 'black'
        self.total_time_label.configure(text=time_text, foreground=color)

    def check_notification_time(self):
        if not self.window_visible and self.work_calendar.should_show_notification(config.notification_time):
            self.show_window()

    def _load_commits(self) -> List[Tuple[str, int, List[str]]]:
        self.loading_overlay.show('Загрузка коммитов...')
        try:
            branches_data = self.git_manager.get_branches_with_commits()
        except Exception as e:
            logger.error(f'Ошибка при получении коммитов: {e}')

            def on_error():
                self.loading_overlay.hide()
                self.loading_container.pack_forget()
                messagebox.showerror('Ошибка', 'Не удалось получить список коммитов. Проверьте путь к репозиторию.')

            self.root.after(0, on_error)
            branches_data = []
        return branches_data

    def _render(self, branches_data, summaries):
        # Скрываем загрузку, показываем основной UI и строим записи
        self.loading_overlay.hide()
        self.loading_container.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.buttons_frame.pack(fill=tk.X, padx=10, pady=5, side=tk.BOTTOM)
        self._update_entries_with_data(branches_data, summaries)
        self.root.focus_force()

    def show_window(self):
        if not self.window_visible:
            self.window_visible = True
            self.root.deiconify()
            self.root.lift()

            self.loading_container.pack(fill=tk.BOTH, expand=True)
            self.main_frame.pack_forget()
            self.buttons_frame.pack_forget()
            branches_data = self._load_commits()
            summaries = self._generate_ai_summary(branches_data)
            self.root.after(0, lambda: self._render(branches_data, summaries))

    def _generate_ai_summary(self, branches_data: List[Tuple[str, int, List[str]]]) -> dict[tuple, str]:
        # Если включен AI — сначала генерируем описания, потом рисуем форму
        summaries = {}
        try:
            if self.summary_generator.is_available:
                total = len(branches_data)
                for idx, (branch_name, card_id, commits) in enumerate(branches_data, start=1):
                    self.root.after(0, self.loading_overlay.update_text, f'Генерация описаний {idx}/{total}...')
                    try:
                        summary = self.summary_generator.generate_task_summary(commits)
                    except Exception as e:
                        logger.error(f'Ошибка генерации описания для {branch_name}: {e}')
                        summary = None
                    summaries[(branch_name, card_id)] = summary
        except Exception as ai_err:
            logger.error(f'Ошибка процесса AI генерации: {ai_err}')
        return summaries

    def hide_window(self):
        self.window_visible = False
        self.root.withdraw()

    def show_settings(self):
        SettingsWindow(self.root, self._init_app, self.kaiten_api)

    def _update_entries_with_data(self, branches_data, summaries: dict | None = None):
        for entry in self.branch_entries:
            entry.frame.destroy()
        self.branch_entries.clear()

        for branch_name, card_id, commits in branches_data:
            summary_text = None
            if summaries:
                summary_text = summaries.get((branch_name, card_id))
            entry = BranchTimeEntry(
                self.main_frame,
                branch_name,
                card_id,
                commits,
                on_time_change=self._update_total_time,
                summary_text=summary_text if summary_text else None,
            )
            self.branch_entries.append(entry)
        logger.info(f'Найдено {len(self.branch_entries)} веток с коммитами')
        self._update_total_time()

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
