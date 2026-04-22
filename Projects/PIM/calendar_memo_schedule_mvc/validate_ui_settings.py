import sqlite3
from models.database import init_db
from config import DB_PATH

init_db()

with sqlite3.connect(DB_PATH) as conn:
    # テーブルの存在確認
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print([t[0] for t in tables])
    # → ['cal_notes', 'compass_roles', 'events', 'ui_settings']

    # テーブル構造の確認
    cols = conn.execute("PRAGMA table_info(ui_settings)").fetchall()
    for col in cols:
        print(col)
    # → (0, 'key', 'TEXT', 0, None, 1)
    # → (1, 'value', 'TEXT', 1, None, 0)
    # → (2, 'updated_at', 'DATETIME', 0, 'CURRENT_TIMESTAMP', 0)
