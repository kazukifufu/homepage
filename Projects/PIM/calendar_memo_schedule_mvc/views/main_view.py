"""
メインウィンドウのレイアウトを担当するViewクラス。
3つの子Viewを生成してPanedWindowに配置する。
"""

import tkinter as tk
from tkinter import ttk
from config import APP_NAME, WIN_SIZE, WIN_WIDTH, WIN_HEIGHT
from views.calendar_view import CalendarView
from views.note_view import NoteView
from views.schedule_view import ScheduleView

# 起動直後のサッシ位置（スクリーンショットの比率に合わせた初期値）
# 左右分割：左ペイン幅 ≒ ウィンドウ幅の 37.5 %
_HORIZONTAL_RATIO: float = 0.375
# 左側上下分割：カレンダー高さ ≒ ウィンドウ高さの 47.5 %
_VERTICAL_RATIO: float = 0.475


class MainView:
    """アプリケーション全体のウィンドウレイアウトを管理するクラス。

    CalendarView / NoteView / ScheduleView の親として機能する。
    """

    def __init__(self, root: tk.Tk, colors: dict[str, str]) -> None:
        """メインウィンドウのレイアウトを構築する。

        Args:
            root: Tkinter ルートウィンドウ。
            colors: テーマカラー辞書。
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
        # ScheduleView のコンテナとして右ペインを用意（背景色を統一）
        frame_right = tk.Frame(pw_horizontal, bg=colors["frame_bg"])
        pw_horizontal.add(frame_right, weight=1)

        self.schedule_view = ScheduleView(frame_right, colors)

        # ── 起動直後のサッシ位置をスクリーンショットの比率に合わせて設定 ──
        # config の定数をベースに目標ピクセルを算出し、ウィンドウが実際に
        # 描画されるまでリトライしながら適用する。
        _target_h_sash = int(WIN_WIDTH  * _HORIZONTAL_RATIO)  # 左右サッシ位置
        _target_v_sash = int(WIN_HEIGHT * _VERTICAL_RATIO)    # 上下サッシ位置

        def _apply_sash() -> None:
            # ウィンドウが描画されていなければ再試行
            if root.winfo_width() <= 1:
                root.after(100, _apply_sash)
                return
            pw_horizontal.sashpos(0, _target_h_sash)
            pw_vertical_left.sashpos(0, _target_v_sash)

        root.after(50, _apply_sash)
