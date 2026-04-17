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

        # 一週間コンパス用テーブル（週の開始日＝日曜日をキーとする）
        conn.execute(textwrap.dedent("""\
            CREATE TABLE IF NOT EXISTS compass_roles (
                week_start        TEXT PRIMARY KEY,
                sharpen_body      TEXT NOT NULL DEFAULT '',
                sharpen_social    TEXT NOT NULL DEFAULT '',
                sharpen_intellect TEXT NOT NULL DEFAULT '',
                sharpen_spirit    TEXT NOT NULL DEFAULT '',
                role1_name        TEXT NOT NULL DEFAULT '',
                role1_goal        TEXT NOT NULL DEFAULT '',
                role2_name        TEXT NOT NULL DEFAULT '',
                role2_goal        TEXT NOT NULL DEFAULT '',
                role3_name        TEXT NOT NULL DEFAULT '',
                role3_goal        TEXT NOT NULL DEFAULT '',
                role4_name        TEXT NOT NULL DEFAULT '',
                role4_goal        TEXT NOT NULL DEFAULT '',
                role5_name        TEXT NOT NULL DEFAULT '',
                role5_goal        TEXT NOT NULL DEFAULT '',
                updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
