"""
スケジュールデータのCRUD操作とキャッシュ管理を担当するモデルクラス。
"""

import sqlite3
import textwrap
from datetime import date, timedelta
from config import DB_PATH


class ScheduleModel:
    """スケジュールのDBアクセスとデータキャッシュを管理するクラス。"""

    def __init__(self) -> None:
        self._db_path: str = DB_PATH
        # { "YYYY-MM-DD": [(category, start_time, end_time, task_name), ...] }
        self._cache: dict[str, list[tuple]] = {}

    @property
    def cache(self) -> dict[str, list[tuple]]:
        """現在のスケジュールキャッシュを返す。"""
        return self._cache

    def load(self, selected_date: date, mode: str) -> None:
        """選択日または週のスケジュールデータをDBから取得してキャッシュに格納する。

        Args:
            selected_date: 選択中の日付。
            mode: "daily"（日次）または "weekly"（週次）。
        """
        self._cache.clear()
        with sqlite3.connect(self._db_path) as conn:
            if mode == "daily":
                d_str = str(selected_date)
                cur = conn.execute(
                    textwrap.dedent("""\
                        SELECT category, start_time, end_time, task_name
                        FROM events
                        WHERE event_date = ?
                    """),
                    (d_str,),
                )
                self._cache[d_str] = cur.fetchall()
            else:
                # 週次モード: 選択日の日曜日〜土曜日を一括取得
                offset = (selected_date.weekday() + 1) % 7
                start = selected_date - timedelta(days=offset)
                dates = [str(start + timedelta(days=i)) for i in range(7)]
                placeholders = ",".join("?" * 7)
                cur = conn.execute(
                    textwrap.dedent(f"""\
                        SELECT event_date, start_time, end_time, task_name
                        FROM events
                        WHERE event_date IN ({placeholders})
                        AND category = ?
                    """),
                    (*dates, "plan"),
                )
                for row in cur.fetchall():
                    event_date = row[0]
                    self._cache.setdefault(event_date, []).append(row[1:])

    def save(
        self,
        date_str: str,
        category: str,
        start: str,
        end: str,
        task: str,
    ) -> None:
        """新規イベントをDBに追加する。

        Args:
            date_str: "YYYY-MM-DD" 形式の日付文字列。
            category: イベントカテゴリ（"plan" または "actual"）。
            start: 開始時刻（"HH:MM" 形式）。
            end: 終了時刻（"HH:MM" 形式）。
            task: タスク名。
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                textwrap.dedent("""\
                    INSERT INTO events (
                        event_date, category, start_time, end_time, task_name
                    ) VALUES (?, ?, ?, ?, ?)
                """),
                (date_str, category, start, end, task),
            )

    def update(self, event_id: int, start: str, end: str, task: str) -> None:
        """既存イベントをDBで更新する。

        Args:
            event_id: 更新対象のイベントID。
            start: 開始時刻（"HH:MM" 形式）。
            end: 終了時刻（"HH:MM" 形式）。
            task: タスク名。
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "UPDATE events "
                "SET start_time=?, end_time=?, task_name=? "
                "WHERE id=?",
                (start, end, task, event_id),
            )

    def delete(self, event_id: int) -> None:
        """指定IDのイベントをDBから削除する。

        Args:
            event_id: 削除対象のイベントID。
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM events WHERE id=?", (event_id,))

    def get_events_for_category(
        self,
        date_str: str,
        category: str,
    ) -> list[tuple]:
        """指定日・カテゴリのイベント一覧を取得する。

        Args:
            date_str: "YYYY-MM-DD" 形式の日付文字列。
            category: イベントカテゴリ（"plan" または "actual"）。

        Returns:
            [(id, start_time, end_time, task_name), ...] 形式のリスト。
        """
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.execute(
                "SELECT id, start_time, end_time, task_name "
                "FROM events "
                "WHERE category=? AND event_date=? "
                "ORDER BY start_time ASC",
                (category, date_str),
            )
            return cur.fetchall()
