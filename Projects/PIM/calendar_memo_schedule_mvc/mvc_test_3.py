import tkinter as tk
from views.compass_view import CompassView

root = tk.Tk()
root.geometry("400x800")

# ダークモードのカラー定義
#colors = {
#    "frame_bg": "#1e2633", "frame_fg": "#ccd4e0",
#    "button_fg": "#ccd4e0", "button_bg": "#2c3848",
#    "cal_fg_sat": "#78b0d8",
#}
# ライトモードのカラー定義
colors = {
    "frame_bg": "#f7f3ee", "frame_fg": "#3c3530",
    "button_fg": "#3c3530", "button_bg": "#ece5db",
    "cal_fg_sat": "#3a78a8",
}

cv = CompassView(root, colors)

# 第1回のCompassModelが返す形式と同じデータを渡してみる
test_data = {
    "sharpen": {
        "body": "筋トレ", "social": "SNS整理",
        "intellect": "読書", "spirit": "瞑想",
    },
    "roles": [
        {"name": "父親", "goal": "毎日一緒に夕食"},
        {"name": "エンジニア", "goal": "設計書を完成させる\n週3回レビュー"},
        {"name": "", "goal": ""},
        {"name": "", "goal": ""},
        {"name": "", "goal": ""},
    ],
}
cv.set_data(test_data)
cv.set_date_label("2026/03/15 〜 03/21")

# 保存ボタンが押されたときの確認
cv.bind_save(lambda: print("保存:", cv.get_data()))

root.mainloop()
