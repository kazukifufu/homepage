"""
アプリケーション全体で使用する定数を管理するモジュール。
"""

from typing import Final

# アプリケーション設定
APP_NAME: Final[str] = "カレンダーアプリ - カレンダー・メモ・スケジュール機能"
WIN_WIDTH: Final[int] = 1200
WIN_HEIGHT: Final[int] = 800
WIN_SIZE: Final[str] = f"{WIN_WIDTH}x{WIN_HEIGHT}"
DB_PATH: Final[str] = "calendar_memo_schedule_app.db"

# スケジュール描画設定
HOUR_HEIGHT: Final[int] = 40
START_HOUR: Final[int] = 0
END_HOUR: Final[int] = 24
TIME_AXIS_WIDTH: Final[int] = 70

# カレンダー表示設定
DATE_FONT_SIZE: Final[int] = 12
CELL_HEIGHT: Final[int] = 70
