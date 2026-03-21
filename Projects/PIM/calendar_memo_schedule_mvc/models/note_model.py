"""
メモデータのCRUD操作を担当するモデルクラス。
"""

import sqlite3
from config import DB_PATH


class NoteModel:
    """メモのDBアクセスを管理するクラス。"""

    def load(self, date_str: str) -> bytes | None:
        """
        指定日付のメモをDBから取得する。
        :param date_str: "YYYY-MM-DD" 形式の日付文字列
        :return: メモのバイトデータ、存在しない場合は None
        """
        with sqlite3.connect(DB_PATH) as conn:
            res = conn.execute(
                "SELECT file_data FROM cal_notes WHERE date = ?", (date_str,)
            ).fetchone()
        return res[0] if res else None

    def save(self, date_str: str, text: str) -> None:
        """
        メモをDBに保存（既存の場合は上書き）する。
        :param date_str: "YYYY-MM-DD" 形式の日付文字列
        :param text: 保存するメモのテキスト
        """
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                'INSERT OR REPLACE INTO cal_notes (date, filename, file_data) VALUES (?, ?, ?)',
                (date_str, f"{date_str}.md", text.encode('utf-8'))
            )

    def delete(self, date_str: str) -> None:
        """
        指定日付のメモをDBから削除する。
        :param date_str: "YYYY-MM-DD" 形式の日付文字列
        """
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('DELETE FROM cal_notes WHERE date = ?', (date_str,))
