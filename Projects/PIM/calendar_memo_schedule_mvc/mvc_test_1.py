from models.database import init_db
from models.compass_model import CompassModel

init_db()
m = CompassModel()

# 存在しない週は空辞書が返る
d = m.load("2026-03-15")
assert d["sharpen"]["body"] == ""
assert len(d["roles"]) == 5

# 書き込みと再読み込み
test_data = {
    "sharpen": {
        "body": "筋トレ", "social": "SNS整理",
        "intellect": "読書", "spirit": "瞑想"
    },
    "roles": [
        {"name": "父親", "goal": "毎日一緒に夕食"},
        {"name": "エンジニア", "goal": "設計書を完成させる\n週3回レビュー"},
        {"name": "", "goal": ""},
        {"name": "", "goal": ""},
        {"name": "", "goal": ""},
    ],
}
m.save("2026-03-15", test_data)

d2 = m.load("2026-03-15")
assert d2["sharpen"]["body"] == "筋トレ"
assert d2["roles"][0]["name"] == "父親"
assert d2["roles"][1]["goal"] == "設計書を完成させる\n週3回レビュー"

print("OK")
