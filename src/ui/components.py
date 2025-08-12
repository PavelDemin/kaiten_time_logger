import re
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import Callable, List, Optional, Tuple

from src.core.config import config

CARD_ID_REGEX = re.compile(r'card/(\d+)|kaiten\.ru/(\d{6,})\b|^(\d{6,})$')


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.scrollable_frame.columnconfigure(0, weight=1)

        self.canvas_frame = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor='nw',
            width=self.canvas.winfo_width(),
        )

        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.bind_mouse_wheel()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def bind_mouse_wheel(self):
        """Привязка колесика мыши к прокрутке."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(-1 * (event.delta // 120), 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mousewheel)


class LoadingOverlay(ttk.Frame):
    """Фрейм загрузки"""

    def __init__(self, parent, text: str = 'Загрузка...', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(style='Main.TFrame')

        self.place(relx=0.5, rely=0.5, anchor='center')
        inner = ttk.Frame(self)
        inner.pack()

        self.progress = ttk.Progressbar(inner, mode='indeterminate', length=280)
        self.progress.pack(pady=10)

        self.label_var = tk.StringVar(value=text)
        self.label = ttk.Label(inner, textvariable=self.label_var, style='Main.TLabel')
        self.label.pack(pady=5)

        self.hide()

    def show(self, text: str | None = None):
        if text is not None:
            self.label_var.set(text)
        self.lift()
        self.place_configure(relx=0.5, rely=0.5, anchor='center')
        self.progress.start(10)
        self.update_idletasks()

    def hide(self):
        try:
            self.progress.stop()
        except Exception:
            pass
        self.place_forget()

    def update_text(self, text: str):
        self.label_var.set(text)
        self.update_idletasks()


class BranchTimeEntry(ttk.Frame):
    """Виджет для ввода времени, потраченного на работу в ветке."""

    def __init__(
        self,
        parent: ScrollableFrame,
        branch_name: str,
        card_id: int,
        commits: List[str],
        on_time_change: Callable = None,
        summary_text: Optional[str] = None,
    ):
        self.card_id = card_id
        self.on_time_change = on_time_change
        super().__init__()

        self.frame = tk.Frame(
            parent.scrollable_frame,
            borderwidth=1,
            relief='solid',
            bg='#ffffff',
        )
        self.frame.pack(fill=tk.X, padx=10, pady=7, ipady=10)
        self.frame.columnconfigure(0, weight=1)

        info_frame = ttk.Frame(self.frame)
        info_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=(10, 5))
        info_frame.columnconfigure(1, weight=1)

        branch_label = ttk.Label(info_frame, text=f'🔀 {branch_name}', font=('Segoe UI', 11, 'bold'))
        branch_label.grid(row=0, column=0, sticky='w')

        ttk.Label(info_frame).grid(row=0, column=1, sticky='ew')

        card_frame = ttk.Frame(info_frame)
        card_frame.grid(row=0, column=2, sticky='e')

        card_label = tk.Label(
            card_frame,
            text=f'#{self.card_id}',
            font=('Segoe UI', 10),
            fg='#0066cc',
            cursor='hand2',
        )
        card_label.pack()

        def open_card(event):
            webbrowser.open(f'{config.kaiten_url}/{self.card_id}')

        card_label.bind('<Button-1>', open_card)

        def on_enter(event):
            card_label.configure(fg='#003366')

        def on_leave(event):
            card_label.configure(fg='#0066cc')

        card_label.bind('<Enter>', on_enter)
        card_label.bind('<Leave>', on_leave)

        commits_frame = ttk.Frame(self.frame)
        commits_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(5, 10))
        commits_frame.columnconfigure(0, weight=1)

        self.commits_text = tk.Text(
            commits_frame,
            height=max(len(commits) + 1, 3),
            wrap=tk.WORD,
            font=('Consolas', 9),
            borderwidth=1,
            relief='solid',
            padx=8,
            pady=8,
        )
        self.commits_text.grid(row=0, column=0, sticky='ew')
        scrollbar = tk.Scrollbar(commits_frame, orient='vertical', command=self.commits_text.yview)
        self.commits_text.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        if summary_text is not None and summary_text.strip():
            self.commits_text.insert(tk.END, f'{summary_text.strip()}\n')
        else:
            for message in commits:
                self.commits_text.insert(tk.END, f'{message}\n')

        time_frame = ttk.Frame(self.frame)
        time_frame.grid(row=2, column=0, sticky='w', padx=15, pady=(0, 10))

        time_label = ttk.Label(time_frame, text='⏱️ Время:', font=('Segoe UI', 10))
        time_label.pack(side=tk.LEFT)

        self.time_var = tk.StringVar()
        self.time_var.trace('w', self._on_time_change)
        time_entry = ttk.Entry(time_frame, textvariable=self.time_var, width=10, font=('Segoe UI', 10))
        time_entry.pack(side=tk.LEFT, padx=5)

    def _on_time_change(self, *args):
        if self.on_time_change:
            self.on_time_change()

    def get_data(self) -> Tuple[int, int, str]:
        hours, minutes = self._prepare_time(self.time_var.get())
        total_minutes = hours * 60 + minutes
        return self.card_id, total_minutes, self.commits_text.get('1.0', tk.END).strip()

    def get_time_minutes(self) -> int:
        hours, minutes = self._prepare_time(self.time_var.get())
        return hours * 60 + minutes

    @staticmethod
    def _prepare_time(time_spent: str) -> tuple[int, int]:
        try:
            if time_spent.isdigit():
                return int(time_spent), 0
            hours, minutes = BranchTimeEntry.parse_time(time_spent)
            return hours, minutes
        except (ValueError, AttributeError):
            return 0, 0

    @staticmethod
    def parse_time(time_str: str) -> Tuple[int, int]:
        """Парсит строку времени в часы и минуты.

        Поддерживаемые форматы:
        - 13:30 (часы:минуты)
        - 1h30m, 1ч30м (часы и минуты без пробелов)
        - 1h 30m, 1ч 30м (часы и минуты с пробелами)
        - 1h, 1ч (только часы)
        - 30m, 30м (только минуты)
        - 1.5h, 1.5ч (десятичные часы)
        - 90m, 90м (минуты больше 60)
        - 5 (целое число как часы)
        """
        import re

        if not time_str or not time_str.strip():
            return 0, 0

        time_str = time_str.strip()
        hours = 0
        minutes = 0

        patterns = [
            # 13:30, 1:0, 0:5
            r'^(\d{1,2}):(\d{1,2})$',
            # 1h30m, 1ч30м
            r'^(\d+(?:\.\d+)?)[hч](\d+)[mм]$',
            # 1h 30m, 1ч 30м
            r'^(\d+(?:\.\d+)?)[hч]\s+(\d+)[mм]$',
            # 1h, 1ч
            r'^(\d+(?:\.\d+)?)[hч]$',
            # 30m, 30м
            r'^(\d+)[mм]$',
            # 5 (целое число как часы)
            r'^(\d+)$',
        ]

        for pattern in patterns:
            match = re.match(pattern, time_str)
            if match:
                groups = match.groups()

                if len(groups) == 2:
                    if ':' in time_str:
                        hours = int(groups[0])
                        minutes = int(groups[1])
                    else:
                        hours = float(groups[0])
                        minutes = int(groups[1])

                        if hours != int(hours):
                            total_minutes = int(hours * 60)
                            hours = total_minutes // 60
                            minutes += total_minutes % 60
                        else:
                            hours = int(hours)

                elif len(groups) == 1:
                    value = float(groups[0])

                    if time_str.endswith(('h', 'ч')):
                        if value != int(value):
                            total_minutes = int(value * 60)
                            hours = total_minutes // 60
                            minutes = total_minutes % 60
                        else:
                            hours = int(value)
                    elif time_str.endswith(('m', 'м')):
                        minutes = int(value)
                        if minutes >= 60:
                            hours = minutes // 60
                            minutes = minutes % 60
                    else:
                        hours = int(value)

                return hours, minutes

        raise ValueError(f'Неизвестный формат времени: {time_str}')


class ManualTimeEntry(ttk.Frame):
    """Виджет для ручного добавления записи времени."""

    def __init__(self, parent: ScrollableFrame, on_add_entry: Callable, on_time_change: Callable = None):
        super().__init__()
        self.on_add_entry = on_add_entry
        self.on_time_change = on_time_change

        self.frame = tk.Frame(
            parent.scrollable_frame,
            borderwidth=1,
            relief='solid',
            bg='#ffffff',
        )
        self.frame.pack(fill=tk.X, padx=10, pady=7, ipady=10)
        self.frame.columnconfigure(0, weight=1)

        # Заголовок
        header_frame = ttk.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky='ew', padx=15, pady=(10, 5))
        header_frame.columnconfigure(1, weight=1)

        header_label = ttk.Label(header_frame, text='➕ Новая запись', font=('Segoe UI', 11, 'bold'))
        header_label.grid(row=0, column=0, sticky='w')

        # Поля ввода
        input_frame = ttk.Frame(self.frame)
        input_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=(5, 10))
        input_frame.columnconfigure(1, weight=1)

        # ID карточки
        card_label = ttk.Label(input_frame, text='URL карточки или ID:', font=('Segoe UI', 10))
        card_label.grid(row=0, column=0, sticky='w', pady=5)
        self.card_id_var = tk.StringVar()
        self.card_entry = ttk.Entry(input_frame, textvariable=self.card_id_var, width=15, font=('Segoe UI', 10))
        self.card_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Привязка обработчика вставки
        self.card_entry.bind('<Control-v>', self._on_card_paste, add='+')
        self.card_entry.bind('<Control-V>', self._on_card_paste, add='+')
        self.card_entry.bind('<<Paste>>', self._on_card_paste, add='+')

        # Описание
        desc_label = ttk.Label(input_frame, text='Описание:', font=('Segoe UI', 10))
        desc_label.grid(row=1, column=0, sticky='w', pady=5)
        self.desc_text = tk.Text(input_frame, height=3, wrap=tk.WORD, font=('Segoe UI', 10))
        self.desc_text.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        # Время
        time_label = ttk.Label(input_frame, text='Время:', font=('Segoe UI', 10))
        time_label.grid(row=2, column=0, sticky='w', pady=5)
        self.time_var = tk.StringVar()
        self.time_var.trace('w', self._on_time_change)
        time_entry = ttk.Entry(input_frame, textvariable=self.time_var, width=10, font=('Segoe UI', 10))
        time_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Кнопка добавления
        add_button = ttk.Button(
            input_frame,
            text='Добавить',
            command=self.add_entry,
            style='Main.TButton',
        )
        add_button.grid(row=3, column=1, sticky='e', pady=10)

    def _on_time_change(self, *args):
        if self.on_time_change:
            self.on_time_change()

    def get_time_minutes(self) -> int:
        time_spent = self.time_var.get()
        if not time_spent:
            return 0
        try:
            hours, minutes = BranchTimeEntry.parse_time(time_spent)
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return 0

    def add_entry(self):
        """Обработчик нажатия кнопки добавления."""
        card_id = self.card_id_var.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        time_spent = self.time_var.get().strip()

        if not all((card_id, description, time_spent)):
            messagebox.showwarning('Предупреждение', 'Пожалуйста, заполните все поля')
            return
        if not card_id.isdigit():
            messagebox.showwarning('Предупреждение', '"ID карточки" должно быть только числовым значением')
        try:
            hours, minutes = BranchTimeEntry.parse_time(time_spent)
            if not (0 <= hours <= 24 and 0 <= minutes <= 59):
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                title='Предупреждение',
                message=(
                    'Не верный формат времени. '
                    'Поддерживаемые форматы 13:30, 1h30m, 1ч30м, 1h 10m, 1ч 10м, 1h, 1ч, 10m, 10м или 1'
                ),
            )
            return

        self.on_add_entry(int(card_id), time_spent, description)
        self.card_id_var.set('')
        self.desc_text.delete('1.0', tk.END)
        self.time_var.set('')

    def _on_card_paste(self, event):
        try:
            clipboard = event.widget.clipboard_get().strip()
            card_id = self._fetch_card_id(clipboard)
            if card_id:
                self.card_id_var.set(card_id)
                return 'break'
        except tk.TclError:
            pass
        return None

    @classmethod
    def _fetch_card_id(cls, value: str) -> Optional[str]:
        if match := CARD_ID_REGEX.search(value):
            return next(group for group in match.groups() if group)
        return None
