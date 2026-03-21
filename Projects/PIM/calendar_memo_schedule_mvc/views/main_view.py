"""
メインウィンドウのレイアウトを担当するViewクラス。
3つの子Viewを生成してPanedWindowに配置する。
"""

import tkinter as tk
from tkinter import ttk
from config import APP_NAME, WIN_SIZE
from views.calendar_view import CalendarView
from views.note_view import NoteView
from views.schedule_view import ScheduleView


class MainView:
    """
    アプリケーション全体のウィンドウレイアウトを管理するクラス。
    CalendarView / NoteView / ScheduleView の親として機能する。
    """

    def __init__(self, root: tk.Tk, colors: dict):
        """
        :param root: Tkinter ルートウィンドウ
        :param colors: テーマカラー辞書
        """
        root.title(APP_NAME)
        root.geometry(WIN_SIZE)

        # ── 外側: 左右分割 PanedWindow ──────────────────────────────
        pw_horizontal = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        pw_horizontal.pack(fill=tk.BOTH, expand=True)

        # ── 左側: 上下分割 PanedWindow ──────────────────────────────
        pw_vertical_left = ttk.Panedwindow(pw_horizontal, orient=tk.VERTICAL)
        pw_horizontal.add(pw_vertical_left, weight=1)

        # カレンダーView（左上）
        self.calendar_view = CalendarView(pw_vertical_left, colors)
        pw_vertical_left.add(self.calendar_view.container, weight=1)

        # メモView（左下）
        self.note_view = NoteView(pw_vertical_left, colors)
        pw_vertical_left.add(self.note_view.container, weight=1)

        # ── 右側: スケジュールView ───────────────────────────────────
        frame_right = tk.Frame(pw_horizontal, bg=colors["frame_bg"])
        pw_horizontal.add(frame_right, weight=1)

        self.schedule_view = ScheduleView(frame_right, colors)
