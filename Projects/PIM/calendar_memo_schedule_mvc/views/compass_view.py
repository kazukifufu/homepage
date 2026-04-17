"""
一週間コンパスWidgetのレイアウトと表示を担当するViewクラス。
"""

import tkinter as tk
from typing import Callable


# 刃を研ぐ: ラベルとデータキーの対応
_SHARPEN_FIELDS: tuple[tuple[str, str], ...] = (
    ("肉体",       "body"),
    ("社会・情報", "social"),
    ("知性",       "intellect"),
    ("精神・趣味", "spirit"),
)

_QUESTION_TEXT = "今週この役割において、私にできる\n最も大切な事柄は、何だろう？"


class CompassView:
    """一週間コンパスエリアのウィジェット管理を行うクラス。

    役割・目標の入力フォームを提供し、ロジックはコントローラに委ねる。
    """

    def __init__(self, parent: tk.Widget, colors: dict[str, str]) -> None:
        """一週間コンパスエリアのウィジェットを初期化する。

        Args:
            parent: 親ウィジェット（PanedWindow ペイン）。
            colors: テーマカラー辞書。
        """
        self.colors = colors

        # ── 外枠 ────────────────────────────────────────────────────
        self.container = tk.Frame(parent, bg=colors["frame_bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        # ── ヘッダー ────────────────────────────────────────────────
        self._build_header()

        # ── スクロール可能なフォームエリア ────────────────────────────
        self._build_scroll_area()

        # ── 刃を研ぐ セクション ──────────────────────────────────────
        self._sharpen_entries: dict[str, tk.Entry] = {}
        self._build_sharpen_section()

        # ── 役割・目標 セクション (5セット) ──────────────────────────
        self._role_name_entries: list[tk.Entry] = []
        self._goal_text_areas:   list[tk.Text]  = []
        for i in range(1, 6):
            self._build_role_section(i)

        # スクロール領域のサイズをコンテンツに合わせて更新
        self._inner_frame.update_idletasks()
        self._canvas.config(
            scrollregion=self._canvas.bbox("all")
        )

    # ── ウィジェット構築 ─────────────────────────────────────────────

    def _build_header(self) -> None:
        """タイトル・質問文・日付レンジ・保存ボタンを含むヘッダーを構築する。"""
        header = tk.Frame(self.container, bg=self.colors["frame_bg"], pady=6)
        header.pack(fill=tk.X)

        # タイトル
        tk.Label(
            header,
            text="一週間コンパス",
            font=("Arial", 13, "bold"),
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
        ).pack()

        # 質問文
        tk.Label(
            header,
            text=_QUESTION_TEXT,
            font=("Arial", 9),
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
            justify=tk.CENTER,
        ).pack(pady=(2, 4))

        # 日付レンジ + 保存ボタン 行
        date_row = tk.Frame(header, bg=self.colors["frame_bg"])
        date_row.pack(fill=tk.X, padx=10)

        tk.Label(
            date_row,
            text="Date:",
            font=("Arial", 9),
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
        ).pack(side=tk.LEFT)

        self._date_label = tk.Label(
            date_row,
            text="",
            font=("Arial", 9),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=6,
            pady=2,
            highlightthickness=0,
        )
        self._date_label.pack(side=tk.LEFT, padx=(4, 0), expand=True, fill=tk.X)

        self._save_btn = tk.Label(
            date_row,
            text="保存",
            font=("Arial", 9),
            width=6,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            cursor="hand2",
            padx=4,
            pady=2,
            highlightthickness=0,
        )
        self._save_btn.pack(side=tk.RIGHT, padx=(6, 0))

    def _build_scroll_area(self) -> None:
        """スクロール可能な内部フレームを構築する。"""
        wrapper = tk.Frame(self.container, bg=self.colors["frame_bg"])
        wrapper.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._canvas = tk.Canvas(
            wrapper,
            bg=self.colors["frame_bg"],
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            wrapper, orient="vertical", command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._inner_frame = tk.Frame(self._canvas, bg=self.colors["frame_bg"])
        self._canvas.create_window((0, 0), window=self._inner_frame, anchor="nw")

        self._inner_frame.bind(
            "<Configure>",
            lambda e: self._canvas.config(
                scrollregion=self._canvas.bbox("all")
            ),
        )

        # マウスホイールスクロール（Windows / macOS 対応）
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(
                -1 if e.delta > 0 else 1, "units"
            ),
        )

    def _build_sharpen_section(self) -> None:
        """「刃を研ぐ」セクションを構築する。"""
        outer = tk.Frame(
            self._inner_frame,
            bg=self.colors["frame_bg"],
            highlightthickness=1,
            highlightbackground=self.colors["button_fg"],
            padx=6,
            pady=6,
        )
        outer.pack(fill=tk.X, padx=6, pady=(6, 4))

        tk.Label(
            outer,
            text="役割：刃を研ぐ",
            font=("Arial", 9, "bold"),
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        for label_text, key in _SHARPEN_FIELDS:
            row = tk.Frame(outer, bg=self.colors["frame_bg"])
            row.pack(fill=tk.X, pady=1)

            tk.Label(
                row,
                text=label_text,
                font=("Arial", 9),
                width=10,
                anchor="w",
                bg=self.colors["frame_bg"],
                fg=self.colors["frame_fg"],
            ).pack(side=tk.LEFT)

            entry = tk.Entry(
                row,
                font=("Arial", 9),
                bg=self.colors["button_bg"],
                fg=self.colors["button_fg"],
                insertbackground=self.colors["button_fg"],
                relief=tk.FLAT,
                highlightthickness=1,
                highlightbackground=self.colors["button_fg"],
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._sharpen_entries[key] = entry

    def _build_role_section(self, index: int) -> None:
        """役割・目標の入力セクションを1セット構築する。

        Args:
            index: 役割番号（1〜5）。
        """
        outer = tk.Frame(
            self._inner_frame,
            bg=self.colors["frame_bg"],
            highlightthickness=1,
            highlightbackground=self.colors["button_fg"],
            padx=6,
            pady=6,
        )
        outer.pack(fill=tk.X, padx=6, pady=3)

        # 役割入力行
        role_row = tk.Frame(outer, bg=self.colors["frame_bg"])
        role_row.pack(fill=tk.X, pady=(0, 3))

        tk.Label(
            role_row,
            text=f"役割({index})",
            font=("Arial", 9),
            width=8,
            anchor="w",
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
        ).pack(side=tk.LEFT)

        name_entry = tk.Entry(
            role_row,
            font=("Arial", 9),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            insertbackground=self.colors["button_fg"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.colors["button_fg"],
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._role_name_entries.append(name_entry)

        # 目標入力行（2行テキストエリア）
        goal_row = tk.Frame(outer, bg=self.colors["frame_bg"])
        goal_row.pack(fill=tk.X)

        tk.Label(
            goal_row,
            text=f"目標({index})",
            font=("Arial", 9),
            width=8,
            anchor="nw",
            bg=self.colors["frame_bg"],
            fg=self.colors["frame_fg"],
        ).pack(side=tk.LEFT, anchor="n", pady=(2, 0))

        goal_area = tk.Text(
            goal_row,
            font=("Arial", 9),
            height=2,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            insertbackground=self.colors["button_fg"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.colors["button_fg"],
            wrap=tk.WORD,
        )
        goal_area.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._goal_text_areas.append(goal_area)

    # ── コールバック登録 ─────────────────────────────────────────────

    def bind_save(self, callback: Callable[[], None]) -> None:
        """「保存」ボタンクリック時のコールバックを登録する。"""
        self._save_btn.bind("<Button-1>", lambda e: callback())

    # ── データ入出力 ─────────────────────────────────────────────────

    def set_date_label(self, text: str) -> None:
        """ヘッダーの日付レンジラベルを更新する。

        Args:
            text: 表示する日付レンジ文字列（例: \"2026/03/15 〜 03/21\"）。
        """
        self._date_label.config(text=text)

    def set_data(self, data: dict) -> None:
        """コントローラから受け取ったデータをフォームに反映する。

        Args:
            data: compass_model.CompassModel.load() が返す形式の辞書。
        """
        sharpen = data.get("sharpen", {})
        for key, entry in self._sharpen_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, sharpen.get(key, ""))

        roles = data.get("roles", [])
        for i, (name_entry, goal_area) in enumerate(
            zip(self._role_name_entries, self._goal_text_areas)
        ):
            role = roles[i] if i < len(roles) else {}
            name_entry.delete(0, tk.END)
            name_entry.insert(0, role.get("name", ""))

            goal_area.delete("1.0", tk.END)
            goal_area.insert("1.0", role.get("goal", ""))

    def get_data(self) -> dict:
        """フォームの現在の入力内容を辞書として返す。

        Returns:
            compass_model.CompassModel.save() に渡す形式の辞書。
        """
        return {
            "sharpen": {
                key: entry.get()
                for key, entry in self._sharpen_entries.items()
            },
            "roles": [
                {
                    "name": name_entry.get(),
                    "goal": goal_area.get("1.0", "end-1c"),
                }
                for name_entry, goal_area in zip(
                    self._role_name_entries, self._goal_text_areas
                )
            ],
        }