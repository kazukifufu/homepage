"""
カレンダー、メモ、スケジュール機能を備えたデスクトップアプリケーションのモジュール。
TkinterのPanedWindowをネストしてレイアウトを構築します。
"""

import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
from datetime import datetime
from datetime import timedelta
import calendar
import sqlite3
import jpholiday


# 定数管理
APP_NAME = "カレンダーアプリ - カレンダー・メモ・スケジュール機能"
WIN_SIZE = "1200x800"
DB_PATH = "calendar_memo_schedule_app.db"

# スケジュール描画設定
HOUR_HEIGHT = 40
START_HOUR = 0
END_HOUR = 24
TIME_AXIS_WIDTH = 70

# 固定設定
DATE_FONT_SIZE = 12  # 日付の数字
CELL_HEIGHT = 70      # すべてのセルで共通の高さ


class CalendarMemoScheduleApp:
    # 属性数が多いのはGUIクラスの特性であるため、Pylintの警告を抑制
    # pylint: disable=too-many-instance-attributes
    """
    アプリケーションのメインウィンドウとUIコンポーネントを管理するクラス。
    """

    def __init__(self, root):
        """
        初期化メソッド。
        :param root: Tkinterのルートウィンドウインスタンス
        """
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry(WIN_SIZE)

        # インスタンス属性の初期化 (W0201対策)
        self.pw_horizontal = None
        self.pw_vertical_left = None
        self.calendar_container = None
        self.calendar_header_frame = None
        self.calendar_prev_button = None
        self.calendar_month_label = None
        self.calendar_next_button = None
        self.calendar_frame = None
        self.note_container = None
        self.note_header_frame = None
        self.note_date_label = None
        self.note_save_button = None
        self.note_holiday_label = None
        self.note_text_frame = None
        self.note_text_area = None
        self.note_text_area_placeholder = None
        self.frame_right = None
        self.schedule_container = None
        self.schedule_view_mode = None
        self.schedule_header_frame = None
        self.schedule_header_upper_frame = None
        self.schedule_header_mode_frame = None
        self.schedule_date_label = None
        self.schedule_header_lower_frame = None
        self.schedule_canvas = None
        self.schedule_daily_button = None
        self.schedule_weekly_button = None

        if self._is_dark_mode():
            # ダークモード: ディープネイビー系 - 純黒を避けた目に優しい落ち着いたダークブルーグレー
            self.colors = {"frame_bg": "#1e2633", "frame_fg": "#ccd4e0",
                           "button_fg": "#ccd4e0", "button_bg": "#2c3848",
                           "cal_fg_sun": "#e07878", "cal_fg_sat": "#78b0d8", "cal_fg_not_sunsat": "#ccd4e0", "cal_bg": "#242f3e", "cal_selected": "#3d5470",
                           "holiday_fg": "#e07878", "holiday_bg": "#242f3e",
                           "placeholder_hide_fg": "#242f3e", "placeholder_show_fg": "#667788", "note_text_fg": "#ccd4e0",
                           "schedule_plan": "#0063b4", "schedule_actual": "#028639"}
        else:
            # 通常モード: ウォームクリーム系 - 紙のような温かみのある淡い背景で長時間使用でも目が疲れにくい
            self.colors = {"frame_bg": "#f7f3ee", "frame_fg": "#3c3530",
                           "button_fg": "#3c3530", "button_bg": "#ece5db",
                           "cal_fg_sun": "#bf4040", "cal_fg_sat": "#3a78a8", "cal_fg_not_sunsat": "#3c3530", "cal_bg": "#faf7f3", "cal_selected": "#d9cfc4",
                           "holiday_fg": "#bf4040", "holiday_bg": "#faf7f3",
                           "placeholder_hide_fg": "#faf7f3", "placeholder_show_fg": "#b0a898", "note_text_fg": "#3c3530",
                           "schedule_plan": "#98B3C8", "schedule_actual": "#8FC59C"}

        # 現在の年月を初期値として設定
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_date = datetime.now().date()

        # スケジュールデータのキャッシュ
        # { "YYYY-MM-DD": [(category, start_time, end_time, task_name), ...] }
        self._schedule_cache: dict = {}

        # DB初期化メソッドの呼び出し
        self._init_databases()

        # 内部用UI構築メソッドの呼び出し
        self._setup_ui()

        # 当日のノートの読み込み
        self._load_note()

    def _is_dark_mode(self):
        # 1. コマンドライン引数を確認 (例: python app.py dark)
        if len(sys.argv) > 1:
            return sys.argv[1].lower() == "dark"
        return False

    def _init_databases(self):
        """統合データベースの初期化。"""
        with sqlite3.connect(DB_PATH) as conn:
            # 1. ノート用テーブル (date text primary key)
            conn.execute('''CREATE TABLE IF NOT EXISTS cal_notes (
                date TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_data BLOB NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')

            # 2. スケジュール用テーブル (id PK, 次に event_date)
            # これにより1日に複数のイベントをIDで管理可能
            conn.execute('''CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_date TEXT,
                category TEXT,
                start_time TEXT,
                end_time TEXT,
                task_name TEXT)''')

    def _setup_ui(self):
        """メインのUIレイアウトを設定"""
        self._create_paned_widgets()

    def _create_paned_widgets(self):
        """PanedWindowを生成し、各ペインにウィジェットを追加します。"""
        # 1. 一番外側のPanedWindow（左右分割）
        self.pw_horizontal = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.pw_horizontal.pack(fill=tk.BOTH, expand=True)

        # --- 左側のエリア ---
        self._setup_left_area()

        # --- 右側のエリア ---
        self._setup_right_area()

    def _setup_left_area(self):
        """左側のペイン（カレンダーとメモ）を構築します。"""
        # 左ペインの中に「上下分割」のPanedWindowを作成
        self.pw_vertical_left = ttk.Panedwindow(self.pw_horizontal, orient=tk.VERTICAL)
        self.pw_horizontal.add(self.pw_vertical_left, weight=1)

        # カレンダー部分の構築
        self._create_calendar_section()

        # メモエリアの構築
        self._create_memo_section()

    def _create_calendar_section(self):
        """左ペイン上部のカレンダーセクション（ヘッダーとフレーム）を生成します。"""
        # カレンダー全体のコンテナ
        self.calendar_container = tk.Frame(self.pw_vertical_left, bg=self.colors["frame_bg"])
        self.pw_vertical_left.add(self.calendar_container, weight=1)

        # ヘッダー（月移動ナビゲーション）
        self.calendar_header_frame = tk.Frame(self.calendar_container, bg=self.colors["frame_bg"], pady=5)
        self.calendar_header_frame.pack(fill=tk.X)

        # 前月ボタン
        self.calendar_prev_button = tk.Label(
            self.calendar_header_frame, text="< 前月",
            font=("Arial", 10), width=8,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.calendar_prev_button.bind("<Button-1>", lambda e: self._previous_month())
        self.calendar_prev_button.pack(side=tk.LEFT, padx=20)

        # 年月表示ラベル
        self.calendar_month_label = tk.Label(
            self.calendar_header_frame, text="",
            font=("Arial", 10), width=15,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.calendar_month_label.pack(side=tk.LEFT, expand=True)

        # 次月ボタン
        self.calendar_next_button = tk.Label(
            self.calendar_header_frame, text="次月 >",
            font=("Arial", 10), width=8,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.calendar_next_button.bind("<Button-1>", lambda e: self._next_month())
        self.calendar_next_button.pack(side=tk.RIGHT, padx=20)

        # カレンダーの日付グリッド表示エリア
        self.calendar_frame = tk.Frame(self.calendar_container, bg=self.colors["frame_bg"])
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # カレンダーの表示
        self._display_calendar()

    def _previous_month(self):
        """カレンダーを前月に切り替えます。"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._display_calendar()

    def _next_month(self):
        """カレンダーを翌月に切り替えます。"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._display_calendar()

    def _display_calendar(self):
        """カレンダーを表示します。"""
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.calendar_frame.config(bg=self.colors["frame_fg"])
        self.calendar_month_label.config(text=f"{self.current_year}年{self.current_month}月")

        weekdays = ["日", "月", "火", "水", "木", "金", "土"]
        day_colors = [self.colors["cal_fg_sun"], self.colors["cal_fg_not_sunsat"], self.colors["cal_fg_not_sunsat"],
                      self.colors["cal_fg_not_sunsat"], self.colors["cal_fg_not_sunsat"], self.colors["cal_fg_not_sunsat"],
                      self.colors["cal_fg_sat"]]
        for i, day in enumerate(weekdays):
            label = tk.Label(
                self.calendar_frame, text=day, font=("Arial", 11, "bold"),
                bg=self.colors["cal_bg"], fg=day_colors[i], width=8, height=1
            )
            label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)

        cal = calendar.Calendar(firstweekday=6)  # 6=Started from Sunday
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        for week_num, week in enumerate(month_days, start=1):
            for day_num, day in enumerate(week):
                calendar_cell_frame = tk.Frame(
                    self.calendar_frame, bg=self.colors["cal_bg"], height=CELL_HEIGHT, width=100
                )
                calendar_cell_frame.grid(row=week_num, column=day_num, sticky="nsew", padx=1, pady=1)
                calendar_cell_frame.grid_propagate(False)
                calendar_cell_frame.pack_propagate(False)

                if day != 0:
                    date_obj = datetime(self.current_year, self.current_month, day)
                    holiday_name = jpholiday.is_holiday_name(date_obj.date())

                    if holiday_name or day_num == 0:
                        fg_color = self.colors["cal_fg_sun"]
                    elif day_num == 6:
                        fg_color = self.colors["cal_fg_sat"]
                    else:
                        fg_color = self.colors["cal_fg_not_sunsat"]

                    date_label = tk.Label(
                        calendar_cell_frame, text=str(day), font=("Arial", DATE_FONT_SIZE),
                        bg=self.colors["cal_bg"], fg=fg_color
                    )
                    click_targets = [calendar_cell_frame, date_label]
                    for target in click_targets:
                        target.bind("<Button-1>", lambda e, d=date_obj.date(), h=holiday_name: self._select_date(d, h))
                        target.config(cursor="hand2")

                    date_label.pack(side=tk.TOP, pady=(5, 0))

                    if date_obj.date() == self.selected_date:
                        selected_bg = self.colors["cal_selected"]
                        calendar_cell_frame.config(bg=selected_bg)
                        date_label.config(bg=selected_bg)

        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(month_days) + 1):
            self.calendar_frame.rowconfigure(i, weight=1)

    def _select_date(self, date, holiday_name):
        """日付セルがクリックされた時の処理"""
        self.selected_date = date
        self.note_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
        )
        self.schedule_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
        )

        if holiday_name:
            self.note_holiday_label.config(text=f"【{holiday_name}】")
        else:
            self.note_holiday_label.config(text="")

        self.root.focus()
        # The event is triggered when the text area changes from a blurred state
        # to a focused state. Therefore, it needs to be unfocused once beforehand.
        self._display_calendar()
        self._load_note()
        self._load_schedule_data()
        self._draw_schedule(self.schedule_canvas)

    def _create_memo_section(self):
        """左ペイン下部のメモセクション（ヘッダーとフレーム）を生成します。"""
        self.note_container = tk.Frame(self.pw_vertical_left, bg=self.colors["frame_bg"])
        self.pw_vertical_left.add(self.note_container, weight=1)

        self.note_header_frame = tk.Frame(self.note_container, bg=self.colors["frame_bg"], pady=5)
        self.note_header_frame.pack(fill=tk.X)

        self.note_date_label = tk.Label(
            self.note_header_frame, text="xxxxx",
            font=("Arial", 10), width=15,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.note_date_label.pack(side=tk.LEFT, padx=20)
        self.note_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
        )

        self.note_holiday_label = tk.Label(
            self.note_header_frame, text="",
            font=("Arial", 10),
            bg=self.colors["holiday_bg"],
            fg=self.colors["holiday_fg"],
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.note_holiday_label.pack(side=tk.LEFT)

        self.note_save_button = tk.Label(
            self.note_header_frame, text="保存",
            font=("Arial", 10), width=8,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.note_save_button.bind("<Button-1>", lambda e: self._save_note())
        self.note_save_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.note_text_frame = tk.Frame(self.note_container, bg=self.colors["frame_bg"])
        self.note_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.note_text_area = scrolledtext.ScrolledText(
            self.note_text_frame, wrap=tk.WORD, font=("Arial", 10),
            bg=self.colors["frame_bg"], fg=self.colors["note_text_fg"],
            insertbackground=self.colors["frame_fg"],
            relief=tk.FLAT, padx=5, pady=5
        )
        self.note_text_area.pack(fill=tk.BOTH, expand=True)

        self.note_text_area_placeholder = "ここにメモを入力してください...\n\nMarkdown形式で記述できます:\n# 見出し1\n## 見出し2\n- リスト項目\n**太字**\n*斜体*"
        self.show_note_text_area_placeholder()

        self.note_text_area.bind("<FocusIn>", self.hide_note_text_area_placeholder)
        self.note_text_area.bind("<FocusOut>", self.show_note_text_area_placeholder_if_empty)

    def hide_note_text_area_placeholder(self, _event=None):
        """初期メッセージを表示をしない"""
        if self.note_text_area.get("1.0", "end-1c") == self.note_text_area_placeholder:
            self.note_text_area.delete("1.0", tk.END)
            self.note_text_area.config(fg=self.colors["note_text_fg"])

    def show_note_text_area_placeholder(self):
        """ブランクのノートエリアにガイドの表示"""
        if not self.note_text_area.get("1.0", "end-1c"):
            self.note_text_area.insert("1.0", self.note_text_area_placeholder)
            self.note_text_area.config(fg=self.colors["placeholder_show_fg"])

    def show_note_text_area_placeholder_if_empty(self, _event=None):
        """ノートエリアがブランク場合の処理"""
        if not self.note_text_area.get("1.0", "end-1c").strip():
            self.show_note_text_area_placeholder()

    def _save_note(self):
        """ノートを保存します。"""
        txt = self.note_text_area.get("1.0", "end-1c")
        d_str = self.selected_date.strftime("%Y-%m-%d")
        if not txt.strip() or txt == self.note_text_area_placeholder:
            # テキストが空の場合はDBから削除する
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('DELETE FROM cal_notes WHERE date = ?', (d_str,))
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('INSERT OR REPLACE INTO cal_notes (date, filename, file_data) VALUES (?, ?, ?)',
                         (d_str, f"{d_str}.md", txt.encode('utf-8')))
        messagebox.showinfo("保存", "メモを保存しました")

    def _load_note(self):
        """DBからメモ読込。"""
        d_str = self.selected_date.strftime("%Y-%m-%d")
        self.note_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
        )

        self.note_text_area.delete("1.0", tk.END)
        with sqlite3.connect(DB_PATH) as conn:
            res = conn.execute("SELECT file_data FROM cal_notes WHERE date = ?", (d_str,)).fetchone()
        if res:
            self.note_text_area.insert("1.0", res[0].decode('utf-8'))
            self.note_text_area.config(fg=self.colors["note_text_fg"])
        else:
            self.note_text_area.insert("1.0", self.note_text_area_placeholder)
            self.note_text_area.config(fg=self.colors["placeholder_show_fg"])

    def _setup_right_area(self):
        """右側のペイン（スケジュール）を構築します。"""
        self.frame_right = tk.Frame(self.pw_horizontal, bg=self.colors["frame_bg"])
        self.pw_horizontal.add(self.frame_right, weight=1)
        self._create_schedule_section()

    def _create_schedule_section(self):
        """右ペインのスケジュールセクション（ヘッダーとフレーム）を生成します。"""
        self.schedule_container = tk.Frame(self.frame_right)
        self.schedule_container.pack(fill=tk.BOTH, expand=True)

        self.schedule_header_frame = tk.Frame(self.schedule_container, bg=self.colors["frame_bg"], pady=5)
        self.schedule_header_frame.pack(fill=tk.X)

        self.schedule_header_mode_frame = tk.Frame(self.schedule_header_frame, bg=self.colors["frame_bg"])
        self.schedule_header_mode_frame.pack(side=tk.TOP, pady=2)

        self.schedule_daily_button = tk.Label(
            self.schedule_header_mode_frame, text="Daily (日次)",
            font=("Arial", 10), width=12,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.schedule_daily_button.bind("<Button-1>", lambda e: self._toggle_schedule_view("daily"))
        self.schedule_daily_button.pack(side=tk.LEFT, padx=5)

        self.schedule_weekly_button = tk.Label(
            self.schedule_header_mode_frame, text="Weekly (週次)",
            font=("Arial", 10), width=12,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.schedule_weekly_button.bind("<Button-1>", lambda e: self._toggle_schedule_view("weekly"))
        self.schedule_weekly_button.pack(side=tk.LEFT, padx=5)

        self.schedule_header_upper_frame = tk.Frame(self.schedule_header_frame, bg=self.colors["frame_bg"])
        self.schedule_header_upper_frame.pack(fill=tk.X, padx=10, pady=5)

        self.schedule_date_label = tk.Label(
            self.schedule_header_upper_frame, text="",
            font=("Arial", 10),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=5, pady=2,
            highlightthickness=0,
            highlightbackground=self.colors["button_fg"]
        )
        self.schedule_date_label.pack(expand=True)
        self.schedule_date_label.config(
            text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
        )

        self.schedule_header_lower_frame = tk.Frame(self.schedule_header_frame, bg=self.colors["frame_bg"])
        self.schedule_header_lower_frame.pack()

        self._toggle_schedule_view("daily")
        self._create_schedule_canvas(self.schedule_container)

    def _toggle_schedule_view(self, mode):
        """スケジュールの表示モードを切替え"""
        self.schedule_view_mode = mode
        self._load_schedule_data()
        self._update_schedule_action_buttons()
        if self.schedule_canvas is not None:
            self._draw_schedule(self.schedule_canvas)

    def _update_schedule_action_buttons(self):
        """モードに応じて操作ボタンを更新"""
        for widget in self.schedule_header_lower_frame.winfo_children():
            widget.destroy()

        if self.schedule_view_mode == "daily":
            configs = [
                ("plan", self.colors["schedule_plan"], "予定", 0),
                ("actual", self.colors["schedule_actual"], "実績", 1)
            ]
            for cat, clr, txt, col in configs:
                frame = tk.Frame(self.schedule_header_lower_frame, bg=self.colors["frame_bg"])
                frame.grid(row=0, column=col, padx=10)

                add_label = tk.Label(
                    frame, text=f"{txt}を追加",
                    font=("Arial", 10), width=15,
                    bg=clr,
                    fg=self.colors.get("button_fg", "white"),
                    cursor="hand2",
                    padx=5, pady=2,
                    highlightthickness=0,
                    highlightbackground=self.colors.get("button_fg", "white")
                )
                add_label.bind("<Button-1>", lambda e, c=cat: self.open_schedule_input_dialog(c))
                add_label.pack(pady=2)

                edit_label = tk.Label(
                    frame, text=f"{txt}を更新/削除",
                    font=("Arial", 10), width=15,
                    bg=clr,
                    fg=self.colors.get("button_fg", "white"),
                    cursor="hand2",
                    padx=5, pady=2,
                    highlightthickness=0,
                    highlightbackground=self.colors.get("button_fg", "white")
                )
                edit_label.bind("<Button-1>", lambda e, c=cat: self.show_registered_task(c))
                edit_label.pack(pady=1)
        else:
            tk.Label(
                self.schedule_header_lower_frame,
                text="※週次モード：予定のみを表示します",
                fg=self.colors["button_fg"], bg=self.colors["button_bg"]
            ).pack()

    def open_schedule_input_dialog(self, category, edit_id=None, initial_data=None):
        """スケジュール入力ダイアログの表示"""
        schedule_input_dialog = tk.Toplevel(self.root)
        schedule_input_dialog.title("スケジュールの入力")
        schedule_input_dialog.geometry("350x280")
        schedule_input_dialog.grab_set()

        data = initial_data or {}
        task_start_init = data.get('s', "09:00")
        task_end_init = data.get('e', "10:00")
        task_name_init = data.get('t', "")

        tk.Label(schedule_input_dialog, text=f"日付: {self.selected_date}").pack(pady=5)
        task_start_entered = self._create_schedule_entry_fields(schedule_input_dialog, "開始:", task_start_init)
        task_end_entered = self._create_schedule_entry_fields(schedule_input_dialog, "終了:", task_end_init)
        task_name_entered = self._create_schedule_entry_fields(schedule_input_dialog, "内容:", task_name_init, 30)

        def _save_schedule():
            start_value, end_value, name_value = (
                task_start_entered.get(), task_end_entered.get(), task_name_entered.get()
            )
            try:
                if datetime.strptime(end_value, "%H:%M") <= datetime.strptime(start_value, "%H:%M"):
                    messagebox.showerror("エラー", "時刻順序が不正です")
                    return
            except ValueError:
                messagebox.showerror("エラー", "形式不正")
                return

            self._save_schedule_task(category, edit_id, (start_value, end_value, name_value))
            schedule_input_dialog.destroy()
            self._draw_schedule(self.schedule_canvas)

        tk.Button(
            schedule_input_dialog, text="保存", command=_save_schedule,
            bg=self.colors["button_bg"], width=15
        ).pack(pady=20)

    def _create_schedule_entry_fields(self, parent, lbl, val, w=20):
        """スケジュールエントリフィールド作成"""
        tk.Label(parent, text=lbl).pack()
        e = tk.Entry(parent, width=w)
        e.insert(0, val)
        e.pack()
        return e

    def _save_schedule_task(self, cat, eid, vals):
        """DB保存。"""
        s, e, t = vals
        d_str = str(self.selected_date)
        with sqlite3.connect(DB_PATH) as conn:
            if eid:
                conn.execute(
                    'UPDATE events SET start_time=?, end_time=?, task_name=? WHERE id=?',
                    (s, e, t, eid)
                )
            else:
                conn.execute(
                    'INSERT INTO events (event_date, category, start_time, end_time, task_name) '
                    'VALUES (?,?,?,?,?)', (d_str, cat, s, e, t)
                )
        self._load_schedule_data()

    def _create_schedule_canvas(self, parent):
        """スケジュールのキャンバス作成。"""
        container = tk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.schedule_canvas = tk.Canvas(container, bg=self.colors["frame_bg"], highlightthickness=0)
        sb = tk.Scrollbar(container, orient="vertical", command=self.schedule_canvas.yview)
        self.schedule_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.schedule_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        total_height = 20 + (END_HOUR - START_HOUR) * HOUR_HEIGHT + 20
        self.schedule_canvas.config(scrollregion=(0, 0, 800, total_height))
        self.schedule_canvas.bind('<Configure>', lambda e, canv=self.schedule_canvas: self._draw_schedule(canv))

        # Windows/macOSでのマウスホイール対応
        self.schedule_canvas.bind(
            "<MouseWheel>",
            lambda e: self.schedule_canvas.yview_scroll(int("-1" if e.delta > 0 else "1"), "units")
        )

    def _load_schedule_data(self):
        """選択日（日次）または週（週次）のスケジュールデータをDBから取得してキャッシュに格納する。"""
        self._schedule_cache.clear()

        with sqlite3.connect(DB_PATH) as conn:
            if self.schedule_view_mode == "daily":
                d_str = str(self.selected_date)
                cur = conn.execute(
                    'SELECT category, start_time, end_time, task_name FROM events WHERE event_date = ?',
                    (d_str,)
                )
                self._schedule_cache[d_str] = cur.fetchall()
            else:
                # 週次モード: 週の日曜日から土曜日までの7日分を1クエリで取得
                offset = (self.selected_date.weekday() + 1) % 7
                start_date = self.selected_date - timedelta(days=offset)
                dates = [str(start_date + timedelta(days=i)) for i in range(7)]
                placeholders = ",".join("?" * 7)
                cur = conn.execute(
                    f'SELECT event_date, start_time, end_time, task_name FROM events '
                    f'WHERE event_date IN ({placeholders}) AND category = "plan"',
                    dates
                )
                for row in cur.fetchall():
                    self._schedule_cache.setdefault(row[0], []).append(row[1:])

    def _draw_schedule(self, canv):
        """キャッシュデータをもとにスケジュールを描画する（DB接続なし）。"""
        canv.delete("all")
        width = canv.winfo_width()
        if width < 100:
            width = 800

        if self.schedule_view_mode == "daily":
            num_cols = 2
            col_labels = ["予定", "実績"]
            self.schedule_date_label.config(
                text=f"{self.selected_date.year}年{self.selected_date.month}月{self.selected_date.day}日"
            )
            start_date = None
        else:
            num_cols = 7
            col_labels = ["日", "月", "火", "水", "木", "金", "土"]
            offset = (self.selected_date.weekday() + 1) % 7
            start_date = self.selected_date - timedelta(days=offset)
            end_date = start_date + timedelta(days=6)
            self.schedule_date_label.config(
                text=f"{start_date.strftime('%Y/%m/%d')} 〜 {end_date.strftime('%m/%d')} (週間)"
            )

        col_w = (width - TIME_AXIS_WIDTH - 20) / num_cols
        col_h = 20 + 24 * HOUR_HEIGHT

        # 1. 背景グリッドと時間ラベル
        for h in range(START_HOUR, END_HOUR + 1):
            y_pixel = 20 + (h - START_HOUR) * HOUR_HEIGHT
            canv.create_text(TIME_AXIS_WIDTH - 10, y_pixel, text=f"{h:02d}:00",
                             anchor="e", font=("Arial", 9), fill=self.colors["frame_fg"])
            canv.create_line(TIME_AXIS_WIDTH, y_pixel, width - 20, y_pixel, fill=self.colors["frame_fg"])

        # 2. 列の見出しと境界線
        for i in range(num_cols):
            x_left = TIME_AXIS_WIDTH + (i * col_w)
            canv.create_text(x_left + col_w / 2, 10, text=col_labels[i],
                             font=("Arial", 8, "bold"), fill=self.colors["frame_fg"])
            if i > 0:
                canv.create_line(x_left, 0, x_left, col_h + 20, fill=self.colors["frame_fg"])

        # 3. キャッシュからデータを描画（DB接続なし）
        if self.schedule_view_mode == "daily":
            d_str = str(self.selected_date)
            for cat, s_time, e_time, t_name in self._schedule_cache.get(d_str, []):
                y_s = self._convert_time_to_y_axis(s_time)
                y_e = self._convert_time_to_y_axis(e_time)
                base_x = TIME_AXIS_WIDTH if cat == 'plan' else TIME_AXIS_WIDTH + col_w
                clr = self.colors["schedule_plan"] if cat == 'plan' else self.colors["schedule_actual"]
                self._draw_task_bar(canv, base_x, y_s, y_e, t_name, clr, col_w)
        else:
            for i in range(7):
                # str() でキャッシュキーの型（文字列）と一致させる
                curr = str(start_date + timedelta(days=i))
                base_x = TIME_AXIS_WIDTH + (i * col_w)
                for s_time, e_time, t_name in self._schedule_cache.get(curr, []):
                    y_s = self._convert_time_to_y_axis(s_time)
                    y_e = self._convert_time_to_y_axis(e_time)
                    self._draw_task_bar(canv, base_x, y_s, y_e, t_name,
                                        self.colors["schedule_plan"], col_w)

    def _draw_task_bar(self, canv, base_x, y_s, y_e, task_name, clr, w):
        """タスクバーの描画ヘルパー"""
        line_x = base_x + 15
        canv.create_line(line_x, y_s, line_x, y_e, arrow=tk.BOTH, width=4, fill=clr)

        text_x = line_x + 10
        text_y = (y_s + y_e) / 2

        display_text = task_name
        if self.schedule_view_mode == "weekly" and w < 70:
            display_text = task_name[:4] + ".." if len(task_name) > 4 else task_name

        canv.create_text(text_x, text_y, text=display_text, anchor="w",
                         font=("Arial", 9, "bold"), fill=clr)

    def _convert_time_to_y_axis(self, t_str):
        """時間を縦軸座標に変換"""
        try:
            h, m = map(int, t_str.split(':'))
            return 20 + (h - START_HOUR) * HOUR_HEIGHT + (m / 60) * HOUR_HEIGHT
        except ValueError:
            return 20

    def show_registered_task(self, category):
        """登録タスクを一覧で表示"""
        schedule_edit_dialog = tk.Toplevel(self.root)
        schedule_edit_dialog.title("登録タスク一覧")
        tree = ttk.Treeview(schedule_edit_dialog, columns=("id", "s", "e", "t"), show='headings')
        tree.heading("s", text="開始")
        tree.heading("e", text="終了")
        tree.heading("t", text="タスク")
        tree.column("id", width=0, stretch=tk.NO)
        tree.pack(fill=tk.BOTH, expand=True)

        def refresh_tree():
            tree.delete(*tree.get_children())
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.execute(
                    'SELECT id, start_time, end_time, task_name FROM events '
                    'WHERE category=? AND event_date=? ORDER BY start_time ASC',
                    (category, str(self.selected_date))
                )
                for r in cur.fetchall():
                    tree.insert("", tk.END, values=r)

        refresh_tree()

        btn_f = tk.Frame(schedule_edit_dialog)
        btn_f.pack()
        tk.Button(btn_f, text="削除", command=lambda: self._on_del(tree, refresh_tree)).pack(side=tk.LEFT)

    def _on_del(self, tree, call_refresh_tree):
        sel = tree.selection()
        if not sel:
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('DELETE FROM events WHERE id=?', (tree.item(sel[0], "values")[0],))
        self._load_schedule_data()
        call_refresh_tree()
        self._draw_schedule(self.schedule_canvas)


def main():
    """アプリケーションのエントリーポイント。"""
    root = tk.Tk()
    CalendarMemoScheduleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
