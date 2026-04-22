"""
アプリケーションのロジックとイベント処理を担当するコントローラクラス。
ModelとViewの橋渡し役。
"""

import sys
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk, messagebox
from datetime import datetime, date

from models.database import init_db
from models.note_model import NoteModel
from models.schedule_model import ScheduleModel
from models.ui_settings_model import UiSettingsModel
from views.main_view import MainView


@dataclass
class AppState:
    """アプリケーションの表示状態を管理するデータクラス。"""

    current_year: int = field(default_factory=lambda: datetime.now().year)
    current_month: int = field(default_factory=lambda: datetime.now().month)
    selected_date: date = field(default_factory=lambda: datetime.now().date())
    schedule_mode: str = "daily"


@dataclass
class ScheduleEntries:
    """スケジュールダイアログの入力フィールド群。"""

    s_entry: tk.Entry
    e_entry: tk.Entry
    t_entry: tk.Entry


class AppController:
    """全ドメインロジック・状態管理・イベントハンドリングを集約するクラス。"""

    def __init__(self, root: tk.Tk) -> None:
        """アプリケーションのモデル・ビュー・コントローラを初期化する。

        Args:
            root: Tkinter ルートウィンドウ。
        """
        self.root = root

        # ── モデル初期化 ─────────────────────────────────────────────
        init_db()
        self._note_model = NoteModel()
        self._schedule_model = ScheduleModel()
        self._ui_settings_model = UiSettingsModel()

        # ── アプリケーション状態 ──────────────────────────────────────
        self._state = AppState()

        # ── View 構築 ────────────────────────────────────────────────
        colors = self._build_colors()
        self._view = MainView(root, colors)

        # ── 保存済みレイアウトを復元 ──────────────────────────────────
        # MainView.__init__ がデフォルト値でサッシを初期化した直後に
        # DB の保存値で上書きする。after() の FIFO 順により保存値が必ず後に適用される。
        self._view.apply_sash_positions(self._ui_settings_model.load())

        # ── ウィンドウ終了ハンドラを登録 ─────────────────────────────
        # × ルートウィンドウを直接破棄すると保存処理が走らないため
        # root.protocol で終了をインターセプトして _on_close を呼ぶ。
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── View へコールバックを登録 ────────────────────────────────
        cal = self._view.calendar_view
        cal.bind_prev(self._on_prev_month)
        cal.bind_next(self._on_next_month)

        note = self._view.note_view
        note.bind_save(self._on_save_note)
        note.bind_focus_in(self._on_note_focus_in)
        note.bind_focus_out(self._on_note_focus_out)

        sched = self._view.schedule_view
        sched.bind_daily(self._on_toggle_mode)
        sched.bind_weekly(self._on_toggle_mode)

        canvas = sched.create_canvas()
        canvas.bind(
            "<Configure>",
            lambda e: sched.draw(
                self._schedule_model.cache,
                self._state.schedule_mode,
                self._state.selected_date,
            ),
        )

        # ── 初期表示 ─────────────────────────────────────────────────
        cal.render(
            self._state.current_year, self._state.current_month,
            self._state.selected_date, self._on_date_click,
        )
        note.set_date(self._format_date(self._state.selected_date))
        self._on_toggle_mode("daily")
        self._load_note()

    # ── テーマカラー ─────────────────────────────────────────────────

    def _build_colors(self) -> dict[str, str]:
        """コマンドライン引数を参照してテーマカラー辞書を生成する。"""
        is_dark = len(sys.argv) > 1 and sys.argv[1].lower() == "dark"
        if is_dark:
            return {
                "frame_bg": "#1e2633", "frame_fg": "#ccd4e0",
                "button_fg": "#ccd4e0", "button_bg": "#2c3848",
                "cal_fg_sun": "#e07878", "cal_fg_sat": "#78b0d8",
                "cal_fg_not_sunsat": "#ccd4e0", "cal_bg": "#242f3e",
                "cal_selected": "#3d5470",
                "holiday_fg": "#e07878", "holiday_bg": "#242f3e",
                "placeholder_hide_fg": "#242f3e",
                "placeholder_show_fg": "#667788",
                "note_text_fg": "#ccd4e0",
                "schedule_plan": "#0063b4", "schedule_actual": "#028639",
            }
        return {
            "frame_bg": "#f7f3ee", "frame_fg": "#3c3530",
            "button_fg": "#3c3530", "button_bg": "#ece5db",
            "cal_fg_sun": "#bf4040", "cal_fg_sat": "#3a78a8",
            "cal_fg_not_sunsat": "#3c3530", "cal_bg": "#faf7f3",
            "cal_selected": "#d9cfc4",
            "holiday_fg": "#bf4040", "holiday_bg": "#faf7f3",
            "placeholder_hide_fg": "#faf7f3",
            "placeholder_show_fg": "#b0a898",
            "note_text_fg": "#3c3530",
            "schedule_plan": "#98B3C8", "schedule_actual": "#8FC59C",
        }

    # ── カレンダー操作 ───────────────────────────────────────────────

    def _on_prev_month(self) -> None:
        """前月へ移動する。"""
        if self._state.current_month == 1:
            self._state.current_month = 12
            self._state.current_year -= 1
        else:
            self._state.current_month -= 1
        self._refresh_calendar()

    def _on_next_month(self) -> None:
        """翌月へ移動する。"""
        if self._state.current_month == 12:
            self._state.current_month = 1
            self._state.current_year += 1
        else:
            self._state.current_month += 1
        self._refresh_calendar()

    def _refresh_calendar(self) -> None:
        """カレンダーグリッドを再描画する。"""
        self._view.calendar_view.render(
            self._state.current_year, self._state.current_month,
            self._state.selected_date, self._on_date_click,
        )

    def _on_date_click(self, clicked_date: date, holiday_name: str) -> None:
        """日付セルがクリックされたときの処理。"""
        self._state.selected_date = clicked_date
        note = self._view.note_view
        note.set_date(self._format_date(clicked_date))
        note.set_holiday(holiday_name)

        # フォーカスをルートへ移してフォーカスアウトイベントを発火させる
        self.root.focus()
        self._refresh_calendar()
        self._load_note()
        self._reload_schedule()

    # ── メモ操作 ──────────────────────────────────────────────────────

    def _load_note(self) -> None:
        """選択日のメモをDBから読み込んでノートViewに反映する。"""
        d_str = self._state.selected_date.strftime("%Y-%m-%d")
        note = self._view.note_view
        note.set_date(self._format_date(self._state.selected_date))

        data = self._note_model.load(d_str)
        if data:
            note.set_content(data.decode("utf-8"))
        else:
            note.set_content(note.PLACEHOLDER, placeholder=True)

    def _on_save_note(self) -> None:
        """メモを保存する。テキストが空の場合はDBから削除する。"""
        note = self._view.note_view
        text = note.get_text()
        d_str = self._state.selected_date.strftime("%Y-%m-%d")

        if not text.strip() or note.is_showing_placeholder():
            self._note_model.delete(d_str)
            return
        self._note_model.save(d_str, text)
        messagebox.showinfo("保存", "メモを保存しました")

    def _on_note_focus_in(self, _event=None) -> None:
        """テキストエリアにフォーカスが当たったとき、プレースホルダーを消す。"""
        note = self._view.note_view
        if note.is_showing_placeholder():
            note.enter_edit_mode()

    def _on_note_focus_out(self, _event=None) -> None:
        """テキストエリアからフォーカスが外れたとき、空ならプレースホルダーを表示する。"""
        note = self._view.note_view
        if not note.get_text().strip():
            note.set_content(note.PLACEHOLDER, placeholder=True)

    # ── スケジュール操作 ──────────────────────────────────────────────

    def _on_toggle_mode(self, mode: str) -> None:
        """日次 / 週次モードを切り替える。"""
        self._state.schedule_mode = mode
        self._reload_schedule()
        self._view.schedule_view.update_action_buttons(
            mode,
            on_add=self._on_open_schedule_dialog,
            on_edit=self._on_show_registered_tasks,
        )

    def _reload_schedule(self) -> None:
        """スケジュールデータを再読み込みし、キャンバスを再描画する。"""
        self._schedule_model.load(self._state.selected_date, self._state.schedule_mode)
        sched = self._view.schedule_view
        if sched.canvas is not None:
            sched.draw(
                self._schedule_model.cache,
                self._state.schedule_mode,
                self._state.selected_date,
            )

    def _on_open_schedule_dialog(
        self,
        category: str,
        edit_id: int | None = None,
        initial_data: dict | None = None,
    ) -> None:
        """スケジュール入力ダイアログを開く（新規追加 / 編集共通）。"""
        dialog = tk.Toplevel(self.root)
        dialog.title("スケジュールの入力")
        dialog.geometry("350x280")
        dialog.grab_set()

        data = initial_data or {}
        entries = ScheduleEntries(
            s_entry=self._make_labeled_entry(dialog, "開始:", data.get("s", "09:00")),
            e_entry=self._make_labeled_entry(dialog, "終了:", data.get("e", "10:00")),
            t_entry=self._make_labeled_entry(dialog, "内容:", data.get("t", ""), width=30),
        )
        tk.Label(dialog, text=f"日付: {self._state.selected_date}").pack(pady=5)

        tk.Button(
            dialog,
            text="保存",
            command=lambda: self._save_schedule(
                dialog, category, edit_id, data, entries
            ),
            width=15,
        ).pack(pady=20)

    def _save_schedule(
        self,
        dialog: tk.Toplevel,
        category: str,
        edit_id: int | None,
        data: dict,
        entries: ScheduleEntries,
    ) -> None:
        """スケジュールダイアログの保存処理。

        Args:
            dialog: 閉じる対象のダイアログ。
            category: イベントカテゴリ（"plan" または "actual"）。
            edit_id: 編集対象のイベントID。新規の場合は None。
            data: ダイアログの初期データ（callback を含む場合がある）。
            entries: ダイアログの入力フィールド群。
        """
        s, e, t = entries.s_entry.get(), entries.e_entry.get(), entries.t_entry.get()
        try:
            if datetime.strptime(e, "%H:%M") <= datetime.strptime(s, "%H:%M"):
                messagebox.showerror("エラー", "時刻順序が不正です")
                return
        except ValueError:
            messagebox.showerror("エラー", "時刻の形式が不正です（HH:MM）")
            return

        d_str = str(self._state.selected_date)
        if edit_id:
            self._schedule_model.update(edit_id, s, e, t)
        else:
            self._schedule_model.save(d_str, category, s, e, t)

        self._reload_schedule()
        dialog.destroy()
        if "callback" in data:
            data["callback"]()

    def _on_show_registered_tasks(self, category: str) -> None:
        """登録済みタスクの一覧ダイアログを表示する。"""
        dialog = tk.Toplevel(self.root)
        dialog.title("登録タスク一覧")

        tree = ttk.Treeview(dialog, columns=("id", "s", "e", "t"), show="headings")
        tree.heading("s", text="開始")
        tree.heading("e", text="終了")
        tree.heading("t", text="タスク")
        tree.column("id", width=0, stretch=tk.NO)
        tree.pack(fill=tk.BOTH, expand=True)

        def refresh():
            tree.delete(*tree.get_children())
            for row in self._schedule_model.get_events_for_category(
                str(self._state.selected_date), category
            ):
                tree.insert("", tk.END, values=row)

        refresh()

        def on_edit():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0], "values")
            self._on_open_schedule_dialog(
                category,
                edit_id=vals[0],
                initial_data={"s": vals[1], "e": vals[2], "t": vals[3], "callback": refresh},
            )

        def on_delete():
            sel = tree.selection()
            if not sel:
                return
            self._schedule_model.delete(tree.item(sel[0], "values")[0])
            self._reload_schedule()
            refresh()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack()
        tk.Button(btn_frame, text="修正", command=on_edit).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="削除", command=on_delete).pack(side=tk.LEFT)

    # ── レイアウト保存 ────────────────────────────────────────────────

    def _on_close(self) -> None:
        """ウィンドウ終了時にサッシ位置を保存してからアプリを終了する。"""
        self._ui_settings_model.save(self._view.get_sash_positions())
        self.root.destroy()

    # ── ユーティリティ ───────────────────────────────────────────────

    @staticmethod
    def _format_date(d: date) -> str:
        """date オブジェクトを日本語表示形式に変換する。"""
        return f"{d.year}年{d.month}月{d.day}日"

    @staticmethod
    def _make_labeled_entry(
        parent: tk.Widget,
        label: str,
        value: str,
        width: int = 20,
    ) -> tk.Entry:
        """ラベル付き入力フィールドを生成して Entry を返す。"""
        tk.Label(parent, text=label).pack()
        entry = tk.Entry(parent, width=width)
        entry.insert(0, value)
        entry.pack()
        return entry
