import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox
from typing import List, Tuple

from src.core.config import config


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


class BranchTimeEntry(ttk.Frame):
    """Виджет для ввода времени, потраченного на работу в ветке."""

    def __init__(self, parent: ScrollableFrame, branch_name: str, card_id: str, commits: List[str]):
        self.card_id = card_id
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

        for message in commits:
            self.commits_text.insert(tk.END, f'{message}\n')

        time_frame = ttk.Frame(self.frame)
        time_frame.grid(row=2, column=0, sticky='w', padx=15, pady=(0, 10))

        time_label = ttk.Label(time_frame, text='⏱️ Время:', font=('Segoe UI', 10))
        time_label.pack(side=tk.LEFT)

        self.time_var = tk.StringVar()
        time_entry = ttk.Entry(time_frame, textvariable=self.time_var, width=10, font=('Segoe UI', 10))
        time_entry.pack(side=tk.LEFT, padx=5)

    def get_data(self) -> Tuple[str, str, str]:
        return self.card_id, self.time_var.get(), self.commits_text.get('1.0', tk.END).strip()


class ManualTimeEntry(ttk.Frame):
    """Виджет для ручного добавления записи времени."""

    def __init__(self, parent: ScrollableFrame):
        super().__init__()

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
        card_label = ttk.Label(input_frame, text='ID карточки:', font=('Segoe UI', 10))
        card_label.grid(row=0, column=0, sticky='w', pady=5)
        self.card_id_var = tk.StringVar()
        card_entry = ttk.Entry(input_frame, textvariable=self.card_id_var, width=10, font=('Segoe UI', 10))
        card_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        # Описание
        desc_label = ttk.Label(input_frame, text='Описание:', font=('Segoe UI', 10))
        desc_label.grid(row=1, column=0, sticky='w', pady=5)
        self.desc_text = tk.Text(input_frame, height=3, wrap=tk.WORD, font=('Segoe UI', 10))
        self.desc_text.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        # Время
        time_label = ttk.Label(input_frame, text='Время:', font=('Segoe UI', 10))
        time_label.grid(row=2, column=0, sticky='w', pady=5)
        self.time_var = tk.StringVar()
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

    def add_entry(self):
        """Обработчик нажатия кнопки добавления."""
        card_id = self.card_id_var.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        time_spent = self.time_var.get().strip()

        if not all([card_id, description, time_spent]):
            messagebox.showwarning('Предупреждение', 'Пожалуйста, заполните все поля')
            return

        try:
            hours, minutes = map(int, time_spent.split('.'))
            if not (0 <= hours <= 24 and 0 <= minutes <= 59):
                raise ValueError
        except ValueError:
            messagebox.showwarning('Предупреждение', 'Время должно быть в формате ЧЧ.ММ')
            return

        # Здесь будет обработка добавления записи
        # TODO: Добавить callback для обработки добавления записи

        # Очистка полей после добавления
        self.card_id_var.set('')
        self.desc_text.delete('1.0', tk.END)
        self.time_var.set('')

    def get_data(self) -> Tuple[str, str, str]:
        """Возвращает данные из полей ввода."""
        return (
            self.card_id_var.get().strip(),
            self.time_var.get().strip(),
            self.desc_text.get('1.0', tk.END).strip(),
        )
