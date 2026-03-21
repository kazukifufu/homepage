"""
スケジュール表示エリア（ヘッダー・キャンバス・操作ボタン）を担当するViewクラス。
"""

import tkinter as tk
from datetime import date, timedelta
from typing import Callable
from config import HOUR_HEIGHT, START_HOUR, END_HOUR, TIME_AXIS_WIDTH


class ScheduleView:
    """
    スケジュールセクションのウィジェット管理と描画を行うクラス。
    描画データはコントローラから受け取る（DBアクセスなし）。
    """

    def __init__(self, parent, colors: dict):
        """
        :param parent: 親ウィジェット（右ペインフレーム）
        :param colors: テーマカラー辞書
        """
        self.colors = colors
        self.canvas: tk.Canvas | None = None

        # コンテナ
        self.container = tk.Frame(parent)
        self.container.pack(fill=tk.BOTH, expand=True)

        # ── ヘッダー ────────────────────────────────────────────────
        header = tk.Frame(self.container, bg=colors["frame_bg"], pady=5)
        header.pack(fill=tk.X)

        # モード切替ボタン行
        mode_row = tk.Frame(header, bg=colors["frame_bg"])
        mode_row.pack(side=tk.TOP, pady=2)

        self._daily_btn = tk.Label(
            mode_row, text="Daily (日次)", font=("Arial", 10), width=12,
            bg=colors["button_bg"], fg=colors["button_fg"],
            cursor="hand2", padx=5, pady=2,
            highlightthickness=0, highlightbackground=colors["button_fg"]
        )
        self._daily_btn.pack(side=tk.LEFT, padx=5)

        self._weekly_btn = tk.Label(
            mode_row, text="Weekly (週次)", font=("Arial", 10), width=12,
            bg=colors["button_bg"], fg=colors["button_fg"],
            cursor="hand2", padx=5, pady=2,
            highlightthickness=0, highlightbackground=colors["button_fg"]
        )
        self._weekly_btn.pack(side=tk.LEFT, padx=5)

        # 日付表示行
        upper_row = tk.Frame(header, bg=colors["frame_bg"])
        upper_row.pack(fill=tk.X, padx=10, pady=5)

        self._date_label = tk.Label(
            upper_row, text="", font=("Arial", 10),
            bg=colors["button_bg"], fg=colors["button_fg"],
            padx=5, pady=2, highlightthickness=0,
            highlightbackground=colors["button_fg"]
        )
        self._date_label.pack(expand=True)

        # 操作ボタン行（モード切替で内容が変わる）
        self._action_row = tk.Frame(header, bg=colors["frame_bg"])
        self._action_row.pack()

    # ── コールバック登録 ─────────────────────────────────────────────

    def bind_daily(self, callback: Callable) -> None:
        """「Daily」ボタンクリック時のコールバックを登録する。"""
        self._daily_btn.bind("<Button-1>", lambda e: callback("daily"))

    def bind_weekly(self, callback: Callable) -> None:
        """「Weekly」ボタンクリック時のコールバックを登録する。"""
        self._weekly_btn.bind("<Button-1>", lambda e: callback("weekly"))

    # ── ウィジェット構築 ─────────────────────────────────────────────

    def create_canvas(self) -> tk.Canvas:
        """
        スクロール対応のスケジュールキャンバスを生成して返す。
        :return: 生成した Canvas ウィジェット
        """
        wrapper = tk.Frame(self.container)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(wrapper, bg=self.colors["frame_bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        total_height = 20 + (END_HOUR - START_HOUR) * HOUR_HEIGHT + 20
        self.canvas.config(scrollregion=(0, 0, 800, total_height))

        # マウスホイールスクロール（Windows / macOS 対応）
        self.canvas.bind(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int("-1" if e.delta > 0 else "1"), "units")
        )
        return self.canvas

    def set_date_label(self, text: str) -> None:
        """ヘッダーの日付表示ラベルを更新する。"""
        self._date_label.config(text=text)

    def update_action_buttons(
        self,
        mode: str,
        on_add: Callable,
        on_edit: Callable
    ) -> None:
        """
        モードに応じて操作ボタン行を再構築する。
        :param mode: "daily" または "weekly"
        :param on_add: 追加ボタンのコールバック (category: str) -> None
        :param on_edit: 更新/削除ボタンのコールバック (category: str) -> None
        """
        for widget in self._action_row.winfo_children():
            widget.destroy()

        if mode == "daily":
            configs = [
                ("plan",   self.colors["schedule_plan"],   "予定", 0),
                ("actual", self.colors["schedule_actual"], "実績", 1),
            ]
            for cat, clr, label, col in configs:
                frame = tk.Frame(self._action_row, bg=self.colors["frame_bg"])
                frame.grid(row=0, column=col, padx=10)

                add_btn = tk.Label(
                    frame, text=f"{label}を追加", font=("Arial", 10), width=15,
                    bg=clr, fg=self.colors.get("button_fg", "white"),
                    cursor="hand2", padx=5, pady=2,
                    highlightthickness=0, highlightbackground=self.colors.get("button_fg", "white")
                )
                add_btn.bind("<Button-1>", lambda e, c=cat: on_add(c))
                add_btn.pack(pady=2)

                edit_btn = tk.Label(
                    frame, text=f"{label}を更新/削除", font=("Arial", 10), width=15,
                    bg=clr, fg=self.colors.get("button_fg", "white"),
                    cursor="hand2", padx=5, pady=2,
                    highlightthickness=0, highlightbackground=self.colors.get("button_fg", "white")
                )
                edit_btn.bind("<Button-1>", lambda e, c=cat: on_edit(c))
                edit_btn.pack(pady=1)
        else:
            tk.Label(
                self._action_row,
                text="※週次モード：予定のみを表示します",
                fg=self.colors["button_fg"],
                bg=self.colors["button_bg"]
            ).pack()

    # ── スケジュール描画 ─────────────────────────────────────────────

    def draw(
        self,
        schedule_cache: dict,
        mode: str,
        selected_date: date
    ) -> None:
        """
        キャッシュデータをもとにスケジュールを描画する（DB接続なし）。
        :param schedule_cache: { "YYYY-MM-DD": [(...), ...] } のキャッシュ
        :param mode: "daily" または "weekly"
        :param selected_date: 選択中の日付
        """
        canv = self.canvas
        canv.delete("all")

        width = canv.winfo_width()
        if width < 100:
            width = 800

        if mode == "daily":
            num_cols = 2
            col_labels = ["予定", "実績"]
            self._date_label.config(
                text=f"{selected_date.year}年{selected_date.month}月{selected_date.day}日"
            )
        else:
            num_cols = 7
            col_labels = ["日", "月", "火", "水", "木", "金", "土"]
            offset = (selected_date.weekday() + 1) % 7
            week_start = selected_date - timedelta(days=offset)
            week_end = week_start + timedelta(days=6)
            self._date_label.config(
                text=f"{week_start.strftime('%Y/%m/%d')} 〜 {week_end.strftime('%m/%d')} (週間)"
            )

        col_w = (width - TIME_AXIS_WIDTH - 20) / num_cols
        col_h = 20 + 24 * HOUR_HEIGHT

        # 1. 時間軸グリッド
        for h in range(START_HOUR, END_HOUR + 1):
            y = 20 + (h - START_HOUR) * HOUR_HEIGHT
            canv.create_text(
                TIME_AXIS_WIDTH - 10, y,
                text=f"{h:02d}:00", anchor="e",
                font=("Arial", 9), fill=self.colors["frame_fg"]
            )
            canv.create_line(TIME_AXIS_WIDTH, y, width - 20, y, fill=self.colors["frame_fg"])

        # 2. 列見出しと境界線
        for i in range(num_cols):
            x_left = TIME_AXIS_WIDTH + (i * col_w)
            canv.create_text(
                x_left + col_w / 2, 10,
                text=col_labels[i], font=("Arial", 8, "bold"),
                fill=self.colors["frame_fg"]
            )
            if i > 0:
                canv.create_line(x_left, 0, x_left, col_h + 20, fill=self.colors["frame_fg"])

        # 3. タスクバー描画
        if mode == "daily":
            d_str = str(selected_date)
            for cat, s_time, e_time, t_name in schedule_cache.get(d_str, []):
                y_s = self._time_to_y(s_time)
                y_e = self._time_to_y(e_time)
                base_x = TIME_AXIS_WIDTH if cat == "plan" else TIME_AXIS_WIDTH + col_w
                clr = self.colors["schedule_plan"] if cat == "plan" else self.colors["schedule_actual"]
                self._draw_task_bar(canv, base_x, y_s, y_e, t_name, clr, col_w, mode)
        else:
            offset = (selected_date.weekday() + 1) % 7
            week_start = selected_date - timedelta(days=offset)
            for i in range(7):
                curr = str(week_start + timedelta(days=i))
                base_x = TIME_AXIS_WIDTH + (i * col_w)
                for s_time, e_time, t_name in schedule_cache.get(curr, []):
                    y_s = self._time_to_y(s_time)
                    y_e = self._time_to_y(e_time)
                    self._draw_task_bar(
                        canv, base_x, y_s, y_e, t_name,
                        self.colors["schedule_plan"], col_w, mode
                    )

    def _draw_task_bar(
        self,
        canv: tk.Canvas,
        base_x: float, y_s: float, y_e: float,
        task_name: str, clr: str, col_w: float, mode: str
    ) -> None:
        """タスクを矢印線＋テキストで描画するヘルパー。"""
        line_x = base_x + 15
        canv.create_line(line_x, y_s, line_x, y_e, arrow=tk.BOTH, width=4, fill=clr)

        text_x = line_x + 10
        text_y = (y_s + y_e) / 2

        # 週次モードで列幅が狭い場合はテキストを省略
        display_text = task_name
        if mode == "weekly" and col_w < 70:
            display_text = task_name[:4] + ".." if len(task_name) > 4 else task_name

        canv.create_text(
            text_x, text_y, text=display_text,
            anchor="w", font=("Arial", 9, "bold"), fill=clr
        )

    def _time_to_y(self, t_str: str) -> float:
        """時間文字列 "HH:MM" を縦軸ピクセル座標に変換する。"""
        try:
            h, m = map(int, t_str.split(":"))
            return 20 + (h - START_HOUR) * HOUR_HEIGHT + (m / 60) * HOUR_HEIGHT
        except ValueError:
            return 20
