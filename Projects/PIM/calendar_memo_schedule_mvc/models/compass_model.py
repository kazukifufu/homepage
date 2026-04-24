"""
一週間コンパスデータのCRUD操作を担当するモデルクラス。
"""

import sqlite3
import textwrap
from config import DB_PATH


class CompassModel:
    """一週間コンパスのDBアクセスを管理するクラス。

    週の開始日（日曜日）をキーとして、役割・目標データを1行で管理する。
    """

    # 刃を研ぐ: 4カテゴリのDBカラム名
    _SHARPEN_COLS: tuple[str, ...] = (
        "sharpen_body",
        "sharpen_social",
        "sharpen_intellect",
        "sharpen_spirit",
    )

    # 役割・目標: 5セット分のDBカラム名
    _ROLE_COLS: tuple[str, ...] = tuple(
        col
        for i in range(1, 6)
        for col in (f"role{i}_name", f"role{i}_goal")
    )

    def load(self, week_start: str) -> dict:
        """指定週のコンパスデータをDBから取得する。

        Args:
            week_start: 週の開始日（日曜日）を表す \"YYYY-MM-DD\" 形式の文字列。

        Returns:
            以下の構造を持つ辞書。存在しない場合は空値で初期化された辞書を返す。
            {
                "sharpen": {"body": str, "social": str,
                            "intellect": str, "spirit": str},
                "roles": [{"name": str, "goal": str}, ...],  # 5要素
            }
        """
        all_cols = self._SHARPEN_COLS + self._ROLE_COLS
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                f"SELECT {', '.join(all_cols)} "
                "FROM compass_roles WHERE week_start = ?",
                (week_start,),
            ).fetchone()

        if row is None:
            return self._empty_data()

        sharpen_vals = row[:4]
        role_vals = row[4:]

        return {
            "sharpen": {
                "body":      sharpen_vals[0] or "",
                "social":    sharpen_vals[1] or "",
                "intellect": sharpen_vals[2] or "",
                "spirit":    sharpen_vals[3] or "",
            },
            "roles": [
                {
                    "name": role_vals[i * 2] or "",
                    "goal": role_vals[i * 2 + 1] or "",
                }
                for i in range(5)
            ],
        }

    def save(self, week_start: str, data: dict) -> None:
        """コンパスデータをDBに保存（既存の場合は上書き）する。

        Args:
            week_start: 週の開始日（日曜日）を表す \"YYYY-MM-DD\" 形式の文字列。
            data: load() が返す形式と同じ辞書。
        """
        sharpen = data.get("sharpen", {})
        roles = data.get("roles", [{}] * 5)

        values = (
            week_start,
            sharpen.get("body", ""),
            sharpen.get("social", ""),
            sharpen.get("intellect", ""),
            sharpen.get("spirit", ""),
            *(
                val
                for role in roles
                for val in (role.get("name", ""), role.get("goal", ""))
            ),
        )

        all_cols = ("week_start",) + self._SHARPEN_COLS + self._ROLE_COLS
        placeholders = ", ".join("?" * len(all_cols))

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                textwrap.dedent(f"""\
                    INSERT OR REPLACE INTO compass_roles (
                        {', '.join(all_cols)}
                    ) VALUES ({placeholders})
                """),
                values,
            )

    # ── ユーティリティ ────────────────────────────────────────────────

    @staticmethod
    def _empty_data() -> dict:
        """空値で初期化されたコンパスデータ辞書を返す。"""
        return {
            "sharpen": {
                "body": "", "social": "", "intellect": "", "spirit": "",
            },
            "roles": [{"name": "", "goal": ""} for _ in range(5)],
        }
