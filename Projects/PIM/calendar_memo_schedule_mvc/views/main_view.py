"""
メインウィンドウのレイアウトを担当するViewクラス。
4つの子Viewを生成してPanedWindowに配置する。
"""

import tkinter as tk
from tkinter import ttk
from config import APP_NAME, WIN_SIZE, WIN_WIDTH, WIN_HEIGHT
from views.calendar_view import CalendarView
from views.note_view import NoteView
from views.compass_view import CompassView
from views.schedule_view import ScheduleView

_LEFT_RATIO:    float = 0.25
_CENTER_RATIO:  float = 0.50
_VERTICAL_RATIO: float = 0.475


class MainView:
    """アプリケーション全体のウィンドウレイアウトを管理するクラス。

    CalendarView / NoteView / CompassView / ScheduleView の親として機能する。
    """

    def __init__(self, root: tk.Tk, colors: dict[str, str]) -> None:
        root.title(APP_NAME)
        root.geometry(WIN_SIZE)

        pw_horizontal = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        pw_horizontal.pack(fill=tk.BOTH, expand=True)

        pw_vertical_left = ttk.Panedwindow(pw_horizontal, orient=tk.VERTICAL)
        pw_horizontal.add(pw_vertical_left, weight=1)

        self.calendar_view = CalendarView(pw_vertical_left, colors)
        pw_vertical_left.add(self.calendar_view.container, weight=1)

        self.note_view = NoteView(pw_vertical_left, colors)
        pw_vertical_left.add(self.note_view.container, weight=1)

        # ── 中央: 一週間コンパスView ─────────────────────────────────
        self.compass_view = CompassView(pw_horizontal, colors)
        pw_horizontal.add(self.compass_view.container, weight=1)

        frame_right = tk.Frame(pw_horizontal, bg=colors["frame_bg"])
        pw_horizontal.add(frame_right, weight=2)

        self.schedule_view = ScheduleView(frame_right, colors)

        _target_left_sash   = int(WIN_WIDTH * _LEFT_RATIO)
        _target_center_sash = int(WIN_WIDTH * _CENTER_RATIO)
        _target_v_sash      = int(WIN_HEIGHT * _VERTICAL_RATIO)

        def _apply_sash() -> None:
            if root.winfo_width() <= 1:
                root.after(100, _apply_sash)
                return
            pw_horizontal.sashpos(0, _target_left_sash)
            pw_horizontal.sashpos(1, _target_center_sash)
            pw_vertical_left.sashpos(0, _target_v_sash)

        root.after(50, _apply_sash)
