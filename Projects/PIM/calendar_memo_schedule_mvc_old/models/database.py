"""
データベースの初期化を担当するモジュール。
"""

import sqlite3
import textwrap
from config import DB_PATH


def init_db() -> None:
    """統合データベースのテーブルを初期化する。"""
    with sqlite3.connect(DB_PATH) as conn:
        # ノート用テーブル
        conn.execute(textwrap.dedent("""\
            CREATE TABLE IF NOT EXISTS cal_notes (
                date       TEXT     PRIMARY KEY,
                filename   TEXT     NOT NULL,
                file_data  BLOB     NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # スケジュール用テーブル
        conn.execute(textwrap.dedent("""\
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER  PRIMARY KEY AUTOINCREMENT,
                event_date TEXT     NOT NULL,
                category   TEXT     NOT NULL,
                start_time TEXT     NOT NULL,
                end_time   TEXT     NOT NULL,
                task_name  TEXT     NOT NULL
            )
        """))
