"""
カレンダーグリッドの表示を担当するViewクラス。
"""

import tkinter as tk
import calendar
from datetime import datetime, date
from typing import Callable
import jpholiday
from config import DATE_FONT_SIZE, CELL_HEIGHT


class CalendarView:
    """
    月間カレンダーのヘッダー・グリッドウィジェットを管理するクラス。
    ロジックは保持せず、描画とコールバックの口だけを提供する。
    """

    def __init__(self, parent, colors: dict):
        """
        :param parent: 親ウィジェット（PanedWindowペイン）
        :param colors: テーマカラー辞書
        """
        self.colors = colors

        # コンテナ（PanedWindowへ追加される単位）
        self.container = tk.Frame(parent, bg=colors["frame_bg"])

        # ヘッダー（月ナビゲーション）
        header = tk.Frame(self.container, bg=colors["frame_bg"], pady=5)
        header.pack(fill=tk.X)

        self._prev_btn = tk.Label(
            header, text="< 前月", font=("Arial", 10), width=8,
            bg=colors["button_bg"], fg=colors["button_fg"],
            cursor="hand2", padx=5, pady=2,
            highlightthickness=0, highlightbackground=colors["button_fg"]
        )
        self._prev_btn.pack(side=tk.LEFT, padx=20)

        self._month_label = tk.Label(
            header, text="", font=("Arial", 10), width=15,
            bg=colors["button_bg"], fg=colors["button_fg"],
            padx=5, pady=2, highlightthickness=0,
            highlightbackground=colors["button_fg"]
        )
        self._month_label.pack(side=tk.LEFT, expand=True)

        self._next_btn = tk.Label(
            header, text="次月 >", font=("Arial", 10), width=8,
            bg=colors["button_bg"], fg=colors["button_fg"],
            cursor="hand2", padx=5, pady=2,
            highlightthickness=0, highlightbackground=colors["button_fg"]
        )
        self._next_btn.pack(side=tk.RIGHT, padx=20)

        # 日付グリッドエリア
        self._grid_frame = tk.Frame(self.container, bg=colors["frame_bg"])
        self._grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # コールバック登録

    def bind_prev(self, callback: Callable) -> None:
        """「前月」ボタンクリック時のコールバックを登録する。"""
        self._prev_btn.bind("<Button-1>", lambda e: callback())

    def bind_next(self, callback: Callable) -> None:
        """「次月」ボタンクリック時のコールバックを登録する。"""
        self._next_btn.bind("<Button-1>", lambda e: callback())

    # 描画

    def render(self, year: int, month: int, selected_date: date, on_date_click: Callable) -> None:
        """
        カレンダーグリッドを再描画する。
        :param year: 表示年
        :param month: 表示月
        :param selected_date: 選択中の日付（ハイライト用）
        :param on_date_click: 日付セルクリック時のコールバック (date, holiday_name) -> None
        """
        # 既存ウィジェットをすべて破棄
        for widget in self._grid_frame.winfo_children():
            widget.destroy()

        # グリッドフレームの背景色 = 1px のセル区切り線として機能
        self._grid_frame.config(bg=self.colors["frame_fg"])
        self._month_label.config(text=f"{year}年{month}月")

        # 曜日ヘッダー行
        weekdays = ["日", "月", "火", "水", "木", "金", "土"]
        day_fg_colors = [
            self.colors["cal_fg_sun"],
            *[self.colors["cal_fg_not_sunsat"]] * 5,
            self.colors["cal_fg_sat"],
        ]
        for i, label in enumerate(weekdays):
            tk.Label(
                self._grid_frame, text=label, font=("Arial", 11, "bold"),
                bg=self.colors["cal_bg"], fg=day_fg_colors[i], width=8, height=1
            ).grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        # 日付セル描画（日曜始まり）
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(year, month)

        for week_idx, week in enumerate(month_days, start=1):
            for day_idx, day in enumerate(week):
                cell = tk.Frame(
                    self._grid_frame, bg=self.colors["cal_bg"],
                    height=CELL_HEIGHT, width=100
                )
                cell.grid(row=week_idx, column=day_idx, sticky="nsew", padx=1, pady=1)
                cell.grid_propagate(False)
                cell.pack_propagate(False)

                if day == 0:
                    continue

                date_obj = datetime(year, month, day)
                holiday_name = jpholiday.is_holiday_name(date_obj.date())

                # 日付の文字色を決定
                if holiday_name or day_idx == 0:
                    fg = self.colors["cal_fg_sun"]
                elif day_idx == 6:
                    fg = self.colors["cal_fg_sat"]
                else:
                    fg = self.colors["cal_fg_not_sunsat"]

                date_lbl = tk.Label(
                    cell, text=str(day), font=("Arial", DATE_FONT_SIZE),
                    bg=self.colors["cal_bg"], fg=fg
                )
                # セルフレームと日付ラベル両方にクリックイベントを設定
                for target in (cell, date_lbl):
                    target.bind(
                        "<Button-1>",
                        lambda e, d=date_obj.date(), h=holiday_name: on_date_click(d, h)
                    )
                    target.config(cursor="hand2")

                date_lbl.pack(side=tk.TOP, pady=(5, 0))

                # 選択日のハイライト
                if date_obj.date() == selected_date:
                    sel_bg = self.colors["cal_selected"]
                    cell.config(bg=sel_bg)
                    date_lbl.config(bg=sel_bg)

        # グリッドの伸縮設定
        for i in range(7):
            self._grid_frame.columnconfigure(i, weight=1)
        for i in range(len(month_days) + 1):
            self._grid_frame.rowconfigure(i, weight=1)
