"""
メモ（ノート）エリアのウィジェット管理を担当するViewクラス。
"""

import tkinter as tk
from tkinter import scrolledtext
from typing import Callable


class NoteView:
    """メモ入力エリアのヘッダー・テキストウィジェットを管理するクラス。

    プレースホルダーの表示状態のみ保持し、ロジックはコントローラに委ねる。
    """

    PLACEHOLDER = (
        "ここにメモを入力してください...\n\n"
        "Markdown形式で記述できます:\n"
        "# 見出し1\n"
        "## 見出し2\n"
        "- リスト項目\n"
        "**太字**\n"
        "*斜体*"
    )

    def __init__(self, parent: tk.Widget, colors: dict[str, str]) -> None:
        """メモエリアのヘッダーとテキストウィジェットを初期化する。

        Args:
            parent: 親ウィジェット（PanedWindowペイン）。
            colors: テーマカラー辞書。
        """
        self.colors = colors

        self.container = tk.Frame(parent, bg=colors["frame_bg"])

        # ── ヘッダー ────────────────────────────────────────────────
        header = tk.Frame(self.container, bg=colors["frame_bg"], pady=5)
        header.pack(fill=tk.X)

        self._date_label = tk.Label(
            header,
            text="",
            font=("Arial", 10),
            width=15,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=5,
            pady=2,
            highlightthickness=0,
            highlightbackground=colors["button_fg"],
        )
        self._date_label.pack(side=tk.LEFT, padx=20)

        self._holiday_label = tk.Label(
            header,
            text="",
            font=("Arial", 10),
            bg=colors["holiday_bg"],
            fg=colors["holiday_fg"],
            padx=5,
            pady=2,
            highlightthickness=0,
            highlightbackground=colors["button_fg"],
        )
        self._holiday_label.pack(side=tk.LEFT)

        self._save_btn = tk.Label(
            header,
            text="保存",
            font=("Arial", 10),
            width=8,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            cursor="hand2",
            padx=5,
            pady=2,
            highlightthickness=0,
            highlightbackground=colors["button_fg"],
        )
        self._save_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # ── テキストエリア ───────────────────────────────────────────
        text_frame = tk.Frame(self.container, bg=colors["frame_bg"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["frame_bg"],
            fg=colors["note_text_fg"],
            insertbackground=colors["frame_fg"],
            relief=tk.FLAT,
            padx=5,
            pady=5,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

    # ── コールバック登録 ─────────────────────────────────────────────

    def bind_save(self, callback: Callable[[], None]) -> None:
        """「保存」ボタンクリック時のコールバックを登録する。"""
        self._save_btn.bind("<Button-1>", lambda e: callback())

    def bind_focus_in(self, callback: Callable[[tk.Event], None]) -> None:
        """テキストエリアのフォーカスイン時のコールバックを登録する。"""
        self.text_area.bind("<FocusIn>", callback)

    def bind_focus_out(self, callback: Callable[[tk.Event], None]) -> None:
        """テキストエリアのフォーカスアウト時のコールバックを登録する。"""
        self.text_area.bind("<FocusOut>", callback)

    # ── ラベル更新 ───────────────────────────────────────────────────

    def set_date(self, text: str) -> None:
        """ヘッダーの日付ラベルを更新する。"""
        self._date_label.config(text=text)

    def set_holiday(self, holiday_name: str) -> None:
        """祝日名ラベルを更新する（空文字で非表示）。"""
        self._holiday_label.config(
            text=f"【{holiday_name}】" if holiday_name else ""
        )

    # ── テキストエリア操作 ────────────────────────────────────────────

    def get_text(self) -> str:
        """テキストエリアの現在の内容を返す。"""
        return self.text_area.get("1.0", "end-1c")

    def is_showing_placeholder(self) -> bool:
        """現在プレースホルダーが表示中かどうかを返す。"""
        return self.get_text() == self.PLACEHOLDER

    def set_content(self, text: str, placeholder: bool = False) -> None:
        """テキストエリアに内容をセットする。

        Args:
            text: 設定するテキスト。
            placeholder: True の場合プレースホルダー色で表示。
        """
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
        self.text_area.config(
            fg=self.colors["placeholder_show_fg"] if placeholder
            else self.colors["note_text_fg"]
        )

    def enter_edit_mode(self) -> None:
        """プレースホルダーを消去し、通常テキスト入力モードに切り替える。"""
        self.text_area.delete("1.0", tk.END)
        self.text_area.config(fg=self.colors["note_text_fg"])
