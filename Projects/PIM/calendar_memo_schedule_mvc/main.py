"""
アプリケーションのエントリーポイント。
"""

import tkinter as tk
from controllers.app_controller import AppController


def main() -> None:
    """アプリケーションを起動する。"""
    root = tk.Tk()
    AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
