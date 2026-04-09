"""
カレンダー・メモ・スケジュール統合管理アプリの起動スクリプト。

tkinter を使ったデスクトップアプリケーションで、
月間カレンダーの表示・日付ごとのメモ管理・
日次/週次スケジュールの記録と可視化を一画面で提供する。

Usage:
    python main.py           # ライトモード
    python main.py dark      # ダークモード
"""


import tkinter as tk
from controllers.app_controller import AppController


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    AppController(root)
    # ウィンドウを一度描画確定させてからイベントループへ移行する。
    # これにより after() コールバック内で winfo_width() が正しい値を返す。
    root.update_idletasks()
    root.mainloop()


if __name__ == "__main__":
    main()
