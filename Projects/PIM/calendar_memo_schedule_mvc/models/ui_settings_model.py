"""
UIレイアウト設定のCRUD操作を担当するモデルクラス。
"""

import sqlite3
from config import DB_PATH, WIN_WIDTH, WIN_HEIGHT

# main_view.py の初期比率と同じ値からデフォルトを算出する
_LEFT_RATIO:     float = 0.25
_CENTER_RATIO:   float = 0.50
_VERTICAL_RATIO: float = 0.475


class UiSettingsModel:
    """UIレイアウト設定のDBアクセスを管理するクラス。

    ui_settings テーブルをキー・バリューストアとして使い、
    サッシ位置などのウィンドウ状態を永続化する。
    """

    # 管理するキーとデフォルト値の対応
    # デフォルト値は main_view.py の初期比率と同一になるよう config 定数から算出する
    _DEFAULTS: dict[str, int] = {
        "sash_h0": int(WIN_WIDTH  * _LEFT_RATIO),    # 左 / 中央境界
        "sash_h1": int(WIN_WIDTH  * _CENTER_RATIO),  # 中央 / 右境界
        "sash_v0": int(WIN_HEIGHT * _VERTICAL_RATIO), # カレンダー / メモ境界
    }

    def load(self) -> dict[str, int]:
        """保存済みのUI設定を読み込む。

        Returns:
            {"sash_h0": int, "sash_h1": int, "sash_v0": int} 形式の辞書。
            DBに保存されていないキーは _DEFAULTS の値で補完する。
        """
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT key, value FROM ui_settings"
            ).fetchall()
        saved = {k: int(v) for k, v in rows}
        return {k: saved.get(k, default) for k, default in self._DEFAULTS.items()}

    def save(self, settings: dict[str, int]) -> None:
        """UI設定をDBに保存（既存キーは上書き）する。

        Args:
            settings: {"sash_h0": int, ...} 形式の辞書。
                      _DEFAULTS に含まれないキーは無視する。
        """
        rows = [
            (k, str(v))
            for k, v in settings.items()
            if k in self._DEFAULTS
        ]
        if not rows:
            return
        with sqlite3.connect(DB_PATH) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO ui_settings (key, value) VALUES (?, ?)",
                rows,
            )
