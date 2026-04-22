import sqlite3
from models.database import init_db
from config import DB_PATH

init_db()

with sqlite3.connect(DB_PATH) as conn:
    # 書き込み: INSERT OR REPLACE でなければ追加・あれば上書き
    defaults = {
        "sash_h0": "300",
        "sash_h1": "600",
        "sash_v0": "380",
    }
    conn.executemany(
        "INSERT OR REPLACE INTO ui_settings (key, value) VALUES (?, ?)",
        defaults.items(),
    )

    # 読み出し
    rows = conn.execute("SELECT key, value FROM ui_settings").fetchall()
    settings = {k: int(v) for k, v in rows}
    print(settings)
    # → {'sash_h0': 300, 'sash_h1': 600, 'sash_v0': 380}

    # 上書き確認（sash_h0 だけ変更）
    conn.execute(
        "INSERT OR REPLACE INTO ui_settings (key, value) VALUES (?, ?)",
        ("sash_h0", "350"),
    )
    val = conn.execute(
        "SELECT value FROM ui_settings WHERE key = 'sash_h0'"
    ).fetchone()[0]
    print(int(val))  # → 350
