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

# 起動直後のサッシ位置（保存データがない初回起動時に使うデフォルト比率）
# 左右分割：左ペイン幅 ≒ ウィンドウ幅の 25 %
_LEFT_RATIO:    float = 0.25
# 左右分割：コンパスペイン右端 ≒ ウィンドウ幅の 50 %
_CENTER_RATIO:  float = 0.50
# 左側上下分割：カレンダー高さ ≒ ウィンドウ高さの 47.5 %
_VERTICAL_RATIO: float = 0.475


class MainView:
    """アプリケーション全体のウィンドウレイアウトを管理するクラス。

    CalendarView / NoteView / CompassView / ScheduleView の親として機能する。
    """

    def __init__(self, root: tk.Tk, colors: dict[str, str]) -> None:
        """メインウィンドウのレイアウトを構築する。

        Args:
            root: Tkinter ルートウィンドウ。
            colors: テーマカラー辞書。
        """
        self._root = root                          # apply_sash_positions から参照するため保持
        root.title(APP_NAME)
        root.geometry(WIN_SIZE)

        # ── 外側: 左右分割 PanedWindow ──────────────────────────────
        # get_sash_positions / apply_sash_positions から参照するためインスタンス変数に昇格
        self._pw_horizontal = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        self._pw_horizontal.pack(fill=tk.BOTH, expand=True)

        # ── 左側: 上下分割 PanedWindow ──────────────────────────────
        self._pw_vertical_left = ttk.Panedwindow(self._pw_horizontal, orient=tk.VERTICAL)
        self._pw_horizontal.add(self._pw_vertical_left, weight=1)

        # カレンダーView（左上）
        self.calendar_view = CalendarView(self._pw_vertical_left, colors)
        self._pw_vertical_left.add(self.calendar_view.container, weight=1)

        # メモView（左下）
        self.note_view = NoteView(self._pw_vertical_left, colors)
        self._pw_vertical_left.add(self.note_view.container, weight=1)

        # ── 中央: 一週間コンパスView ─────────────────────────────────
        self.compass_view = CompassView(self._pw_horizontal, colors)
        self._pw_horizontal.add(self.compass_view.container, weight=1)

        # ── 右側: スケジュールView ───────────────────────────────────
        # ScheduleView のコンテナとして右ペインを用意（背景色を統一）
        frame_right = tk.Frame(self._pw_horizontal, bg=colors["frame_bg"])
        self._pw_horizontal.add(frame_right, weight=2)

        self.schedule_view = ScheduleView(frame_right, colors)

        # ── 起動直後のサッシ位置をデフォルト値で適用 ─────────────────
        # Controller が保存値を持っている場合は __init__ 後に
        # apply_sash_positions() を再呼び出しして上書きする。
        default_positions = {
            "sash_h0": int(WIN_WIDTH * _LEFT_RATIO),
            "sash_h1": int(WIN_WIDTH * _CENTER_RATIO),
            "sash_v0": int(WIN_HEIGHT * _VERTICAL_RATIO),
        }
        self.apply_sash_positions(default_positions)

    # ── レイアウト操作 ────────────────────────────────────────────────

    def get_sash_positions(self) -> dict[str, int]:
        """現在のサッシ位置を辞書で返す。

        Returns:
            {"sash_h0": int, "sash_h1": int, "sash_v0": int} 形式の辞書。
            UiSettingsModel.save() にそのまま渡せる形式。
        """
        return {
            "sash_h0": self._pw_horizontal.sashpos(0),
            "sash_h1": self._pw_horizontal.sashpos(1),
            "sash_v0": self._pw_vertical_left.sashpos(0),
        }

    def apply_sash_positions(self, positions: dict[str, int]) -> None:
        """指定されたサッシ位置を適用する。

        ウィンドウの描画が確定してから sashpos() を呼ぶため、
        root.after() で遅延実行する。描画前であれば 100ms 後に再試行する。

        Args:
            positions: {"sash_h0": int, "sash_h1": int, "sash_v0": int} 形式の辞書。
                       UiSettingsModel.load() の戻り値をそのまま渡せる。
        """
        def _apply() -> None:
            if self._root.winfo_width() <= 1:
                self._root.after(100, _apply)
                return
            self._pw_horizontal.sashpos(0, positions["sash_h0"])
            self._pw_horizontal.sashpos(1, positions["sash_h1"])
            self._pw_vertical_left.sashpos(0, positions["sash_v0"])

        self._root.after(50, _apply)
